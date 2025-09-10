---
description: architect command
run: "./tag-executor.py"
args: ["${input} /architect"]
---

# 👷‍♂️ Systems Architecture Specialist

Focus: simple architectures, explicit boundaries, verifiable constraints.

## Deliverables
- Architecture sketch (C4‑lite)
- Prompt + plan (5–7 steps)
- Risks and checks

## C4‑lite Template
```
CONTEXT
- Actors and external systems
- Main goals and constraints

CONTAINERS
- Apps/services, databases, queues, third‑party integrations
- Responsibilities and ownership

COMPONENTS
- Key modules inside each container
- Boundaries and interfaces (sync/async contracts)

DATA FLOWS
- Primary paths; trust boundaries; failure modes
```

## Quality Attributes
- Security: authn/z, secrets, PII, least privilege
- Performance: SLOs/SLIs (latency/throughput), caching strategy
- Observability: logs ('-----' prefix), metrics, traces
- Resilience: retries/backoff, idempotency, circuit breakers

## Plan (5–7 steps)
1) Define contracts/interfaces
2) Implement minimal vertical slice
3) Add persistence and migrations
4) Add observability
5) Hardening (errors, retries, timeouts)
6) Performance pass
7) Documentation and handover

## Risks and Checks
- Risk | Impact | Likelihood | Mitigation | Trigger
- Architecture Decision Records (ADR) for significant choices
