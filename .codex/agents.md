# Codex Agent — Project Guidance (AMR + State Machine)

## Memory & Merge Order
- Codex merges AGENTS.md top‑down:
  1) `~/.codex/AGENTS.md` (global)
  2) `AGENTS.md` at repo root (shared)
  3) `AGENTS.md` in current working directory (feature‑specific)
- This file (`.codex/agents.md`) provides Codex‑specific guidance for this repo.

## Language & Logging
- English only. Keep tone precise, concise, production‑oriented.
- All incidental logs MUST start with: `--------`.
- Never print real secrets; mask like `sk-***`.

## Auto Model Router (AMR: medium ↔ high)
- Start in `gpt-5` reasoning=medium.
- Heavy reasoning (architecture, security/perf review, root‑cause, multi‑module, ambiguous):
  - Switch up: `/model gpt-5 high` then `--------router: switch to high (reason=deep_planning)`
  - After planning: `/model gpt-5 medium` then `--------router: back to medium (reason=execution)`
- Failures/flaky/unclear root cause → analyze at high, then execute at medium.

## Fixed State Machine (per turn)
- `[INTENT] → [TASK_CLASSIFY] → [PLAN] → [EXECUTE] → [VERIFY] → [REPORT]`
- H tasks: produce a short PLAN first (Goal, Plan, Risks, Test/Verify, Rollback) before EXECUTE.
- EXECUTE: minimal diffs only; include exact macOS zsh commands with `--------run:` prefix.
- VERIFY: show commands and a brief pass/fail summary (smallest failing snippet if any).

## Personas (Codex‑friendly flags)
- Use CLI flags (no slash commands in Codex):
  - `super-prompt optimize --frontend  "Design responsive layout"`
  - `super-prompt optimize --backend   "Retry + idempotency strategy"`
  - `super-prompt optimize --architect "Modular structure for feature X"`
- Single‑model debate (Positive vs Critical selves):
  - `super-prompt optimize --debate --rounds 8 "Should we adopt feature flags?"`

## Codex Tips
- File search: type `@` and select a path.
- Image input: `codex -i img.png "Explain this error"`
- Edit previous message: press Esc when composer is empty, then Esc again to backtrack.
- Shell completions: `codex completion bash|zsh|fish`
- Use `--cd`/`-C` to set Codex working root.

## Expectations
- Keep diffs minimal; avoid unrelated changes.
- Always provide verification commands and a short result summary.
- Prioritize clarity, reproducibility, and low noise.
