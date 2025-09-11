# AGENTS.md — Super‑Prompt × Codex: Auto Model Router (medium ↔ high)

## Policy: Language & Logs
- Output language: English. Tone: precise, concise, production‑oriented.
- All debug/console lines MUST start with `--------`.

## Router Rules (AMR)
- Start: gpt‑5, reasoning=medium.
- Classify tasks:
  - L0: lint/format/rename/find‑replace/small refactor → stay medium.
  - L1: tests/small type/API change/routine migrations → stay medium.
  - H: architecture/security/perf/complex debugging/multi‑module planning → **switch to high** for PLAN/REVIEW, then **back to medium** for EXECUTION.
- Switching:
  - To high: first line `/model gpt-5 high` then log `--------router: switch to high (reason=deep_planning)`
  - Back to medium: first line `/model gpt-5 medium` then log `--------router: back to medium (reason=execution)`
- Failure/Flaky/Unclear root cause → temporarily analyze at high then execute at medium.
- User override: if the user pins a level, never auto‑switch.

## Output Discipline
- Minimal diffs, explicit test commands, and a short verification report.
- H tasks: produce a PLAN first (Goal/Plan/Risks/Test/Rollback), then EXECUTION + VERIFY + REPORT.
- Keep noise low; if long, add a 5‑line executive summary.

## Stack Defaults (opt‑in)
- FE: React/Next.js/React Router/Flutter (small reusable components).
- BE: Java 8 + Spring Boot (or Node.js on request).
- DB: MySQL + Flyway (utf8mb4, KST, proper indexes/FKs).
- Infra: AWS EC2/ALB/Route53; Blue‑Green deployments.
- Cache/Lock: Redis with explicit TTLs and `namespace:sub:resource` keys.
- Shopify: rate limits/backoff/idempotency, bulk minimized.
