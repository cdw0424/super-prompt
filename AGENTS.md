# Repository Guidelines

## Project Structure & Module Organization
- Node wrapper: `bin/super-prompt`, package metadata in `package.json`.
- Python core (MCP server & tools): `packages/core-py/super_prompt/`
- Cursor assets: `.cursor/commands/super-prompt/`, `.cursor/rules/`
- Codex assets: `.codex/`
- Personas manifest (SSOT): `packages/cursor-assets/manifests/personas.yaml` (project override: `personas/manifest.yaml`)

## Build, Test, and Development Commands
- Initialize project assets: `npx super-prompt init`
- Start MCP server: `npx super-prompt mcp:serve`
- Guards: `.codex/router-check.sh` and `scripts/codex/prompt-qa.sh <transcript>`

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

## Agent‑Specific Instructions (AMR + SSOT)
- AMR: start at medium; escalate to high for PLAN/REVIEW or deep root‑cause, then return to medium for EXECUTION.
- SSOT: personas manifest → `.cursor/rules` → `AGENTS.md`. Avoid drift; prefer materialized overrides via mode toggles.
- Modes: `/gpt-mode-on` (GPT‑5), `/grok-mode-on` (Grok); mutual exclusivity enforced.
