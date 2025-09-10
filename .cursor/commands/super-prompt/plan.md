---
description: plan command
run: "./tag-executor.py"
args: ["sdd plan ${{input}}"]
---
# 📅 PLAN Designer (SDD)

Create a concrete, SDD‑aligned implementation plan. No implementation before SPEC and PLAN are approved.

## Inputs
- Problem statement and scope
- Constraints (tech, security, performance, compliance)
- Acceptance criteria
- Existing architecture/context

## Deliverables
1) Architecture sketch (C4‑lite): Context, Containers, major Components + responsibilities
2) Contract overview: API/Events/Data shapes (OpenAPI/JSON Schema hints allowed)
3) Phased plan: small, verifiable steps with rollback points
4) Risks and alternatives with mitigations
5) Non‑functional considerations: security, performance, observability, reliability
6) Acceptance checklist mapped to steps

## Plan Template
### 1. Goals and Non‑Goals
- Goals:
- Non‑Goals:

### 2. Constraints and Assumptions
- Constraints:
- Assumptions:

### 3. Architecture (C4‑lite)
- Context: actors and external systems
- Containers: services/apps, data stores, queues
- Components: key modules and boundaries
- Data flow: main paths; note trust boundaries

### 4. Contracts
- APIs: name, purpose, request/response examples, error model
- Events: name, schema, producer/consumer
- Data: tables/collections with critical fields and indexes

### 5. Phased Plan
- Phase 0: Pre‑checks (SPEC presence, repo rules, env)
- Phase 1: Minimal slice (feature toggle if applicable)
- Phase 2: Complete path + tests
- Phase 3: Hardening (observability, edge cases)
- Phase 4: Cleanup/Docs
For each phase list:
- Steps (small, atomic)
- Rollback point
- Owner and ETA (optional)
- Validation/checks

### 6. Risks and Alternatives
- Risk | Impact | Likelihood | Mitigation | Trigger
- Alternatives with tradeoffs

### 7. Non‑Functional Requirements
- Security: authn/z, secrets, PII handling, least privilege
- Performance: budgets/SLIs (e.g., LCP/INP/CLS for FE; p95 latency/throughput for BE)
- Observability: logs (use '-----' prefix), metrics, traces, alerts
- Reliability: idempotency, retries, backoff, circuit breakers

### 8. Acceptance Checklist
- All success criteria satisfied
- Tests cover critical paths
- Security checks pass; secrets masked
- Performance budgets met
- Documentation updated

### 9. Out of Scope
- Explicit boundaries to prevent scope creep
