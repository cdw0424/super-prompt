# packages/core-py/super_prompt/mcp_server.py
# pip dep: mcp >= 0.4.0  (pyproject.toml 또는 setup.cfg에 추가)
import os
import sys
import asyncio
from pathlib import Path

# MCP SDK (Anthropic 공개 라이브러리)
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# 내부 CLI 재사용
from .cli import app as cli_app  # typer app import
from .paths import package_root, project_root, project_data_dir

mcp = FastMCP("super-prompt")

def _pkg_root():
    return package_root()

def _project_root():
    return project_root()

def _guard_allow_init():
    if os.environ.get("SUPER_PROMPT_ALLOW_INIT", "").lower() not in ("1", "true", "yes"):
        raise PermissionError(
            "MCP: init/refresh는 기본적으로 비활성화입니다. "
            "환경변수 SUPER_PROMPT_ALLOW_INIT=true 설정 후 다시 시도하세요."
        )

@mcp.tool()  # 도구명: sp.version
def version() -> TextContent:
    """Get Super Prompt version"""
    # CLI의 버전 출력과 동일한 값 노출
    from .cli import get_current_version
    version_str = get_current_version()
    return TextContent(type="text", text=f"Super Prompt v{version_str}")

@mcp.tool()  # 도구명: sp.init
def init(force: bool = False) -> TextContent:
    """Initialize Super Prompt for current project"""
    _guard_allow_init()

    # 프로젝트 데이터 디렉터리 준비
    data_dir = project_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    # Cursor 어댑터로 초기화
    from .adapters.cursor_adapter import CursorAdapter
    from .adapters.codex_adapter import CodexAdapter

    cursor_adapter = CursorAdapter()
    codex_adapter = CodexAdapter()

    project_path = _project_root()
    cursor_adapter.generate_commands(project_path)
    cursor_adapter.generate_rules(project_path)
    codex_adapter.generate_assets(project_path)

    return TextContent(type="text", text=f"Super Prompt initialized in {project_path}")

@mcp.tool()  # 도구명: sp.refresh
def refresh() -> TextContent:
    """Refresh Super Prompt assets in current project"""
    _guard_allow_init()

    # 동일한 초기화 로직 재실행
    return init(force=True)

@mcp.tool()  # 도구명: sp.list_commands
def list_commands() -> TextContent:
    """List available Super Prompt commands"""
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

if __name__ == "__main__":
    mcp.run()  # stdio로 MCP 서버 실행
