"""
Super Prompt CLI - Modern modular command-line interface
"""

import typer
from typing import Optional
from pathlib import Path

from .engine.execution_pipeline import ExecutionPipeline
from .context.collector import ContextCollector
from .sdd.gates import check_implementation_ready
from .personas.loader import PersonaLoader
from .adapters.cursor_adapter import CursorAdapter
from .adapters.codex_adapter import CodexAdapter
from .validation.todo_validator import TodoValidator

app = typer.Typer(
    name="super-prompt-core",
    help="Super Prompt v3 - Modular prompt engineering toolkit",
    add_completion=False,
)


@app.callback()
def callback():
    """Super Prompt Core CLI"""
    pass


@app.command()
def optimize(
    query: str = typer.Argument(..., help="Query or request to process"),
    persona: str = typer.Option("auto", "--persona", "-p", help="Persona to use"),
    model: str = typer.Option("medium", "--model", "-m", help="Reasoning level (light/moderate/heavy)"),
    context_tokens: int = typer.Option(16000, "--context-tokens", "-c", help="Maximum context tokens"),
    project_root: Optional[Path] = typer.Option(None, "--project-root", help="Project root directory"),
):
    """Execute prompt optimization with full context awareness"""
    try:
        # Initialize components
        pipeline = ExecutionPipeline()
        collector = ContextCollector(str(project_root) if project_root else ".")

        # Collect context
        context = collector.collect_context(query, max_tokens=context_tokens)

        # Execute pipeline
        result = pipeline.execute(query, context=context, persona=persona, model=model)

        # Display results
        typer.echo(f"✅ Completed in {result['metadata']['execution_time']:.2f}s")
        typer.echo(f"📊 Tokens used: {result['metadata'].get('context_tokens', 0)}")

        if result.get("errors"):
            typer.echo("⚠️  Warnings:")
            for error in result["errors"]:
                typer.echo(f"   - {error}")

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def sdd(
    action: str = typer.Argument(..., help="SDD action (spec/plan/tasks/implement)"),
    feature: str = typer.Argument(..., help="Feature name"),
    project_root: Optional[Path] = typer.Option(None, "--project-root", help="Project root directory"),
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
        target_dir = Path(project_root)

        # Initialize adapters
        cursor_adapter = CursorAdapter()
        codex_adapter = CodexAdapter()

        # Create necessary directories
        dirs_to_create = [
            target_dir / ".cursor" / "commands" / "super-prompt",
            target_dir / ".cursor" / "rules",
            target_dir / "specs",
            target_dir / "memory" / "constitution",
            target_dir / "memory" / "rules",
        ]

        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Generate Cursor integration
        cursor_adapter.generate_commands(target_dir)
        cursor_adapter.generate_rules(target_dir)

        # Generate initial SDD structure
        sdd_dir = target_dir / "specs" / "example-feature"
        sdd_dir.mkdir(exist_ok=True)

        # Create basic spec template
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

        # Best‑effort: install local dev dependencies for SQLite LTM helpers (pinned)
        try:
            import subprocess
            import os
            typer.echo("Installing dev dependencies for LTM helpers (SQLite/FTS)…")
            pinned = [
                "better-sqlite3@12.2.0",
                "ajv@8.17.1",
                "zod@4.1.8",
                "ioredis@5.7.0",
            ]
            override = os.environ.get("SUPER_PROMPT_LTM_PKGS")
            pkgs = override.split() if override else pinned
            subprocess.run(["npm", "install", "-D", *pkgs], cwd=str(target_dir), check=False)
        except Exception as e:
            typer.echo(f"⚠️  Skipped dev dependency install: {e}")

        # Add Cursor commands for init-sp and re-init
        try:
            commands_dir = target_dir / ".cursor" / "commands" / "super-prompt"
            commands_dir.mkdir(parents=True, exist_ok=True)

            init_sp = commands_dir / "init-sp.md"
            init_sp.write_text("""---
description: Initialize Super Prompt memory (project analysis)
run: "python3"
args: [".super-prompt/utils/init/init_sp.py", "--mode", "init"]
---

🧭 Initialize Super Prompt memory with project structure snapshot.
""")

            reinit = commands_dir / "re-init-sp.md"
            reinit.write_text("""---
description: Re-Initialize project analysis (refresh memory)
run: "python3"
args: [".super-prompt/utils/init/init_sp.py", "--mode", "reinit"]
---

🔄 Refresh project analysis and update memory.
""")
        except Exception as e:
            typer.echo(f"⚠️  Could not write Cursor commands: {e}")

        # Cleanup legacy assets (safe, idempotent)
        try:
            legacy_dir = target_dir / "legacy" / f"cleanup-{int(__import__('time').time())}"
            # 1) Move old Cursor command Python scripts out of .cursor/commands/super-prompt
            sp_cmd_dir = target_dir / ".cursor" / "commands" / "super-prompt"
            py_legacy = []
            if sp_cmd_dir.exists():
                for p in sp_cmd_dir.glob("*.py"):
                    py_legacy.append(p)
            if py_legacy:
                (legacy_dir / "cursor-commands").mkdir(parents=True, exist_ok=True)
                for p in py_legacy:
                    p.rename(legacy_dir / "cursor-commands" / p.name)
                typer.echo(f"🧹 Moved legacy Cursor command scripts → {legacy_dir / 'cursor-commands'}")

            # 2) Remove deprecated command names (re-init → re-init-sp)
            deprecated = target_dir / ".cursor" / "commands" / "super-prompt" / "re-init.md"
            if deprecated.exists():
                (legacy_dir / "deprecated").mkdir(parents=True, exist_ok=True)
                deprecated.rename(legacy_dir / "deprecated" / deprecated.name)
                typer.echo("🧹 Deprecated /re-init removed (use /re-init-sp)")
        except Exception as e:
            typer.echo(f"⚠️  Legacy cleanup skipped: {e}")

        typer.echo("✅ Super Prompt initialized!")
        typer.echo(f"   Project root: {target_dir.absolute()}")
        typer.echo("   Next steps:")
        typer.echo("   1. Use Cursor: /init-sp (initial index), /re-init-sp (refresh)")
        typer.echo("   2. Personas: /architect, /frontend, /doc-master, etc.")
        typer.echo("   3. SDD: /specify → /plan → /tasks")

    except Exception as e:
        typer.echo(f"❌ Initialization failed: {e}", err=True)
        raise typer.Exit(1)


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()
