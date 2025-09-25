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
- Review `.super-prompt/context/project-dossier.md`; if it is missing, run `/super-prompt/init` to regenerate it.
- Collect feature goal, affected surfaces, acceptance criteria, and any blocking constraints before touching code.
- Draft only the essential TODO list (≤5 items) needed to ship; then execute those TODOs sequentially.
- Focus on concrete deliverables (code, tests, docs). Delay Double-Check MCP until every TODO is complete.
- Use MCP Only (MCP server call): /super-prompt/dev "<your feature request>"

## Phases & Checklist
### Phase 0 — Scope Intake
- [ ] Confirm objective, consumers, and Definition of Done
- [ ] Capture environment/branch, dependencies, and rollout guardrails

### Phase 1 — TODO Backlog (≤5 items)
- [ ] Summarize current architecture and highlight impacted modules
- [ ] Break the work into ordered TODOs with owners/ETA where helpful
- [ ] Surface unknowns or blockers that must resolve before execution

### Phase 2 — Execute TODOs
- [ ] For each TODO, outline the specific files/functions to touch and apply the change
- [ ] Record test coverage expectations and monitoring hooks per TODO
- [ ] Track completed TODOs with evidence (diff snippets, command output)

### Phase 3 — Validation & Polish
- [ ] Run/outline required tests, linting, type checks, and report outcomes with evidence
- [ ] Update docs/changelog/config as needed and note any rollout or migration steps
- [ ] Capture remaining risks, debt, or follow-ups generated during execution

### Phase 4 — Closeout & Handoff
- [ ] Summarize status of TODOs/tests, flag debt or follow-ups
- [ ] Provide release/readiness checklist with owners and timestamps
- [ ] Run Double-Check MCP: /super-prompt/double-check "Confession review for delivery"

## Outputs
- TODO board (≤5 items) with status, evidence, and links to code/test updates
- Code-level deliverables (diff snippets, new files, config changes) with validation results
- Final handoff summary covering residual risks, monitoring steps, follow-up owners, and the Double-Check MCP confirmation number
