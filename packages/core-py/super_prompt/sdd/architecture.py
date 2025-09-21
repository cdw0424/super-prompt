"""Spec-Driven Development (SDD) architecture helpers.

This module translates the observed Spec Kit workflow (uvx-powered specify CLI,
template bundles, slash-command driven IDE flow, etc.) into reusable guidance
that Super Prompt personas and MCP tools can surface. The data is distilled from
the documented operational lifecycle and intentionally kept in English to stay
aligned with repository guidelines.
"""

from __future__ import annotations

from textwrap import dedent
from typing import Dict, Iterable, List


SECTION_TITLES: Dict[str, str] = {
    "overview": "Overview",
    "components": "Architecture Components",
    "workspace": "Workspace Layout & Templates",
    "cli_flow": "CLI Flow (specify init/check)",
    "networking": "Networking & Security",
    "slash_commands": "Slash Command Contract",
    "runners": "Runner Expectations",
    "operations": "Operations & Risk Notes",
    "dev_cycle": "SDD Execution Cycle",
    "repo_layout": "Repository Responsibilities",
    "principles": "Design Principles",
    "quality": "Quality & Risk Watchlist",
    "troubleshooting": "Troubleshooting",
}


SDD_SECTIONS: Dict[str, str] = {
    "overview": dedent(
        """
        Spec Kit combines Spec-Driven Development with AI coding agents. The
        specify CLI runs ephemerally (`uvx --from git+https://github.com/github/spec-kit.git`
        specify ...) and scaffolds a workspace that the agent drives with slash
        commands progressing `/constitution → /specify → /plan → /tasks → /implement`.
        """
    ).strip(),
    "components": dedent(
        """
        Components:
        - *Specify CLI*: Python package executed via uvx; key commands are
          `init` and `check` with switches such as `--ai`, `--script`, `--here`,
          `--no-git`, `--debug`, `--skip-tls`, and GitHub token support.
        - *Template bundles*: release assets named like
          `spec-kit-template-<agent>-<shell>-v*.zip` downloaded per agent/shell
          combination.
        - *Workspace scripts*: `.specify/scripts/...` update agent context files
          (CLAUDE.md, GEMINI.md, etc.).
        - *Deliverables*: `spec.md`, `plan.md`, `tasks.md`, `quickstart.md`
          become the shared contract across agents and runners.
        """
    ).strip(),
    "workspace": dedent(
        """
        Workspace guardrails include `.specify/memory/constitution.md` for team
        charter, scripts for context hydration, and template directories for
        specs, plans, and tasks. Constitution overwrites during upgrades are a
        known risk and require backup/merge strategies.
        """
    ).strip(),
    "cli_flow": dedent(
        """
        `specify init` flow:
        1. Environment check (`specify check`) validates git and supported
           agents.
        2. Template selection downloads the release ZIP matching `--ai` and
           `--script`.
        3. Unpack into either the current directory (`--here`) or a new project
           folder; lay down `.specify/...` assets.
        4. Initialize git unless `--no-git` is set.
        5. Print guidance for continuing inside the IDE via slash commands.
        """
    ).strip(),
    "networking": dedent(
        """
        Networking:
        - Optional `--github-token` (or GH_TOKEN env) lifts rate limits when
          calling GitHub Releases.
        - `--skip-tls` disables verification (avoid unless debugging).
        - httpx is used for downloads; proxy/socks extras may be required in
          restricted networks.
        """
    ).strip(),
    "slash_commands": dedent(
        """
        Slash-command semantics inside the IDE:
        - `/constitution`: author or refine guardrails in
          `.specify/memory/constitution.md`.
        - `/specify`: capture requirements in `spec.md`.
        - `/plan`: create architectural decisions `plan.md`.
        - `/tasks`: break work into `tasks.md`.
        - `/implement`: execute tasks via scripted runners that read `tasks.md`.
        """
    ).strip(),
    "runners": dedent(
        """
        Runner contract expectations:
        - Batch mode follows the ordered list in `tasks.md`, halting on failures
          with clear task IDs.
        - Single-task mode executes a selected task and reports success,
          blockage, or failure plus file deltas.
        - Both modes rely on spec/plan/tasks consistency to avoid drift.
        """
    ).strip(),
    "operations": dedent(
        """
        Operational notes:
        - Always prefix commands with `uvx --from ... specify` to avoid “command
          not found” incidents.
        - Constitution updates should never be overwritten blindly; merge or
          back up customized guardrails.
        - Validate release assets—empty template ZIPs have been reported in past
          versions.
        """
    ).strip(),
    "dev_cycle": dedent(
        """
        Day-to-day SDD cycle:
        1. Run `specify init` (optionally with `--here`) for the chosen agent and
           shell.
        2. Inside the IDE, advance through `/constitution → /specify → /plan →
           /tasks → /implement`.
        3. Use the generated files (`spec.md`, `plan.md`, `tasks.md`,
           `quickstart.md`) as the single source of truth.
        """
    ).strip(),
    "repo_layout": dedent(
        """
        Repository responsibilities:
        - `src/specify_cli`: Python CLI implementation.
        - `templates/`: source templates shipped in release bundles.
        - `scripts/`: release packaging/verification helpers.
        - `memory/`: reference guardrail assets mirrored into `.specify/memory`.
        - `AGENTS.md`: enumerates supported agents and runtime expectations.
        """
    ).strip(),
    "principles": dedent(
        """
        Principles:
        - Specs lead the work; implementation follows the documented spec → plan
          → tasks flow.
        - Tool-agnostic design keeps the process portable across editors and
          frameworks.
        - Tight agent integration depends on the shared file contract and
          context update scripts.
        """
    ).strip(),
    "quality": dedent(
        """
        Quality watchlist:
        - Documentation must mirror the uvx invocation syntax.
        - Verify template integrity (prefer checksum validation) before rollout.
        - Provide merge strategy for constitution changes.
        - Ensure runners adhere to stop/rollback rules to keep humans in the
          loop.
        """
    ).strip(),
    "troubleshooting": dedent(
        """
        Troubleshooting quick hits:
        - “Command not found”: confirm you prefixed `uvx --from ... specify`.
        - Proxy failures: install `httpx[socks]` or adjust network settings.
        - Empty templates: pin to a known-good release or re-download once fixed.
        - Constitution overwrite risk: back up `.specify/memory/constitution.md`
          before re-initializing.
        """
    ).strip(),
}


SDD_WORKFLOW_STAGES: Dict[str, str] = {
    "constitution": dedent(
        """
        Establish or revise guardrails in `.specify/memory/constitution.md`; capture
        security, UX, and quality bars before drafting specs.
        """
    ).strip(),
    "specify": dedent(
        """
        Translate the problem into `spec.md` with measurable outcomes and keep it
        synced with the constitution.
        """
    ).strip(),
    "plan": dedent(
        """
        Document architecture and technology choices in `plan.md`, linking back to
        spec and guardrails.
        """
    ).strip(),
    "tasks": dedent(
        """
        Break the plan into actionable units in `tasks.md`; ensure each task
        references the relevant spec sections.
        """
    ).strip(),
    "implement": dedent(
        """
        Execute tasks via runners, update `quickstart.md`, and report
        success/blockers with explicit task identifiers.
        """
    ).strip(),
}


PERSONA_FOCUS: Dict[str, Dict[str, Iterable[str]]] = {
    "architect": {
        "sections": ["overview", "components", "workspace", "slash_commands"],
        "stages": ["constitution", "specify", "plan"],
        "notes": [
            "Map constraints from constitution into every architectural choice.",
            "Call out runner requirements when defining interfaces to keep plan and tasks consistent.",
        ],
    },
    "backend": {
        "sections": ["components", "cli_flow", "networking", "runners"],
        "stages": ["plan", "tasks", "implement"],
        "notes": [
            "Document API contracts inside `plan.md` and reflect validation steps in `tasks.md`.",
            "Highlight integration tests that runners must execute before marking tasks complete.",
        ],
    },
    "frontend": {
        "sections": ["overview", "workspace", "slash_commands", "operations"],
        "stages": ["specify", "plan", "tasks"],
        "notes": [
            "Capture UX acceptance criteria inside `spec.md` so `/implement` can gate regressions.",
            "Ensure context update scripts expose visual artifacts to the relevant agent files (CLAUDE.md, GEMINI.md).",
        ],
    },
    "qa": {
        "sections": ["runners", "operations", "quality", "troubleshooting"],
        "stages": ["plan", "tasks", "implement"],
        "notes": [
            "Embed acceptance self-checks into `tasks.md` with clear stop criteria.",
            "Maintain rollback guidance in case template downloads are inconsistent.",
        ],
    },
    "dev": {
        "sections": ["dev_cycle", "slash_commands", "runners", "quality"],
        "stages": ["tasks", "implement"],
        "notes": [
            "Respect task ordering from Spec Kit runners; report blockers with task IDs.",
            "Update `quickstart.md` whenever local verification steps change.",
        ],
    },
    "implement": {
        "sections": ["dev_cycle", "runners", "quality"],
        "stages": ["tasks", "implement"],
        "notes": [
            "Confirm each task traces back to spec/plan before execution.",
            "Document verification evidence in `quickstart.md` so deliverables stay reproducible.",
        ],
    },
    "security": {
        "sections": ["overview", "components", "operations", "quality"],
        "stages": ["constitution", "plan"],
        "notes": [
            "Infuse security guardrails into constitution updates before specs evolve.",
            "Trace data-handling decisions from plan to tasks so `/implement` enforces them.",
        ],
    },
    "performance": {
        "sections": ["components", "cli_flow", "runners", "quality"],
        "stages": ["plan", "tasks"],
        "notes": [
            "Add performance acceptance criteria into `spec.md` and metrics into `tasks.md`.",
            "Recommend profiling checkpoints for the implement stage to keep runners deterministic.",
        ],
    },
    "analyzer": {
        "sections": ["overview", "runners", "troubleshooting", "operations"],
        "stages": ["plan", "tasks", "implement"],
        "notes": [
            "Record evidence collection inside `plan.md` and thread findings back to `tasks.md` follow-ups.",
            "Capture unresolved risks so `/implement` can stage mitigation tasks.",
        ],
    },
    "devops": {
        "sections": ["components", "cli_flow", "operations", "quality"],
        "stages": ["plan", "tasks", "implement"],
        "notes": [
            "Reflect CI/CD and infrastructure contracts inside `plan.md` and make them executable via `tasks.md`.",
            "Document rollback and monitoring hooks so runners enforce deployment safety.",
        ],
    },
    "doc-master": {
        "sections": ["workspace", "repo_layout", "principles"],
        "stages": ["specify", "plan", "tasks"],
        "notes": [
            "Keep documentation artifacts aligned with `spec.md`/`plan.md` revisions.",
            "Insert documentation update tasks into `tasks.md` to maintain parity during `/implement`.",
        ],
    },
    "debate": {
        "sections": ["overview", "operations", "principles"],
        "stages": ["specify", "plan"],
        "notes": [
            "Summarize competing options in `plan.md` with decision records tied to constitution guardrails.",
            "Capture follow-up tasks for the chosen path inside `tasks.md`.",
        ],
    },
    "db-expert": {
        "sections": ["components", "cli_flow", "quality"],
        "stages": ["plan", "tasks"],
        "notes": [
            "Trace schema decisions from `plan.md` and ensure migrations/tests land in `tasks.md`.",
            "Highlight data integrity checks for `/implement` runners to verify.",
        ],
    },
    "mentor": {
        "sections": ["overview", "dev_cycle", "principles"],
        "stages": ["specify", "plan"],
        "notes": [
            "Coach teams to guard constitution updates before altering specs.",
            "Encourage writing actionable tasks so new contributors can execute `/implement` safely.",
        ],
    },
    "scribe": {
        "sections": ["workspace", "operations", "quality"],
        "stages": ["specify", "plan", "tasks"],
        "notes": [
            "Document every slash-command artifact and note when templates change.",
            "Ensure task outputs include doc updates so `/implement` keeps knowledge current.",
        ],
    },
    "tr": {
        "label": "Troubleshooting",
        "sections": ["operations", "troubleshooting", "quality"],
        "stages": ["plan", "tasks", "implement"],
        "notes": [
            "Capture incident facts and hypotheses inside `plan.md` before executing fixes.",
            "Record mitigation and verification steps in `tasks.md` so `/implement` can execute safely.",
        ],
    },
    "gpt": {
        "sections": ["overview", "principles", "operations"],
        "stages": ["specify", "plan", "tasks"],
        "notes": [
            "When operating in GPT mode, keep prompt outputs synchronized with Spec Kit file expectations.",
            "Double-check constitution alignment before finalizing responses.",
        ],
    },
    "grok": {
        "sections": ["overview", "operations", "quality"],
        "stages": ["specify", "plan", "tasks", "implement"],
        "notes": [
            "Surface data integrity and security considerations explicitly for Grok outputs.",
            "Call out template anomalies (like empty ZIPs) so humans can intervene.",
        ],
    },
    "optimize": {
        "sections": ["components", "cli_flow", "runners", "quality"],
        "stages": ["plan", "tasks"],
        "notes": [
            "Tie optimization levers back to metrics defined in `spec.md`.",
            "Schedule follow-up measurement tasks for `/implement` to validate gains.",
        ],
    },
    "service-planner": {
        "sections": ["components", "dev_cycle", "operations"],
        "stages": ["specify", "plan", "tasks"],
        "notes": [
            "Align service blueprints with constitution mandates before specs change.",
            "Ensure runbooks and onboarding docs are appended to plan/tasks for `/implement`.",
        ],
    },
    "seq": {
        "sections": ["dev_cycle", "slash_commands", "runners"],
        "stages": ["specify", "plan", "tasks"],
        "notes": [
            "Maintain a step-by-step log so humans can rejoin the sequence midstream.",
            "Highlight risk checkpoints that `/implement` should pause on for approval.",
        ],
    },
    "seq-ultra": {
        "sections": ["dev_cycle", "operations", "quality"],
        "stages": ["specify", "plan", "tasks", "implement"],
        "notes": [
            "Expose deep reasoning branches alongside the single source of truth in spec/plan.",
            "Document contingency tasks for complex branches to guide `/implement`.",
        ],
    },
    "high": {
        "sections": ["overview", "principles", "quality", "operations"],
        "stages": ["constitution", "specify", "plan", "tasks", "implement"],
        "notes": [
            "Maintain strategic linkage across every stage so downstream agents inherit the same constraints.",
            "Surface enterprise checklists (tokens, TLS, template integrity) while expanding strategies.",
        ],
    },
    "default": {
        "sections": ["overview", "dev_cycle", "operations", "principles"],
        "stages": ["specify", "plan", "tasks"],
        "notes": [
            "Keep the slash-command cadence intact to avoid diverging from Spec Kit expectations.",
            "Reference template integrity and constitution protection whenever you alter workflows.",
        ],
    },
}


def list_sdd_sections() -> List[str]:
    """Return all known section keys."""

    return list(SECTION_TITLES.keys())


def get_sdd_section(section: str) -> str:
    """Return a section summary by key, raising ValueError when unknown."""

    key = section.lower()
    if key not in SDD_SECTIONS:
        raise ValueError(f"Unknown SDD section: {section}")
    return f"{SECTION_TITLES[key]}\n\n{SDD_SECTIONS[key]}"


def generate_sdd_persona_overlay(persona: str, query: str) -> str:
    """Generate persona-specific SDD guidance to append to persona outputs."""

    persona_key = (persona or "").lower() or "default"
    focus = PERSONA_FOCUS.get(persona_key, PERSONA_FOCUS["default"])
    label = focus.get("label") or (persona.replace('-', ' ').title() if persona else "Persona")

    lines: List[str] = []
    lines.append(f"SDD Alignment for {label}")
    lines.append("")
    lines.append("Key sections to reference:")
    for section in focus.get("sections", []):
        summary = SDD_SECTIONS.get(section)
        if summary:
            title = SECTION_TITLES.get(section, section.title())
            lines.append(f"- {title}: {summary}")
    lines.append("")
    if focus.get("stages"):
        lines.append("Workflow checkpoints:")
        for stage in focus["stages"]:
            stage_summary = SDD_WORKFLOW_STAGES.get(stage)
            if stage_summary:
                stage_title = stage.replace("_", " ").title()
                lines.append(f"- {stage_title}: {stage_summary}")
        lines.append("")
    if focus.get("notes"):
        lines.append("Persona guidance:")
        for note in focus["notes"]:
            lines.append(f"- {note}")
        lines.append("")
    truncated_query = (query or "").strip().replace("\n", " ")
    if len(truncated_query) > 200:
        truncated_query = truncated_query[:197] + "..."
    if truncated_query:
        lines.append(f"Active query context: {truncated_query}")
    else:
        lines.append("Active query context: (not provided)")
    return "\n".join(lines).strip()


def render_sdd_brief(section: str | None = None, persona: str | None = None) -> str:
    """Render a standalone SDD brief for MCP consumers."""

    if section:
        return get_sdd_section(section)

    persona_overlay = generate_sdd_persona_overlay(persona or "default", "") if persona else None
    overview = [get_sdd_section("overview"), get_sdd_section("dev_cycle"), get_sdd_section("slash_commands")]
    brief = "\n\n---\n".join(overview)
    if persona_overlay:
        brief = f"{brief}\n\n---\n{persona_overlay}"
    return brief
