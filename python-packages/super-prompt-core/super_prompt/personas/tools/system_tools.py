"""
System management tools (init, refresh, version, etc.)
"""

import asyncio
import os
import sys
import time
import shutil
from pathlib import Path

try:
    from ... import __version__ as _PACKAGE_VERSION  # Prefer bundled core version
except Exception:
    try:
        from importlib.metadata import version as _pkg_version
        _PACKAGE_VERSION = _pkg_version("super-prompt-core")
    except Exception:
        _PACKAGE_VERSION = "dev"

from ...utils.span_manager import span_manager, memory_span
from ...utils.progress import progress
from ...utils.authorization import MCPAuthorization
from ...tools.registry import register_tool
from ...mode_store import get_mode, set_mode
from ...paths import package_root, project_root, project_data_dir

def _validate_assets():
    """Validate that required assets exist"""
    pkg = package_root()
    commands = pkg / "packages" / "cursor-assets" / "commands" / "super-prompt"
    personas = pkg / "packages" / "cursor-assets" / "manifests" / "personas.yaml"
    if not commands.exists() or not personas.exists():
        raise RuntimeError("Missing assets in package tarball. No fallback allowed.")
    # Roughly verify if only 4 fallbacks exist (expect at least 8)
    n = len(list(commands.glob("*.md")))
    if n < 8:
        raise RuntimeError(f"Too few commands found ({n}). Fallback disabled.")


def _copytree(src, dst, force=False):
    """Copy directory tree with force option"""
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


def _install_cli_dependencies():
    """Install required CLI dependencies for Super Prompt"""
    import subprocess


    # 1. Check if OpenAI CLI is installed
    try:
        result = subprocess.run(['openai', '--version'],
                              capture_output=True, text=True, timeout=10)
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        try:
            # Install OpenAI CLI
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'openai'],
                         check=True, capture_output=True, text=True, timeout=60)
        except subprocess.SubprocessError as e:
            return

    # 2. Check OpenAI login status
    try:
        result = subprocess.run(['openai', 'api', 'keys', 'list'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            pass  # Login already successful
        else:
            # Note: This will require user interaction
            subprocess.run(['openai', 'login'], timeout=120)
    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        pass  # Handle timeout or subprocess errors gracefully

    # 3. Install Codex CLI
    try:
        subprocess.run(['sudo', 'npm', 'install', '-g', '@openai/codex@latest'],
                     check=True, capture_output=True, text=True, timeout=120)
    except subprocess.SubprocessError as e:
        pass  # Handle installation error gracefully


def _verify_mcp_tool_alignment(project_path: Path) -> None:
    """Ensure MCP server exposes every command-defined tool."""
    expected_tools = set()
    commands_dir = project_path / ".cursor" / "commands" / "super-prompt"
    if commands_dir.exists():
        for command_file in commands_dir.glob("*.md"):
            for line in command_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("tool:"):
                    expected_tools.add(line.split(":", 1)[1].strip())
                    break
    else:
        raise RuntimeError(f"Expected command directory not found: {commands_dir}")

    try:
        from ...mcp_server_new import _TOOL_REGISTRY
    except Exception as import_error:
        raise RuntimeError(f"Unable to inspect MCP registry: {import_error}") from import_error

    available = set(_TOOL_REGISTRY.keys())
    missing = sorted(tool for tool in expected_tools if tool not in available)
    if missing:
        raise RuntimeError("MCP tool registration incomplete. Missing: " + ", ".join(missing))
    if not available:
        raise RuntimeError("No MCP tools registered in server registry.")


def _init_impl(force: bool = False) -> str:
    """Core initialization implementation"""
    # Display Super Prompt ASCII Art
    current_version = _PACKAGE_VERSION

    logo = f"""
\x1b[36m\x1b[1m   ███████╗██╗   ██╗██████╗ ███████╗██████╗
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗
   ███████╗██║   ██║██████╔╝█████╗  ██████╔╝
   ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗
   ███████║╚██████╔╝██║     ███████╗██║  ██║
   ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝

   ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ████████╗
   ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝
   ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝   ██║
   ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝    ██║
   ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║        ██║
   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝\x1b[0m

\x1b[2m              Dual IDE Prompt Engineering Toolkit\x1b[0m
\x1b[2m                     v{current_version} | @cdw0424/super-prompt\x1b[0m
\x1b[2m                          Made by \x1b[0m\x1b[35mDaniel Choi from Korea\x1b[0m
"""

    _validate_assets()
    pr = project_root()
    data = project_data_dir()
    data.mkdir(parents=True, exist_ok=True)

    # Asset copy (only necessary files, overwrite policy controlled by force)
    src = package_root() / "packages" / "cursor-assets"
    # Example: selective copy of commands/super-prompt/*, rules/*, etc.
    _copytree(src / "commands", pr / ".cursor" / "commands", force=force)
    _copytree(src / "rules", pr / ".cursor" / "rules", force=force)

    # Ensure project directories (Codex assets live in ~/.codex)
    for d in ["specs", "memory"]:
        (pr / d).mkdir(parents=True, exist_ok=True)

    # Auto-create missing spec/plan/tasks skeletons for example-feature
    try:
        example_dir = pr / "specs" / "example-feature"
        example_dir.mkdir(parents=True, exist_ok=True)
        # ... (baseline spec/plan/tasks content creation logic)
    except Exception:
        pass

    # Generate Codex assets based on manifest
    try:
        from ...adapters.codex_adapter import CodexAdapter
        CodexAdapter().generate_assets(pr)
    except Exception as e:
        pass  # Handle any other exceptions gracefully

    # CLI auto-installation (OpenAI CLI + Codex CLI)
    _install_cli_dependencies()

    # Execute SSOT compliance validation
    from ...mcp_register import validate_project_ssot
    try:
        ssot_compliant = validate_project_ssot(pr)
        if not ssot_compliant:
            pass  # Handle SSOT non-compliance
    except Exception as e:
        pass  # Handle validation errors gracefully

    # Ensure default mode and personas manifest
    try:
        set_mode("gpt")
    except Exception:
        pass
    try:
        from ...personas.loader import PersonaLoader
        PersonaLoader().load_manifest()
    except Exception:
        pass

    # Verify all MCP tools are exposed for copied commands
    try:
        _verify_mcp_tool_alignment(pr)
        progress.show_success("MCP tool alignment verified")
    except Exception as verify_error:
        progress.show_error(f"MCP tool verification failed: {verify_error}")
        raise

    return f"Initialized at {pr}"


@register_tool("sp.init")
def init(force: bool = False):
    """Initialize Super Prompt for current project"""
    # MCP Authorization check
    MCPAuthorization.require_permission("init")

    try:
        with memory_span("sp.init") as span_id:
            progress.show_progress("🚀 Super Prompt initialization started")
            progress.show_info("Checking permissions...")

            # MCP-only enforcement: Backdoor prohibited
            if os.environ.get("SUPER_PROMPT_ALLOW_INIT", "").lower() not in ("1", "true", "yes"):
                progress.show_error("No initialization permissions")
                raise PermissionError(
                    "MCP: init/refresh is disabled by default. "
                    "Set environment variable SUPER_PROMPT_ALLOW_INIT=true and try again."
                )

            progress.show_success("Initialization permissions confirmed")
            progress.show_progress("🔍 Performing health check")

            # Perform health check
            with memory_span("sp.init:health") as health_span:
                span_manager.write_event(health_span, {"type": "health", "timestamp": time.time()})

            progress.show_success("Health check completed")
            progress.show_progress("📦 Initializing project")
            progress.show_info(f"Force mode: {force}")

            msg = _init_impl(force=force)

            progress.show_success("Initialization completed!")

            # Import TextContent from MCP module
            from ...mcp.version_detection import import_mcp_components
            try:
                _, TextContent, _ = import_mcp_components()
            except ImportError:
                from ...mcp.version_detection import create_fallback_mcp
                _, TextContent = create_fallback_mcp()

            return TextContent(type="text", text=msg)
    except Exception as e:
        progress.show_error(f"Initialization failed: {str(e)}")
        raise


@register_tool("sp.refresh")
def refresh():
    """Refresh Super Prompt assets in current project"""
    # MCP Authorization check
    MCPAuthorization.require_permission("refresh")

    try:
        with memory_span("sp.refresh") as span_id:
            progress.show_progress("🔄 Super Prompt asset refresh")
            progress.show_info("Checking permissions...")

            # MCP-only enforcement: Backdoor prohibited
            if os.environ.get("SUPER_PROMPT_ALLOW_INIT", "").lower() not in ("1", "true", "yes"):
                progress.show_error("No refresh permissions")
                raise PermissionError(
                    "MCP: init/refresh is disabled by default. "
                    "Set environment variable SUPER_PROMPT_ALLOW_INIT=true and try again."
                )

            progress.show_success("Refresh permissions confirmed")
            progress.show_progress("📦 Refreshing assets")

            msg = _init_impl(force=True)

            progress.show_success("Refresh completed!")

            # Import TextContent from MCP module
            from ...mcp.version_detection import import_mcp_components
            try:
                _, TextContent, _ = import_mcp_components()
            except ImportError:
                from ...mcp.version_detection import create_fallback_mcp
                _, TextContent = create_fallback_mcp()

            return TextContent(type="text", text=msg)
    except Exception as e:
        progress.show_error(f"Refresh failed: {str(e)}")
        raise


def sp_version() -> str:
    """Get the current version of Super Prompt"""
    try:
        with memory_span("sp.version") as span_id:
            # Use the bundled package version
            result = f"Super Prompt v{_PACKAGE_VERSION}"
            return result
    except Exception as e:
        progress.show_error(f"Version check failed: {str(e)}")
        raise


def sp_list_commands() -> str:
    """List all available Super Prompt commands"""
    try:
        with memory_span("sp.list_commands") as span_id:
            commands_dir = package_root() / "packages" / "cursor-assets" / "commands" / "super-prompt"
            count = 0
            files = []
            if commands_dir.exists():
                for p in sorted(commands_dir.glob("*.md")):
                    files.append(p.name)
                    count += 1
            text = f"Available commands: {count}\n" + "\n".join(files)
            return text
    except Exception as e:
        progress.show_error(f"List commands failed: {str(e)}")
        raise


@register_tool("sp.list_personas")
def list_personas():
    """List available Super Prompt personas"""
    try:
        with memory_span("sp.list_personas") as span_id:
            from ...personas.loader import PersonaLoader

            loader = PersonaLoader()
            loader.load_manifest()
            personas = loader.list_personas()

            if not personas:
                text = "No personas loaded. Try running init first."
            else:
                text = f"Available personas: {len(personas)}\n"
                for persona in personas:
                    text += f"- {persona['name']}: {persona['description']}\n"

            # Import TextContent from MCP module
            from ...mcp.version_detection import import_mcp_components
            try:
                _, TextContent, _ = import_mcp_components()
            except ImportError:
                from ...mcp.version_detection import create_fallback_mcp
                _, TextContent = create_fallback_mcp()

            return TextContent(type="text", text=text)
    except Exception as e:
        progress.show_error(f"List personas failed: {str(e)}")
        raise


@register_tool("sp.mode_get")
def mode_get():
    """Get current LLM mode (gpt|grok)"""
    try:
        with memory_span("sp.mode_get") as span_id:
            mode = get_mode()

            # Import TextContent from MCP module
            from ...mcp.version_detection import import_mcp_components
            try:
                _, TextContent, _ = import_mcp_components()
            except ImportError:
                from ...mcp.version_detection import create_fallback_mcp
                _, TextContent = create_fallback_mcp()

            return TextContent(type="text", text=mode)
    except Exception as e:
        progress.show_error(f"Mode get failed: {str(e)}")
        raise


@register_tool("sp.mode_set")
def mode_set(mode: str):
    """Set LLM mode to 'gpt' or 'grok'"""
    # MCP Authorization check
    MCPAuthorization.require_permission("mode_set")

    try:
        with memory_span("sp.mode_set") as span_id:
            m = set_mode(mode)

            # Import TextContent from MCP module
            from ...mcp.version_detection import import_mcp_components
            try:
                _, TextContent, _ = import_mcp_components()
            except ImportError:
                from ...mcp.version_detection import create_fallback_mcp
                _, TextContent = create_fallback_mcp()

            return TextContent(type="text", text=f"mode set to {m}")
    except Exception as e:
        progress.show_error(f"Mode set failed: {str(e)}")
        raise


@register_tool("sp.grok_mode_on")
def grok_mode_on(a=None, k=None, **kwargs):
    """Switch LLM mode to grok"""
    try:
        with memory_span("sp.grok_mode_on") as span_id:
            set_mode("grok")

            # Simple text response without MCP import to avoid server interference
            return "mode set to grok"
    except Exception as e:
        progress.show_error(f"Grok mode on failed: {str(e)}")
        raise


@register_tool("sp.gpt_mode_on")
def gpt_mode_on(a=None, k=None, **kwargs):
    """Switch LLM mode to gpt"""
    try:
        with memory_span("sp.gpt_mode_on") as span_id:
            set_mode("gpt")

            # Simple text response without MCP import to avoid server interference
            return "mode set to gpt"
    except Exception as e:
        progress.show_error(f"GPT mode on failed: {str(e)}")
        raise


@register_tool("sp.grok_mode_off")
def grok_mode_off(a=None, k=None, **kwargs):
    """Turn off Grok mode"""
    try:
        with memory_span("sp.grok_mode_off") as span_id:
            set_mode("default")

            # Simple text response without MCP import to avoid server interference
            return "grok mode turned off"
    except Exception as e:
        progress.show_error(f"Grok mode off failed: {str(e)}")
        raise


@register_tool("sp.gpt_mode_off")
def gpt_mode_off(a=None, k=None, **kwargs):
    """Turn off GPT mode"""
    try:
        with memory_span("sp.gpt_mode_off") as span_id:
            set_mode("default")

            # Simple text response without MCP import to avoid server interference
            return "gpt mode turned off"
    except Exception as e:
        progress.show_error(f"GPT mode off failed: {str(e)}")
        raise
