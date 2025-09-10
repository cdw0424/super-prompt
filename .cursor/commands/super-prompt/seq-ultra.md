---
description: seq-ultra command
run: "./tag-executor.py"
args: ["${input} /seq-ultra"]
---

# 🔄 Advanced Sequential (10)
Deep, multi-iteration reasoning loop for complex tasks. Designed to run inside Cursor.

## Intent
Drive deliberate problem solving through bounded iterations that produce auditable artifacts, with guardrails to prevent hallucinations and scope drift.

## Inputs
- Goal (required): concise objective to achieve
- Context (optional): code, files, constraints, acceptance criteria
- Limits (optional): max iterations, token budget, timebox

## Output Artifacts (each iteration)
- Reasoning Note: short narrative of thinking and decisions
- Action Plan: next concrete step(s) with expected outcome
- Evidence Log: facts with sources (file paths, line refs, URLs)
- Risk Register: active risks + mitigations
- Delta Summary: what changed since last iteration
- Exit Check: whether success criteria are met

## Protocol
1) Frame
   - Restate goal in your own words
   - List constraints and unknowns
   - Define success criteria and stop conditions
2) Hypothesize
   - Generate 2–3 candidate approaches
   - Choose one using a brief tradeoff note
3) Act (Small Step)
   - Execute the smallest high‑leverage step
   - Produce artifacts and collect evidence
   - All runtime/debug logs MUST use the '-----' prefix; never print secrets/PII
4) Critique
   - Validate against success criteria and constraints
   - Run a contradiction check: does any evidence refute assumptions?
   - If blocked, pivot with a justification
5) Decide
   - Continue, pivot to another approach, or stop

Repeat 3–5 up to N iterations (default 10) or until exit checks pass.

## Guardrails
- Source of Truth: prefer repo code and project rules over memory
- Verification First: assert expected outcomes; write quick checks when possible
- Conservatism: choose reversible edits; avoid broad refactors without plan
- Safety: mask secrets/tokens/PII; no external calls without explicit intent
- Logging: prefix runtime or debug lines with '-----'

## Evidence Catalog
- Code citations as: `path: Lstart → Lend`
- Decisions should reference evidence IDs
- Maintain a compact table: EvidenceID | Source | Claim | Confidence

## Exit Criteria
- Success criteria satisfied AND
- No failing validations AND
- Risks acceptable or mitigated

## Failure Handling
- Produce a minimal incident note: symptom, scope, suspected cause, next probes
- Offer two fallback strategies with tradeoffs

## Quick Template
```
FRAMING
- Goal:
- Constraints:
- Success criteria:

ITERATION k/N
- Hypothesis:
- Action Plan:
- Evidence:
- Risks:
- Exit Check: pass/fail + reason

DECISION
- Continue | Pivot | Stop (why)
```

## Notes
- Prefer parallel read‑only scans; sequence only when outputs are dependent
- Keep steps small, observable, and easy to roll back
