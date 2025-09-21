# packages/core-py/super_prompt/personas/defaults.py
"""
페르소나별 기본 계획 및 실행 라인 정의
"""

from typing import Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .pipeline_manager import PipelineState


DEFAULT_PLAN_LINES: Dict[str, List[str]] = {
    "tr": [
        "- Identify source and target locale requirements",
        "- Gather glossary or domain terminology",
        "- Determine tone, formality, and formatting rules",
    ],
    "analyzer": [
        "- Collect reproduction steps and relevant logs",
        "- Map symptom timeline against recent changes",
        "- Formulate top hypotheses ranked by likelihood",
    ],
    "architect": [
        "- Define system boundaries, domains, and capabilities",
        "- Choose data flows, storage, and integration contracts",
        "- Address scalability, observability, and risk mitigation",
    ],
    "frontend": [
        "- Audit component states, accessibility, and responsive breakpoints",
        "- Align visuals with design tokens and interaction patterns",
        "- Identify performance or UX risks across target devices",
    ],
    "backend": [
        "- Map endpoint contracts, data flows, and error handling",
        "- Review database access patterns and transaction boundaries",
        "- Evaluate observability, scaling, and resiliency requirements",
    ],
    "security": [
        "- Enumerate potential threats and sensitive assets",
        "- Review authentication, authorization, and data protection",
        "- Prioritize vulnerabilities and compliance obligations",
    ],
    "performance": [
        "- Profile hot paths and identify resource bottlenecks",
        "- Propose caching, batching, or parallelization strategies",
        "- Define baseline metrics and regression safeguards",
    ],
    "qa": [
        "- Determine critical workflows and risk-based scenarios",
        "- Plan edge cases, negative tests, and data variations",
        "- Align acceptance criteria with automation strategy",
    ],
    "refactorer": [
        "- Locate code smells, duplication, and architectural drift",
        "- Propose incremental refactor plan with safety nets",
        "- Coordinate regression tests and migration notes",
    ],
    "devops": [
        "- Review deployment topology, pipelines, and secrets handling",
        "- Assess monitoring, alerting, and rollout strategies",
        "- Outline reliability risks and mitigation steps",
    ],
    "dev": [
        "- Clarify product requirements and success metrics",
        "- Break work into testable, incremental deliverables",
        "- Align validation, release, and stakeholder coordination",
    ],
    "service-planner": [
        "- Capture goals, KPIs, and success metrics",
        "- Map discovery research, experiments, and risks",
        "- Define cross-team alignment and governance checkpoints",
    ],
    "doc-master": [
        "- Inventory audiences, doc types, and information gaps",
        "- Design IA, templates, and contributor workflow",
        "- Plan verification, localization, and maintenance cadence",
    ],
    "docs-refector": [
        "- Identify duplicate or outdated documentation clusters",
        "- Propose consolidation structure and redirect plan",
        "- Define review owners and migration sequencing",
    ],
    "ultracompressed": [
        "- Select critical insights and supporting evidence",
        "- Prioritize messaging hierarchy under token budget",
        "- Flag trade-offs or details omitted for brevity",
    ],
    "seq": [
        "- Define hypothesis list and evidence required",
        "- Outline sequential reasoning checkpoints",
        "- Prepare validation tests for each conclusion",
    ],
    "seq-ultra": [
        "- Establish ten-step investigation agenda",
        "- Maintain branching options and re-evaluation criteria",
        "- Record open questions and ownership for follow-up",
    ],
    "high": [
        "- Frame strategic context, stakeholders, and constraints",
        "- Analyze scenarios, risks, and potential experiments",
        "- Recommend decision guardrails and success metrics",
    ],
}


DEFAULT_EXEC_LINES: Dict[str, List[str]] = {
    "tr": [
        "- Produce draft translation and run terminology QA",
        "- Validate locale-specific formatting and constraints",
        "- Schedule stakeholder review and acceptance testing",
    ],
    "analyzer": [
        "- Run experiments to confirm or eliminate hypotheses",
        "- Document root cause evidence and proposed fixes",
        "- Share mitigation plan and monitoring actions",
    ],
    "architect": [
        "- Draft ADRs and architecture diagrams for consensus",
        "- Stage rollout phases with validation checkpoints",
        "- Align observability, SLOs, and governance updates",
    ],
    "frontend": [
        "- Implement component or layout adjustments with accessibility tests",
        "- Run visual/unit regression suites and manual UX checks",
        "- Capture follow-up UX debt and release notes",
    ],
    "backend": [
        "- Implement API or data changes behind feature guards",
        "- Execute contract, integration, and load tests",
        "- Update telemetry dashboards and rollback plan",
    ],
    "security": [
        "- Apply mitigations or compensating controls",
        "- Schedule penetration/system tests and policy updates",
        "- Document residual risk and monitoring actions",
    ],
    "performance": [
        "- Prototype and benchmark prioritized optimizations",
        "- Deploy behind experiment/feature flags",
        "- Monitor long-run metrics and guardrails",
    ],
    "qa": [
        "- Author automated and exploratory test cases",
        "- Execute regression plan and triage defects",
        "- Update coverage dashboards and flake watchlist",
    ],
    "refactorer": [
        "- Execute safe refactors with incremental commits",
        "- Run full test suite and static analysis",
        "- Communicate migration guides and deprecation timeline",
    ],
    "devops": [
        "- Update CI/CD pipelines and infrastructure as code",
        "- Perform canary deployments with health checks",
        "- Document incident response and rollback SOPs",
    ],
    "dev": [
        "- Implement feature slices with instrumentation",
        "- Validate acceptance tests and code review",
        "- Prepare release notes and rollout checklist",
    ],
    "service-planner": [
        "- Draft PRD, discovery plan, and telemetry hooks",
        "- Align cross-functional owners and decision gates",
        "- Schedule backlog grooming and launch readiness reviews",
    ],
    "doc-master": [
        "- Produce IA map, templates, and contributor guide",
        "- Coordinate doc sprints and validation reviews",
        "- Establish upkeep cadence and analytics tracking",
    ],
    "docs-refector": [
        "- Merge or retire redundant docs with redirects",
        "- Normalize style and examples across remaining docs",
        "- Log future documentation debt and owners",
    ],
    "ultracompressed": [
        "- Draft concise response and confirm key facts",
        "- Run peer or stakeholder verification for omissions",
        "- Capture optional deep-dive references",
    ],
    "seq": [
        "- Execute sequential reasoning steps with evidence",
        "- Validate conclusions against assumptions",
        "- Track unresolved branches for future exploration",
    ],
    "seq-ultra": [
        "- Document each iteration outcome and decision",
        "- Maintain branch ledger and revisit pivot criteria",
        "- Summarize insights with remaining unknowns",
    ],
    "high": [
        "- Present strategic recommendation with rationale",
        "- Align stakeholders on risks and contingency plans",
        "- Define monitoring metrics and follow-up checkpoints",
    ],
}


def build_plan_lines_from_state(persona: str, state: "PipelineState") -> List[str]:
    dynamic: List[str] = []
    patterns = state.context_info.get("patterns") or []
    relevance = state.context_info.get("query_relevance") or []

    if not patterns:
        dynamic.append("- [dynamic] Collect repository signals (files, commands, patterns)")
    else:
        dynamic.append("- [dynamic] Focus areas: " + ", ".join(map(str, patterns[:3])))
    if relevance:
        dynamic.append("- [dynamic] Relevant entities: " + ", ".join(map(str, relevance[:5])))
    if state.codex_response:
        dynamic.append("- [dynamic] Incorporate Codex insights into hypotheses and checks")
    if state.persona_result_text:
        snippet = state.persona_result_text.strip().splitlines()[0][:160]
        if snippet:
            dynamic.append("- [dynamic] Persona insight: " + snippet)

    # Fallback defaults per persona
    base = list(
        DEFAULT_PLAN_LINES.get(
            persona,
            [
                "- Clarify requirements and constraints",
                "- Break down the problem into manageable steps",
                "- Identify risks and mitigation strategies",
            ],
        )
    )

    return (dynamic + base) if dynamic else base


def build_exec_lines_from_state(persona: str, state: "PipelineState") -> List[str]:
    dynamic: List[str] = []
    if state.errors:
        dynamic.append("- [dynamic] Address pipeline errors before proceeding")
    if state.decisions:
        dynamic.append("- [dynamic] Execute the agreed decision and capture evidence")
    if state.codex_response:
        dynamic.append("- [dynamic] Validate Codex-derived steps against ground truth")
    relevance = state.context_info.get("query_relevance") or []
    if relevance:
        dynamic.append("- [dynamic] Verify changes impacting: " + ", ".join(map(str, relevance[:5])))

    base = list(
        DEFAULT_EXEC_LINES.get(
            persona,
            [
                "- Implement prioritized actions",
                "- Validate outcomes against definition of done",
                "- Record follow-ups and monitor for regressions",
            ],
        )
    )

    return (dynamic + base) if dynamic else base


def evaluate_gates(state: "PipelineState") -> "Tuple[bool, List[str]]":
    missing: List[str] = []
    patterns = state.context_info.get("patterns") or []
    relevance = state.context_info.get("query_relevance") or []

    if not patterns and not relevance:
        missing.append("context_signals")

    return (len(missing) == 0, missing)
