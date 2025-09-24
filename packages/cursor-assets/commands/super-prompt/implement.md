---
description: implement command
run: mcp
server: super-prompt
tool: sp_implement
args:
  query: "${input}"
  persona: "implement"
---

## Execution Mode

# Implement — Guided Execution

## Instructions
- Review the SDD artifacts first: `specs/*.md` (spec), `specs/*/plan.md`, and `specs/*/tasks.md`. Escalate if any are missing or out of date.
- Accept only inputs referencing an approved SDD task (e.g., `TASK-123`). Capture task IDs before executing.
- Execute strictly within SDD constraints: honor gates, dependencies, and acceptance criteria documented in the tasks file.
- Use MCP Only (MCP server call): /super-prompt/implement "<task id or brief>"

## SDD Execution Checklist
### Phase 0 — Artifact Intake
- [ ] Load latest spec/plan/tasks for the feature; confirm timestamps and owners
- [ ] Note gating criteria (readiness, approvals, rollout requirements)

### Phase 1 — Task Validation
- [ ] Enumerate the SDD task(s) to execute with references to sections in `tasks.md`
- [ ] Flag blockers, dependencies, or missing assets before coding begins

### Phase 2 — Guided Implementation
- [ ] For each task, apply the documented steps in order; include file paths and diff-style snippets
- [ ] Record validation commands (tests, linters) tied to each task and capture outcomes

### Phase 3 — SDD Compliance Wrap-up
- [ ] Update the SDD artifacts if acceptance criteria or status changed (spec, plan, tasks)
- [ ] Summarize completed work versus outstanding tasks and note required follow-ups
- [ ] Run Double-Check MCP: /super-prompt/double-check "Confession review for SDD implementation"

## Outputs
- Task-by-task execution log referencing SDD task IDs and acceptance criteria
- Code/test/doc updates aligned to each task with proof of validation
- Updated SDD status summary plus Double-Check MCP confirmation
