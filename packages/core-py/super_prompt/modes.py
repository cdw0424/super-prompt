"""
Mode management helpers (MCP-first)

Provides model mode toggles and guidance rule management.
Used by both MCP tools and thin CLI wrappers.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml


def _disable_all_modes(root: Path, except_mode: Optional[str] = None) -> List[str]:
    logs: List[str] = []
    cursor_dir = root / ".cursor"
    rules_dir = cursor_dir / "rules"

    known_flags = {
        "codex": [cursor_dir / ".codex-mode", root / ".codex" / ".codex-mode"],
        "grok": [cursor_dir / ".grok-mode"],
    }
    known_rules = {
        "codex": rules_dir / "20-gpt5-guidance.mdc",
        "grok": rules_dir / "20-grok-guidance.mdc",
    }

    for mode, paths in known_flags.items():
        if except_mode and mode == except_mode:
            continue
        for p in paths:
            try:
                if p.exists():
                    p.unlink()
                    logs.append(f"-------- {mode.capitalize()} mode disabled (mutual exclusivity)")
            except Exception:
                pass

    for mode, rule in known_rules.items():
        if except_mode and mode == except_mode:
            continue
        try:
            if rule.exists():
                rule.unlink()
                logs.append(f"-------- Removed {mode.capitalize()} guidance rules (mutual exclusivity)")
        except Exception:
            pass

    return logs


def enable_codex_mode(project_root: Optional[Path] = None) -> List[str]:
    """Enable GPT/Codex AMR mode and install GPT-5 guidance rules."""
    root = Path(project_root or ".")
    logs: List[str] = []
    cursor_dir = root / ".cursor"
    cursor_dir.mkdir(parents=True, exist_ok=True)

    logs.extend(_disable_all_modes(root, except_mode="codex"))

    # Enable flag
    (cursor_dir / ".codex-mode").write_text("", encoding="utf-8")

    # Install GPT-5 guidance rules
    rules_dir = cursor_dir / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    gpt5_rule = rules_dir / "20-gpt5-guidance.mdc"
    gpt5_rule.write_text(
        """---
description: "GPT-5 guidance for personas (applies in GPT mode)"
globs: ["**/*"]
alwaysApply: true
---
# GPT-5 Usage Guidelines (GPT Mode)
- Scope: Applies when GPT mode is enabled for all personas.
- Language: English only. All logs must be prefixed with `--------`.
- Safety: Never print secrets (mask like `sk-***`). Ask confirmation before destructive ops or network calls.

## 1) Be Precise; Avoid Conflicts
- Prefer unambiguous, specific instructions; avoid mixing competing goals.
- Resolve conflicts in favor of AGENTS.md and `.cursor/rules` in this repo.
- SSOT first: Follow personas manifest/.cursor/rules/AGENTS.md as single source of truth.

## 2) Use the Right Reasoning Effort
- Default to gpt-5 with reasoning=medium.
- Escalate to high only for heavy planning/review or complex root-cause work.
- After planning/review, return to medium for execution.

## 3) Use XML-like Blocks for Structure
Include and follow structured blocks when present:

```xml
<code_editing_rules>
  <guiding_principles>
    - Modular, reusable components
    - Clarity over cleverness
    - Minimal diffs; focused changes
  </guiding_principles>
  <frontend_stack_defaults>
    - Styling: TailwindCSS
  </frontend_stack_defaults>
</code_editing_rules>

<self_reflection>
  - Think in a private rubric (5–7 categories) before building
  - Iterate internally until the solution scores high across the rubric
</self_reflection>

<persistence>
  - Be decisive without asking for clarification unless blocking
  - Do not over-gather context; respect tool budgets
  - Still ASK CONFIRMATION before destructive ops or any network calls
</persistence>
```

## 4) Calibrated Tone (Avoid Overly Firm Language)
- Avoid hyperbolic mandates (e.g., "ALWAYS be THOROUGH").
- Stay concise and practical; be specific about what to do next.

## 5) Allow Planning and Self‑Reflection
- For zero‑to‑one or ambiguous tasks, add a brief internal plan before code.
- Use the AMR high reasoning phase for PLAN/REVIEW; then return to medium.

## 6) Control Eagerness of the Coding Agent
- Be explicit about tool budgets and sequencing.
- Parallelize only when it reduces latency without sacrificing safety.
- Defer to the fixed AMR state machine and repository guards.
""",
        encoding="utf-8",
    )

    # Persona overrides for GPT
    logs.extend(_install_persona_overrides(root, model="gpt"))
    # Materialize GPT prompting guide from docs
    try:
        _write_model_prompt_guide(root, model="gpt")
        logs.append("-------- Installed GPT prompting guide (.cursor/rules/22-model-guide.mdc)")
    except Exception:
        # Non-fatal if docs are missing
        pass
    logs.append("-------- Codex AMR mode: ENABLED (.cursor/.codex-mode)")
    logs.append("-------- Installed GPT-5 guidance rules (.cursor/rules/20-gpt5-guidance.mdc)")
    return logs


def disable_codex_mode(project_root: Optional[Path] = None) -> List[str]:
    root = Path(project_root or ".")
    logs: List[str] = []
    flag = root / ".cursor" / ".codex-mode"
    if flag.exists():
        flag.unlink()
        logs.append("-------- Codex AMR mode: DISABLED")
    else:
        logs.append("-------- Codex AMR mode: Already disabled")

    gpt5_rule = root / ".cursor" / "rules" / "20-gpt5-guidance.mdc"
    if gpt5_rule.exists():
        gpt5_rule.unlink()
        logs.append("-------- Removed GPT-5 guidance rules")
    # Remove persona overrides
    ov = root / ".cursor" / "rules" / "21-persona-overrides.mdc"
    if ov.exists():
        ov.unlink()
        logs.append("-------- Removed persona overrides")
    # Remove model guide
    mg = root / ".cursor" / "rules" / "22-model-guide.mdc"
    if mg.exists():
        mg.unlink()
        logs.append("-------- Removed model prompting guide")
    return logs


def enable_grok_mode(project_root: Optional[Path] = None) -> List[str]:
    """Enable Grok mode and install Grok guidance rules."""
    root = Path(project_root or ".")
    logs: List[str] = []
    cursor_dir = root / ".cursor"
    cursor_dir.mkdir(parents=True, exist_ok=True)

    logs.extend(_disable_all_modes(root, except_mode="grok"))

    (cursor_dir / ".grok-mode").write_text("", encoding="utf-8")

    # Install Grok guidance
    rules_dir = cursor_dir / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    grok_rule = rules_dir / "20-grok-guidance.mdc"
    grok_rule.write_text(
        """---
description: "Grok guidance for personas (applies in Grok mode)"
globs: ["**/*"]
alwaysApply: true
---
# Grok Usage Guidelines (Grok Mode)
- Scope: Applies when Grok mode is enabled for all personas.
- Language: English only. All logs must be prefixed with `--------`.
- Safety: Never print secrets (mask like `sk-***`). Ask confirmation before destructive ops or network calls.

## 1) Keep Instructions Lean and Focused
- Prefer direct, concise prompts; avoid excessive scaffolding.
- Resolve conflicts in favor of AGENTS.md and `.cursor/rules` in this repo.
- SSOT first: Follow personas manifest/.cursor/rules/AGENTS.md as single source of truth.

## 2) Reasoning Effort
- Default to medium for execution.
- Escalate only for non-obvious planning or ambiguous requirements.
- Return to medium after brief planning.

## 3) Structure
- Use Markdown headings and short lists for clarity.
- Introduce context via XML/Markdown tags with clear section names when helpful.

## 4) Tone
- Be crisp and action-oriented; avoid verbosity.
- Avoid overly firm mandates; state next steps precisely.

## 5) Eagerness Control
- Avoid over-collection of context; use minimal tool calls.
- Parallelize only when it clearly reduces latency without risk.

## 6) Provide Necessary Context
- Prefer explicit code/file references (e.g., @file.ts, paths, dependencies) over no-context prompts.
- Avoid irrelevant context; keep inputs scoped to the task.

## 7) Set Explicit Goals and Requirements
- Define goals, constraints, acceptance upfront to guide concise solutions.

## 8) Continual Refinement
- Leverage Grok Code Fast speed/cost to iterate rapidly; refine based on first-attempt failures.

## 9) Native Tool Calling
- Prefer native tool calling (e.g., MCP tools) over XML-based tool-call outputs.
- Use sections to delineate context (<files>, <project_structure>, <dependencies>) when passing context.

## 10) Optimize for Cache Hits
- Keep prompt prefixes/history stable across tool sequences to maximize cache reuse and latency gains.
""",
        encoding="utf-8",
    )

    logs.extend(_install_persona_overrides(root, model="grok"))
    # Materialize Grok prompting guide from docs
    try:
        _write_model_prompt_guide(root, model="grok")
        logs.append("-------- Installed Grok prompting guide (.cursor/rules/22-model-guide.mdc)")
    except Exception:
        pass
    logs.append("-------- Grok mode: ENABLED (.cursor/.grok-mode)")
    logs.append("-------- Installed Grok guidance rules (.cursor/rules/20-grok-guidance.mdc)")
    return logs


def disable_grok_mode(project_root: Optional[Path] = None) -> List[str]:
    root = Path(project_root or ".")
    logs: List[str] = []
    flag = root / ".cursor" / ".grok-mode"
    if flag.exists():
        flag.unlink()
        logs.append("-------- Grok mode: DISABLED")
    else:
        logs.append("-------- Grok mode: Already disabled")

    grok_rule = root / ".cursor" / "rules" / "20-grok-guidance.mdc"
    if grok_rule.exists():
        grok_rule.unlink()
        logs.append("-------- Removed Grok guidance rules")
    # Remove persona overrides
    ov = root / ".cursor" / "rules" / "21-persona-overrides.mdc"
    if ov.exists():
        ov.unlink()
        logs.append("-------- Removed persona overrides")
    mg = root / ".cursor" / "rules" / "22-model-guide.mdc"
    if mg.exists():
        mg.unlink()
        logs.append("-------- Removed model prompting guide")
    return logs


def _load_personas_manifest(root: Path) -> Dict[str, Any]:
    # Project-local override
    local = root / "personas" / "manifest.yaml"
    if local.exists():
        try:
            return yaml.safe_load(local.read_text()) or {}
        except Exception:
            pass
    # Packaged canonical
    pkg = Path(__file__).parent.parent.parent / "cursor-assets" / "manifests" / "personas.yaml"
    if pkg.exists():
        try:
            return yaml.safe_load(pkg.read_text()) or {}
        except Exception:
            pass
    return {}


def _install_persona_overrides(root: Path, model: str) -> List[str]:
    logs: List[str] = []
    manifest = _load_personas_manifest(root)
    personas = manifest.get("personas", {})
    if not personas:
        return logs

    lines: List[str] = []
    lines.append("---")
    lines.append("description: \"Persona model-specific overrides\"")
    lines.append("globs: [\"**/*\"]")
    lines.append("alwaysApply: true")
    lines.append("---")
    lines.append(f"# Persona Overrides — model={model}")

    count = 0
    for key, cfg in personas.items():
        overrides = (cfg or {}).get("model_overrides", {})
        o = overrides.get(model)
        if not o:
            continue
        count += 1
        lines.append("")
        lines.append(f"## {cfg.get('name', key)}")
        if o.get("flags"):
            flags = ", ".join(o.get("flags") or [])
            lines.append(f"- Flags: {flags}")
        guidance = o.get("guidance")
        if guidance:
            lines.append("")
            lines.append(guidance.rstrip())

        # Standardized MCP usage block (SSOT-aligned) for all personas
        pname = str(cfg.get('name', key)).lower()
        lines.append("")
        lines.append("<mcp_usage>")
        lines.append("- Always start with: amr_persona_orchestrate(persona, project_root, query, tool_budget=2)")
        # Persona-specific recommendations
        if pname in ("frontend", "backend", "dev", "architect"):
            lines.append("- Then: context_collect(project_root, query) if more context is needed")
        if pname in ("security", "qa"):
            lines.append("- Then: validate_check(project_root) for quick quality/security gate")
        if pname in ("performance",):
            lines.append("- Then: context_collect(project_root, 'perf hotspots, p95, traces')")
        lines.append("- Record task tag and events via memory_set_task / memory_append_event for continuity")
        lines.append("- Follow SSOT (AGENTS.md, .cursor/rules, personas manifest) as first principle")
        lines.append("</mcp_usage>")

    if count == 0:
        return logs

    rules_dir = root / ".cursor" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "21-persona-overrides.mdc").write_text("\n".join(lines), encoding="utf-8")
    logs.append("-------- Installed persona overrides (.cursor/rules/21-persona-overrides.mdc)")
    return logs


def _write_model_prompt_guide(root: Path, model: str) -> None:
    """Write model-specific prompting guide from docs into .cursor/rules.

    Reads docs/gpt_promt_guide.md or docs/grok_promt_guide.md and writes a
    rule file so the agent consistently sees the correct guidance.
    """
    docs_map = {
        "gpt": Path("docs") / "gpt_promt_guide.md",
        "grok": Path("docs") / "grok_promt_guide.md",
    }
    src = docs_map.get(model)
    if not src:
        return
    try:
        text = src.read_text(encoding="utf-8")
    except Exception:
        # Try project root relative
        try:
            text = (root / src).read_text(encoding="utf-8")
        except Exception:
            return

    rules_dir = root / ".cursor" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    header = (
        "---\n"
        f"description: \"Model prompting guide materialized from {src}\"\n"
        "globs: [\"**/*\"]\n"
        "alwaysApply: true\n"
        "---\n"
    )
    (rules_dir / "22-model-guide.mdc").write_text(header + "\n" + text, encoding="utf-8")
