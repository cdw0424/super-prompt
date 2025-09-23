# Repository Guidelines

This guide summarizes the conventions required to contribute effectively to `super-prompt`. Follow each section to keep changes aligned with the Cursor/Codex tooling that powers the project.

## Project Structure & Module Organization
- Node CLI wrapper lives in `bin/super-prompt`; metadata sits in `package.json`.
- Python MCP core and tools are under `packages/core-py/super_prompt/`.
- Cursor assets: `.cursor/commands/super-prompt/` and `.cursor/rules/`; Codex assets: `.codex/`.
- Personas manifest source of truth is `packages/cursor-assets/manifests/personas.yaml`; override via `personas/manifest.yaml` when needed.

## Build, Test, and Development Commands
- `npm run sp:init` (alias for `npx -y @cdw0424/super-prompt@latest super:init`) bootstraps local assets.
- `npm run sp:mcp` (alias for `npx --yes --package=@cdw0424/super-prompt sp-mcp`) starts the MCP server for Cursor or Codex.
- `scripts/codex/router-check.sh` validates routing rules before publishing.
- `scripts/codex/prompt-qa.sh <transcript>` performs prompt QA on saved conversation logs.

## Coding Style & Naming Conventions
- Use 2-space indent for JavaScript/JSON, 4-space indent for Python.
- Prefer descriptive snake_case in Python, kebab-case for CLI entrypoints, and keep prompts/docs in English only.
- Mask any secrets in output (e.g., `sk-***`) and start custom logs with `--------`.

## Testing Guidelines
- Favor Jest integration tests (`*.int.test.js`) for CLI features; add focused smoke tests when full coverage is costly.
- Store sample transcripts under `docs/examples/` and validate prompts with `prompt-qa.sh` before merging.
- Run `npm test` when JavaScript changes impact runtime behavior.

## Commit & Pull Request Guidelines
- Follow Conventional Commits such as `feat(cli): add persona loader` or `fix: handle mcp timeout`.
- PRs must include a concise summary, rationale, relevant screenshots for UX changes, and verification steps (e.g., commands run).
- Keep diffs minimal and avoid unrelated refactors in the same change set.

## Agent-Specific Instructions
- Auto Model Router (AMR) enforces medium ↔ high switching: start in medium, escalate to high for planning, reviews, or deep root-cause, then drop back to medium for execution.
- Respect SSOT precedence order `personas manifest → .cursor/rules → AGENTS.md`; prefer toggle-based overrides instead of ad-hoc edits.
- `/gpt-mode-on` and `/grok-mode-on` are mutually exclusive—activate only one mode per session.
