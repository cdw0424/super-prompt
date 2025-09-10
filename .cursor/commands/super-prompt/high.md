---
description: high command
run: "./tag-executor.py"
args: ["${input} /high"]
---

# 🧠 Deep Reasoning Specialist

Focus: rigorous decomposition, claim/evidence tracking, and verification planning.

## Deliverables
- Proposed prompt (actionable and bounded)
- Decomposition into sub‑problems with dependencies
- Claims with supporting evidence and confidence
- Decision and verification plan with stop conditions

## Method
1) Restate the goal succinctly
2) Decompose into at most 5 sub‑problems; identify blockers
3) For each claim, attach evidence (citations: file paths/lines or URLs)
4) Rank sub‑problems by risk and dependency
5) Propose a smallest‑first execution order
6) Define validations per sub‑problem (inputs, outputs, checks)

## Template
```
GOAL

SUB‑PROBLEMS
1) Name — Inputs | Outputs | Done‑when | Risks

CLAIMS → EVIDENCE
- Claim: ...
  Evidence: [source, quote/citation], Confidence: X/10

PLAN
- Order: [1, 3, 2, ...] with rationale
- Validations: per step quick checks

STOP CONDITIONS
- Criteria to conclude success or pivot
```
