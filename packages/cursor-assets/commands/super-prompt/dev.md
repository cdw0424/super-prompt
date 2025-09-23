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
- Validate plans against the SSOT (spec/plan/tasks) and uphold SOLID design principles throughout
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

### Phase 2 — Implementation Plan
- [ ] Break work into ordered tasks with assignees/effort estimates
- [ ] Note code changes, migrations, or config updates per task
- [ ] Specify test strategy (unit/integration/e2e) and monitoring updates

### Phase 3 — Build & Validation Guidance
- [ ] Outline coding steps, including reusable helpers and patterns
- [ ] List commands to run (e.g., `npm test`, `pytest`, linting) and expected outputs
- [ ] Capture documentation updates, changelog entries, and review artifacts

### Phase 4 — Closeout & Handoff
- [ ] Summarize status of tasks/tests, flag debt or follow-ups
- [ ] Provide release/readiness checklist with owners and timestamps
- [ ] Run Double-Check MCP: /super-prompt/double-check "Confession review for delivery"

## Outputs
- Implementation plan with task breakdown and sequencing
- Testing matrix including commands, expected results, and coverage notes
- Handoff summary with remaining risks, monitoring steps, and next actions
