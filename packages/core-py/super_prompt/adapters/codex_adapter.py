"""
Codex CLI Adapter - Generate Codex-specific integrations
"""

from pathlib import Path
from typing import Dict, Any
import yaml


class CodexAdapter:
    """Adapter for Codex CLI integration"""

    def __init__(self):
        # Resolve project root robustly whether running from repo packages/core-py
        # or bundled under .super-prompt/packages/core-py
        here = Path(__file__).resolve()
        self.project_root = here
        # Search upwards for a directory that contains packages/codex-assets/manifests/agents.yaml
        marker_rel = Path("packages") / "codex-assets" / "manifests" / "agents.yaml"
        for p in [here.parent, *here.parents]:
            candidate = p
            if (candidate / marker_rel).exists():
                self.project_root = candidate
                break
        else:
            # Fallback to historical 4-level assumption
            self.project_root = Path(__file__).parent.parent.parent.parent

        self.assets_root = self.project_root / "packages" / "codex-assets"

    def load_agents_manifest(self) -> Dict[str, Any]:
        """Load agents configuration from manifest"""
        manifest_path = self.assets_root / "manifests" / "agents.yaml"
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {"agents": {}, "workflows": {}}

    def generate_assets(self, project_root: Path) -> None:
        """Generate Codex integration assets from manifests"""
        codex_dir = project_root / ".codex"
        codex_dir.mkdir(parents=True, exist_ok=True)

        # Load manifest
        manifest = self.load_agents_manifest()

        # Generate agents.md from manifest
        self._generate_agents_md(codex_dir, manifest)

        # Generate bootstrap prompt from template
        self._generate_bootstrap_prompt(codex_dir)

        # Generate router check script
        self._generate_router_check(codex_dir)

    def _generate_agents_md(self, codex_dir: Path, manifest: Dict[str, Any]) -> None:
        """Generate Codex agents documentation from manifest"""
        agents_file = codex_dir / "agents.md"

        agents = manifest.get("agents", {})
        workflows = manifest.get("workflows", {})

        content = f'''# Codex Agent — Super Prompt Integration

Use flag-based personas (no slash commands in Codex). Each persona supports a long flag and an `--sp-` alias.

## Available Personas
'''

        # Group personas by category if available
        for category, category_agents in agents.items():
            content += f'''
### {category.replace('_', ' ').title()}
'''
            for agent_key, agent_config in category_agents.items():
                name = agent_config.get("name", agent_key)
                description = agent_config.get("description", "")
                flags = agent_config.get("flags", [])
                content += f'''- `{agent_key}` - {description}
'''

        content += '''
## Usage Examples

```bash
# Architecture planning
super-prompt --architect "Propose modular structure for feature X"
super-prompt --sp-architect "Propose modular structure for feature X"

# Root cause analysis
super-prompt --analyzer "Audit error handling and logging"
super-prompt --sp-analyzer --out .codex/reports/analysis.md "Audit error handling and logging"
```

## SDD Workflow (flag-based)
'''

        # Add workflow examples from manifest
        sdd_workflows = workflows.get("sdd", {})
        for workflow_key, workflow_config in sdd_workflows.items():
            example = workflow_config.get("example", "")
            if example:
                content += f'''
{example}'''

        content += '''
## Tips
- Logs MUST start with `--------`
- Keep all content in English
- Auto Model Router switches between medium/high reasoning based on complexity

## MCP Integration (Context7)
- Auto-detects Context7 MCP (env `CONTEXT7_MCP=1`)
- Planning personas include MCP usage block for real-source grounding
'''

        agents_file.write_text(content)

    def _generate_bootstrap_prompt(self, codex_dir: Path) -> None:
        """Generate bootstrap prompt for AMR initialization"""
        bootstrap_file = codex_dir / "bootstrap_prompt_en.txt"

        content = '''# Super Prompt AMR Bootstrap

## System Context
You are an advanced AI coding assistant integrated with Super Prompt's Auto Model Router (AMR) system. This system automatically routes tasks between different reasoning levels (light/moderate/heavy) based on complexity analysis.

## AMR Decision Framework
- **Light (L0)**: Simple, straightforward tasks
- **Moderate (L1)**: Standard development tasks with some complexity
- **Heavy (H)**: Complex reasoning, architecture, multi-step analysis

## Routing Triggers
Switch to HIGH reasoning for:
- System architecture decisions
- Security analysis and threat modeling
- Performance optimization planning
- Complex refactoring or migration
- Multi-stakeholder coordination
- Root cause analysis of systemic issues

## State Machine Execution
Follow the fixed workflow: INTENT → TASK_CLASSIFY → PLAN → EXECUTE → VERIFY → REPORT

## Quality Standards
- Maintain English-only communication
- Use `--------` prefix for all debug logs
- Ensure SDD compliance when applicable
- Provide actionable, specific recommendations
'''

        bootstrap_file.write_text(content)

    def _generate_router_check(self, codex_dir: Path) -> None:
        """Generate router check script"""
        router_check_file = codex_dir / "router-check.sh"

        content = '''#!/usr/bin/env zsh
set -euo pipefail

# Super Prompt Router Check
# Validates AMR integration and SDD compliance

root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
AGENTS_PATH=""
for p in "$root/.codex/agents.md" "$root/.codex/AGENTS.md" "$root/AGENTS.md"; do
  if [ -f "$p" ]; then AGENTS_PATH="$p"; break; fi
done

if [ -z "$AGENTS_PATH" ]; then
  echo "--------router-check: FAIL (no agents/AGENTS.md found)"
  exit 1
fi

missing=0
grep -q "Auto Model Router" "$AGENTS_PATH" || { echo "AGENTS.md missing AMR marker"; missing=1; }
grep -q "medium ↔ high" "$AGENTS_PATH" || { echo "AGENTS.md missing medium↔high"; missing=1; }
grep -q "SDD" "$AGENTS_PATH" || { echo "AGENTS.md missing SDD reference"; missing=1; }

if [ "$missing" -ne 0 ]; then
  echo "--------router-check: FAIL"
  exit 1
fi

echo "--------router-check: OK"
'''

        router_check_file.write_text(content)
        router_check_file.chmod(0o755)
