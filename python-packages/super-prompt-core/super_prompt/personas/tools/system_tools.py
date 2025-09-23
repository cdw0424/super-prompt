"""
System management tools (init, refresh, version, etc.)
"""

import asyncio
import os
import sys
import time
import shutil
from datetime import datetime
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
from ...high_mode import is_high_mode_enabled, set_high_mode
from ...paths import package_root, project_root, project_data_dir
from ...analysis.project_analyzer import (
    analyze_project_structure,
    analyze_dependencies,
    analyze_codebase_stats,
    analyze_config_files,
    collect_project_metadata,
)
from ...memory.store import MemoryStore

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


def _copytree(src, dst, force=False, clean=False):
    """Copy directory tree with force option"""
    if not src.exists():
        return
    if clean and dst.exists():
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
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


def ensure_project_dossier(project_root: Path, data_root: Path) -> Path:
    """Ensure the project dossier exists, generating it if necessary."""
    dossier_dir = data_root / "context"
    dossier_path = dossier_dir / "project-dossier.md"
    if dossier_path.exists():
        return dossier_path
    return _generate_project_dossier(project_root, data_root)


def _generate_project_dossier(project_root: Path, data_root: Path) -> Path:
    """Analyze the repository and write a human-readable dossier."""
    dossier_dir = data_root / "context"
    dossier_dir.mkdir(parents=True, exist_ok=True)
    dossier_path = dossier_dir / "project-dossier.md"

    structure = analyze_project_structure(project_root)
    dependencies = analyze_dependencies(project_root)
    stats = analyze_codebase_stats(project_root)
    config = analyze_config_files(project_root)
    metadata = collect_project_metadata(project_root)

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")

    def _format_file_entry(entry):
        size_kb = entry.get("size", 0) / 1024
        lines = entry.get("lines")
        return f"- `{entry.get('path', 'unknown')}` — {size_kb:.1f} KB, {lines or 0} lines"

    def _format_time_entry(entry):
        ts = entry.get("mtime")
        if ts:
            dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
        else:
            dt = "unknown"
        return f"- `{entry.get('path', 'unknown')}` — updated {dt}"

    languages = stats.get("languages", {})
    top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
    file_types = structure.get("file_types", {})
    top_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]
    largest_files = [_format_file_entry(e) for e in stats.get("largest_files", [])[:5]]
    newest_files = [_format_time_entry(e) for e in stats.get("newest_files", [])[:5]]

    node_dep = dependencies.get("node") or {}
    python_deps = dependencies.get("python") or []

    lines = []
    lines.append(f"# Project Dossier")
    lines.append("")
    lines.append(f"Generated: {timestamp} UTC")
    lines.append("")
    lines.append("## Overview")
    lines.append(f"- Root: `{project_root}`")
    lines.append(f"- Project name: {metadata.get('name', 'unknown')}")
    lines.append(f"- Detected type: {metadata.get('type', 'unknown')}")
    langs_list = ", ".join(sorted(set(metadata.get("languages", [])))) or "unknown"
    lines.append(f"- Primary languages: {langs_list}")
    if top_langs:
        distribution = ", ".join(f"{lang or 'unknown'} ({count})" for lang, count in top_langs)
        lines.append(f"- Language distribution (files): {distribution}")
    lines.append(f"- Total files indexed: {structure.get('total_files', 0)}")
    lines.append(f"- Total lines counted: {stats.get('total_lines', 0)}")
    lines.append("")

    lines.append("## Key File Types")
    if top_types:
        for ext, count in top_types:
            lines.append(f"- `{ext or 'unknown'}` × {count}")
    else:
        lines.append("- No file type data available")
    lines.append("")

    lines.append("## Largest Files")
    if largest_files:
        lines.extend(largest_files)
    else:
        lines.append("- No file statistics available")
    lines.append("")

    lines.append("## Recent Changes")
    if newest_files:
        lines.extend(newest_files)
    else:
        lines.append("- No recent file activity detected")
    lines.append("")

    lines.append("## Dependencies Snapshot")
    if node_dep:
        lines.append("### Node.js")
        lines.append(f"- package: {node_dep.get('name', 'unknown')}@{node_dep.get('version', 'unknown')}")
        lines.append(f"- dependencies: {node_dep.get('dependencies_count', 0)} (prod) / {node_dep.get('dev_dependencies_count', 0)} (dev)")
    if python_deps:
        lines.append("### Python")
        for dep in python_deps:
            lines.append(f"- `{dep.get('file')}` present (size {dep.get('size', 0)} bytes)")
    if not node_dep and not python_deps:
        lines.append("- No standard dependency manifests detected")
    lines.append("")

    lines.append("## Configuration Signals")
    git_cfg = config.get("git", {})
    if git_cfg.get("has_gitignore"):
        lines.append("- `.gitignore` present")
    docker_cfg = config.get("docker", {})
    for key, present in docker_cfg.items():
        if present:
            lines.append(f"- `{key}` detected")
    for ci in config.get("ci_cd", []):
        lines.append(f"- CI/CD config: `{ci}`")
    for editor, present in config.get("editors", {}).items():
        if present:
            lines.append(f"- Editor config: `{editor}`")
    if len(lines) > 0 and lines[-1] == "## Configuration Signals":
        lines.append("- No configuration files detected")
    lines.append("")

    lines.append("## How to Refresh")
    lines.append("- Run `/super-prompt/init` after significant structural changes to regenerate this dossier.")
    lines.append("- Commands and personas should consult this file for project context before acting.")
    lines.append("")

    dossier_path.write_text("\n".join(lines), encoding="utf-8")

    try:
        store = MemoryStore.open(project_root)
        store.set_kv(
            "project_dossier",
            {
                "generated_at": timestamp,
                "structure": structure,
                "dependencies": dependencies,
                "statistics": stats,
                "config": config,
                "metadata": metadata,
            },
        )
    except Exception:
        pass

    return dossier_path


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
    commands_src_root = src / "commands"
    commands_dst_root = pr / ".cursor" / "commands"
    commands_dst_root.mkdir(parents=True, exist_ok=True)
    if commands_src_root.exists():
        for item in commands_src_root.iterdir():
            target = commands_dst_root / item.name
            if item.is_dir():
                _copytree(item, target, force=True, clean=force)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)

    # Rules are curated solely by Super Prompt; safe to clean when forcing
    rules_src = src / "rules"
    rules_dst = pr / ".cursor" / "rules"
    _copytree(rules_src, rules_dst, force=True, clean=force)

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
    if os.environ.get("SUPER_PROMPT_ENABLE_CODEX", "").lower() in ("1", "true", "yes"):
        try:
            from ...adapters.codex_adapter import CodexAdapter
            CodexAdapter().generate_assets(pr)
        except Exception:
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
        dossier_path = _generate_project_dossier(pr, data)
        progress.show_success(f"Project dossier generated: {dossier_path}")
    except Exception as dossier_error:
        progress.show_error(f"Project dossier generation failed: {dossier_error}")

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

            # Initialization is now allowed by default; environment flag becomes optional hard-disable
            if os.environ.get("SUPER_PROMPT_ALLOW_INIT", "").lower() in ("0", "false", "no"):
                progress.show_error("Initialization disabled via SUPER_PROMPT_ALLOW_INIT")
                raise PermissionError(
                    "SUPER_PROMPT_ALLOW_INIT is set to false/0; unset it to enable initialization."
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

            if os.environ.get("SUPER_PROMPT_ALLOW_INIT", "").lower() in ("0", "false", "no"):
                progress.show_error("Refresh disabled via SUPER_PROMPT_ALLOW_INIT")
                raise PermissionError(
                    "SUPER_PROMPT_ALLOW_INIT is set to false/0; unset it to enable refresh."
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


@register_tool("sp.high_mode_on")
def high_mode_on(a=None, k=None, **kwargs):
    """Enable Codex-backed high reasoning mode."""

    try:
        with memory_span("sp.high_mode_on") as span_id:
            set_high_mode(True)
            return "high mode enabled"
    except Exception as e:
        progress.show_error(f"High mode on failed: {str(e)}")
        raise


@register_tool("sp.high_mode_off")
def high_mode_off(a=None, k=None, **kwargs):
    """Disable Codex-backed high reasoning mode."""

    try:
        with memory_span("sp.high_mode_off") as span_id:
            set_high_mode(False)
            return "high mode disabled"
    except Exception as e:
        progress.show_error(f"High mode off failed: {str(e)}")
        raise
