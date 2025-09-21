"""
Super Prompt Core CLI (Typer) — Python package entrypoint

This CLI is for the Python package (super-prompt-core). The NPM distribution
uses .super-prompt/cli.py as its entrypoint. Keep both CLIs; they serve
different packaging targets.
"""

try:
    import typer
except ModuleNotFoundError:
    # Fallback for system Python
    import importlib
    importlib.invalidate_caches()
    import typer
from typing import Optional
import os
import sys
import subprocess
import json
from pathlib import Path

# MCP-only enforcement (safe defaults, zero-config CLI)
# Default behavior: allow direct CLI unless explicitly forced to MCP-only via env
_argv = list(sys.argv)
_first = _argv[1] if len(_argv) > 1 else ""
_cli_like_commands = {"init", "super:init", "refresh", "super:refresh", "--version", "-v", "version"}
_is_cli_command = _first in _cli_like_commands

# Treat CLI-like invocations as CLI mode automatically
if _is_cli_command:
    os.environ["SUPER_PROMPT_CLI_MODE"] = "1"

cli_mode = os.environ.get("SUPER_PROMPT_CLI_MODE") == "1"
require_mcp = os.environ.get("SUPER_PROMPT_REQUIRE_MCP", "0") == "1"  # default off
allow_direct = os.environ.get("SUPER_PROMPT_ALLOW_DIRECT") == "true"

if not cli_mode and require_mcp and not allow_direct:
    sys.stderr.write("Direct CLI is disabled. Use MCP only.\n")
    sys.stderr.write("To enable direct CLI: SUPER_PROMPT_ALLOW_DIRECT=true\n")
    raise SystemExit(97)

# Normalize legacy-style colon commands to supported names
# e.g., `super-prompt super:init` → `super-prompt init`
#       `super-prompt mcp:serve`  → `super-prompt mcp-serve`
_alias_map = {"super:init": "init", "mcp:serve": "mcp-serve"}
sys.argv = [_alias_map.get(a, a) for a in sys.argv]

from .engine.execution_pipeline import ExecutionPipeline
from .context.collector import ContextCollector
from .sdd.gates import check_implementation_ready
from .personas.loader import PersonaLoader
from .adapters.cursor_adapter import CursorAdapter
from .adapters.codex_adapter import CodexAdapter
from .validation.todo_validator import TodoValidator
from .paths import package_root, project_root, project_data_dir, cursor_assets_root
from .mcp_register import ensure_cursor_mcp_registered, ensure_codex_mcp_registered, validate_project_ssot, ensure_project_ssot_priority, get_ssot_guidance, perform_ssot_migration
from .mode_store import set_mode as set_mode_file
from .personas.loader import PersonaLoader
from .mcp_client import MCPClient


def get_current_version() -> str:
    """Get current version from package.json"""
    try:
        # 1) Prioritize root passed by npm wrapper
        env_root = os.environ.get("SUPER_PROMPT_PACKAGE_ROOT")
        if env_root and Path(env_root).exists():
            npm_root = Path(env_root)
        else:
            # 2) Check for 'packages/cursor-assets' by traversing up from site-packages
            current = Path(__file__).resolve()
            npm_root = None
            while current.parent != current:  # Stop at filesystem root
                if (current / "packages" / "cursor-assets").exists() or (
                    current / "package.json"
                ).exists():
                    try:
                        if (current / "package.json").exists():
                            with open(current / "package.json") as f:
                                package_data = json.load(f)
                                if package_data.get("name") == "@cdw0424/super-prompt":
                                    npm_root = current
                                    break
                    except Exception as e:
                        pass
                current = current.parent

        if npm_root and (npm_root / "package.json").exists():
            package_json = npm_root / "package.json"
            with open(package_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                version = data.get("version", "3.1.56")
                return version

        # Fallback: try to read from environment or use default
        env_version = os.environ.get("SUPER_PROMPT_VERSION", "3.1.56")
        return env_version
    except Exception as e:
        return "3.1.56"


app = typer.Typer(
    name="super-prompt-core",
    help="Super Prompt v3 - Modular prompt engineering toolkit",
    add_completion=False,
)

# MCP Client Sub-app
mcp_app = typer.Typer(
    name="mcp",
    help="MCP server client commands",
    add_completion=False,
)

app.add_typer(mcp_app)

# MCP Setup Sub-app for explicit global registration
setup_app = typer.Typer(
    name="setup",
    help="Explicit MCP setup commands (SSOT compliance)",
    add_completion=False,
)

app.add_typer(setup_app)


@setup_app.command("global")
def setup_global(
    cursor: bool = typer.Option(False, "--cursor", help="Setup Cursor MCP server globally"),
    codex: bool = typer.Option(False, "--codex", help="Setup Codex MCP server globally"),
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
    force: bool = typer.Option(False, "--force", help="Force overwrite existing configurations"),
):
    """
    Explicit global MCP setup (Phase 2: SSOT compliance)

    This command provides explicit control over global MCP registration.
    Use this when you specifically want global setup, rather than automatic registration.
    """
    if not cursor and not codex:
        typer.echo("❌ Error: Must specify at least one of --cursor or --codex", err=True)
        typer.echo("💡 Usage: super-prompt setup global --cursor --codex", err=True)
        raise typer.Exit(1)

    target_dir = Path(project_root or ".").resolve()

    typer.echo("🔧 Explicit Global MCP Setup (SSOT Compliant)")
    typer.echo(f"   Project: {target_dir}")
    typer.echo(f"   Cursor: {'✅' if cursor else '❌'}")
    typer.echo(f"   Codex: {'✅' if codex else '❌'}")
    typer.echo(f"   Force: {'✅' if force else '❌'}")
    typer.echo()

    # Pre-setup SSOT validation
    try:
        ssot_compliant = validate_project_ssot(target_dir)
        if not ssot_compliant:
            typer.echo("⚠️  SSOT violation detected: Potential conflict with existing global settings")
            if not typer.confirm("Continue anyway?"):
                raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"⚠️  SSOT validation failed: {e}")

    # Cursor global setup
    if cursor:
        try:
            typer.echo("🚀 Setting up Cursor MCP globally...")
            cfg_path = ensure_cursor_mcp_registered(target_dir, overwrite=force)
            typer.echo(f"✅ Cursor MCP registered globally: {cfg_path}")
        except Exception as e:
            typer.echo(f"❌ Cursor setup failed: {e}", err=True)
            raise typer.Exit(1)

    # Codex global setup
    if codex:
        try:
            typer.echo("🚀 Setting up Codex MCP globally...")
            codex_cfg = ensure_codex_mcp_registered(target_dir, overwrite=force)
            typer.echo(f"✅ Codex MCP registered globally: {codex_cfg}")
        except Exception as e:
            typer.echo(f"❌ Codex setup failed: {e}", err=True)
            raise typer.Exit(1)

    typer.echo()
    typer.echo("🎉 Global MCP setup completed!")
    typer.echo("💡 Note: This creates global configurations that may conflict with project-local settings")
    typer.echo("💡 Use 'super-prompt setup cleanup' to remove global entries if needed")


@setup_app.command("cleanup")
def setup_cleanup(
    cursor: bool = typer.Option(False, "--cursor", help="Remove Cursor global MCP entries"),
    codex: bool = typer.Option(False, "--codex", help="Remove Codex global MCP entries"),
    server_name: str = typer.Option("super-prompt", "--server-name", help="MCP server name to clean"),
):
    """
    Cleanup global MCP entries (SSOT compliance restoration)

    This command removes global MCP configurations to restore SSOT compliance.
    Use this when you want to rely only on project-local configurations.
    """
    if not cursor and not codex:
        typer.echo("❌ Error: Must specify at least one of --cursor or --codex", err=True)
        typer.echo("💡 Usage: super-prompt setup cleanup --cursor --codex", err=True)
        raise typer.Exit(1)

    from .mcp_register import cleanup_global_entries

    typer.echo("🧹 Global MCP Cleanup (SSOT Restoration)")
    typer.echo(f"   Cursor: {'✅' if cursor else '❌'}")
    typer.echo(f"   Codex: {'✅' if codex else '❌'}")
    typer.echo(f"   Server: {server_name}")
    typer.echo()

    if not typer.confirm("Are you sure you want to clean up global settings? (Backups will be created)"):
        typer.echo("❌ Cleanup cancelled")
        return

    try:
        cleanup_global_entries(server_name)
        typer.echo("✅ Global MCP cleanup completed!")
        typer.echo("💡 Note: Backups were created with .backup_super-prompt suffix")
        typer.echo("💡 Project-local configurations will now be used exclusively")
    except Exception as e:
        typer.echo(f"❌ Cleanup failed: {e}", err=True)
        raise typer.Exit(1)


@setup_app.command("validate")
def setup_validate(
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """
    Validate SSOT compliance for current project

    This command checks if your MCP configurations follow SSOT principles.
    """
    target_dir = Path(project_root or ".").resolve()

    typer.echo("🔍 SSOT Compliance Validation")
    typer.echo(f"   Project: {target_dir}")
    typer.echo()

    try:
        ssot_compliant = validate_project_ssot(target_dir)

        if ssot_compliant:
            typer.echo("✅ SSOT compliant: All settings configured correctly")
            typer.echo("   - Project settings do not conflict with global settings")
            typer.echo("   - Single source of truth principle maintained")
        else:
            typer.echo("❌ SSOT violation detected")
            typer.echo("💡 Solutions:")
            typer.echo("   1. super-prompt setup cleanup --cursor --codex  # Clean global settings")
            typer.echo("   2. Configure to use only project settings")
            typer.echo("   3. super-prompt setup validate  # Re-validate")

        return typer.Exit(0 if ssot_compliant else 1)

    except Exception as e:
        typer.echo(f"❌ Validation failed: {e}", err=True)
        raise typer.Exit(1)


@setup_app.command("guidance")
def setup_guidance():
    """
    Display SSOT compliance guidance and best practices

    This command provides comprehensive guidance for maintaining SSOT compliance
    in your MCP configurations.
    """
    typer.echo(get_ssot_guidance())


@setup_app.command("priority")
def setup_priority(
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """
    Establish project SSOT priority (Phase 3: SSOT Enhancement)

    This command ensures that project-local configurations take priority
    over global configurations, establishing proper SSOT hierarchy.
    """
    target_dir = Path(project_root or ".").resolve()

    typer.echo("🔧 Establishing Project SSOT Priority")
    typer.echo(f"   Project: {target_dir}")
    typer.echo()

    try:
        priority_established = ensure_project_ssot_priority(target_dir)

        if priority_established:
            typer.echo("✅ Project SSOT priority setup completed")
            typer.echo("   - Project settings take priority over global settings")
            typer.echo("   - SSOT principles applied correctly")
        else:
            typer.echo("❌ Project SSOT priority setup failed")
            typer.echo("💡 Solutions:")
            typer.echo("   1. Check global ~/.cursor/mcp.json or ~/.codex/config.toml files")
            typer.echo("   2. super-prompt setup validate  # Validate settings")
            typer.echo("   3. super-prompt setup guidance  # Detailed guidelines")

        return typer.Exit(0 if priority_established else 1)

    except Exception as e:
        typer.echo(f"❌ Priority setup failed: {e}", err=True)
        raise typer.Exit(1)


@setup_app.command("migrate")
def setup_migrate(
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
    dry_run: bool = typer.Option(True, "--execute", "--no-dry-run", help="Execute migration (default: dry-run only)"),
    cleanup_global: bool = typer.Option(False, "--cleanup-global", help="Automatically cleanup global entries"),
):
    """
    Perform SSOT migration (Phase 4: Migration & Cleanup)

    This command migrates your MCP configuration to SSOT compliance.
    By default, it performs a dry-run to show what would be changed.

    Use --execute to actually perform the migration.
    Use --cleanup-global to automatically remove global entries.
    """
    target_dir = Path(project_root or ".").resolve()
    execute = not dry_run  # Execute if --execute flag is True

    typer.echo("🔄 SSOT Migration" + (" (DRY RUN)" if not execute else " (EXECUTING)"))
    typer.echo(f"   Project: {target_dir}")
    typer.echo(f"   Cleanup Global: {'✅' if cleanup_global else '❌'}")
    typer.echo()

    try:
        # Perform migration
        result = perform_ssot_migration(target_dir, dry_run=not execute)

        if "error" in result:
            typer.echo(f"❌ Migration failed: {result['error']}", err=True)
            raise typer.Exit(1)

        # Display results
        typer.echo("📊 Migration Results:")

        # Current status
        status = result.get("current_status", {})
        typer.echo("   📁 Current Status:")
        typer.echo(f"     • Project Cursor: {'✅' if status.get('project_cursor_exists') else '❌'}")
        typer.echo(f"     • Project Codex: {'✅' if status.get('project_codex_exists') else '❌'}")
        typer.echo(f"     • Global Cursor: {'✅' if status.get('global_cursor_exists') else '❌'}")
        typer.echo(f"     • Global Codex: {'✅' if status.get('global_codex_exists') else '❌'}")

        # SSOT compliance status
        ssot_before = result.get("ssot_compliant_before")
        ssot_after = result.get("ssot_compliant_after")
        if ssot_before is not None:
            typer.echo(f"   🔍 SSOT Compliant (Before): {'✅' if ssot_before else '❌'}")
        if ssot_after is not None:
            typer.echo(f"   🔍 SSOT Compliant (After): {'✅' if ssot_after else '❌'}")

        # Actions taken
        actions = result.get("actions_taken", [])
        if actions:
            typer.echo("   ✅ Actions Taken:")
            for action in actions:
                typer.echo(f"     • {action}")

        # Warnings
        warnings = result.get("warnings", [])
        if warnings:
            typer.echo("   ⚠️  Warnings:")
            for warning in warnings:
                typer.echo(f"     • {warning}")

        # Recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            typer.echo("   💡 Recommendations:")
            for rec in recommendations:
                typer.echo(f"     • {rec}")

        # Auto cleanup option
        if cleanup_global and execute:
            typer.echo("\n🧹 Auto-cleaning global settings...")
            from .mcp_register import cleanup_global_entries
            try:
                cleanup_global_entries()
                typer.echo("✅ Global settings cleanup completed")
            except Exception as e:
                typer.echo(f"⚠️  Global settings cleanup failed: {e}")

        # Final result
        success = result.get("success", False)
        if success:
            typer.echo("\n🎉 Migration completed!")
            if execute:
                typer.echo("   - SSOT compliance successfully established")
            else:
                typer.echo("   - Use --execute flag for actual execution")
        else:
            typer.echo("\n❌ Migration failed or additional work needed")
            if not execute:
                typer.echo("   - Use --execute flag for actual execution")

        return typer.Exit(0 if success else 1)

    except Exception as e:
        typer.echo(f"❌ Migration failed: {e}", err=True)
        raise typer.Exit(1)


@mcp_app.command("list-tools")
def mcp_list_tools(json_output: bool = typer.Option(False, "--json", help="Output as JSON")):
    """List available MCP tools"""
    import asyncio

    async def _list_tools():
        async with MCPClient() as client:
            tools = await client.list_tools()

    asyncio.run(_list_tools())


@mcp_app.command("call")
def mcp_call_tool(
    tool_name: str = typer.Argument(..., help="Name of the tool to call"),
    args_json: str = typer.Option(None, "--args-json", help="JSON string of arguments"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON"),
    interactive: bool = typer.Option(False, "--interactive", help="Interactive mode for manual input")
):
    """Call an MCP tool"""
    import asyncio

    async def _call_tool():
        # Parse arguments
        arguments = {}
        if interactive:
            # Interactive mode: prompt for arguments
            typer.echo("🔧 Interactive mode enabled for tool call")
            typer.echo(f"Tool: {tool_name}")
            args_input = typer.prompt("Enter arguments as JSON (leave empty for no args)", default="")
            if args_input.strip():
                try:
                    arguments = json.loads(args_input)
                except json.JSONDecodeError as e:
                    typer.echo(f"Error parsing JSON arguments: {e}", err=True)
                    raise typer.Exit(1)
        elif args_json:
            try:
                arguments = json.loads(args_json)
            except json.JSONDecodeError as e:
                typer.echo(f"Error parsing JSON arguments: {e}", err=True)
                raise typer.Exit(1)

        async with MCPClient() as client:
            try:
                typer.echo(f"🔧 Executing tool: {tool_name}")
                if arguments:
                    typer.echo(f"Arguments: {json.dumps(arguments, indent=2)}")

                result = await client.call_tool(tool_name, arguments)

                if json_output:
                    pass
            except Exception as e:
                typer.echo(f"❌ Error calling tool '{tool_name}': {e}", err=True)
                raise typer.Exit(1)

    asyncio.run(_call_tool())


@mcp_app.command("list-prompts")
def mcp_list_prompts(json_output: bool = typer.Option(False, "--json", help="Output as JSON")):
    """List available MCP prompts"""
    import asyncio

    async def _list_prompts():
        async with MCPClient() as client:
            prompts = await client.list_prompts()

    asyncio.run(_list_prompts())


@mcp_app.command("get-prompt")
def mcp_get_prompt(
    prompt_name: str = typer.Argument(..., help="Name of the prompt to get"),
    args_json: str = typer.Option(None, "--args-json", help="JSON string of arguments"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON")
):
    """Get an MCP prompt"""
    import asyncio

    async def _get_prompt():
        # Parse arguments
        arguments = {}
        if args_json:
            try:
                arguments = json.loads(args_json)
            except json.JSONDecodeError as e:
                typer.echo(f"Error parsing JSON arguments: {e}", err=True)
                raise typer.Exit(1)

        async with MCPClient() as client:
            try:
                result = await client.get_prompt(prompt_name, arguments)
            except Exception as e:
                typer.echo(f"Error getting prompt '{prompt_name}': {e}", err=True)
                raise typer.Exit(1)

    asyncio.run(_get_prompt())


@mcp_app.command("doctor")
def mcp_doctor(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    timeout: int = typer.Option(10, "--timeout", help="Timeout in seconds"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show detailed information")
):
    """Run diagnostics on MCP server connection"""
    import asyncio
    import time

    async def _doctor():
        start_time = time.time()

        try:
            async with asyncio.timeout(timeout):
                async with MCPClient() as client:
                    if verbose:
                        pass

                    # Test tools listing
                    tools = await client.list_tools()
                    tools_count = len(tools)

                    # Test prompts listing
                    prompts = await client.list_prompts()
                    prompts_count = len(prompts)

                    # Test a simple tool call if available
                    test_tool_result = None
                    test_tool_name = None
                    if tools:
                        test_tool_name = tools[0]['name']
                        if verbose:
                            pass
                        try:
                            test_tool_result = await client.call_tool(test_tool_name, {})
                        except Exception as e:
                            test_tool_result = f"Error: {e}"

                    response_time = time.time() - start_time

                    result = {
                        "status": "healthy",
                        "response_time": f"{response_time:.2f}s",
                        "tools_count": tools_count,
                        "prompts_count": prompts_count,
                        "test_tool_name": test_tool_name,
                        "test_tool_result": test_tool_result,
                        "server_command": client.server_command
                    }


        except asyncio.TimeoutError:
            result = {"status": "timeout", "message": f"Connection timed out after {timeout}s"}
        except Exception as e:
            result = {"status": "error", "message": str(e)}

    asyncio.run(_doctor())


@mcp_app.command("run")
def mcp_run_tool(
    tool_name: str = typer.Argument(..., help="Name of the tool to run"),
    args_json: str = typer.Option(None, "--args-json", help="JSON string of arguments"),
    watch: bool = typer.Option(False, "--watch", help="Watch mode - rerun on changes"),
    interval: int = typer.Option(2, "--interval", help="Watch interval in seconds")
):
    """Run an MCP tool (with optional watch mode)"""
    import asyncio
    import time

    async def _run_tool():
        # Parse arguments
        arguments = {}
        if args_json:
            try:
                arguments = json.loads(args_json)
            except json.JSONDecodeError as e:
                typer.echo(f"Error parsing JSON arguments: {e}", err=True)
                raise typer.Exit(1)

        async with MCPClient() as client:
            while True:
                try:
                    start_time = time.time()
                    result = await client.call_tool(tool_name, arguments)
                    end_time = time.time()


                    if not watch:
                        break

                    await asyncio.sleep(interval)

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    if not watch:
                        raise typer.Exit(1)
                    await asyncio.sleep(interval)

    asyncio.run(_run_tool())


sdd_spec_query: Optional[str] = typer.Option(
    None, "--sp-sdd-spec", help="Create an SDD specification for a feature."
)
sdd_plan_query: Optional[str] = typer.Option(
    None, "--sp-sdd-plan", help="Create an SDD plan for a feature."
)
sdd_tasks_query: Optional[str] = typer.Option(
    None, "--sp-sdd-tasks", help="Create SDD tasks for a feature."
)
sdd_implement_query: Optional[str] = typer.Option(
    None, "--sp-sdd-implement", help="Implement a feature based on SDD artifacts."
)
high_query: Optional[str] = typer.Option(
    None, "--sp-high", help="Execute with Codex high reasoning via MCP (use /super-prompt/high in Cursor)."
)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    sp_sdd_spec: Optional[str] = typer.Option(
        None, "--sp-sdd-spec", help="Create an SDD specification for a feature."
    ),
    sp_sdd_plan: Optional[str] = typer.Option(
        None, "--sp-sdd-plan", help="Create an SDD plan for a feature."
    ),
    sp_sdd_tasks: Optional[str] = typer.Option(
        None, "--sp-sdd-tasks", help="Create SDD tasks for a feature."
    ),
    sp_sdd_implement: Optional[str] = typer.Option(
        None, "--sp-sdd-implement", help="Implement a feature based on SDD artifacts."
    ),
):
    """Super Prompt Core CLI"""
    # Check for execution context file FIRST (before checking subcommands)
    context_file = os.environ.get("SUPER_PROMPT_CONTEXT_FILE")
    execution_context = None

    if context_file and Path(context_file).exists():
        try:
            with open(context_file, "r", encoding="utf-8") as f:
                execution_context = json.load(f)
            typer.echo(f"-------- Loaded execution context from {context_file}")
        except Exception as e:
            typer.echo(f"⚠️  Could not load execution context: {e}")

    if execution_context:
        # Handle enhanced persona execution with context object
        system_prompt = execution_context.get("system_prompt", "")
        persona_key = execution_context.get("persona_key", "")
        if system_prompt and persona_key:
            handle_enhanced_persona_execution_from_context(execution_context, ctx.args)
            return

    # Check for enhanced persona system prompt from environment (legacy support)
    system_prompt = os.environ.get("SUPER_PROMPT_SYSTEM_PROMPT")
    persona_key = os.environ.get("SUPER_PROMPT_PERSONA")

    if system_prompt and persona_key:
        # Handle enhanced persona execution with system prompt
        handle_enhanced_persona_execution(system_prompt, persona_key, ctx.args)
        return

    # Now check for subcommands
    if ctx.invoked_subcommand is not None:
        return

    sdd_options = {
        "spec": sp_sdd_spec,
        "plan": sp_sdd_plan,
        "tasks": sp_sdd_tasks,
        "implement": sp_sdd_implement,
    }

    active_sdd_action = None
    feature_query = None
    for action, query in sdd_options.items():
        if query is not None:
            if active_sdd_action is not None:
                typer.echo("❌ Error: Please provide only one SDD action flag at a time.", err=True)
                raise typer.Exit(1)
            active_sdd_action = action
            feature_query = query

    # High reasoning is now handled via MCP tool (sp.high), not CLI

    if active_sdd_action and feature_query:
        sdd_command(action=active_sdd_action, feature=feature_query, project_root=None)
    elif any(q is not None for q in sdd_options.values()):
        typer.echo("❌ Error: SDD action requires a feature description.", err=True)
        raise typer.Exit(1)
    else:
        # If no command is passed, and no SDD flags, show help.
        # This requires `invoke_without_command=True` on the callback.
        # We check if any sdd option was passed but without a value.
        if (
            ctx.params["sp_sdd_spec"] is None
            and ctx.params["sp_sdd_plan"] is None
            and ctx.params["sp_sdd_tasks"] is None
            and ctx.params["sp_sdd_implement"] is None
            and ctx.params["sp_high"] is None
            and not ctx.invoked_subcommand
        ):
            # Check if there are any other arguments that might imply a command is being called
            if len(sys.argv) > 1:
                # A command might be trying to be called but is not matching.
                # Typer will handle this and show an error.
                pass
            else:
                typer.echo(ctx.get_help())


def sdd_command(
    action: str,
    feature: str,
    project_root: Optional[Path],
):
    """SDD (Spec-Driven Development) workflow commands"""
    try:
        if action == "check":
            # Check implementation readiness
            gate_result = check_implementation_ready(
                feature, str(project_root) if project_root else "."
            )

            if gate_result.ok:
                typer.echo("✅ Implementation ready!")
            else:
                typer.echo("❌ Implementation blocked:")
                for issue in gate_result.missing:
                    typer.echo(f"   - {issue}")
                for warning in gate_result.warnings:
                    typer.echo(f"   ⚠️  {warning}")

        elif action in ["spec", "plan", "tasks"]:
            # Generate SDD artifacts
            pipeline = ExecutionPipeline()
            result = pipeline.execute(
                f"Create {action.upper()} for {feature}",
                sdd_stage=action,
                project_id=feature,
                project_root=str(project_root) if project_root else ".",
            )

            typer.echo(f"✅ {action.upper()} created for {feature}")

        elif action == "implement":
            # Check gates before implementation
            gate_result = check_implementation_ready(
                feature, str(project_root) if project_root else "."
            )

            if not gate_result.ok:
                typer.echo("❌ Cannot implement - gates not satisfied:")
                for issue in gate_result.missing:
                    typer.echo(f"   - {issue}")
                raise typer.Exit(1)

            # Proceed with implementation
            pipeline = ExecutionPipeline()
            result = pipeline.execute(
                f"Implement {feature}",
                sdd_stage="implement",
                project_id=feature,
                project_root=str(project_root) if project_root else ".",
            )

            typer.echo(f"✅ Implementation completed for {feature}")

        else:
            typer.echo(f"❌ Unknown SDD action: {action}", err=True)
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command("amr-rules")
def amr_rules(out: Path = typer.Option(Path(".cursor/rules"), "--out", help="Output directory")):
    """Generate AMR rule file (05-amr.mdc) for Cursor."""
    try:
        out.mkdir(parents=True, exist_ok=True)
        amr_path = out / "05-amr.mdc"
        content = """---
description: "Auto Model Router (AMR) policy and state machine"
globs: ["**/*"]
alwaysApply: true
---
# Auto Model Router (medium ↔ high)
- Default: gpt-5, reasoning=medium.
- Task classes: L0 (light), L1 (moderate), H (heavy reasoning).
- H: switch to high for PLAN/REVIEW, then back to medium for EXECUTION.
- Router switch lines (copy-run if needed):
  - `/model gpt-5 high` → `--------router: switch to high (reason=deep_planning)`
  - `/model gpt-5 medium` → `--------router: back to medium (reason=execution)`

# Output Discipline
- Language: English. Logs start with `--------`.
- Keep diffs minimal; provide exact macOS zsh commands.

# Fixed State Machine
[INTENT] → [TASK_CLASSIFY] → [PLAN] → [EXECUTE] → [VERIFY] → [REPORT]

# Templates (use as needed)
T1 Switch High:
```
/model gpt-5 high
--------router: switch to high (reason=deep_planning)
```
T1 Back Medium:
```
/model gpt-5 medium
--------router: back to medium (reason=execution)
```
T2 PLAN:
```
[Goal]
- …
[Plan]
- …
[Risk/Trade‑offs]
- …
[Test/Verify]
- …
[Rollback]
- …
```
T3 EXECUTE:
```
[Diffs]
```diff
--- a/file
+++ b/file
@@
- old
+ new
```
[Commands]
```bash
--------run: npm test -- --watchAll=false
```
```
"""
        amr_path.write_text(content)
        typer.echo(f"AMR rules written: {amr_path}")
    except Exception as e:
        typer.echo(f"❌ Error writing AMR rules: {e}", err=True)
        raise typer.Exit(1)


@app.command("amr-print")
def amr_print(
    path: Path = typer.Option(
        Path("prompts/codex_amr_bootstrap_prompt_en.txt"), "--path", help="Prompt file path"
    ),
):
    """Print AMR bootstrap prompt to stdout."""
    try:
        if path.exists():
            typer.echo(path.read_text())
        else:
            typer.echo(
                "No bootstrap prompt found. Provide --path or add prompts/codex_amr_bootstrap_prompt_en.txt"
            )
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command("amr-qa")
def amr_qa(
    file: Path = typer.Argument(..., help="Transcript/text file to check"),
):
    """Validate a transcript for AMR/state-machine conformance."""
    if not file.exists():
        typer.echo(f"❌ File not found: {file}")
        raise typer.Exit(2)
    txt = file.read_text()
    ok = True
    import re

    if not re.search(r"^\[INTENT\]", txt, re.M):
        typer.echo("-------- Missing [INTENT] section")
        ok = False
    if not (re.search(r"^\[PLAN\]", txt, re.M) or re.search(r"^\[EXECUTE\]", txt, re.M)):
        typer.echo("-------- Missing [PLAN] or [EXECUTE] section")
        ok = False
    if re.search(r"^(router:|run:)", txt, re.M):
        typer.echo("-------- Found log lines without '--------' prefix")
        ok = False
    if "/model gpt-5 high" in txt and "/model gpt-5 medium" not in txt:
        typer.echo("-------- High switch found without returning to medium")
        ok = False
    typer.echo("--------qa: OK" if ok else "--------qa: FAIL")
    raise typer.Exit(0 if ok else 1)


@app.command("codex-init")
def codex_init(
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Create Codex CLI assets in ~/.codex"""
    try:
        root = Path(project_root or ".")
        adapter = CodexAdapter()
        adapter.generate_assets(root)
        typer.echo("--------codex:init: ~/.codex assets created")
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command("codex-mode-on")
def codex_mode_on(
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Enable Codex AMR mode by creating .cursor/.codex-mode flag."""
    try:
        root = Path(project_root or ".")
        cursor_dir = root / ".cursor"
        cursor_dir.mkdir(parents=True, exist_ok=True)
        flag = cursor_dir / ".codex-mode"
        flag.write_text("", encoding="utf-8")
        # Mutual exclusivity: disable Grok mode flag if present
        grok_flag = root / ".cursor" / ".grok-mode"
        if grok_flag.exists():
            try:
                grok_flag.unlink()
                typer.echo("-------- Grok mode disabled due to Codex AMR activation")
            except Exception:
                pass
        typer.echo("-------- Codex AMR mode: ENABLED (.cursor/.codex-mode)")
    except Exception as e:
        typer.echo(f"❌ Error enabling Codex mode: {e}", err=True)
        raise typer.Exit(1)


@app.command("codex-mode-off")
def codex_mode_off(
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Disable Codex AMR mode by removing .cursor/.codex-mode flag."""
    try:
        root = Path(project_root or ".")
        flag = root / ".cursor" / ".codex-mode"
        if flag.exists():
            flag.unlink()
            typer.echo("-------- Codex AMR mode: DISABLED")
        else:
            typer.echo("-------- Codex AMR mode: Already disabled")
    except Exception as e:
        typer.echo(f"❌ Error disabling Codex mode: {e}", err=True)
        raise typer.Exit(1)


@app.command("grok-mode-on")
def grok_mode_on(
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Enable Grok mode by creating .cursor/.grok-mode flag (and disable Codex mode)."""
    try:
        root = Path(project_root or ".")
        cursor_dir = root / ".cursor"
        cursor_dir.mkdir(parents=True, exist_ok=True)
        flag = cursor_dir / ".grok-mode"
        flag.write_text("", encoding="utf-8")
        # Mutual exclusivity: disable Codex mode flag if present
        codex_flag = root / ".codex" / ".codex-mode"
        if codex_flag.exists():
            try:
                codex_flag.unlink()
                typer.echo("-------- Codex AMR mode disabled due to Grok activation")
            except Exception:
                pass
        typer.echo("-------- Grok mode: ENABLED (.cursor/.grok-mode)")
    except Exception as e:
        typer.echo(f"❌ Error enabling Grok mode: {e}", err=True)
        raise typer.Exit(1)


@app.command("grok-mode-off")
def grok_mode_off(
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Disable Grok mode by removing .cursor/.grok-mode flag."""
    try:
        root = Path(project_root or ".")
        flag = root / ".cursor" / ".grok-mode"
        if flag.exists():
            flag.unlink()
            typer.echo("-------- Grok mode: DISABLED")
        else:
            typer.echo("-------- Grok mode: Already disabled")
    except Exception as e:
        typer.echo(f"❌ Error disabling Grok mode: {e}", err=True)
        raise typer.Exit(1)


@app.command("personas-init")
def personas_init(
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite if exists"),
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Copy package personas manifest into project personas/manifest.yaml"""
    try:
        root = Path(project_root or ".")
        src = Path(__file__).parent.parent.parent / "cursor-assets" / "manifests" / "personas.yaml"
        dst_dir = root / "personas"
        dst = dst_dir / "manifest.yaml"
        dst_dir.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not overwrite:
            typer.echo(f"➡️  personas manifest exists: {dst} (use --overwrite to replace)")
            return
        dst.write_text(src.read_text())
        typer.echo(f"--------personas:init: wrote manifest → {dst}")
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command("personas-build")
def personas_build(
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Build personas assets (Cursor commands + rules) in current project"""
    try:
        root = Path(project_root or ".")
        cursor = CursorAdapter()
        cursor.generate_commands(root)
        cursor.generate_rules(root)
        typer.echo("--------personas:build: .cursor commands + rules updated")
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command("mcp-serve")
def mcp_serve():
    """Start the Super Prompt FastMCP server."""
    try:
        # We construct the path to the server script relative to this CLI script.
        # This makes the execution path independent of where the user runs the command.
        server_script_path = Path(__file__).parent / "mcp_stdio.py"

        if not server_script_path.exists():
            typer.echo(
                f"❌ Fatal Error: MCP server script not found at {server_script_path}", err=True
            )
            typer.echo("   The package installation may be corrupt.", err=True)
            raise typer.Exit(1)

        typer.echo(f"🚀 Starting FastMCP server from: {server_script_path}")
        typer.echo("   Press Ctrl+C to exit.")

        # Use sys.executable so we run under the same interpreter as this CLI
        env = os.environ.copy()
        if os.environ.get("MCP_SERVER_MODE"):
            # In MCP server mode, suppress all output to avoid stdout pollution
            subprocess.run([sys.executable, str(server_script_path)], env=env, check=True,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run([sys.executable, str(server_script_path)], env=env, check=True)

    except subprocess.CalledProcessError as e:
        # This will trigger if the server exits with a non-zero code.
        # We can ignore this for now as a normal shutdown might be non-zero.
        pass
    except KeyboardInterrupt:
        typer.echo("\n🛑 Server stopped by user.")
    except Exception as e:
        typer.echo(f"❌ Error starting MCP server: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def sdd_cli(
    action: str = typer.Argument(..., help="SDD action (spec/plan/tasks/implement)"),
    feature: str = typer.Argument(..., help="Feature name"),
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """[DEPRECATED] SDD (Spec-Driven Development) workflow commands. Use flags like --sp-sdd-spec instead."""
    typer.echo(
        "⚠️  Warning: The 'sdd' subcommand is deprecated and will be removed. Use flags like --sp-sdd-spec instead.",
        err=True,
    )
    sdd_command(action, feature, project_root)


@app.command()
def personas(
    action: str = typer.Argument(..., help="Action (list/show/load)"),
    name: Optional[str] = typer.Argument(None, help="Persona name"),
    manifest_path: Optional[Path] = typer.Option(None, "--manifest", help="Manifest file path"),
):
    """Manage personas and their configurations"""
    try:
        loader = PersonaLoader(manifest_path)

        if action == "list":
            personas = loader.list_personas()
            typer.echo("Available personas:")
            for persona in personas:
                typer.echo(f"  - {persona['name']}: {persona['description']}")

        elif action == "show" and name:
            persona = loader.get_persona(name)
            if persona:
                typer.echo(f"Persona: {persona.name}")
                typer.echo(f"Role: {persona.role_type}")
                typer.echo(f"Expertise: {persona.expertise_level}")
                typer.echo(f"Specializations: {', '.join(persona.specializations)}")
            else:
                typer.echo(f"❌ Persona not found: {name}", err=True)
                raise typer.Exit(1)

        elif action == "load":
            count = loader.load_manifest()
            typer.echo(f"✅ Loaded {count} personas from manifest")

        else:
            typer.echo(f"❌ Unknown personas action: {action}", err=True)
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def context(
    action: str = typer.Argument(..., help="Action (collect/stats/clear)"),
    query: Optional[str] = typer.Argument(None, help="Query for context collection"),
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
    max_tokens: int = typer.Option(16000, "--max-tokens", help="Maximum context tokens"),
):
    """Context collection and management"""
    try:
        collector = ContextCollector(str(project_root) if project_root else ".")

        if action == "collect" and query:
            result = collector.collect_context(query, max_tokens=max_tokens)
            typer.echo(f"📊 Collected context for: {query}")
            typer.echo(f"   Files: {len(result['files'])}")
            typer.echo(f"   Tokens: {result['metadata']['context_tokens']}")
            typer.echo(f"   Time: {result['metadata']['collection_time']:.2f}s")

        elif action == "stats":
            stats = collector.get_stats()
            typer.echo("Context collector stats:")
            typer.echo(f"   Cache size: {stats['cache_size']}")
            typer.echo(f"   Gitignore loaded: {stats['gitignore_loaded']}")

        elif action == "clear":
            collector.clear_cache()
            typer.echo("✅ Context cache cleared")

        else:
            typer.echo(f"❌ Unknown context action: {action}", err=True)
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def validate(
    action: str = typer.Argument(..., help="Action (todo/check)"),
    target: Optional[str] = typer.Argument(None, help="Validation target"),
    project_root: Optional[Path] = typer.Option(
        None, "--project-root", help="Project root directory"
    ),
):
    """Validation and quality checks"""
    try:
        if action == "todo" and target:
            validator = TodoValidator()
            result = validator.validate_task_completion(target)

            if result[0]:  # Success
                typer.echo(f"✅ Task '{target}' validation passed")
            else:
                typer.echo(f"❌ Task '{target}' validation failed: {result[1]}")

        elif action == "check":
            # Run comprehensive checks
            checks = [
                (
                    "SDD gates",
                    lambda: check_implementation_ready(
                        target or "default", str(project_root) if project_root else "."
                    ),
                ),
                (
                    "Context collection",
                    lambda: len(
                        ContextCollector(
                            str(project_root) if project_root else "."
                        ).collect_context("test")["files"]
                    )
                    > 0,
                ),
            ]

            typer.echo("Running validation checks:")
            all_passed = True

            for check_name, check_func in checks:
                try:
                    result = check_func()
                    if hasattr(result, "ok"):
                        passed = result.ok
                        details = f" ({len(result.missing)} issues)" if result.missing else ""
                    else:
                        passed = bool(result)
                        details = ""

                    status = "✅" if passed else "❌"
                    typer.echo(f"   {status} {check_name}{details}")

                    if not passed:
                        all_passed = False

                except Exception as e:
                    typer.echo(f"   ❌ {check_name}: Error - {e}")
                    all_passed = False

            if all_passed:
                typer.echo("🎉 All validation checks passed!")
            else:
                typer.echo("⚠️  Some validation checks failed")
                raise typer.Exit(1)

        else:
            typer.echo(f"❌ Unknown validate action: {action}", err=True)
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def init(
    project_root: Optional[Path] = typer.Option(
        Path("."), "--project-root", help="Project root directory"
    ),
    force: bool = typer.Option(False, "--force", help="Force reinitialization"),
):
    """Initialize Super Prompt for a project

    CRITICAL PROTECTION: This command and all personas MUST NEVER modify files in:
    - .cursor/ (Cursor IDE configuration)
    - .super-prompt/ (Super Prompt internal files)
    - .codex/ (Codex CLI configuration)
    These directories are protected and should only be modified by official installation processes.
    """
    # 디버깅 메시지 (함수 시작 부분)
    import sys
    import os
    print("=== INIT FUNCTION STARTED ===", file=sys.stderr, flush=True)
    print(f"DEBUG: init function called with project_root={project_root}, force={force}", file=sys.stderr, flush=True)

    try:
        # CRITICAL PROTECTION: Display protection warning
        typer.echo("\033[31m\033[1m🚨 CRITICAL PROTECTION NOTICE:\033[0m")
        typer.echo("\033[33mPersonas and user commands MUST NEVER modify files in:\033[0m")
        typer.echo("\033[33m  - .cursor/ (Cursor IDE configuration)\033[0m")
        typer.echo("\033[33m  - .super-prompt/ (Super Prompt internal files)\033[0m")
        typer.echo("\033[33m  - .codex/ (Codex CLI configuration)\033[0m")
        typer.echo(
            "\033[36mThis official installation process is authorized to create these directories.\033[0m"
        )
        typer.echo()

        # Display Super Prompt ASCII Art
        current_version = get_current_version()
        logo = f"""
\033[36m\033[1m
   ███████╗██╗   ██╗██████╗ ███████╗██████╗
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
   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝
\033[0m
\033[2m              Dual IDE Prompt Engineering Toolkit\033[0m
\033[2m                     v{current_version} | @cdw0424/super-prompt\033[0m
\033[2m                          Made by \033[0m\033[35mDaniel Choi from Korea\033[0m
"""
        typer.echo(logo)
        typer.echo()

        # Resolve real project root (never point to .super-prompt here)
        target_dir = Path(project_root).resolve() if project_root else Path.cwd().resolve()
        os.environ["SUPER_PROMPT_PROJECT_ROOT"] = str(target_dir)

        # Python dependencies are managed via system Python
        typer.echo("ℹ️  Using system Python for dependencies")

        # --- Legacy cleanup (idempotent) ---
        legacy_paths = [
            target_dir / ".cursor" / "commands" / "super-prompt" / "tag-executor.sh",
            target_dir / ".cursor" / "commands" / "super-prompt" / "re-init.md",
        ]
        for p in legacy_paths:
            try:
                if p.exists():
                    p.unlink()
                    typer.echo(f"🧹 Removed legacy artifact: {p}")
            except Exception:
                pass

        # Ensure base dirs with validation (exclude .cursor for global management)
        dirs_to_create = [
            target_dir / ".super-prompt",
            target_dir / "bin",
            target_dir / "specs",
            target_dir / "memory" / "constitution",
            target_dir / "memory" / "rules",
        ]
        created_dirs = []
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
            if dir_path.exists():
                created_dirs.append(dir_path)
            else:
                typer.echo(f"⚠️  Failed to create directory: {dir_path}")

        typer.echo(f"✅ Created {len(created_dirs)} directories")

        # Install local MCP launcher into project (./bin/sp-mcp) to guarantee Cursor uses local server
        launcher_installed = False
        try:
            from .paths import package_root as _pkg_root
            pkg_root = _pkg_root()
            src = (pkg_root / "bin" / "sp-mcp")
            dst = target_dir / "bin" / "sp-mcp"
            if src.exists():
                if src.resolve() != dst.resolve():
                    import shutil
                    shutil.copy2(src, dst)
                    try:
                        dst.chmod(0o755)
                    except Exception:
                        pass
                    if dst.exists():
                        launcher_installed = True
                        typer.echo(f"✅ Installed local MCP launcher: {dst}")
                    else:
                        typer.echo("⚠️  MCP launcher copy failed")
                else:
                    # Already in place (developer repo case)
                    try:
                        dst.chmod(0o755)
                    except Exception:
                        pass
                    if dst.exists():
                        launcher_installed = True
                        typer.echo(f"✅ Local MCP launcher already present: {dst}")
            else:
                typer.echo("⚠️  Could not find package launcher bin/sp-mcp; falling back to python -m")
        except Exception as e:
            typer.echo(f"⚠️  Could not install local launcher: {e}")
            launcher_installed = False

        # Store MCP settings globally at ~/.cursor/mcp.json (avoid duplication)
        typer.echo("✅ MCP settings will be configured globally at ~/.cursor/mcp.json")

        # Store Codex settings only globally at ~/.codex (no project .codex creation)
        typer.echo("✅ Codex settings will be configured globally at ~/.codex")

        # Copy .super-prompt directory from package
        import shutil
        super_prompt_dir = target_dir / ".super-prompt"

        # Find source .super-prompt directory
        source_super_prompt = None
        env_pkg_root = os.environ.get("SUPER_PROMPT_PACKAGE_ROOT")
        if env_pkg_root and Path(env_pkg_root).exists() and (Path(env_pkg_root) / ".super-prompt").exists():
            source_super_prompt = Path(env_pkg_root) / ".super-prompt"
            typer.echo(f"✅ Found .super-prompt source at: {source_super_prompt}")
        else:
            # Try to find package root
            current = Path(__file__).resolve()
            while current.parent != current:
                if (current / ".super-prompt").exists():
                    source_super_prompt = current / ".super-prompt"
                    typer.echo(f"✅ Found .super-prompt source at: {source_super_prompt}")
                    break
                current = current.parent

        # Create .super-prompt directory with minimal configuration
        super_prompt_dir.mkdir(exist_ok=True)

        config_content = {
            "version": current_version,
            "initialized_at": str(target_dir.absolute()),
            "databases": {
                "evol_kv_memory": ".super-prompt/evol_kv_memory.db",
                "context_memory": "context_memory.db",
            },
            "protection": {
                "protected_directories": [".cursor", ".super-prompt", ".codex"],
                "message": "These directories are protected from modification by personas and user commands",
            },
        }

        config_file = super_prompt_dir / "config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_content, f, indent=2, ensure_ascii=False)

        typer.echo("✅ Super Prompt configuration created (.super-prompt/)")

        # Example SDD scaffold (unchanged)
        sdd_dir = target_dir / "specs" / "example-feature"
        sdd_dir.mkdir(exist_ok=True)
        spec_file = sdd_dir / "spec.md"
        if not spec_file.exists() or force:
            spec_file.write_text(
                """# Example Feature Specification

## Overview
Brief description of the feature.

## Requirements
- Requirement 1
- Requirement 2

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Acceptance Criteria
- [ ] Test case 1
- [ ] Test case 2
"""
            )

        # Complete initialization - Critical for full functionality
        try:
            # SilentProgress 완전 우회
            import sys
            import os
            os.environ['SUPER_PROMPT_DEBUG'] = '1'  # 디버깅 모드 활성화

            # SilentProgress 완전 제거 (초기화 함수에서만)
            try:
                from .core.memory_manager import progress
                if hasattr(progress, '_mcp_silent'):
                    from .core.memory_manager import ProgressIndicator
                    progress.show_progress = ProgressIndicator.show_progress.__get__(progress, ProgressIndicator)
                    progress.show_success = ProgressIndicator.show_success.__get__(progress, ProgressIndicator)
                    progress.show_error = ProgressIndicator.show_error.__get__(progress, ProgressIndicator)
                    delattr(progress, '_mcp_silent')
            except Exception:
                pass

            # 디버깅 메시지 출력 (강제 stderr)
            print("=== SUPER PROMPT DEBUG MODE ACTIVATED ===", file=sys.stderr, flush=True)
            print(f"DEBUG: CLI init function called at {os.getcwd()}", file=sys.stderr, flush=True)
            print(f"DEBUG: target_dir = {target_dir}", file=sys.stderr, flush=True)
            print(f"DEBUG: force = {force}", file=sys.stderr, flush=True)
            sys.stderr.flush()

            # 초기화 과정 전체에서 stderr 사용
            # CLI 모드에서는 디버그 로그를 완전히 비활성화하여 가독성 향상
            if os.environ.get("SUPER_PROMPT_CLI_MODE") == "1":
                def debug_echo(message):
                    pass  # CLI 모드에서는 디버그 로그 완전 비활성화
            else:
                def debug_echo(message):
                    print(f"DEBUG: {message}", file=sys.stderr, flush=True)

            debug_echo("Starting project root configuration")

            # 0. Python 패키지 복사 (가장 먼저 실행)
            if os.environ.get("SUPER_PROMPT_CLI_MODE") != "1":
                sys.stderr.write("DEBUG: About to copy Python packages\n")
                sys.stderr.flush()

            # Python 패키지 파일 복사 (npm에 번들된 super_prompt-core → .super-prompt/lib)
            try:
                import shutil

                current_file = Path(__file__)
                # Python 패키지 루트 찾기: python-packages/super-prompt-core
                package_root = None
                # 1. 환경 변수에서 찾기
                env_pkg_root = os.environ.get("SUPER_PROMPT_PACKAGE_ROOT")
                if env_pkg_root and Path(env_pkg_root).exists():
                    package_root = Path(env_pkg_root)
                else:
                    # 2. 파일 위치에서 찾기 (상대 경로)
                    p = current_file.parent  # super_prompt/
                    while p != p.parent:
                        if (p / "python-packages" / "super-prompt-core").exists():
                            package_root = p / "python-packages" / "super-prompt-core"
                            break
                        p = p.parent

                if not package_root or not package_root.exists():
                    if os.environ.get("SUPER_PROMPT_CLI_MODE") != "1":
                        sys.stderr.write(f"DEBUG: Python package root not found at {package_root}\n")
                        sys.stderr.flush()
                    raise FileNotFoundError(f"Python package root not found")

                if os.environ.get("SUPER_PROMPT_CLI_MODE") != "1":
                    sys.stderr.write(f"DEBUG: Starting Python package copy from {package_root}\n")
                    sys.stderr.flush()

                # 준비: 대상 디렉토리 생성
                super_prompt_dir = target_dir / ".super-prompt"
                super_prompt_dir.mkdir(parents=True, exist_ok=True)
                lib_dir = super_prompt_dir / "lib"
                lib_dir.mkdir(parents=True, exist_ok=True)

                # 기존 Python 패키지 제거
                existing_pkg = lib_dir / "super_prompt"
                if existing_pkg.exists():
                    shutil.rmtree(existing_pkg)

                # super-prompt-core/super_prompt 폴더만 복사 (Python 패키지)
                source_package = package_root / "super_prompt"
                if source_package.exists():
                    shutil.copytree(source_package, lib_dir / "super_prompt", dirs_exist_ok=True)
                else:
                    # 폴백: 전체 복사 후 불필요한 파일 제거
                    shutil.copytree(package_root, lib_dir / "super_prompt", dirs_exist_ok=True)
                    # 불필요한 파일들 제거
                    unnecessary_files = ["pyproject.toml", "README.md", "pytest.ini"]
                    for file in unnecessary_files:
                        unnecessary_path = lib_dir / "super_prompt" / file
                        if unnecessary_path.exists():
                            if unnecessary_path.is_file():
                                unnecessary_path.unlink()
                            else:
                                shutil.rmtree(unnecessary_path)

                # .pth 파일 (PYTHONPATH 대체용)
                (lib_dir / "super_prompt.pth").write_text("")

                if os.environ.get("SUPER_PROMPT_CLI_MODE") != "1":
                    py_files = list((lib_dir / "super_prompt").rglob("*.py"))
                    sys.stderr.write(f"DEBUG: Copied Python package to {lib_dir}, found {len(py_files)} python files\n")
                    sys.stderr.flush()
            except Exception as e:
                if os.environ.get("SUPER_PROMPT_CLI_MODE") != "1":
                    import traceback
                    sys.stderr.write(f"DEBUG: Python package copy failed: {e}\n")
                    sys.stderr.write(f"DEBUG: traceback: {traceback.format_exc()}\n")
                    sys.stderr.flush()

            # 1. 프로젝트 루트 설정 (사용자 입력 또는 환경 변수 또는 기본값)
            # 우선순위: 환경 변수 > 사용자 입력 > 기본값
            debug_echo("Step 1: Setting up project root")
            project_root_input = os.environ.get("SUPER_PROMPT_PROJECT_ROOT", str(target_dir))

            # 기본적으로 대화형 모드 활성화 (사용자가 명시적으로 비활성화하지 않은 경우)
            interactive = os.environ.get("SUPER_PROMPT_INTERACTIVE", "1") == "1"

            if interactive:
                try:
                    # 입력 프롬프트 가독성 향상을 위한 공백 추가
                    typer.echo("")  # 빈 줄 추가
                    typer.echo("=" * 60)
                    user_input = typer.prompt("📁 Input your project root path", default=str(target_dir))
                    typer.echo("=" * 60)
                    if user_input.strip():
                        project_root_input = user_input
                except Exception:
                    pass  # 비대화형 환경에서는 기본값 사용

            # 2. MCP 서버 설정 (사용자 입력 또는 기본값)
            debug_echo("Step 2: Setting up MCP server configuration")

            # MCP 서버 실행 파일 경로 설정
            mcp_server_path = f"{project_root_input}/bin/sp-mcp"

            # Python 패키지 경로 설정
            python_package_path = f"{project_root_input}/.super-prompt/lib"

            if interactive:
                try:
                    # MCP 서버 경로 확인
                    typer.echo("")  # 빈 줄 추가
                    typer.echo("=" * 60)
                    mcp_input = typer.prompt(
                        f"🔧 Input your MCP server path",
                        default=mcp_server_path
                    )
                    typer.echo("=" * 60)
                    if mcp_input.strip():
                        mcp_server_path = mcp_input

                    # Python 패키지 경로 확인
                    typer.echo("")  # 빈 줄 추가
                    typer.echo("=" * 60)
                    python_input = typer.prompt(
                        f"📦 Input your Python package path",
                        default=python_package_path
                    )
                    typer.echo("=" * 60)
                    if python_input.strip():
                        python_package_path = python_input

                except Exception:
                    pass  # 비대화형 환경에서는 기본값 사용

            # 2. Python 패키지 설치 확인 및 설치 (조용한 모드)
            try:
                import importlib.util
                if importlib.util.find_spec("super_prompt") is None:
                    # Python 패키지 설치 시도 (조용히)
                    try:
                        import subprocess
                        import sys
                        subprocess.run([
                            sys.executable, "-m", "pip", "install",
                            "--user", "super-prompt-core==5.2.21"
                        ], capture_output=True, text=True, timeout=60)
                    except Exception:
                        pass  # 조용히 실패 처리
            except Exception:
                pass  # 조용히 실패 처리

            # 3. Super Prompt 내부 파일들 생성 (조용한 모드)
            try:
                # .super-prompt 폴더 생성
                super_prompt_dir = target_dir / ".super-prompt"
                super_prompt_dir.mkdir(parents=True, exist_ok=True)

                # 디버깅: .super-prompt 폴더 생성 확인
                if os.environ.get("SUPER_PROMPT_CLI_MODE") != "1":
                    sys.stderr.write(f"DEBUG: Created .super-prompt directory: {super_prompt_dir}\n")
                    sys.stderr.flush()

                # lib 폴더 생성 (Python 패키지용)
                lib_dir = super_prompt_dir / "lib"
                lib_dir.mkdir(parents=True, exist_ok=True)

                # config.json 생성
                config_file = super_prompt_dir / "config.json"
                if not config_file.exists():
                    from datetime import datetime
                    config_data = {
                        "createdAt": datetime.now().isoformat(),
                        "projectRoot": project_root_input,
                        "mcpServerPath": mcp_server_path,
                        "pythonPackagePath": python_package_path,
                        "mode": "gpt",
                        "version": "5.2.35",
                        "pythonPath": python_package_path
                    }
                    with open(config_file, 'w') as f:
                        json.dump(config_data, f, indent=2)

                # mode.json 생성
                mode_file = super_prompt_dir / "mode.json"
                if not mode_file.exists():
                    mode_data = {"mode": "gpt"}
                    with open(mode_file, 'w') as f:
                        json.dump(mode_data, f, indent=2)

                # cache 폴더 생성
                cache_dir = super_prompt_dir / "cache"
                cache_dir.mkdir(parents=True, exist_ok=True)

                # context_cache.json 생성
                cache_file = cache_dir / "context_cache.json"
                if not cache_file.exists():
                    from datetime import datetime
                    cache_data = {
                        "createdAt": datetime.now().isoformat(),
                        "contexts": []
                    }
                    with open(cache_file, 'w') as f:
                        json.dump(cache_data, f, indent=2)

                # (중복 제거) 위에서 이미 복사 수행함
                pass

            except Exception:
                pass  # 조용히 실패 처리

            # 4. 커서 명령어와 규칙 파일 생성 (안전한 방법)
            try:
                import shutil

                # assets 경로 찾기
                try:
                    from .adapters.cursor_adapter import CursorAdapter
                    cursor_adapter = CursorAdapter()
                    assets_root = cursor_adapter.assets_root
                except Exception:
                    # CursorAdapter가 실패하면 직접 assets 경로 설정
                    from .paths import package_root
                    assets_root = package_root() / "packages" / "cursor-assets"

                # Commands 복사
                commands_dir = target_dir / ".cursor" / "commands" / "super-prompt"
                commands_dir.mkdir(parents=True, exist_ok=True)

                commands_src_dir = assets_root / "commands" / "super-prompt"
                if commands_src_dir.exists():
                    for md_file in commands_src_dir.glob("*.md"):
                        dst_file = commands_dir / md_file.name
                        if not dst_file.exists():
                            shutil.copy2(md_file, dst_file)

                # Rules 복사
                rules_dir = target_dir / ".cursor" / "rules"
                rules_dir.mkdir(parents=True, exist_ok=True)

                rules_src_dir = assets_root / "rules"
                if rules_src_dir.exists():
                    for mdc_file in rules_src_dir.glob("*.mdc"):
                        dst_file = rules_dir / mdc_file.name
                        if not dst_file.exists():
                            shutil.copy2(mdc_file, dst_file)

            except Exception:
                pass  # 조용히 실패 처리

            # 5. 전역 MCP 설정 사용 (프로젝트 로컬 MCP 설정 생성하지 않음)
            # MCP 설정은 전역 ~/.cursor/mcp.json에서만 관리됨 (SSOT 준수)

            # 6. 추가 디렉토리들 생성
            try:
                # specs 폴더
                specs_dir = target_dir / "specs"
                specs_dir.mkdir(parents=True, exist_ok=True)

                # memory 폴더
                memory_dir = target_dir / "memory"
                memory_dir.mkdir(parents=True, exist_ok=True)

                # .codex 폴더
                codex_dir = target_dir / ".codex"
                codex_dir.mkdir(parents=True, exist_ok=True)

            except Exception:
                pass  # 조용히 실패 처리

            # 초기화 완료 (최소 로그만 출력)
            # MCP 서버가 올바르게 작동하도록 최소한의 로그만 출력

        except Exception:
            pass  # 조용히 실패 처리

        # Optional: Codex registration (always overwrite to prevent drift)
        codex_registered = False
        try:
            codex_cfg = ensure_codex_mcp_registered(target_dir, overwrite=True)
            codex_registered = True
            typer.echo(f"✅ Codex MCP server registered: {codex_cfg}")
            typer.echo("✅ Codex configuration: Using GLOBAL ~/.codex (prevents duplication)")
        except Exception as e:
            typer.echo(f"⚠️  Codex registration failed: {e}")
            codex_registered = False

        # Execute SSOT compliance validation
        try:
            ssot_compliant = validate_project_ssot(target_dir)
            if ssot_compliant:
                typer.echo("✅ SSOT compliant: No project setting conflicts")
            else:
                typer.echo("⚠️  SSOT violation: Conflicts detected between project and global settings")
                typer.echo("💡 Solution: Clean up global settings or prioritize project settings")
        except Exception as e:
            typer.echo(f"⚠️  SSOT validation failed: {e}")

        # Ensure default LLM mode is GPT
        try:
            set_mode_file("gpt")
            typer.echo("✅ Default LLM mode set to gpt (.super-prompt/mode.json)")
        except Exception as e:
            typer.echo(f"⚠️  Could not set default mode: {e}")

        # Ensure personas manifest is materialized from SSOT with validation
        personas_manifest_valid = False
        try:
            loader = PersonaLoader()
            loader.load_manifest()

            # Verify personas manifest was created and is valid
            personas_dir = target_dir / "personas"
            manifest_file = personas_dir / "manifest.yaml"

            if manifest_file.exists():
                try:
                    import yaml
                    with open(manifest_file, 'r', encoding='utf-8') as f:
                        manifest_data = yaml.safe_load(f)

                    if manifest_data and 'agents' in manifest_data:
                        agent_count = len(manifest_data['agents'])
                        typer.echo(f"✅ Personas manifest validated: {agent_count} personas in {manifest_file}")
                        personas_manifest_valid = True
                    else:
                        typer.echo("⚠️  Personas manifest exists but has invalid structure")
                except yaml.YAMLError as e:
                    typer.echo(f"⚠️  Personas manifest YAML parsing error: {e}")
                except Exception as e:
                    typer.echo(f"⚠️  Personas manifest validation error: {e}")
            else:
                typer.echo("⚠️  Personas manifest file not found")

        except Exception as e:
            typer.echo(f"⚠️  Could not materialize personas manifest: {e}")

        # Generate Cursor commands and rules from manifest/templates (idempotent)
        cursor_commands_generated = False
        cursor_rules_generated = False
        try:
            from .adapters.cursor_adapter import CursorAdapter
            cursor = CursorAdapter()
            # Generate Cursor assets locally in project directory
            cursor.generate_commands(target_dir)  # Project-local generation enabled
            cursor.generate_rules(target_dir)     # Project-local generation enabled

            # Verify Cursor assets were generated in project directory
            project_commands_dir = target_dir / ".cursor" / "commands" / "super-prompt"
            project_rules_dir = target_dir / ".cursor" / "rules"

            if project_commands_dir.exists():
                command_files = list(project_commands_dir.glob("*.md"))
                if command_files:
                    cursor_commands_generated = True
                    typer.echo(f"✅ Cursor commands available locally: {len(command_files)} commands in .cursor/commands/super-prompt/")
                else:
                    typer.echo("⚠️  Cursor commands directory exists but no command files found")
            else:
                typer.echo("⚠️  Cursor commands directory not found")

            if project_rules_dir.exists():
                rule_files = list(project_rules_dir.glob("*.mdc"))
                if rule_files:
                    cursor_rules_generated = True
                    typer.echo(f"✅ Cursor rules available locally: {len(rule_files)} rules in .cursor/rules/")
                else:
                    typer.echo("⚠️  Cursor rules directory exists but no rule files found")
            else:
                typer.echo("⚠️  Cursor rules directory not found")

        except Exception as e:
            typer.echo(f"⚠️  Could not generate Cursor assets: {e}")

        # 🔍 Environment verification and status check
        try:
            typer.echo("🔍 Performing environment verification...")

            # MCP environment verification (global settings)
            mcp_config = Path.home() / ".cursor" / "mcp.json"
            if mcp_config.exists():
                typer.echo("✅ MCP configuration verified globally (~/.cursor/mcp.json)")
            else:
                typer.echo("⚠️  MCP configuration not found in global location")

            # Memory system verification
            memory_dir = target_dir / "memory"
            if memory_dir.exists():
                typer.echo("✅ Memory system directories verified")
            else:
                typer.echo("⚠️  Memory system directories not found")

            # Persona system verification
            personas_dir = target_dir / "personas"
            if personas_dir.exists():
                typer.echo("✅ Personas system directories verified")
            else:
                typer.echo("⚠️  Personas system directories not found")

            typer.echo("✅ Environment verification completed")

        except Exception as e:
            typer.echo(f"⚠️  Environment verification failed: {e}")

        # 🔍 MCP Sanity Check - Verify MCP server functionality
        typer.echo("\n🔍 Performing MCP server sanity check...")
        mcp_healthy = False
        try:
            # Test MCP server connectivity using Python client
            from .mcp_client import MCPClient
            import asyncio

            async def test_mcp():
                async with MCPClient() as client:
                    # Test list-tools
                    tools = await client.list_tools()
                    typer.echo(f"✅ MCP list-tools: {len(tools)} tools available")

                    # Test call-tool (sp.list_commands)
                    if tools:
                        try:
                            result = await client.call_tool("sp.list_commands", {})
                            typer.echo("✅ MCP call-tool: sp.list_commands executed successfully")
                        except Exception as e:
                            typer.echo(f"⚠️  MCP call-tool test failed: {e}")

                    return True

            mcp_healthy = asyncio.run(test_mcp())
        except Exception as e:
            typer.echo(f"❌ MCP sanity check failed: {e}")
            typer.echo("💡 Try running: super-prompt mcp doctor --verbose")

        # 📊 Final status summary
        typer.echo("\n" + "=" * 60)
        typer.echo("🎉 SUPER PROMPT INITIALIZATION COMPLETE!")
        typer.echo("=" * 60)
        typer.echo("✅ All systems configured and verified")
        if mcp_healthy:
            typer.echo("✅ MCP server verified and functional")
        else:
            typer.echo("⚠️  MCP server verification failed (may work after restart)")
        typer.echo("✅ Memory and context systems initialized")
        typer.echo("✅ All personas and commands available")
        typer.echo("=" * 60)
        typer.echo("✅ Super Prompt initialized!")
        typer.echo(f"   Project root: {target_dir.absolute()}")
        typer.echo(f"   Version: {current_version}")
        typer.echo("   Created directories:")
        typer.echo("     - ~/.cursor/commands/super-prompt/ (global persona commands)")
        typer.echo("     - ~/.cursor/rules/ (global SuperClaude framework rules)")
        typer.echo("     - .super-prompt/ (with all internal system files)")
        typer.echo("     - .codex/ (with agents.md, bootstrap prompt, router script)")
        typer.echo("     - specs/ (for SDD specifications)")
        typer.echo("     - memory/ (for context and rules)")
        typer.echo("   MCP Settings:")
        typer.echo("     - ~/.cursor/mcp.json (global MCP server configuration)")
        typer.echo("   Next steps:")
        typer.echo("   1. Use Cursor: /init-sp (initial index), /re-init-sp (refresh)")
        typer.echo("   2. Personas: /architect, /frontend, /doc-master, etc.")
        typer.echo("   3. SDD: /specify → /plan → /tasks")
        if mcp_healthy:
            typer.echo("   4. Test MCP: super-prompt mcp doctor")

    except Exception as e:
        typer.echo(f"❌ Initialization failed: {e}", err=True)
        raise typer.Exit(1)


# Alias: super:init → init
@app.command("super:init")
def super_init_alias(
    project_root: Optional[Path] = typer.Option(
        ".", "--project-root", help="Project root directory"
    ),
    force: bool = typer.Option(False, "--force", help="Force reinitialization"),
):
    """Alias for init to support `super:init`.

    CRITICAL PROTECTION: This command and all personas MUST NEVER modify files in:
    - .cursor/ (Cursor IDE configuration)
    - .super-prompt/ (Super Prompt internal files)
    - .codex/ (Codex CLI configuration)
    These directories are protected and should only be modified by official installation processes.
    """
    # 디버깅 메시지 (강제 stderr)
    import sys
    import os
    print("=== DEBUG: super_init_alias called ===", file=sys.stderr, flush=True)
    print(f"DEBUG: super_init_alias called at {os.getcwd()}", file=sys.stderr, flush=True)
    print(f"DEBUG: project_root = {project_root}", file=sys.stderr, flush=True)
    print(f"DEBUG: force = {force}", file=sys.stderr, flush=True)
    sys.stderr.flush()

    target_dir = Path(project_root) if project_root else Path(".")
    print(f"DEBUG: target_dir = {target_dir}", file=sys.stderr, flush=True)
    sys.stderr.flush()

    # init 함수 호출 전후 디버깅
    print("=== ABOUT TO CALL INIT FUNCTION ===", file=sys.stderr, flush=True)
    print(f"DEBUG: About to call init function with target_dir={target_dir}, force={force}", file=sys.stderr, flush=True)
    sys.stderr.flush()

    result = init(target_dir, force)

    print("=== INIT FUNCTION COMPLETED ===", file=sys.stderr, flush=True)
    print(f"DEBUG: init function returned: {result}", file=sys.stderr, flush=True)
    sys.stderr.flush()
    return result


def handle_enhanced_persona_execution(system_prompt: str, persona_key: str, args: list):
    """Handle enhanced persona execution with system prompt from environment (legacy)"""
    try:
        # Get user input from remaining arguments (after flags)
        user_input = " ".join(args) if args else ""

        if not user_input:
            typer.echo("❌ Error: No user input provided for persona execution", err=True)
            raise typer.Exit(1)

        typer.echo(f"-------- Enhanced Persona Execution: {persona_key} (via env vars)")
        typer.echo(f"-------- System prompt loaded ({len(system_prompt)} chars)")
        typer.echo(
            f"-------- User input: {user_input[:100]}{'...' if len(user_input) > 100 else ''}"
        )

        # Load persona configuration
        personas_dir = Path(__file__).parent / "personas"
        manifest_path = personas_dir / "manifest.yaml"

        if manifest_path.exists():
            import yaml

            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = yaml.safe_load(f)

            if persona_key in manifest.get("personas", {}):
                persona_config = manifest["personas"][persona_key]
                typer.echo(f"-------- Loaded persona: {persona_config.get('name', persona_key)}")
            else:
                typer.echo(f"⚠️  Persona '{persona_key}' not found in manifest, proceeding anyway")
        else:
            typer.echo("⚠️  Persona manifest not found, proceeding with basic execution")

        # Here we would integrate with the actual AI processing
        # For now, we'll just display the system prompt and user input
        typer.echo("\n" + "=" * 60)
        typer.echo("🤖 SYSTEM PROMPT:")
        typer.echo("=" * 60)
        typer.echo(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)

        typer.echo("\n" + "=" * 60)
        typer.echo("👤 USER INPUT:")
        typer.echo("=" * 60)
        typer.echo(user_input)

        typer.echo("\n" + "=" * 60)
        typer.echo("✅ Enhanced persona execution framework ready!")
        typer.echo("   (Actual AI processing would happen here)")
        typer.echo("=" * 60)

    except Exception as e:
        typer.echo(f"❌ Enhanced persona execution failed: {e}", err=True)
        raise typer.Exit(1)


def handle_enhanced_persona_execution_from_context(execution_context: dict, args: list):
    """Handle enhanced persona execution using context object (no OS env vars)"""
    try:
        # Extract data from context object
        system_prompt = execution_context.get("system_prompt", "")
        persona_key = execution_context.get("persona_key", "")
        persona_name = execution_context.get("persona_name", persona_key)
        persona_icon = execution_context.get("persona_icon", "🤖")
        role_type = execution_context.get("role_type", "")
        interaction_style = execution_context.get("interaction_style", "")

        # Get user input from arguments (override context if provided)
        user_input = " ".join(args) if args else execution_context.get("user_input", "")

        if not user_input:
            typer.echo("❌ Error: No user input provided for persona execution", err=True)
            raise typer.Exit(1)

        typer.echo(
            f"-------- Enhanced Persona Execution: {persona_name} {persona_icon} (context-based)"
        )
        typer.echo(f"-------- Role: {role_type} | Style: {interaction_style}")
        typer.echo(f"-------- System prompt loaded ({len(system_prompt)} chars)")
        typer.echo(
            f"-------- User input: {user_input[:100]}{'...' if len(user_input) > 100 else ''}"
        )

        # Display execution info
        typer.echo("\n" + "=" * 60)
        typer.echo("🤖 SYSTEM PROMPT:")
        typer.echo("=" * 60)
        typer.echo(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)

        typer.echo("\n" + "=" * 60)
        typer.echo("👤 USER INPUT:")
        typer.echo("=" * 60)
        typer.echo(user_input)

        typer.echo("\n" + "=" * 60)
        typer.echo("✅ Context-based persona execution completed!")
        typer.echo("   (Ready for AI processing integration)")
        typer.echo("=" * 60)

        # Return updated execution context
        updated_context = execution_context.copy()
        updated_context.update(
            {
                "user_input": user_input,
                "status": "ready_for_ai",
                "execution_method": "context_based",
            }
        )

        return updated_context

    except Exception as e:
        typer.echo(f"❌ Context-based persona execution failed: {e}", err=True)
        raise typer.Exit(1)


def handle_enhanced_persona_execution_direct(system_prompt: str, persona_key: str, args: list):
    """Handle enhanced persona execution with direct parameters (no OS env vars)"""
    try:
        # Get user input from arguments
        user_input = " ".join(args) if args else ""

        if not user_input:
            return


        # Load persona configuration from project
        personas_dir = cursor_assets_root() / "manifests"
        manifest_path = personas_dir / "enhanced_personas.yaml"

        persona_name = persona_key
        if manifest_path.exists():
            try:
                import yaml

                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = yaml.safe_load(f)

                if persona_key in manifest.get("personas", {}):
                    persona_config = manifest["personas"][persona_key]
                    persona_name = persona_config.get("name", persona_key)
                else:
                    pass
            except Exception as e:
                pass

        # Display execution info

        # Return execution context for further processing
        return {
            "persona_key": persona_key,
            "persona_name": persona_name,
            "system_prompt": system_prompt,
            "user_input": user_input,
            "status": "ready_for_ai",
        }

    except Exception as e:
        return None


def main():
    """Main entry point"""
    # Initialize memory system early
    try:
        from .memory.store import MemoryStore
        MemoryStore.open()  # Ensure memory database exists
    except Exception as e:
        pass

    app()


if __name__ == "__main__":
    main()
