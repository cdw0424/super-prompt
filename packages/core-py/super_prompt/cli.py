"""
Super Prompt Core CLI (Typer) — Python package entrypoint

This CLI is for the Python package (super-prompt-core). The NPM distribution
uses .super-prompt/cli.py as its entrypoint. Keep both CLIs; they serve
different packaging targets.
"""

import typer
from typing import Optional
import os
import sys
import subprocess
import json
from pathlib import Path

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


def get_current_version() -> str:
    """Get current version from package.json"""
    try:
        # Try to find package.json in parent directories (for development)
        current_dir = Path(__file__).resolve()
        print(f"----- DEBUG: Starting version detection from {current_dir}")
        for i in range(5):  # Check up to 5 levels up
            package_json = current_dir / "package.json"
            print(f"----- DEBUG: Checking {package_json}")
            if package_json.exists():
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    version = data.get('version', '3.1.56')
                    print(f"----- DEBUG: Found version {version} in {package_json}")
                    return version
            current_dir = current_dir.parent
            print(f"----- DEBUG: Moving up to {current_dir}")

        # Fallback: try to read from environment or use default
        env_version = os.environ.get('SUPER_PROMPT_VERSION', '3.1.56')
        print(f"----- DEBUG: Using environment/default version {env_version}")
        return env_version
    except Exception as e:
        print(f"----- DEBUG: Exception in version detection: {e}")
        return '3.1.56'


app = typer.Typer(
    name="super-prompt-core",
    help="Super Prompt v3 - Modular prompt engineering toolkit",
    add_completion=False,
)

sdd_spec_query: Optional[str] = typer.Option(None, "--sp-sdd-spec", help="Create an SDD specification for a feature.")
sdd_plan_query: Optional[str] = typer.Option(None, "--sp-sdd-plan", help="Create an SDD plan for a feature.")
sdd_tasks_query: Optional[str] = typer.Option(None, "--sp-sdd-tasks", help="Create SDD tasks for a feature.")
sdd_implement_query: Optional[str] = typer.Option(None, "--sp-sdd-implement", help="Implement a feature based on SDD artifacts.")
high_query: Optional[str] = typer.Option(None, "--sp-high", help="Execute with GPT-5 high reasoning model.")


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    sp_sdd_spec: Optional[str] = typer.Option(None, "--sp-sdd-spec", help="Create an SDD specification for a feature."),
    sp_sdd_plan: Optional[str] = typer.Option(None, "--sp-sdd-plan", help="Create an SDD plan for a feature."),
    sp_sdd_tasks: Optional[str] = typer.Option(None, "--sp-sdd-tasks", help="Create SDD tasks for a feature."),
    sp_sdd_implement: Optional[str] = typer.Option(None, "--sp-sdd-implement", help="Implement a feature based on SDD artifacts."),
    sp_high: Optional[str] = typer.Option(None, "--sp-high", help="Execute with GPT-5 high reasoning model."),
):
    """Super Prompt Core CLI"""
    # Check for execution context file FIRST (before checking subcommands)
    context_file = os.environ.get("SUPER_PROMPT_CONTEXT_FILE")
    execution_context = None

    if context_file and Path(context_file).exists():
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
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

    # Handle high reasoning option
    if sp_high is not None:
        if active_sdd_action is not None:
            typer.echo("❌ Error: Cannot combine --sp-high with SDD actions.", err=True)
            raise typer.Exit(1)
        print("🚀 Executing with GPT-5 High Reasoning Model...")
        print(f"📝 Query: {sp_high}")
        # For now, just print the high reasoning message
        # In future, this should integrate with actual GPT-5 high model
        print("🔬 High reasoning analysis would be performed here.")
        print("💡 This is a placeholder for GPT-5 high model integration.")
        return

    if active_sdd_action and feature_query:
        sdd_command(action=active_sdd_action, feature=feature_query, project_root=None)
    elif any(q is not None for q in sdd_options.values()):
        typer.echo("❌ Error: SDD action requires a feature description.", err=True)
        raise typer.Exit(1)
    else:
        # If no command is passed, and no SDD flags, show help.
        # This requires `invoke_without_command=True` on the callback.
        # We check if any sdd option was passed but without a value.
        if ctx.params['sp_sdd_spec'] is None and \
           ctx.params['sp_sdd_plan'] is None and \
           ctx.params['sp_sdd_tasks'] is None and \
           ctx.params['sp_sdd_implement'] is None and \
           ctx.params['sp_high'] is None and \
           not ctx.invoked_subcommand:
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
            gate_result = check_implementation_ready(feature, str(project_root) if project_root else ".")

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
                project_root=str(project_root) if project_root else "."
            )

            typer.echo(f"✅ {action.upper()} created for {feature}")

        elif action == "implement":
            # Check gates before implementation
            gate_result = check_implementation_ready(feature, str(project_root) if project_root else ".")

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
                project_root=str(project_root) if project_root else "."
            )

            typer.echo(f"✅ Implementation completed for {feature}")

        else:
            typer.echo(f"❌ Unknown SDD action: {action}", err=True)
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command("amr-rules")
def amr_rules(
    out: Path = typer.Option(Path(".cursor/rules"), "--out", help="Output directory")
):
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
    path: Path = typer.Option(Path("prompts/codex_amr_bootstrap_prompt_en.txt"), "--path", help="Prompt file path"),
):
    """Print AMR bootstrap prompt to stdout."""
    try:
        if path.exists():
            typer.echo(path.read_text())
        else:
            typer.echo("No bootstrap prompt found. Provide --path or add prompts/codex_amr_bootstrap_prompt_en.txt")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True); raise typer.Exit(1)


@app.command("amr-qa")
def amr_qa(
    file: Path = typer.Argument(..., help="Transcript/text file to check"),
):
    """Validate a transcript for AMR/state-machine conformance."""
    if not file.exists():
        typer.echo(f"❌ File not found: {file}"); raise typer.Exit(2)
    txt = file.read_text()
    ok = True
    import re
    if not re.search(r"^\[INTENT\]", txt, re.M):
        typer.echo("-------- Missing [INTENT] section"); ok = False
    if not (re.search(r"^\[PLAN\]", txt, re.M) or re.search(r"^\[EXECUTE\]", txt, re.M)):
        typer.echo("-------- Missing [PLAN] or [EXECUTE] section"); ok = False
    if re.search(r"^(router:|run:)", txt, re.M):
        typer.echo("-------- Found log lines without '--------' prefix"); ok = False
    if "/model gpt-5 high" in txt and "/model gpt-5 medium" not in txt:
        typer.echo("-------- High switch found without returning to medium"); ok = False
    typer.echo("--------qa: OK" if ok else "--------qa: FAIL")
    raise typer.Exit(0 if ok else 1)


@app.command("codex-init")
def codex_init(
    project_root: Optional[Path] = typer.Option(None, "--project-root", help="Project root directory"),
):
    """Create Codex CLI assets in .codex/"""
    try:
        root = Path(project_root or ".")
        adapter = CodexAdapter()
        adapter.generate_assets(root)
        typer.echo("--------codex:init: .codex assets created")
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True); raise typer.Exit(1)


@app.command("codex-mode-on")
def codex_mode_on(
    project_root: Optional[Path] = typer.Option(None, "--project-root", help="Project root directory"),
):
    """Enable Codex AMR mode by creating .codex/.codex-mode flag."""
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
        typer.echo("-------- Codex AMR mode: ENABLED (.codex/.codex-mode)")
    except Exception as e:
        typer.echo(f"❌ Error enabling Codex mode: {e}", err=True); raise typer.Exit(1)


@app.command("codex-mode-off")
def codex_mode_off(
    project_root: Optional[Path] = typer.Option(None, "--project-root", help="Project root directory"),
):
    """Disable Codex AMR mode by removing .codex/.codex-mode flag."""
    try:
        root = Path(project_root or ".")
        flag = root / ".cursor" / ".codex-mode"
        if flag.exists():
            flag.unlink()
            typer.echo("-------- Codex AMR mode: DISABLED")
        else:
            typer.echo("-------- Codex AMR mode: Already disabled")
    except Exception as e:
        typer.echo(f"❌ Error disabling Codex mode: {e}", err=True); raise typer.Exit(1)


@app.command("grok-mode-on")
def grok_mode_on(
    project_root: Optional[Path] = typer.Option(None, "--project-root", help="Project root directory"),
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
        typer.echo(f"❌ Error enabling Grok mode: {e}", err=True); raise typer.Exit(1)


@app.command("grok-mode-off")
def grok_mode_off(
    project_root: Optional[Path] = typer.Option(None, "--project-root", help="Project root directory"),
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
        typer.echo(f"❌ Error disabling Grok mode: {e}", err=True); raise typer.Exit(1)


@app.command("personas-init")
def personas_init(
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite if exists"),
    project_root: Optional[Path] = typer.Option(None, "--project-root", help="Project root directory"),
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
        typer.echo(f"❌ Error: {e}", err=True); raise typer.Exit(1)


@app.command("personas-build")
def personas_build(
    project_root: Optional[Path] = typer.Option(None, "--project-root", help="Project root directory"),
):
    """Build personas assets (Cursor commands + rules) in current project"""
    try:
        root = Path(project_root or ".")
        cursor = CursorAdapter()
        cursor.generate_commands(root)
        cursor.generate_rules(root)
        typer.echo("--------personas:build: .cursor commands + rules updated")
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True); raise typer.Exit(1)


@app.command("mcp-serve")
def mcp_serve():
    """Start the Super Prompt FastMCP server."""
    try:
        # We construct the path to the server script relative to this CLI script.
        # This makes the execution path independent of where the user runs the command.
        server_script_path = Path(__file__).parent / "mcp_srv" / "server.py"

        if not server_script_path.exists():
            typer.echo(f"❌ Fatal Error: MCP server script not found at {server_script_path}", err=True)
            typer.echo("   The package installation may be corrupt.", err=True)
            raise typer.Exit(1)

        typer.echo(f"🚀 Starting FastMCP server from: {server_script_path}")
        typer.echo("   Press Ctrl+C to exit.")

        # Use sys.executable to ensure we're using the python from the correct venv
        subprocess.run([sys.executable, str(server_script_path)], check=True)

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
    project_root: Optional[Path] = typer.Option(None, "--project-root", help="Project root directory"),
):
    """[DEPRECATED] SDD (Spec-Driven Development) workflow commands. Use flags like --sp-sdd-spec instead."""
    typer.echo("⚠️  Warning: The 'sdd' subcommand is deprecated and will be removed. Use flags like --sp-sdd-spec instead.", err=True)
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
    project_root: Optional[Path] = typer.Option(None, "--project-root", help="Project root directory"),
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
    project_root: Optional[Path] = typer.Option(None, "--project-root", help="Project root directory"),
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
                ("SDD gates", lambda: check_implementation_ready(target or "default", str(project_root) if project_root else ".")),
                ("Context collection", lambda: len(ContextCollector(str(project_root) if project_root else ".").collect_context("test")["files"]) > 0),
            ]

            typer.echo("Running validation checks:")
            all_passed = True

            for check_name, check_func in checks:
                try:
                    result = check_func()
                    if hasattr(result, 'ok'):
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
    project_root: Optional[Path] = typer.Option(".", "--project-root", help="Project root directory"),
    force: bool = typer.Option(False, "--force", help="Force reinitialization"),
):
    """Initialize Super Prompt for a project"""
    try:
        # Display Super Prompt ASCII Art
        logo = """
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
\033[2m                     {get_current_version()} | @cdw0424/super-prompt\033[0m
\033[2m                          Made by \033[0m\033[35mDaniel Choi from Korea\033[0m
"""
        typer.echo(logo)
        typer.echo()

        target_dir = Path(project_root)

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

        # Ensure base dirs
        dirs_to_create = [
            target_dir / ".cursor" / "commands" / "super-prompt",
            target_dir / ".cursor" / "rules",
            target_dir / "specs",
            target_dir / "memory" / "constitution",
            target_dir / "memory" / "rules",
        ]
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Generate latest Cursor integration (no legacy shell runners)
        cursor_adapter = CursorAdapter()
        cursor_adapter.generate_commands(target_dir)
        cursor_adapter.generate_rules(target_dir)

        # Example SDD scaffold (unchanged)
        sdd_dir = target_dir / "specs" / "example-feature"
        sdd_dir.mkdir(exist_ok=True)
        spec_file = sdd_dir / "spec.md"
        if not spec_file.exists() or force:
            spec_file.write_text("""# Example Feature Specification

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
""")

        typer.echo("✅ Super Prompt initialized!")
        typer.echo(f"   Project root: {target_dir.absolute()}")
        typer.echo("   Next steps:")
        typer.echo("   1. Use Cursor: /init-sp (initial index), /re-init-sp (refresh)")
        typer.echo("   2. Personas: /architect, /frontend, /doc-master, etc.")
        typer.echo("   3. SDD: /specify → /plan → /tasks")

    except Exception as e:
        typer.echo(f"❌ Initialization failed: {e}", err=True)
        raise typer.Exit(1)


# Alias: super:init → init
@app.command("super:init")
def super_init_alias(
    project_root: Optional[Path] = typer.Option(".", "--project-root", help="Project root directory"),
    force: bool = typer.Option(False, "--force", help="Force reinitialization"),
):
    """Alias for init to support `super:init`."""
    return init(project_root=project_root, force=force)


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
        typer.echo(f"-------- User input: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")

        # Load persona configuration
        personas_dir = Path(__file__).parent / "personas"
        manifest_path = personas_dir / "manifest.yaml"

        if manifest_path.exists():
            import yaml
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)

            if persona_key in manifest.get('personas', {}):
                persona_config = manifest['personas'][persona_key]
                typer.echo(f"-------- Loaded persona: {persona_config.get('name', persona_key)}")
            else:
                typer.echo(f"⚠️  Persona '{persona_key}' not found in manifest, proceeding anyway")
        else:
            typer.echo("⚠️  Persona manifest not found, proceeding with basic execution")

        # Here we would integrate with the actual AI processing
        # For now, we'll just display the system prompt and user input
        typer.echo("\n" + "="*60)
        typer.echo("🤖 SYSTEM PROMPT:")
        typer.echo("="*60)
        typer.echo(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)

        typer.echo("\n" + "="*60)
        typer.echo("👤 USER INPUT:")
        typer.echo("="*60)
        typer.echo(user_input)

        typer.echo("\n" + "="*60)
        typer.echo("✅ Enhanced persona execution framework ready!")
        typer.echo("   (Actual AI processing would happen here)")
        typer.echo("="*60)

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

        typer.echo(f"-------- Enhanced Persona Execution: {persona_name} {persona_icon} (context-based)")
        typer.echo(f"-------- Role: {role_type} | Style: {interaction_style}")
        typer.echo(f"-------- System prompt loaded ({len(system_prompt)} chars)")
        typer.echo(f"-------- User input: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")

        # Display execution info
        typer.echo("\n" + "="*60)
        typer.echo("🤖 SYSTEM PROMPT:")
        typer.echo("="*60)
        typer.echo(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)

        typer.echo("\n" + "="*60)
        typer.echo("👤 USER INPUT:")
        typer.echo("="*60)
        typer.echo(user_input)

        typer.echo("\n" + "="*60)
        typer.echo("✅ Context-based persona execution completed!")
        typer.echo("   (Ready for AI processing integration)")
        typer.echo("="*60)

        # Return updated execution context
        updated_context = execution_context.copy()
        updated_context.update({
            "user_input": user_input,
            "status": "ready_for_ai",
            "execution_method": "context_based"
        })

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
            print("❌ Error: No user input provided for persona execution")
            return

        print(f"-------- Enhanced Persona Execution: {persona_key} (direct call)")
        print(f"-------- System prompt loaded ({len(system_prompt)} chars)")
        print(f"-------- User input: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")

        # Load persona configuration from project
        personas_dir = Path(__file__).parent.parent.parent / "packages" / "cursor-assets" / "manifests"
        manifest_path = personas_dir / "enhanced_personas.yaml"

        persona_name = persona_key
        if manifest_path.exists():
            try:
                import yaml
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = yaml.safe_load(f)

                if persona_key in manifest.get('personas', {}):
                    persona_config = manifest['personas'][persona_key]
                    persona_name = persona_config.get('name', persona_key)
                    print(f"-------- Loaded persona: {persona_name}")
                else:
                    print(f"⚠️  Persona '{persona_key}' not found in manifest, proceeding anyway")
            except Exception as e:
                print(f"⚠️  Could not load persona manifest: {e}")

        # Display execution info
        print("\n" + "="*60)
        print("🤖 SYSTEM PROMPT:")
        print("="*60)
        print(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)

        print("\n" + "="*60)
        print("👤 USER INPUT:")
        print("="*60)
        print(user_input)

        print("\n" + "="*60)
        print("✅ Direct persona execution completed!")
        print("   (Ready for AI processing integration)")
        print("="*60)

        # Return execution context for further processing
        return {
            "persona_key": persona_key,
            "persona_name": persona_name,
            "system_prompt": system_prompt,
            "user_input": user_input,
            "status": "ready_for_ai"
        }

    except Exception as e:
        print(f"❌ Direct persona execution failed: {e}")
        return None


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()
