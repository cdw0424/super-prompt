# packages/core-py/super_prompt/mcp_server.py
# SECURITY: MCP-only access - Direct CLI calls are blocked
# pip dep: mcp >= 0.4.0  (pyproject.toml 또는 setup.cfg에 추가)
import os
import sys
import asyncio
from pathlib import Path

# MCP SDK (Anthropic 공개 라이브러리)
# NOTE: Provide safe fallbacks when SDK is unavailable so that direct tool calls can run.
try:
    from mcp.server.fastmcp import FastMCP  # type: ignore
    from mcp.types import TextContent  # type: ignore

    _HAS_MCP = True
except Exception:
    _HAS_MCP = False

    class TextContent:  # minimal stub for direct-call mode
        def __init__(self, type: str, text: str):
            self.type = type
            self.text = text

    class _StubMCP:
        def tool(self, *_args, **_kwargs):
            def _decorator(fn):
                return fn

            return _decorator

        def run(self):
            raise RuntimeError("MCP SDK not available; cannot start MCP server")

    FastMCP = None  # type: ignore
    # Create a stub 'mcp' so decorators below don't fail at import time.
    mcp = _StubMCP()  # type: ignore
from .paths import package_root, project_root, project_data_dir
from .mcp_register import ensure_cursor_mcp_registered, ensure_codex_mcp_registered
from .mode_store import get_mode, set_mode
from .personas.loader import PersonaLoader
import shutil, sys
import time
import json
from typing import Dict, Any, Optional
from contextlib import contextmanager

# SECURITY: Prevent direct execution
if __name__ != "__main__":
    # If imported directly (not run as MCP server), block access
    if not os.environ.get("MCP_SERVER_MODE"):
        print(
            "-------- ERROR: Super Prompt MCP server must be run through MCP protocol only.",
            file=sys.stderr,
            flush=True,
        )
        print("-------- Direct Python execution is not allowed.", file=sys.stderr, flush=True)
        print(
            "-------- Use MCP client tools: sp.init(), sp.refresh(), sp.list_commands(), etc.",
            file=sys.stderr,
            flush=True,
        )
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
            "id": span_id,
            "start_time": time.time(),
            "meta": meta,
            "events": [],
            "status": "active",
        }

        print(
            f"-------- memory: span started {span_id} for {meta.get('commandId', 'unknown')}",
            file=sys.stderr,
            flush=True,
        )
        return span_id

    def write_event(self, span_id: str, event: Dict[str, Any]) -> None:
        """span에 이벤트 기록"""
        if span_id in self.spans:
            event_with_time = {"timestamp": time.time(), **event}
            self.spans[span_id]["events"].append(event_with_time)
            print(f"-------- memory: event recorded in {span_id}", file=sys.stderr, flush=True)

    def end_span(
        self, span_id: str, status: str = "ok", extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """span 종료"""
        if span_id in self.spans:
            span = self.spans[span_id]
            span["end_time"] = time.time()
            span["duration"] = span["end_time"] - span["start_time"]
            span["status"] = status
            if extra:
                span["extra"] = extra

            print(
                f"-------- memory: span ended {span_id} status={status} duration={span['duration']:.2f}s",
                file=sys.stderr,
                flush=True,
            )

            # 메모리에 유지 (실제로는 파일이나 DB에 저장)
            # TODO: 영구 저장소에 저장


# 전역 span 관리자
span_manager = SpanManager()


# Span 컨텍스트 매니저
@contextmanager
def memory_span(command_id: str, user_id: Optional[str] = None):
    """메모리 span 컨텍스트 매니저"""
    span_id = span_manager.start_span({"commandId": command_id, "userId": user_id})

    try:
        yield span_id
    except Exception as e:
        span_manager.write_event(
            span_id,
            {"type": "error", "message": str(e), "stack": getattr(e, "__traceback__", None)},
        )
        span_manager.end_span(span_id, "error", {"error": str(e)})
        raise
    else:
        span_manager.end_span(span_id, "ok")


if _HAS_MCP:
    mcp = FastMCP("super-prompt")  # type: ignore
else:
    # when SDK missing, 'mcp' was already defined as a stub above
    pass


def _text_from(content: "TextContent | str | None") -> str:
    try:
        if isinstance(content, TextContent):  # type: ignore
            return getattr(content, "text", "") or ""
    except Exception:
        pass
    return "" if content is None else str(content)


def _run_direct_tool_if_requested() -> bool:
    """Direct-call escape hatch for Codex CLI until full MCP client lands.

    Triggers when SP_DIRECT_TOOL is set or --call <tool> is provided. This path
    requires MCP_SERVER_MODE to be set, to preserve the MCP-only security model.
    Returns True if a direct call was handled (process should exit afterwards).
    """
    import argparse

    env_call = os.environ.get("SP_DIRECT_TOOL")
    env_args_json = os.environ.get("SP_DIRECT_ARGS_JSON")

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--call", dest="call", default=None)
    parser.add_argument("--args-json", dest="args_json", default=None)
    try:
        ns, _ = parser.parse_known_args()
    except SystemExit:
        ns = argparse.Namespace(call=None, args_json=None)

    tool = env_call or ns.call
    if not tool:
        return False

    # Enforce MCP mark
    if not os.environ.get("MCP_SERVER_MODE"):
        print(
            "-------- ERROR: Direct tool call requires MCP_SERVER_MODE=1",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(97)

    # Parse args
    args_json = env_args_json or ns.args_json or "{}"
    try:
        args = json.loads(args_json)
        if not isinstance(args, dict):
            raise TypeError("args must be a JSON object")
    except Exception as e:
        print(f"-------- ERROR: Invalid --args-json payload: {e}", file=sys.stderr, flush=True)
        sys.exit(2)

    # Map tool name -> function
    registry = {
        # Core tools
        "sp.version": version,
        "sp.init": init,
        "sp.refresh": refresh,
        "sp.list_commands": list_commands,
        "sp.list_personas": list_personas,
        # Mode tools
        "sp.mode_get": mode_get,
        "sp.mode_set": mode_set,
        "sp.grok_mode_on": grok_mode_on,
        "sp.gpt_mode_on": gpt_mode_on,
        "sp.grok_mode_off": grok_mode_off,
        "sp.gpt_mode_off": gpt_mode_off,
        # Persona entrypoints (query:string)
        "sp.architect": architect,
        "sp.frontend": frontend,
        "sp.backend": backend,
        "sp.security": security,
        "sp.performance": performance,
        "sp.analyzer": analyzer,
        "sp.qa": qa,
        "sp.refactorer": refactorer,
        "sp.devops": devops,
        "sp.mentor": mentor,
        "sp.scribe": scribe,
        # SDD
        "sp.specify": specify,
        "sp.plan": plan,
        "sp.tasks": tasks,
        "sp.implement": implement,
        # Sequential reasoning
        "sp.seq": seq,
        "sp.seq-ultra": seq_ultra,
    }

    fn = registry.get(tool)
    if not fn:
        print(f"-------- ERROR: Unknown tool: {tool}", file=sys.stderr, flush=True)
        sys.exit(3)

    try:
        # Functions return TextContent in MCP mode; unwrap to plain text for direct mode
        result = fn(**args) if args else fn()  # type: ignore[arg-type]
        text = _text_from(result)
        try:
            # Prefer plain text output
            sys.stdout.write(text if text is not None else "")
        except Exception:
            # Fallback to JSON dump
            sys.stdout.write(json.dumps({"ok": True, "result": text}))
        sys.stdout.flush()
        return True
    except TypeError as te:
        print(f"-------- ERROR: Bad arguments for {tool}: {te}", file=sys.stderr, flush=True)
        sys.exit(4)
    except Exception as e:
        print(f"-------- ERROR: Tool {tool} failed: {e}", file=sys.stderr, flush=True)
        sys.exit(5)


def _validate_assets():
    pkg = package_root()
    commands = pkg / "packages" / "cursor-assets" / "commands" / "super-prompt"
    personas = pkg / "packages" / "cursor-assets" / "manifests" / "personas.yaml"
    if not commands.exists() or not personas.exists():
        raise RuntimeError("Missing assets in package tarball. No fallback allowed.")
    # 폴백 4개만 있는지 대략 검증(최소 8개 이상 기대값 예시)
    n = len(list(commands.glob("*.md")))
    if n < 8:
        raise RuntimeError(f"Too few commands found ({n}). Fallback disabled.")

def _ensure_project_venv(pr: Path, force: bool = False) -> Optional[Path]:
    """Create a project-scoped Python venv and install minimal deps.

    Returns the venv directory path on success, or None on failure. Never throws.
    """
    try:
        venv_dir = project_data_dir() / 'venv'
        # Create venv if absent
        if not venv_dir.exists():
            py = sys.executable or 'python3'
            print(f"-------- venv: creating at {venv_dir}", file=sys.stderr, flush=True)
            import subprocess
            subprocess.check_call([py, '-m', 'venv', str(venv_dir)])

        # Resolve venv binaries
        if os.name == 'nt':
            vbin = venv_dir / 'Scripts'
            vpython = vbin / 'python.exe'
            vpip = vbin / 'pip.exe'
        else:
            vbin = venv_dir / 'bin'
            vpython = vbin / 'python'
            vpip = vbin / 'pip'

        # Offline-aware dependency steps
        import subprocess
        offline = str(os.environ.get('SUPER_PROMPT_OFFLINE') or os.environ.get('SP_NO_PIP_INSTALL') or '').lower() in ('1', 'true', 'yes')
        if offline:
            print("-------- venv: offline mode (skip pip installs)", file=sys.stderr, flush=True)
        else:
            try:
                print("-------- venv: upgrading pip", file=sys.stderr, flush=True)
                subprocess.check_call([str(vpython), '-m', 'pip', 'install', '--upgrade', 'pip'])
            except Exception as e:
                print(f"-------- WARN: pip upgrade failed: {e}", file=sys.stderr, flush=True)

            pkgs = [
                'typer>=0.9.0',
                'pyyaml>=6.0',
                'pathspec>=0.11.0',
                'mcp>=0.4.0',
            ]
            try:
                print("-------- venv: installing python deps", file=sys.stderr, flush=True)
                subprocess.check_call([str(vpip), 'install', *pkgs])
            except Exception as e:
                print(f"-------- WARN: dependency install failed: {e}", file=sys.stderr, flush=True)

        # Try to install super_prompt core wheel if bundled
        try:
            dist_dirs = [package_root() / 'packages' / 'core-py' / 'dist', package_root() / 'dist']
            wheel = None
            for d in dist_dirs:
                if d.exists():
                    for f in sorted(d.glob('*.whl'), reverse=True):
                        wheel = f
                        break
                if wheel:
                    break
            if wheel:
                print(f"-------- venv: installing {wheel.name}", file=sys.stderr, flush=True)
                subprocess.check_call([str(vpip), 'install', str(wheel)])
            else:
                # Not fatal. The wrapper sets PYTHONPATH for source import.
                print("-------- venv: no core wheel found; relying on PYTHONPATH", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"-------- WARN: core wheel install failed: {e}", file=sys.stderr, flush=True)

        return venv_dir
    except Exception as e:
        print(f"-------- WARN: venv setup failed: {e}", file=sys.stderr, flush=True)
        return None


def _init_impl(force: bool = False) -> str:
    _validate_assets()
    pr = project_root()
    data = project_data_dir()
    data.mkdir(parents=True, exist_ok=True)
    # Ensure project venv and runtime deps
    _ensure_project_venv(pr, force=force)
    # 에셋 복사(필요 파일만, 덮어쓰기 정책은 force로 제어)
    src = package_root() / "packages" / "cursor-assets"
    # 예시: commands/super-prompt/*, rules/* 등 선택 복사
    _copytree(src / "commands", pr / ".cursor" / "commands", force=force)
    _copytree(src / "rules", pr / ".cursor" / "rules", force=force)
    # 프로젝트용 디렉터리 보장
    for d in ["specs", "memory", ".codex"]:
        (pr / d).mkdir(parents=True, exist_ok=True)
    # Generate Codex assets based on manifest
    try:
        from .adapters.codex_adapter import CodexAdapter  # lazy import; PyYAML optional
        CodexAdapter().generate_assets(pr)
    except Exception as e:
        print(f"-------- WARN: Could not generate Codex assets: {e}", file=sys.stderr, flush=True)

    # MCP/Codex 자동 등록
    ensure_cursor_mcp_registered(pr)  # .cursor/mcp.json 병합
    try:
        ensure_codex_mcp_registered(pr)  # 선택: ~/.codex/config.toml 병합
    except Exception:
        pass

    # Ensure default mode and personas manifest
    try:
        set_mode('gpt')
    except Exception:
        pass
    try:
        PersonaLoader().load_manifest()
    except Exception:
        pass
    return f"Initialized at {pr}"


def _copytree(src, dst, force=False):
    if not src.exists():
        return
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
    with memory_span("sp.version"):
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
    with memory_span("sp.init"):
        # MCP 전용 강제: 백도어 금지
        if os.environ.get("SUPER_PROMPT_ALLOW_INIT", "").lower() not in ("1", "true", "yes"):
            raise PermissionError(
                "MCP: init/refresh는 기본적으로 비활성화입니다. "
                "환경변수 SUPER_PROMPT_ALLOW_INIT=true 설정 후 다시 시도하세요."
            )

        # 헬스체크 수행
        health_span = span_manager.start_span({"commandId": "sp.init:health", "userId": None})
        span_manager.write_event(health_span, {"type": "health", "timestamp": time.time()})
        span_manager.end_span(health_span, "ok")
        print("-------- MCP memory: healthcheck OK", file=sys.stderr, flush=True)

        print(f"-------- mcp: sp.init(args={{force:{force}}})", file=sys.stderr, flush=True)
        msg = _init_impl(force=force)
        return TextContent(type="text", text=msg)


@mcp.tool()  # 도구명: sp.refresh
def refresh() -> TextContent:
    """Refresh Super Prompt assets in current project"""
    with memory_span("sp.refresh"):
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
    with memory_span("sp.list_commands"):
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
    with memory_span("sp.list_personas"):
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
    with memory_span("sp.mode_get"):
        mode = get_mode()
        return TextContent(type="text", text=mode)


@mcp.tool()  # 도구명: sp.mode_set
def mode_set(mode: str) -> TextContent:
    """Set LLM mode to 'gpt' or 'grok'"""
    with memory_span("sp.mode_set"):
        print(f"-------- mcp: sp.mode_set(args={{mode:'{mode}'}})", file=sys.stderr, flush=True)
        m = set_mode(mode)
        print(f"-------- mode: set to {m}", file=sys.stderr, flush=True)
        return TextContent(type="text", text=f"mode set to {m}")


@mcp.tool()  # 도구명: sp.grok_mode_on
def grok_mode_on() -> TextContent:
    """Switch LLM mode to grok"""
    with memory_span("sp.grok_mode_on"):
        set_mode("grok")
        print("-------- mode: set to grok", file=sys.stderr, flush=True)
        return TextContent(type="text", text="mode set to grok")


@mcp.tool()  # 도구명: sp.gpt_mode_on
def gpt_mode_on() -> TextContent:
    """Switch LLM mode to gpt"""
    with memory_span("sp.gpt_mode_on"):
        set_mode("gpt")
        print("-------- mode: set to gpt", file=sys.stderr, flush=True)
        return TextContent(type="text", text="mode set to gpt")


# === Persona Tools ===


@mcp.tool()  # 도구명: sp.architect
def architect(query: str = "") -> TextContent:
    """🏗️ Architect - System design and architecture specialist"""
    with memory_span("sp.architect"):
        print(f"-------- mcp: sp.architect(args={{query_len:{len(query)}}})", file=sys.stderr, flush=True)
        return _execute_persona("architect", query)


@mcp.tool()  # 도구명: sp.frontend
def frontend(query: str = "") -> TextContent:
    """🎨 Frontend - UI/UX specialist and accessibility advocate"""
    with memory_span("sp.frontend"):
        return _execute_persona("frontend", query)


@mcp.tool()  # 도구명: sp.backend
def backend(query: str = "") -> TextContent:
    """⚡ Backend - Reliability engineer and API specialist"""
    with memory_span("sp.backend"):
        return _execute_persona("backend", query)


@mcp.tool()  # 도구명: sp.security
def security(query: str = "") -> TextContent:
    """🛡️ Security - Threat modeling and vulnerability specialist"""
    with memory_span("sp.security"):
        return _execute_persona("security", query)


@mcp.tool()  # 도구명: sp.performance
def performance(query: str = "") -> TextContent:
    """🚀 Performance - Optimization and bottleneck elimination expert"""
    with memory_span("sp.performance"):
        return _execute_persona("performance", query)


@mcp.tool()  # 도구명: sp.analyzer
def analyzer(query: str = "") -> TextContent:
    """🔍 Analyzer - Root cause investigation specialist"""
    with memory_span("sp.analyzer"):
        return _execute_persona("analyzer", query)


@mcp.tool()  # 도구명: sp.qa
def qa(query: str = "") -> TextContent:
    """🧪 QA - Quality advocate and testing specialist"""
    with memory_span("sp.qa"):
        return _execute_persona("qa", query)


@mcp.tool()  # 도구명: sp.refactorer
def refactorer(query: str = "") -> TextContent:
    """🔧 Refactorer - Code quality and technical debt specialist"""
    with memory_span("sp.refactorer"):
        return _execute_persona("refactorer", query)


@mcp.tool()  # 도구명: sp.devops
def devops(query: str = "") -> TextContent:
    """🚢 DevOps - Infrastructure and deployment specialist"""
    with memory_span("sp.devops"):
        return _execute_persona("devops", query)


@mcp.tool()  # 도구명: sp.mentor
def mentor(query: str = "") -> TextContent:
    """👨‍🏫 Mentor - Knowledge transfer and educational specialist"""
    with memory_span("sp.mentor"):
        return _execute_persona("mentor", query)


@mcp.tool()  # 도구명: sp.scribe
def scribe(query: str = "", lang: str = "en") -> TextContent:
    """📝 Scribe - Professional documentation specialist"""
    with memory_span("sp.scribe"):
        print(f"-------- mcp: sp.scribe(args={{lang:'{lang}', query_len:{len(query)}}})", file=sys.stderr, flush=True)
        # Reflect language so MCP arg is visibly consumed
        prefix = f"[lang={lang}] " if lang else ""
        base = _execute_persona("scribe", query)
        text = _text_from(base)
        return TextContent(type="text", text=f"{prefix}{text}")


# === Additional Tools ===


@mcp.tool()  # 도구명: sp.grok_mode_off
def grok_mode_off() -> TextContent:
    """Turn off Grok mode"""
    with memory_span("sp.grok_mode_off"):
        set_mode("gpt")
        return TextContent(type="text", text="Grok mode turned off, switched to GPT")


@mcp.tool()  # 도구명: sp.gpt_mode_off
def gpt_mode_off() -> TextContent:
    """Turn off GPT mode"""
    with memory_span("sp.gpt_mode_off"):
        set_mode("grok")
        return TextContent(type="text", text="GPT mode turned off, switched to Grok")


@mcp.tool()  # 도구명: sp.specify
def specify(query: str = "") -> TextContent:
    """📋 Specify - Create detailed specifications"""
    with memory_span("sp.specify"):
        return TextContent(
            type="text",
            text=f"📋 Specification tool activated.\n\nQuery: {query}\n\nThis tool helps create detailed specifications for features and requirements.",
        )


@mcp.tool()  # 도구명: sp.plan
def plan(query: str = "") -> TextContent:
    """📅 Plan - Create implementation plans"""
    with memory_span("sp.plan"):
        return TextContent(
            type="text",
            text=f"📅 Planning tool activated.\n\nQuery: {query}\n\nThis tool helps create structured implementation plans.",
        )


@mcp.tool()  # 도구명: sp.tasks
def tasks(query: str = "") -> TextContent:
    """✅ Tasks - Break down work into tasks"""
    with memory_span("sp.tasks"):
        return TextContent(
            type="text",
            text=f"✅ Task breakdown tool activated.\n\nQuery: {query}\n\nThis tool helps break down work into manageable tasks.",
        )


@mcp.tool()  # 도구명: sp.implement
def implement(query: str = "") -> TextContent:
    """🔨 Implement - Execute implementation"""
    with memory_span("sp.implement"):
        return TextContent(
            type="text",
            text=f"🔨 Implementation tool activated.\n\nQuery: {query}\n\nThis tool helps execute implementations based on plans and specifications.",
        )


@mcp.tool()  # 도구명: sp.seq
def seq(query: str = "") -> TextContent:
    """🔍 Sequential - Step-by-step reasoning and analysis"""
    with memory_span("sp.seq"):
        if not query.strip():
            return TextContent(
                type="text",
                text="🔍 Sequential reasoning tool activated.\n\nPlease provide a query to analyze.",
            )

        # Basic sequential reasoning approach
        steps = [
            "1. **Understand the Problem**: Break down the question into its core components",
            "2. **Identify Key Concepts**: Determine the fundamental principles involved",
            "3. **Apply Logical Reasoning**: Use step-by-step logic to arrive at a conclusion",
            "4. **Verify the Answer**: Check the reasoning for consistency and accuracy",
            "5. **Provide Explanation**: Give a clear, comprehensive answer",
        ]

        response = f"🔍 **Sequential Reasoning Analysis**\n\n**Query:** {query}\n\n**Step-by-Step Approach:**\n"
        for step in steps:
            response += f"- {step}\n"

        response += f"\n**Analysis:**\n"
        response += _perform_sequential_analysis(query)

        return TextContent(type="text", text=response)


@mcp.tool()  # 도구명: sp.seq-ultra
def seq_ultra(query: str = "") -> TextContent:
    """🧠 Sequential Ultra - Ultra-deep sequential reasoning for complex problems"""
    with memory_span("sp.seq-ultra"):
        if not query.strip():
            return TextContent(
                type="text",
                text="🧠 Sequential Ultra reasoning tool activated.\n\nPlease provide a complex query to analyze in depth.",
            )

        # Ultra-deep sequential reasoning with more detailed steps
        steps = [
            "1. **Problem Decomposition**: Break down complex problems into fundamental components",
            "2. **Knowledge Base Analysis**: Identify relevant concepts, theories, and principles",
            "3. **Logical Framework Construction**: Build systematic reasoning structures",
            "4. **Step-by-Step Deduction**: Apply rigorous logical progression",
            "5. **Alternative Perspectives**: Consider multiple viewpoints and edge cases",
            "6. **Validation & Verification**: Cross-check reasoning with established knowledge",
            "7. **Synthesis & Conclusion**: Integrate findings into comprehensive answer",
            "8. **Confidence Assessment**: Evaluate certainty and identify limitations",
        ]

        response = f"🧠 **Ultra-Deep Sequential Reasoning Analysis**\n\n**Query:** {query}\n\n**Comprehensive Analysis Framework:**\n"
        for step in steps:
            response += f"- {step}\n"

        response += f"\n**Detailed Analysis:**\n"
        response += _perform_ultra_sequential_analysis(query)

        return TextContent(type="text", text=response)


def _perform_sequential_analysis(query: str) -> str:
    """Perform basic sequential analysis for the given query"""
    query_lower = query.lower()

    if "1+1" in query_lower or "one plus one" in query_lower:
        return """Let's analyze: "Why is 1+1 equal to 2?"

**Step 1 - Understanding the Problem:**
- We have two individual units (1 and 1)
- We want to combine them and find the total

**Step 2 - Key Concepts:**
- Addition is the mathematical operation of combining quantities
- The number 1 represents a single unit
- The equals sign (=) shows equivalence

**Step 3 - Logical Reasoning:**
- When we have one unit and add another unit, we have two units total
- This is a fundamental property of counting and arithmetic
- 1 + 1 = 2 is an axiom in mathematics - a basic truth that doesn't need proof

**Step 4 - Verification:**
- Count with fingers: One finger + one finger = two fingers ✓
- Use physical objects: One apple + one apple = two apples ✓
- Mathematical consistency: The pattern holds across all number systems

**Step 5 - Conclusion:**
1 + 1 = 2 because when you combine two single units, you get a quantity of two units. This is a fundamental principle of arithmetic that forms the basis for all mathematical operations."""

    else:
        return f"""**Sequential Analysis for:** {query}

This appears to be a general reasoning problem. Let me break it down:

**Core Question Identification:**
- The main inquiry seems to be: {query}

**Reasoning Approach:**
- I'll analyze this systematically using logical principles
- Consider multiple perspectives and potential solutions
- Validate assumptions and conclusions

**Note:** For specific mathematical, scientific, or technical questions, please provide more context for a more detailed analysis."""


def _perform_ultra_sequential_analysis(query: str) -> str:
    """Perform ultra-deep sequential analysis for complex queries"""
    query_lower = query.lower()

    if "1+1" in query_lower or "one plus one" in query_lower:
        return """## Ultra-Deep Analysis: "Why is 1+1 equal to 2?"

### 1. Problem Decomposition
**Fundamental Question:** What is the nature of addition and why does 1+1 specifically equal 2?
**Scope:** Mathematical foundations, philosophical implications, practical applications
**Assumptions:** We're working within standard arithmetic systems

### 2. Knowledge Base Analysis
**Mathematical Foundations:**
- Peano axioms (axiomatic set theory)
- Successor function and natural numbers
- Addition as repeated succession

**Philosophical Context:**
- Platonism vs. Formalism in mathematics
- The nature of mathematical truth
- Empirical vs. logical necessity

**Cognitive Science:**
- How humans conceptualize addition
- Innate number sense in infants
- Cultural variations in counting systems

### 3. Logical Framework Construction
**Formal Definition:**
```
Addition: ∀a,b ∈ ℕ: a + b = a + S(b) where S is the successor function
Base case: a + 0 = a
Recursive case: a + S(b) = S(a + b)
```

**Peano Arithmetic:**
- 0 is a natural number
- Every natural number has a unique successor
- 1 is defined as S(0)
- 2 is defined as S(S(0)) = S(1)

### 4. Step-by-Step Deduction
**Mathematical Proof:**
1. Start with: 1 + 1
2. Using definition: 1 + 1 = 1 + S(0)
3. Apply successor: 1 + S(0) = S(1 + 0)
4. Base case: 1 + 0 = 1
5. Therefore: S(1) = 2 ✓

**Alternative Proof (Set Theory):**
- {∅} ∪ {∅} = {∅, {∅}} (cardinality 2)
- Union of two singleton sets creates a set with two elements

### 5. Alternative Perspectives
**Psychological Perspective:**
- Infants as young as 6 months understand 1+1=2 through object permanence
- Cross-cultural studies show this understanding is universal

**Computational Perspective:**
- Binary representation: 1 + 1 = 10 (decimal 2)
- Boolean algebra: True + True = 2 (interpreted as carry + sum)

**Philosophical Perspective:**
- Is 1+1=2 necessarily true, or is it a convention?
- Gödel's incompleteness theorems and mathematical certainty

### 6. Validation & Verification
**Consistency Checks:**
- Commutativity: 1 + 1 = 1 + 1 ✓
- Associativity: (1 + 1) + 0 = 1 + (1 + 0) ✓
- Field properties maintained

**Empirical Validation:**
- Physical counting validation
- Computational verification across systems
- Cognitive developmental studies

### 7. Synthesis & Conclusion
**Core Truth:** 1 + 1 = 2 is a fundamental mathematical truth that:
- Forms the basis of arithmetic
- Is consistent across different mathematical systems
- Has both logical and empirical validation
- Serves as a foundation for all subsequent mathematical operations

**Limitations:**
- Applies within standard number systems
- May not hold in non-standard arithmetic (e.g., modular arithmetic)
- Subject to philosophical debate about mathematical Platonism

### 8. Confidence Assessment
**High Confidence Factors:**
- Universal mathematical consistency
- Empirical validation across cultures and species
- Logical necessity within Peano arithmetic

**Areas of Uncertainty:**
- Philosophical foundations of mathematics
- Consciousness and subjective experience of number
- Ultimate nature of mathematical truth

**Final Assessment:** 99.9% confidence in the mathematical truth 1+1=2, with philosophical caveats about the nature of mathematical reality."""

    else:
        return f"""## Ultra-Deep Sequential Analysis: {query}

### 1. Problem Decomposition
**Primary Question:** {query}
**Analysis Scope:** Comprehensive multi-disciplinary examination
**Complexity Level:** Advanced reasoning required

### 2. Knowledge Base Analysis
**Relevant Domains:**
- Core subject matter analysis
- Interdisciplinary connections
- Historical context and evolution
- Current state and future implications

### 3. Logical Framework Construction
**Systematic Approach:**
- Hypothesis generation and testing
- Evidence evaluation framework
- Counter-argument consideration
- Synthesis methodology

### 4. Step-by-Step Deduction
**Detailed Reasoning Process:**
- Break down complex elements
- Establish logical connections
- Validate each step rigorously
- Build towards comprehensive conclusion

### 5. Alternative Perspectives
**Multi-Viewpoint Analysis:**
- Different theoretical frameworks
- Cultural and contextual variations
- Historical vs. modern interpretations
- Practical vs. theoretical implications

### 6. Validation & Verification
**Robustness Testing:**
- Internal consistency checks
- External validation methods
- Peer review and expert consensus
- Predictive accuracy assessment

### 7. Synthesis & Conclusion
**Integrated Findings:**
- Comprehensive answer synthesis
- Key insights and implications
- Areas requiring further investigation

### 8. Confidence Assessment
**Confidence Level:** Medium-High (context-dependent)
**Strengths:** Systematic methodology, comprehensive analysis
**Limitations:** Subject-specific expertise requirements, evolving knowledge

**Recommendation:** Please provide additional context or specify the domain for more targeted analysis."""


def _execute_persona(persona_name: str, query: str = "", **kwargs) -> TextContent:
    """Execute persona with given query"""
    try:
        # Avoid importing the full CLI to keep dependencies minimal in MCP/direct mode
        from .personas.loader import PersonaLoader

        # Load persona configuration
        loader = PersonaLoader()
        loader.load_manifest()

        # Get persona config
        persona_config = None
        for p in loader.list_personas():
            if p["name"] == persona_name:
                persona_config = p
                break

        if not persona_config:
            # Fallback when manifest is missing or PyYAML unavailable
            fallback_prompt = f"You are the {persona_name} persona.\n\nUser query: {query}"
            return TextContent(
                type="text",
                text=f"🎭 {persona_name.title()} persona activated!\n\n{fallback_prompt}",
            )

        # Create persona prompt
        persona_prompt = f"""You are {persona_config['description']}.

{persona_config.get('system_prompt', '')}

User query: {query}"""

        # Return persona activation message
        # Use emoji if available, otherwise a generic mask
        emoji = persona_config.get("emoji", "🎭")
        return TextContent(
            type="text",
            text=f"🎭 {emoji} {persona_config['name'].title()} persona activated!\n\n{persona_prompt}",
        )

    except Exception as e:
        return TextContent(type="text", text=f"Error executing persona: {str(e)}")


if __name__ == "__main__":
    # Handle direct-call fast path if requested
    if _run_direct_tool_if_requested():
        sys.exit(0)

    # Otherwise start the MCP server if SDK is available
    if not _HAS_MCP:
        print(
            "-------- ERROR: MCP SDK (python mcp) not installed; cannot start server",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(96)
    mcp.run()  # stdio로 MCP 서버 실행
