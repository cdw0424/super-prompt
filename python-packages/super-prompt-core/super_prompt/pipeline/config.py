"""
Pipeline configuration and data structures
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable


@dataclass
class PersonaPipelineConfig:
    persona: str
    label: str
    memory_tag: str
    use_codex: Optional[bool] = None
    plan_builder: Optional[Callable[[str, dict], List[str]]] = None
    exec_builder: Optional[Callable[[str, dict], List[str]]] = None
    persona_kwargs: Optional[Dict[str, Any]] = None
    empty_prompt: Optional[str] = None


@dataclass
class PipelineState:
    """State container flowing through pipeline stages"""
    query: str
    context_info: Dict[str, Any]
    persona_result_text: str
    codex_response: Optional[str] = None
    validation_logs: Optional[List[str]] = None
    decisions: Optional[List[str]] = None
    errors: Optional[List[str]] = None
    todo: Optional[List[Dict[str, Any]]] = None


# Pipeline labels mapping
PIPELINE_LABELS: Dict[str, str] = {
    "architect": "Architect",
    "frontend": "Frontend",
    "backend": "Backend",
    "security": "Security",
    "performance": "Performance",
    "analyzer": "Analyzer",
    "qa": "QA",
    "refactorer": "Refactorer",
    "devops": "DevOps",
    "debate": "Debate",
    "mentor": "Mentor",
    "scribe": "Scribe",
    "dev": "Dev",
    "grok": "Grok",
    "db-expert": "DB Expert",
    "optimize": "Optimize",
    "review": "Review",
    "service-planner": "Service Planner",
    "tr": "Translate",
    "doc-master": "Doc Master",
    "docs-refector": "Docs Refector",
    "ultracompressed": "Ultra Compressed",
    "high": "High Reasoning",
}


# Pipeline aliases for flexible tool names
PIPELINE_ALIASES: Dict[str, str] = {
    "architect": "architect",
    "architecture": "architect",
    "frontend": "frontend",
    "ui": "frontend",
    "backend": "backend",
    "api": "backend",
    "security": "security",
    "performance": "performance",
    "perf": "performance",
    "analyzer": "analyzer",
    "analysis": "analyzer",
    "qa": "qa",
    "quality": "qa",
    "refactor": "refactorer",
    "refactorer": "refactorer",
    "devops": "devops",
    "debate": "debate",
    "mentor": "mentor",
    "scribe": "scribe",
    "doc": "doc-master",
    "doc-master": "doc-master",
    "docs-refector": "docs-refector",
    "dev": "dev",
    "grok": "grok",
    "db-expert": "db-expert",
    "database": "db-expert",
    "optimize": "optimize",
    "optimization": "optimize",
    "review": "review",
    "code-review": "review",
    "service-planner": "service-planner",
    "service": "service-planner",
    "translate": "tr",
    "translator": "tr",
    "tr": "tr",
    "ultra": "ultracompressed",
    "ultracompressed": "ultracompressed",
    "high": "high",
}


# Default plan lines for each persona
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
    "high": [
        "- Frame strategic context, stakeholders, and constraints",
        "- Analyze scenarios, risks, and potential experiments",
        "- Recommend decision guardrails and success metrics",
    ],
}


# Default execution lines for each persona
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
    "high": [
        "- Present strategic recommendation with rationale",
        "- Align stakeholders on risks and contingency plans",
        "- Define monitoring metrics and follow-up checkpoints",
    ],
}
