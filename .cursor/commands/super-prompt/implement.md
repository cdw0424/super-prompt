---
description: implement command
run: "./tag-executor.py"
args: ["sdd implement ${{input}}"]
---
# 🚀 Implementation Starter (SDD)

Proposes a minimal‑change implementation aligned with approved SPEC/PLAN.

## Preconditions
- SPEC and PLAN exist; if missing, generate minimal drafts and request approval
- Read project rules; follow existing patterns first
- Ensure secrets/PII are masked in code and logs ('-----' prefix for logs)

## Strategy
- Prefer smallest viable change with feature flags/toggles when applicable
- Isolate risk behind interfaces; avoid broad refactors
- Commit in small, revertible units

## Change Set Outline
- Files to add:
- Files to modify:
- Files to remove (if any) and rationale:

## Step‑By‑Step Application
1) Pre‑flight checks: build/test pass baseline
2) Add interfaces/contracts first (types, schemas, OpenAPI)
3) Implement minimal path (happy path only)
4) Add validations and error handling
5) Wire observability: logs (with '-----'), metrics, traces
6) Expand to edge cases
7) Update docs and examples

## Tests
- Unit tests for core logic
- Integration tests for contract compliance
- Regression tests for critical paths
- Performance sanity checks (budgets noted in PLAN)

## Rollback Plan
- Each step identifies a safe revert point
- If failure after step k, revert to k‑1 and open an incident note

## Verification
- Map checks to Acceptance Self‑Check: criteria, constraints, safe logging, regression tests, docs

## Dry‑Run vs Apply
- Dry‑Run: print proposed edits and commands (no changes)
- Apply: execute edits with confirmations where required
