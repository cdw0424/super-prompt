# Repository Guidelines

## Project Structure & Module Organization
- Core CLI: `scripts/super_prompt/cli.py` (Python, single‑file CLI).
- Node package wrapper: `bin/super-prompt`, metadata in `package.json`.
- AMR assets: `prompts/`, `docs/`, `bin/codex-*`, `scripts/codex/*`, `.cursor/rules/*`.
- Keep new personas/rules under `.cursor/commands/super-prompt/` and `.cursor/rules/`.

## Build, Test, and Development Commands
- Initialize Cursor rules: `super-prompt super:init`
- Run personas from CLI: `super-prompt optimize "your query /frontend"`
- AMR helpers: `npm run codex:plan`, `npm run codex:exec`, `npm run amr:rules`, `npm run amr:print`
- Guards: `scripts/codex/router-check.sh` (AMR assets) and `scripts/codex/prompt-qa.sh <transcript>` (state‑machine checks)

## Coding Style & Naming Conventions
- Language: English only in prompts/docs. All logs start with `--------`.
- JavaScript/JSON: 2‑space indent; Python: 4‑space indent.
- Names: CLI files kebab‑case; Python symbols snake_case; keep function names descriptive.
- Do not print secrets/tokens; mask like `sk-***`.

## Testing Guidelines
- For CLI additions, prefer Jest integration tests (`*.int.test.js`) or minimal smoke tests.
- Validate prompt outputs via `prompt-qa.sh` and keep sample transcripts under `docs/examples/`.
- Before PR, run: `scripts/codex/router-check.sh` and, if applicable, `npm test`.

## Commit & Pull Request Guidelines
- Use Conventional Commits (e.g., `feat(cli): ...`, `fix: ...`, `docs: ...`).
- PRs should include: short description, rationale, screenshots (when UX), and steps to verify.
- Keep diffs minimal and scoped; avoid unrelated refactors.

## Agent‑Specific Instructions (AMR)
- Auto Model Router (medium ↔ high): start at medium; escalate to high for PLAN/REVIEW or root‑cause, then return to medium for EXECUTION.
- Manual switches (if TUI does not auto‑run):
  - `/model gpt-5 high` → plan at high
  - `/model gpt-5 medium` → execute at medium
