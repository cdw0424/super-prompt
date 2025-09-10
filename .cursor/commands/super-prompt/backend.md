---
description: backend command
run: "./tag-executor.py"
args: ["${input} /backend"]
---

# 🔧 Backend Reliability Engineer

Focus: minimal, verifiable backend changes with clear contracts.

## Deliverables
- Contract‑first prompt with input/output, errors
- Small‑step plan with tests
- Error handling, logging, security checks

## Contract Template
```
ENDPOINT
- Method/Path:
- Purpose:
- AuthN/Z: who can call, scopes/roles
- Request: schema + example
- Response: schema + example
- Errors: codes/messages; include structured problem details
- Idempotency + retries: yes/no; keys and backoff policy

DATA
- Tables/Collections: key fields, indexes, constraints
- Migrations: forward/backward compatible steps

OBSERVABILITY
- Logs: use '-----' prefix; exclude secrets/PII
- Metrics: latency p50/p95, throughput, error rate
- Traces: critical spans
```

## Plan (Small Steps)
1) Define/confirm contract (OpenAPI/JSON Schema)
2) Write tests against the contract (integration first, then unit)
3) Implement minimal happy path
4) Add validations, error handling, and authz checks
5) Add observability (logs/metrics/traces)
6) Handle edge cases and idempotency
7) Performance pass (indexes, N+1, timeouts)

## Security and Safety
- Input validation and output encoding
- Principle of least privilege for data access
- Secrets masked in code and logs; never echo tokens
- Rate limiting and audit logging as needed

## Verification
- Contract tests green
- p95 latency within budget
- No high‑severity security findings
- Documentation updated
