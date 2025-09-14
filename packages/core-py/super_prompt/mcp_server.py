# packages/core-py/super_prompt/mcp_server.py
# SECURITY: MCP-only access - Direct CLI calls are blocked
# pip dep: mcp >= 0.4.0  (pyproject.toml 또는 setup.cfg에 추가)
import os
import sys
import asyncio
from pathlib import Path

# MCP SDK (Anthropic 공개 라이브러리)
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from .paths import package_root, project_root, project_data_dir
from .mcp_register import ensure_cursor_mcp_registered, ensure_codex_mcp_registered
from .mode_store import get_mode, set_mode
import shutil, sys
import time
import json
from typing import Dict, Any, Optional
from contextlib import contextmanager

# SECURITY: Prevent direct execution
if __name__ != "__main__":
    # If imported directly (not run as MCP server), block access
    if not os.environ.get("MCP_SERVER_MODE"):
        print("-------- ERROR: Super Prompt MCP server must be run through MCP protocol only.", file=sys.stderr, flush=True)
        print("-------- Direct Python execution is not allowed.", file=sys.stderr, flush=True)
        print("-------- Use MCP client tools: sp.init(), sp.refresh(), sp.list_commands(), etc.", file=sys.stderr, flush=True)
        sys.exit(1)

# Span 관리 클래스
class SpanManager:
    def __init__(self):
        self.spans: Dict[str, Dict[str, Any]] = {}
        self._span_counter = 0

    def start_span(self, meta: Dict[str, Any]) -> str:
        """새로운 span 시작"""
        span_id = f"span_{self._span_counter}"
        self._span_counter += 1

        self.spans[span_id] = {
            'id': span_id,
            'start_time': time.time(),
            'meta': meta,
            'events': [],
            'status': 'active'
        }

        print(f"-------- memory: span started {span_id} for {meta.get('commandId', 'unknown')}", file=sys.stderr, flush=True)
        return span_id

    def write_event(self, span_id: str, event: Dict[str, Any]) -> None:
        """span에 이벤트 기록"""
        if span_id in self.spans:
            event_with_time = {
                'timestamp': time.time(),
                **event
            }
            self.spans[span_id]['events'].append(event_with_time)
            print(f"-------- memory: event recorded in {span_id}", file=sys.stderr, flush=True)

    def end_span(self, span_id: str, status: str = 'ok', extra: Optional[Dict[str, Any]] = None) -> None:
        """span 종료"""
        if span_id in self.spans:
            span = self.spans[span_id]
            span['end_time'] = time.time()
            span['duration'] = span['end_time'] - span['start_time']
            span['status'] = status
            if extra:
                span['extra'] = extra

            print(f"-------- memory: span ended {span_id} status={status} duration={span['duration']:.2f}s", file=sys.stderr, flush=True)

            # 메모리에 유지 (실제로는 파일이나 DB에 저장)
            # TODO: 영구 저장소에 저장

# 전역 span 관리자
span_manager = SpanManager()

# Span 컨텍스트 매니저
@contextmanager
def memory_span(command_id: str, user_id: Optional[str] = None):
    """메모리 span 컨텍스트 매니저"""
    span_id = span_manager.start_span({
        'commandId': command_id,
        'userId': user_id
    })

    try:
        yield span_id
    except Exception as e:
        span_manager.write_event(span_id, {
            'type': 'error',
            'message': str(e),
            'stack': getattr(e, '__traceback__', None)
        })
        span_manager.end_span(span_id, 'error', {'error': str(e)})
        raise
    else:
        span_manager.end_span(span_id, 'ok')

mcp = FastMCP("super-prompt")

def _validate_assets():
    pkg = package_root()
    commands = (pkg / "packages" / "cursor-assets" / "commands" / "super-prompt")
    personas = (pkg / "packages" / "cursor-assets" / "manifests" / "personas.yaml")
    if not commands.exists() or not personas.exists():
        raise RuntimeError("Missing assets in package tarball. No fallback allowed.")
    # 폴백 4개만 있는지 대략 검증(최소 8개 이상 기대값 예시)
    n = len(list(commands.glob("*.md")))
    if n < 8:
        raise RuntimeError(f"Too few commands found ({n}). Fallback disabled.")

def _init_impl(force: bool = False) -> str:
    _validate_assets()
    pr = project_root()
    data = project_data_dir()
    data.mkdir(parents=True, exist_ok=True)
    # 에셋 복사(필요 파일만, 덮어쓰기 정책은 force로 제어)
    src = package_root() / "packages" / "cursor-assets"
    # 예시: commands/super-prompt/*, rules/* 등 선택 복사
    _copytree(src / "commands", pr / ".cursor" / "commands", force=force)
    _copytree(src / "rules", pr / ".cursor" / "rules", force=force)
    # 프로젝트용 디렉터리 보장
    for d in ["specs", "memory", ".codex"]:
        (pr / d).mkdir(parents=True, exist_ok=True)
    # MCP 자동 등록
    ensure_cursor_mcp_registered(pr)  # .cursor/mcp.json 병합
    try:
        ensure_codex_mcp_registered(pr)  # 선택: ~/.codex/config.toml 병합
    except Exception:
        pass
    return f"Initialized at {pr}"

def _copytree(src, dst, force=False):
    if not src.exists(): return
    dst.mkdir(parents=True, exist_ok=True)
    for p in src.rglob("*"):
        rel = p.relative_to(src)
        t = dst / rel
        if p.is_dir():
            t.mkdir(parents=True, exist_ok=True)
        else:
            if t.exists() and not force:
                continue
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, t)

@mcp.tool()  # 도구명: sp.version
def version() -> TextContent:
    """Get Super Prompt version"""
    with memory_span('sp.version'):
        # 필요 시 패키지 버전 리턴
        from importlib.metadata import version as _v
        try:
            ver = _v("super-prompt")
        except Exception:
            ver = "unknown"
        return TextContent(type="text", text=f"Super Prompt v{ver}")

@mcp.tool()  # 도구명: sp.init
def init(force: bool = False) -> TextContent:
    """Initialize Super Prompt for current project"""
    with memory_span('sp.init'):
        # MCP 전용 강제: 백도어 금지
        if os.environ.get("SUPER_PROMPT_ALLOW_INIT", "").lower() not in ("1", "true", "yes"):
            raise PermissionError(
                "MCP: init/refresh는 기본적으로 비활성화입니다. "
                "환경변수 SUPER_PROMPT_ALLOW_INIT=true 설정 후 다시 시도하세요."
            )

        # 헬스체크 수행
        health_span = span_manager.start_span({
            'commandId': 'sp.init:health',
            'userId': None
        })
        span_manager.write_event(health_span, {
            'type': 'health',
            'timestamp': time.time()
        })
        span_manager.end_span(health_span, 'ok')
        print("-------- MCP memory: healthcheck OK", file=sys.stderr, flush=True)

        msg = _init_impl(force=force)
        return TextContent(type="text", text=msg)

@mcp.tool()  # 도구명: sp.refresh
def refresh() -> TextContent:
    """Refresh Super Prompt assets in current project"""
    with memory_span('sp.refresh'):
        # MCP 전용 강제: 백도어 금지
        if os.environ.get("SUPER_PROMPT_ALLOW_INIT", "").lower() not in ("1", "true", "yes"):
            raise PermissionError(
                "MCP: init/refresh는 기본적으로 비활성화입니다. "
                "환경변수 SUPER_PROMPT_ALLOW_INIT=true 설정 후 다시 시도하세요."
            )
        msg = _init_impl(force=True)
        return TextContent(type="text", text=msg)

@mcp.tool()  # 도구명: sp.list_commands
def list_commands() -> TextContent:
    """List available Super Prompt commands"""
    with memory_span('sp.list_commands'):
        # 배포물에 실제로 들어간 커맨드 개수 확인용
        commands_dir = _pkg_root() / "packages" / "cursor-assets" / "commands" / "super-prompt"
        count = 0
        files = []
        if commands_dir.exists():
            for p in sorted(commands_dir.glob("*.md")):
                files.append(p.name)
                count += 1
        text = f"Available commands: {count}\n" + "\n".join(files)
        return TextContent(type="text", text=text)

@mcp.tool()  # 도구명: sp.list_personas
def list_personas() -> TextContent:
    """List available Super Prompt personas"""
    with memory_span('sp.list_personas'):
        from .personas.loader import PersonaLoader
        loader = PersonaLoader()
        loader.load_manifest()
        personas = loader.list_personas()

        if not personas:
            return TextContent(type="text", text="No personas loaded. Try running init first.")

        text = f"Available personas: {len(personas)}\n"
        for persona in personas:
            text += f"- {persona['name']}: {persona['description']}\n"

    return TextContent(type="text", text=text)

@mcp.tool()  # 도구명: sp.mode_get
def mode_get() -> TextContent:
    """Get current LLM mode (gpt|grok)"""
    with memory_span('sp.mode_get'):
        mode = get_mode()
        return TextContent(type="text", text=mode)

@mcp.tool()  # 도구명: sp.mode_set
def mode_set(mode: str) -> TextContent:
    """Set LLM mode to 'gpt' or 'grok'"""
    with memory_span('sp.mode_set'):
        m = set_mode(mode)
        print(f"-------- mode: set to {m}", file=sys.stderr, flush=True)
        return TextContent(type="text", text=f"mode set to {m}")

@mcp.tool()  # 도구명: sp.grok_mode_on
def grok_mode_on() -> TextContent:
    """Switch LLM mode to grok"""
    with memory_span('sp.grok_mode_on'):
        set_mode('grok')
        print("-------- mode: set to grok", file=sys.stderr, flush=True)
        return TextContent(type="text", text="mode set to grok")

@mcp.tool()  # 도구명: sp.gpt_mode_on
def gpt_mode_on() -> TextContent:
    """Switch LLM mode to gpt"""
    with memory_span('sp.gpt_mode_on'):
        set_mode('gpt')
        print("-------- mode: set to gpt", file=sys.stderr, flush=True)
        return TextContent(type="text", text="mode set to gpt")

if __name__ == "__main__":
    mcp.run()  # stdio로 MCP 서버 실행
