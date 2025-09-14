"""
Cursor IDE Adapter - Generate Cursor-specific integrations
"""

from pathlib import Path
from typing import Dict, Any, List
import os
import json
import yaml


class CursorAdapter:
    """Adapter for Cursor IDE integration"""

    def __init__(self):
        # Fix: Go up 4 levels from this file to get to package root
        self.project_root = Path(__file__).parent.parent.parent.parent.parent
        self.assets_root = self.project_root / "packages" / "cursor-assets"

    def log(self, message: str) -> None:
        """Uniform adapter log output with required prefix."""
        try:
            print(f"-------- {message}")
        except Exception:
            # Best-effort logging; never break flow due to logging
            pass

    def load_personas_manifest(self, project_root: Optional[Path] = None) -> Dict[str, Any]:
        """Load personas from manifest with project-local override if present"""
        # Prefer project-local override
        if project_root:
            local_manifest = Path(project_root) / "personas" / "manifest.yaml"
            if local_manifest.exists():
                with open(local_manifest, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)

        # Fallback to packaged canonical manifest
        manifest_path = self.assets_root / "manifests" / "personas.yaml"
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {"personas": {}}

    def generate_commands(self, project_root: Path) -> None:
        """Generate Cursor slash commands from manifests and copy existing templates"""
        debug = __import__("os").environ.get("SUPER_PROMPT_DEBUG") == "1"
        def d(msg: str) -> None:
            if debug:
                print(msg)

        d(f"🔍 DEBUG: CursorAdapter called with project_root={project_root}")
        commands_dir = project_root / ".cursor" / "commands" / "super-prompt"
        commands_dir.mkdir(parents=True, exist_ok=True)

        # First, copy all existing .md command files from templates
        templates_dir = self.assets_root / "templates"

        if templates_dir.exists():
            import shutil
            # Copy all .md files from templates
            for md_file in templates_dir.glob("*.md"):
                shutil.copy2(md_file, commands_dir / md_file.name)

            # Copy other template files
            for template_file in templates_dir.glob("*"):
                if template_file.name.endswith(('.json', '.txt', '.md')) and not template_file.name.endswith('.sh'):
                    shutil.copy2(template_file, commands_dir / template_file.name)

            # Also copy the tag-executor.sh script from templates (advanced version)
            tag_executor = self.assets_root / "templates" / "tag-executor.sh"
            if tag_executor.exists():
                shutil.copy2(tag_executor, commands_dir / "tag-executor.sh")
                # Make it executable
                import os
                os.chmod(commands_dir / "tag-executor.sh", 0o755)

        # Note: We no longer auto-generate commands from arbitrary processors.
        # Personas and commands are pre-defined via manifest/templates only.

        # Load personas from manifest
        manifest = self.load_personas_manifest(project_root)
        personas = manifest.get("personas", {})

        # Generate command files for each persona in manifest (if not already exists)
        for persona_key, persona_config in personas.items():
            if not (commands_dir / f"{persona_key}.md").exists():
                self._generate_persona_command(commands_dir, persona_key, persona_config)

        # Generate SDD commands
        self._generate_sdd_commands(commands_dir)

    def _generate_persona_command(self, commands_dir: Path, persona: str, persona_config: Dict[str, Any]) -> None:
        """Generate a persona command file from manifest data or template"""
        command_file = commands_dir / f"{persona}.md"

        # Try to use template from packages/cursor-assets/templates first
        template_file = self.assets_root / "templates" / f"{persona}.md"
        if template_file.exists():
            import shutil
            shutil.copy2(str(template_file), str(command_file))
            return

        # Fallback: Generate from manifest data
        name = persona_config.get("name", persona.title())
        icon = persona_config.get("icon", "🤖")
        description = persona_config.get("description", f"{name} persona")

        content = f'''---
description: {persona} command
run: "./.cursor/commands/super-prompt/tag-executor.sh"
args: ["${{input}} /{persona}"]
---

{icon} {name}\\n{description}.'''

        command_file.write_text(content)

    def _generate_processor_command(self, commands_dir: Path, processor_name: str) -> None:
        """Generate a .md command file for a processor using template if available"""
        command_file = commands_dir / f"{processor_name}.md"

        # Try to use template from packages/cursor-assets/templates first
        template_file = self.assets_root / "templates" / f"{processor_name}.md"
        if template_file.exists():
            import shutil
            shutil.copy2(str(template_file), str(command_file))
            return

        # Fallback: Create human-readable name from processor name
        display_name = processor_name.replace("-", " ").replace("_", " ").title()
        icon = self._get_processor_icon(processor_name)

        content = f'''---
description: {processor_name} command
run: "./.cursor/commands/super-prompt/tag-executor.sh"
args: ["${{input}} /{processor_name}"]
---

{icon} {display_name}\\nSpecialized processor for {processor_name.replace("-", " ").replace("_", " ")} operations.'''

        command_file.write_text(content)

    def _get_processor_icon(self, processor_name: str) -> str:
        """Get appropriate icon for processor"""
        icon_map = {
            "analyzer": "🔍",
            "architect": "🏗️",
            "backend": "⚙️",
            "frontend": "🎨",
            "frontend-ultra": "🎨✨",
            "security": "🛡️",
            "performance": "⚡",
            "qa": "✅",
            "devops": "🚀",
            "mentor": "👨‍🏫",
            "debate": "💬",
            "review": "📋",
            "scribe": "✍️",
            "refactorer": "🔧",
            "tr": "🌐",
            "ultracompressed": "📦",
            "wave": "🌊",
            "implement": "🔨",
            "optimize": "🎯",
            "docs-refector": "📚",
            "doc-master": "📖",
            "auto-setup": "⚙️",
            "emergency-recovery": "🚨",
            "enhanced-auto-setup": "⚙️✨",
            "enhanced-persona-processor": "🤖✨",
            "health-check": "🏥",
            "db-expert-tools": "🗄️",
            "simple-persona-generator": "🤖",
            "tag-executor": "🏃‍♂️",
            "high": "🔥",
            "seq": "🔢",
            "seq-ultra": "🔢✨",
            "dev": "💻",
            "grok": "🧠"
        }
        return icon_map.get(processor_name, "🤖")

    def _generate_sdd_commands(self, commands_dir: Path) -> None:
        """Generate SDD workflow commands using templates if available"""
        sdd_commands = {
            "specify": "Create Feature Specification",
            "plan": "Create Implementation Plan",
            "tasks": "Create Task Breakdown",
            "implement": "Execute Implementation"
        }

        for cmd_name, description in sdd_commands.items():
            command_file = commands_dir / f"{cmd_name}.md"

            # Try to use template first
            template_file = self.assets_root / "templates" / f"{cmd_name}.md"
            if template_file.exists():
                import shutil
                shutil.copy2(str(template_file), str(command_file))
                continue

            # Fallback: Generate basic content
            content = f'''---
description: {cmd_name} command
run: "./.cursor/commands/super-prompt/tag-executor.sh"
args: ["${{input}} /{cmd_name}"]
---

📋 {cmd_name.title()}\\n{description}.'''

            command_file.write_text(content)

    def generate_rules(self, project_root: Path) -> None:
        """Generate Cursor rules files from templates"""
        rules_dir = project_root / ".cursor" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        # Copy rules from templates instead of generating
        templates_dir = self.assets_root / "templates"

        if templates_dir.exists():
            import shutil
            # Copy all .mdc files from templates to rules directory
            for mdc_file in templates_dir.glob("*.mdc"):
                shutil.copy2(mdc_file, rules_dir / mdc_file.name)
                self.log(f"Copied rule file: {mdc_file.name}")
        else:
            # Fallback to generating if templates don't exist
            self._generate_sdd_rules(rules_dir)
            self._generate_ssot_rules(rules_dir)
            self._generate_amr_rules(rules_dir)
            self._generate_persona_rules(rules_dir)

    def _generate_sdd_rules(self, rules_dir: Path) -> None:
        """Generate SDD-related rules"""
        sdd_rule = rules_dir / "10-sdd-core.mdc"

        content = '''---
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
'''

        sdd_rule.write_text(content)

    def _generate_persona_rules(self, rules_dir: Path) -> None:
        """Generate persona-related rules"""
        persona_rule = rules_dir / "15-personas.mdc"

        content = '''---
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
'''

        persona_rule.write_text(content)

    def _generate_ssot_rules(self, rules_dir: Path) -> None:
        """Generate SSOT-first common guidance that applies to everything"""
        ssot_rule = rules_dir / "11-ssot.mdc"

        content = '''---
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
'''

        ssot_rule.write_text(content)

    def _generate_amr_rules(self, rules_dir: Path) -> None:
        """Generate AMR rules that apply to all LLMs and all commands"""
        amr_rule = rules_dir / "12-amr.mdc"

        content = '''---
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
'''

        amr_rule.write_text(content)
