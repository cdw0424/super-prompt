---
description: dev command - Feature development with quality and delivery focus
run: mcp
server: super-prompt
tool: sp_dev
args:
  query: "${input}"
  persona: "dev"
---

## Execution Mode

# Dev — Delivery Pipeline

## Instructions
- Review the project dossier at `.super-prompt/context/project-dossier.md`; if it is missing, run `/super-prompt/init` to regenerate it.
- Provide feature goal, affected surfaces, and acceptance criteria up front
- Link specs/tickets and note test frameworks or deployment constraints
- Validate proposals against current requirements, engineering standards, and Definition of Done—opt for pragmatic execution over ceremony.
- After scope confirmation, bias toward building the solution—keep planning concise (<=5 bullets) and move straight into code, tests, and docs.
- Use MCP Only (MCP server call): /super-prompt/dev "<your feature request>"

## Phases & Checklist
### Phase 0 — Scope Intake
- [ ] Confirm objective, consumers, and Definition of Done
- [ ] Capture environment/branch, dependencies, and rollout guardrails
- [ ] Run Double-Check MCP: /super-prompt/double-check "Confession review for scope framing"

### Phase 1 — Solution Design
- [ ] Summarize current architecture and highlight impacted modules
- [ ] Draft success metrics plus guardrails (perf, security, accessibility)
- [ ] Identify open questions or missing context to unblock implementation

### Phase 2 — Implementation Blueprint (≤5 bullets)
- [ ] Summarize the execution strategy in a handful of actionable steps
- [ ] Identify the specific files/functions to touch and required data or migrations
- [ ] Call out test coverage expectations and monitoring hooks

### Phase 3 — Implementation & Validation
- [ ] Write or modify code following the blueprint; include diff-style snippets
- [ ] Run or outline test/lint/type commands, report outcomes, and attach evidence
- [ ] Update docs/changelog/config as needed and call out deployment or migration steps

### Phase 4 — Closeout & Handoff
- [ ] Summarize status of tasks/tests, flag debt or follow-ups
- [ ] Provide release/readiness checklist with owners and timestamps
- [ ] Run Double-Check MCP: /super-prompt/double-check "Confession review for delivery"

## Outputs
- Concise implementation blueprint linked to acceptance criteria
- Code-level deliverables (diff snippets, new files, config changes) with validation results
- Final handoff summary covering residual risks, monitoring steps, follow-up owners, and the Double-Check MCP confirmation number
