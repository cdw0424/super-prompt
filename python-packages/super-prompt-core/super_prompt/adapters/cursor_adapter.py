"""
Cursor IDE Adapter - Generate Cursor-specific integrations

CRITICAL PROTECTION: This adapter is authorized to modify .cursor/ directory ONLY during official
installation processes. All persona commands and user operations MUST NEVER modify .cursor/,
.super-prompt/, or .codex/ directories. This protection is absolute.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import os
import sys
import yaml
from ..paths import cursor_assets_root
from ..mcp_app import _normalize_query


class CursorAdapter:
    """Adapter for Cursor IDE integration"""

    def __init__(self):
        self.assets_root = cursor_assets_root()
        self.tool_overrides = {
            "gpt-mode-on": "gpt_mode_on",
            "gpt-mode-off": "gpt_mode_off",
            "grok-mode-on": "grok_mode_on",
            "grok-mode-off": "grok_mode_off",
            "translate": "tr",
            "wave": "service-planner",
        }
        self.no_query_personas = {
            "gpt-mode-on",
            "gpt-mode-off",
            "grok-mode-on",
            "grok-mode-off",
            "confession-high",  # Requires multiple parameters
        }

    def _resolve_tool_name(self, persona_key: str) -> str:
        """Map persona key to the actual MCP tool identifier."""
        slug = self.tool_overrides.get(persona_key, persona_key)
        return f"sp.{slug}"

    def log(self, message: str) -> None:
        """Uniform adapter log output with required prefix."""
        try:
            # Logging disabled - no print statements allowed
            pass
        except Exception:
            # Best-effort logging; never break flow due to logging
            pass

    def load_personas_manifest(self, project_root: Optional[Path] = None) -> Dict[str, Any]:
        """Load personas from manifest with project-local override if present"""
        # Prefer project-local override
        if project_root:
            local_manifest = Path(project_root) / "personas" / "manifest.yaml"
            if local_manifest.exists():
                try:
                    with open(local_manifest, "r", encoding="utf-8") as f:
                        manifest = yaml.safe_load(f)
                        if manifest is None:
                            manifest = {"personas": {}, "agents": {}}
                        return manifest
                except Exception as e:
                    print(
                        f"🔍 DEBUG: Error loading local manifest {local_manifest}: {e}",
                        file=sys.stderr,
                    )
                    pass

        # Fallback to packaged canonical manifest
        manifest_path = self.assets_root / "manifests" / "personas.yaml"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = yaml.safe_load(f)
                    if manifest is None:
                        manifest = {"personas": {}, "agents": {}}
                    return manifest
            except Exception as e:
                print(
                    f"🔍 DEBUG: Error loading packaged manifest {manifest_path}: {e}",
                    file=sys.stderr,
                )
                pass

        print(f"🔍 DEBUG: No manifest found, returning empty dict", file=sys.stderr)
        return {"personas": {}, "agents": {}}

    def generate_commands(self, project_root: Path) -> None:
        """Generate Cursor slash commands from manifests and copy existing templates"""
        debug = os.environ.get("SUPER_PROMPT_DEBUG") == "1"

        def d(msg: str) -> None:
            if debug:
                print(f"🔍 DEBUG: {msg}", file=sys.stderr)

        print(
            f"🔍 DEBUG: generate_commands called with project_root={project_root}", file=sys.stderr
        )
        print(
            f"🔍 DEBUG: project_root type: {type(project_root)}, value: {project_root}",
            file=sys.stderr,
        )

        # Check if we have a valid project root
        if not project_root or not project_root.exists():
            print(f"🔍 DEBUG: Invalid project_root: {project_root}", file=sys.stderr)
            return

        print(f"🔍 DEBUG: Starting generate_commands execution", file=sys.stderr)

        try:
            d(f"🔍 DEBUG: CursorAdapter called with project_root={project_root}")
        except Exception as e:
            print(f"🔍 DEBUG: Error in debug function: {e}", file=sys.stderr)

        try:
            commands_dir = project_root / ".cursor" / "commands" / "super-prompt"
            print(f"🔍 DEBUG: commands_dir created: {commands_dir}", file=sys.stderr)
            commands_dir.mkdir(parents=True, exist_ok=True)
            print(f"🔍 DEBUG: commands_dir.mkdir completed", file=sys.stderr)
        except Exception as e:
            print(f"🔍 DEBUG: Error creating commands_dir: {e}", file=sys.stderr)
            raise

        print(f"🔍 DEBUG: Starting to search for commands_src_dir", file=sys.stderr)

        # Define known personas at function level for consistent access
        known_personas = [
            "analyzer",
            "architect",
            "backend",
            "db-expert",
            "debate",
            "dev",
            "devops",
            "doc-master",
            "docs-refector",
            "frontend",
            "gpt-mode-off",
            "gpt-mode-on",
            "grok-mode-off",
            "grok-mode-on",
            "grok",
            "high",
            "implement",
            "mentor",
            "optimize",
            "performance",
            "plan",
            "qa",
            "refactorer",
            "review",
            "scribe",
            "security",
            "seq-ultra",
            "seq",
            "service-planner",
            "specify",
            "tasks",
            "tr",
            "translate",
            "ultracompressed",
            "wave",
        ]

        # First, copy all existing .md command files from commands directory
        # Try multiple possible paths for commands (development vs published package)
        commands_src_dir = None
        possible_command_paths = [
            # Development path
            self.assets_root / "commands" / "super-prompt",
            # Project-relative path from package root
            Path(__file__).parent.parent.parent.parent.parent / "packages" / "cursor-assets" / "commands" / "super-prompt",
            # Published package path (nested in core-py)
            self.assets_root.parent
            / "core-py"
            / "packages"
            / "cursor-assets"
            / "commands"
            / "super-prompt",
            # Alternative paths
            Path(__file__).parent.parent.parent
            / "packages"
            / "cursor-assets"
            / "commands"
            / "super-prompt",
            Path(__file__).parent.parent.parent
            / "packages"
            / "core-py"
            / "packages"
            / "cursor-assets"
            / "commands"
            / "super-prompt",
        ]

        for test_path in possible_command_paths:
            if test_path.exists():
                commands_src_dir = test_path
                break

        if commands_src_dir and commands_src_dir.exists():
            import shutil

            print(f"🔍 DEBUG: Found commands source directory: {commands_src_dir}", file=sys.stderr)
            # Copy all .md files from commands source directory
            copied_count = 0
            force_mode = '--force' in sys.argv
            for md_file in commands_src_dir.glob("*.md"):
                dst_file = commands_dir / md_file.name
                # With --force, always overwrite; otherwise only copy if missing
                if force_mode or not dst_file.exists():
                    shutil.copy2(md_file, dst_file)
                    copied_count += 1
                    mode_str = " (forced)" if force_mode and dst_file.exists() else ""
                    print(f"🔍 DEBUG: Copied {md_file.name}{mode_str}", file=sys.stderr)
            print(f"🔍 DEBUG: Copied {copied_count} command files", file=sys.stderr)
        else:
            # If commands source directory not found, DO NOT generate minimal fallback commands
            print(
                f"❌ ERROR: Commands source directory not found. Command files will NOT be generated.",
                file=sys.stderr,
            )
            print(
                f"❌ Please ensure Super Prompt is properly installed with all template files.",
                file=sys.stderr,
            )
            return  # Exit early - do not generate any fallback commands

        # Note: We no longer auto-generate commands from arbitrary processors.
        # Personas and commands are pre-defined via manifest/templates only.

        # Load personas from manifest
        manifest = self.load_personas_manifest(project_root)
        personas = (manifest.get("personas", {}) if manifest else {}) or {}

        print(
            f"🔍 DEBUG: Loaded personas manifest: {bool(manifest)}, personas count: {len(personas) if personas else 0}",
            file=sys.stderr,
        )
        if personas:
            print(f"🔍 DEBUG: Personas found: {list(personas.keys())}", file=sys.stderr)
        else:
            print(
                f"⚠️  Personas manifest not found or empty, generating from known personas",
                file=sys.stderr,
            )

        # NEVER generate command files programmatically - only copy from templates
        # This prevents the creation of minimal/broken command files
        if personas and isinstance(personas, dict):
            print(
                f"📋 Manifest found with {len(personas)} personas, but commands must come from templates only",
                file=sys.stderr,
            )
        else:
            print(
                f"📋 No manifest found. Commands must be copied from template files only.",
                file=sys.stderr,
            )

        # Generate SDD commands
        print(f"🔍 DEBUG: Calling _generate_sdd_commands", file=sys.stderr)
        self._generate_sdd_commands(commands_dir)
        print(f"🔍 DEBUG: _generate_sdd_commands completed", file=sys.stderr)

        # Ensure MCP commands bind explicitly to the Super Prompt server
        for md_file in commands_dir.glob("*.md"):
            self._ensure_super_prompt_server_binding(md_file)

    def _generate_persona_command(
        self, commands_dir: Path, persona: str, persona_config: Dict[str, Any]
    ) -> None:
        """DEPRECATED: This method should never be called. Only copy templates, never generate."""
        # This method is kept for compatibility but should never actually generate files
        print(
            f"⛔ BLOCKED: Attempted to generate minimal command for '{persona}'. This is not allowed.",
            file=sys.stderr,
        )
        print(
            f"⛔ Commands must only be copied from template files in packages/cursor-assets/commands/super-prompt/",
            file=sys.stderr,
        )
        return  # Do nothing - never generate minimal commands

    def _ensure_super_prompt_server_binding(self, command_file: Path) -> None:
        """Ensure command front matter binds MCP execution to Super Prompt server."""
        try:
            content = command_file.read_text(encoding="utf-8")
        except Exception:
            return

        if not content.startswith("---"):
            return

        parts = self._split_front_matter(content)
        if not parts:
            return

        front_matter, body = parts
        front_lines = front_matter.strip("\n").splitlines()
        if not front_lines:
            return

        run_idx: Optional[int] = None
        for idx, line in enumerate(front_lines):
            stripped = line.strip()
            if not stripped.startswith("run:"):
                continue
            _, _, value = stripped.partition(":")
            if value.strip() == "mcp":
                run_idx = idx
            break

        if run_idx is None:
            return

        changed = False
        server_idx: Optional[int] = None
        for idx, line in enumerate(front_lines):
            stripped = line.strip()
            if not stripped.startswith("server:"):
                continue
            server_idx = idx
            indent = line[: len(line) - len(line.lstrip())]
            desired = f"{indent}server: super-prompt"
            if line != desired:
                front_lines[idx] = desired
                changed = True
            break

        if server_idx is None:
            indent = front_lines[run_idx][
                : len(front_lines[run_idx]) - len(front_lines[run_idx].lstrip())
            ]
            insert_at = run_idx + 1
            front_lines.insert(insert_at, f"{indent}server: super-prompt")
            changed = True

        if not changed:
            return

        new_front = "\n".join(front_lines)
        updated = f"---\n{new_front}\n---{body}"
        command_file.write_text(updated, encoding="utf-8")

    @staticmethod
    def _split_front_matter(content: str) -> Optional[Tuple[str, str]]:
        """Split Markdown file into front matter and remaining body."""
        if not content.startswith("---"):
            return None

        remainder = content[3:]
        end_marker = remainder.find("\n---")
        if end_marker == -1:
            return None

        front = remainder[:end_marker]
        body = remainder[end_marker + 4 :]
        return front, body

    def _generate_sdd_commands(self, commands_dir: Path) -> None:
        """Generate SDD workflow commands using templates if available"""
        sdd_commands = {
            "specify": "Create Feature Specification",
            "plan": "Create Implementation Plan",
            "tasks": "Create Task Breakdown",
            "implement": "Execute Implementation",
        }

        for cmd_name, description in sdd_commands.items():
            command_file = commands_dir / f"{cmd_name}.md"

            # Try to use template first
            template_file = self.assets_root / "templates" / f"{cmd_name}.md"
            if template_file.exists():
                import shutil

                shutil.copy2(str(template_file), str(command_file))
                continue

            # NO FALLBACK - Never generate minimal commands
            print(
                f"⛔ BLOCKED: Template not found for SDD command '{cmd_name}'. Skipping.",
                file=sys.stderr,
            )
            print(
                f"⛔ Commands must only be created from template files.",
                file=sys.stderr,
            )
            continue  # Skip this command - do not generate

    def generate_rules(self, project_root: Path) -> None:
        """Generate Cursor rules files from templates"""
        rules_dir = project_root / ".cursor" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        # Copy rules from rules directory instead of templates
        # Try multiple possible paths for rules (development vs published package)
        rules_src_dir = None
        possible_rule_paths = [
            # Development path
            self.assets_root / "rules",
            # Published package path (nested in core-py)
            self.assets_root.parent / "core-py" / "packages" / "cursor-assets" / "rules",
            # Alternative paths
            Path(__file__).parent.parent.parent / "packages" / "cursor-assets" / "rules",
            Path(__file__).parent.parent.parent
            / "packages"
            / "core-py"
            / "packages"
            / "cursor-assets"
            / "rules",
        ]

        for test_path in possible_rule_paths:
            if test_path.exists():
                rules_src_dir = test_path
                break

        if rules_src_dir and rules_src_dir.exists():
            import shutil

            # Copy all .mdc files from rules source directory
            # Copy all .mdc files from rules source directory
            force_mode = '--force' in sys.argv
            for mdc_file in rules_src_dir.glob("*.mdc"):
                dst_file = rules_dir / mdc_file.name
                # With --force, always overwrite; otherwise only copy if missing
                if force_mode or not dst_file.exists():
                    shutil.copy2(mdc_file, rules_dir / mdc_file.name)
                    mode_str = " (forced)" if force_mode and dst_file.exists() else ""
                    print(f"📋 Copied rule: {mdc_file.name}{mode_str}", file=sys.stderr)
        else:
            # Fallback to generating if rules source doesn't exist
            self._generate_sdd_rules(rules_dir)
            self._generate_ssot_rules(rules_dir)
            self._generate_amr_rules(rules_dir)
            self._generate_persona_rules(rules_dir)

    def _generate_sdd_rules(self, rules_dir: Path) -> None:
        """Generate SDD-related rules"""
        sdd_rule = rules_dir / "10-sdd-core.mdc"

        content = """---
description: "SDD core & self-check — generated by Super Prompt v3"
globs: ["**/*"]
alwaysApply: true
---
# Spec-Driven Development (SDD)
1) No implementation before SPEC and PLAN are approved.
2) SPEC: goals/user value/success criteria/scope boundaries — avoid premature stack choices.
3) PLAN: architecture/constraints/NFR/risks/security/data design.
4) TASKS: small, testable units with tracking IDs.
5) Implementation must pass the Acceptance Self-Check before PR.

## Current SDD Status
- **SPEC Files Found**: 0 files
- **PLAN Files Found**: 0 files
- **SDD Compliance**: ❌ Missing SPEC/PLAN files

## Acceptance Self-Check (auto-draft)
- ✅ Validate success criteria from SPEC
- ✅ Verify agreed non-functional constraints (performance/security as applicable)
- ✅ Ensure safe logging (no secrets/PII) and consistent output
- ✅ Add regression tests for new functionality
- ✅ Update documentation

## Framework Context
- **Detected Frameworks**: python, javascript
- **Project Structure**: SDD-compliant organization required
"""

        sdd_rule.write_text(content)

    def _generate_persona_rules(self, rules_dir: Path) -> None:
        """Generate persona-related rules"""
        persona_rule = rules_dir / "15-personas.mdc"

        content = """---
description: "Persona behaviors and interaction patterns"
globs: ["**/*"]
alwaysApply: false
---
# Persona System
- **Architect**: System design, scalability, architecture decisions
- **Frontend**: UI/UX, accessibility, modern web development
- **Backend**: APIs, databases, server-side reliability
- **Security**: Threat modeling, security hardening, compliance
- **Performance**: Optimization, bottleneck analysis, monitoring
- **Analyzer**: Root cause analysis, systematic debugging

## Interaction Guidelines
- Each persona has specialized expertise and communication style
- Auto-activation based on query patterns and context
- Quality gates ensure appropriate persona selection
- Cross-persona collaboration for complex problems
"""

        persona_rule.write_text(content)

    def _generate_ssot_rules(self, rules_dir: Path) -> None:
        """Generate SSOT-first common guidance that applies to everything"""
        ssot_rule = rules_dir / "11-ssot.mdc"

        content = """---
description: "SSOT First Principle — Single Source of Truth"
globs: ["**/*"]
alwaysApply: true
---
# SSOT (Single Source of Truth)
- Treat the following as the canonical sources in this order:
  1) personas manifest (packages/cursor-assets/manifests/personas.yaml or project personas/manifest.yaml)
  2) .cursor/rules/*.mdc (materialized guidance, modes, overrides)
  3) AGENTS.md / project docs specifying behavior
- Avoid duplicating config; prefer referencing the SSOT to prevent drift.
- When conflicts arise, defer to the SSOT order above.
- Log decisions referencing the SSOT version/path where applicable.
- Mode toggles materialize model-specific overrides; never inline divergent copies.
"""

        ssot_rule.write_text(content)

    def _generate_amr_rules(self, rules_dir: Path) -> None:
        """Generate AMR rules that apply to all LLMs and all commands"""
        amr_rule = rules_dir / "12-amr.mdc"

        content = """---
description: "Auto Model Router (AMR) — global guidance"
globs: ["**/*"]
alwaysApply: true
---
# Auto Model Router (AMR)
- Scope: Applies to all LLM interactions and all commands.
- Language: English. Logs must start with `--------`.

## Reasoning Levels
- Default: medium. Prefer fast, concise execution.
- Escalate to gpt-5 high ONLY when heavy reasoning is required (architecture, deep root-cause, complex planning, cross-module refactor).
- After high PLAN/REVIEW or high EXECUTION, return to medium and continue.

## State Machine (per turn)
- INTENT → TASK_CLASSIFY → PLAN → EXECUTE → VERIFY → REPORT
- Classify task: L0/L1/H. If H → switch to high.
- For execution: if task requires heavy reasoning, execute at gpt-5 high; otherwise execute at medium.

## Commands for Switching
- To high: first line `/model gpt-5 high` then `--------router: switch to high (reason=deep_planning)`
- Back to medium: `/model gpt-5 medium` then `--------router: back to medium (reason=execution)`

## Handoff Brief (small→large)
- Before high reasoning, compile a concise handoff brief:
  - repo languages/frameworks, important files, tests/stubs
  - exact task and constraints, risks, acceptance checks
  - smallest viable context; avoid over-collection
"""

        amr_rule.write_text(content)
