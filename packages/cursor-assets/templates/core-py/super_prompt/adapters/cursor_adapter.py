"""
Cursor IDE Adapter - Generate Cursor-specific integrations
"""

from pathlib import Path
from typing import Dict, Any, List
import json
import yaml


class CursorAdapter:
    """Adapter for Cursor IDE integration"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.assets_root = self.project_root / "packages" / "cursor-assets"

    def load_personas_manifest(self) -> Dict[str, Any]:
        """Load personas from data-driven manifest"""
        manifest_path = self.assets_root / "manifests" / "personas.yaml"
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {"personas": {}}

    def generate_commands(self, project_root: Path) -> None:
        """Generate Cursor slash commands from manifests and copy existing templates"""
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

        # Auto-generate .md commands for ALL .py processors that don't have .md files
        processors_dir = self.project_root / ".super-prompt" / "utils" / "cursor-processors"
        if processors_dir.exists():
            for py_file in processors_dir.glob("*.py"):
                processor_name = py_file.stem
                # Only skip Python module files, generate commands for ALL processors
                if processor_name in ["__init__"]:
                    continue

                md_file = commands_dir / f"{processor_name}.md"
                if not md_file.exists():
                    self._generate_processor_command(commands_dir, processor_name)

        # Load personas from manifest
        manifest = self.load_personas_manifest()
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
