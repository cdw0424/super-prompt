# Codex AMR (medium ↔ high) — Usage

## Quick start (TUI)
1. Run `codex` in the repo root.
2. Paste the bootstrap prompt from `prompts/codex_amr_bootstrap_prompt_en.txt`.
3. For heavy tasks, the agent will switch to **high** for planning, then back to **medium** for execution.
4. Router events are printed with the `--------router:` prefix.

## One-liners
- Manual switches in TUI:
  ```
  /model gpt-5 high
  (plan...)
  /model gpt-5 medium
  (execute and verify)
  ```

## Wrappers
- `./bin/codex-high`  → gpt‑5 with reasoning=high
- `./bin/codex-medium` → gpt‑5 with reasoning=medium

## Node integration (optional)
If `package.json` exists:
- Adds two scripts:
  - `codex:plan` → `bin/codex-high`
  - `codex:exec` → `bin/codex-medium`

## Project defaults
- FE: React/Next.js/React Router/Flutter.
- BE: Java 8 + Spring Boot (or Node.js on request).
- DB: MySQL + Flyway; Infra: AWS EC2/ALB/Route53; Blue‑Green; Redis caching.
- See `AGENTS.md` for the router policy.
