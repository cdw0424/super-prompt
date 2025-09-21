"""
Service Planning tools (MCP-first)

Lightweight generators that scaffold PRD and discovery plans based on the
dual-track discovery and delivery flow. These are non-LLM utilities meant
to be orchestrated by the model via MCP tool calls.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def service_planner_prd(query: str) -> Dict[str, Any]:
    """Generate a PRD scaffold with success metrics and counter-metrics.

    Args:
        query: Problem/feature statement or context from the user.

    Returns:
        Dict with ok/logs and a markdown PRD scaffold in `prd`.
    """
    title = (query or "New Service/Feature").strip().splitlines()[0][:80]
    now = datetime.utcnow().strftime("%Y-%m-%d")
    prd = f"""# PRD — {title}

## 0) Context Summary
- Date: {now}
- Author: Service Planner
- Source Query: {query or 'n/a'}

## 1) Problem & Goals (Problem-Fit)
- Problem statement
- Target users & JTBD
- Business goals & OKRs linkage
- Constraints (Tech/Cost/Brand/Policy)

## 2) Solution Overview (Solution-Fit)
- Proposed approach & alternatives
- Key scenarios / user journeys
- Risks & open questions

## 3) Metrics (Biz/Feasibility-Fit)
- Success metrics (leading/lagging)
- Counter-metrics (guardrails)
- Measurement plan (telemetry, ETL)

## 4) Scope & Slices
- MVP scope and exclusions
- Slice plan (phases/waves)
- Non-functional requirements (perf, sec, a11y)

## 5) Design & IA Hooks
- IA overview
- Design system components and states

## 6) Engineering Plan
- Architecture sketch & dependencies
- Data model / API contracts
- Rollout plan (flags/gradual/A/B)

## 7) QA & Validation
- Unit/E2E/Sec test strategy
- Experiment plan (A/B, concierge/WoZ)

## 8) Governance
- Risk/Privacy/AI Safety
- Legal/Compliance
- Ops/SLOs/Incident mgmt

## 9) Knowledge Base Updates
- Product Knowledge Graph entries
- Links to evidence and research
"""
    return {
        "ok": True,
        "logs": ["-------- service_planner: generated PRD scaffold"],
        "prd": prd,
    }


def service_planner_discovery(query: str, depth: int = 1) -> Dict[str, Any]:
    """Generate a dual-track discovery outline aligned to the flow.

    Args:
        query: Problem/opportunity statement
        depth: 1 (overview) or 2 (detailed bullets)
    """
    lines = []
    lines.append("# Dual-Track Discovery Plan")
    lines.append("")
    lines.append(f"- Input: { (query or 'n/a').strip() }")
    lines.append("- Depth: overview" if depth <= 1 else "- Depth: detailed")
    lines.append("")

    def add(section: str, bullets: list[str]):
        lines.append(f"## {section}")
        for b in bullets:
            lines.append(f"- {b}")
        lines.append("")

    add("Problem Framing & Opportunity Tree", [
        "Define problem and desired outcomes",
        "Map opportunities and sub-problems",
    ])
    add("Assumption Map (D/V/F/E)", [
        "List desirability, viability, feasibility, ethics assumptions",
        "Prioritize by risk/uncertainty",
    ])
    add("Research", [
        "Qualitative (interviews, usability)",
        "Quantitative (logs, usage, surveys)",
    ])
    add("Opportunity Sizing", [
        "Estimate impact/effort",
        "Define decision thresholds",
    ])
    add("Experiment Engine", [
        "Prototype and feasibility spikes",
        "Concierge/WoZ and A/B experiments",
        "Define success & stop criteria",
    ])
    add("Evidence Repo", [
        "Centralize findings and decisions",
        "Link to Product Knowledge Graph",
    ])

    return {
        "ok": True,
        "logs": ["-------- service_planner: generated discovery outline"],
        "plan": "\n".join(lines),
    }

