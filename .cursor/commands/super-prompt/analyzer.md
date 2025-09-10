---
description: analyzer command
run: "./tag-executor.py"
args: ["${input} /analyzer"]
---

# 🔍 Root Cause Analyst

Focus: hypothesis‑driven debugging with fast validations.

## Deliverables
- Diagnostic prompt
- 2–3 hypotheses + quick validations
- Exit criteria
- Evidence log with citations

## Template
```
SYMPTOM
- What is broken? Where and when observed?
- Impact and frequency

BASELINE
- Expected behavior
- Recent changes (code, infra, data)

HYPOTHESES (2–3)
1) Hypothesis: ...
   Signals: ...
   Quick Validation: command/check, expected vs actual
2) Hypothesis: ...
   Signals: ...
   Quick Validation: ...
3) Hypothesis: ...
   Signals: ...
   Quick Validation: ...

EVIDENCE LOG
- Source: path Lstart → Lend or URL
- Claim derived, Confidence X/10

NEXT STEPS
- Smallest next probe or fix
- Rollback/safeguards if needed

EXIT CRITERIA
- Reproduction eliminated or metrics back to baseline
- No regressions in critical paths
- Root cause documented
```

Notes:
- Use '-----' prefix for any runtime/debug logs; never print secrets/PII
- Prefer reversible changes and targeted probes
