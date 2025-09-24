# Repository Guidelines

## Project Structure & Module Organization
CLI entry points live in `bin/super-prompt` and `bin/sp-mcp`. JavaScript orchestration resides under `src/`, with integration tests in `src/**/__tests__`. Python MCP core modules sit in `packages/core-py/super_prompt/` and ship via `python-packages/super-prompt-core/`. Cursor assets are curated in `.cursor/commands/super-prompt/` and `.cursor/rules/`. Personas rely on `packages/cursor-assets/manifests/personas.yaml`; place experimental overrides in `personas/manifest.yaml`. Documentation lives in `docs/`, templates in `templates/`, and integration specs in `specs/`.

## Build, Test, and Development Commands
Run `npm run sp:init` to sync Cursor assets and AMR rules. Use `npm run sp:mcp` or `python -m super_prompt.mcp_client` to launch the MCP server. Start the CLI locally with `npm run dev`, or prepare local scaffolding via `npm run dev:init`. Execute `npm test` for the Node suite and `npm run sp:verify:all` to lint SSOT state. Target Python coverage with `python -m pytest packages/core-py`.

## Coding Style & Naming Conventions
JavaScript and JSON files use 2-space indentation; Python modules use 4 spaces. Prefer camelCase for JS internals, snake_case for Python, and kebab-case for executables. Mask credentials as `sk-***` in logs. Rely on repository linters via `npm run sp:verify:all`, and keep prompts and docs in English only.

## Testing Guidelines
Favor behaviour-driven Node tests under `src/**/__tests__/*.int.test.js`. Extend `test_mcp.py` or colocate Python tests beside the modules they cover. Store prompt transcripts in `docs/examples/` and validate prompt changes with `./prompt-qa.sh`. Always run `npm test` plus relevant `python -m pytest` targets before opening a PR.

## Commit & Pull Request Guidelines
Follow Conventional Commits (e.g., `feat(cli): add persona loader`, `fix: handle mcp timeout`). Keep each PR focused, summarize rationale, list verification commands, and attach Cursor screenshots for UX updates. Link issues when possible and avoid sweeping refactors alongside feature work.

## Agent-Specific Workflow
Start in medium mode and escalate to high only for planning, reviews, or deep debugging, then return to medium for execution. Respect configuration precedence: personas manifest → `.cursor/rules` → this guide. Activate a single mode toggle (`/gpt-mode-on`, `/grok-mode-on`, or `/claude-mode-on`) per session, and only enable `/super-prompt/high-mode-on` when high reasoning is essential.
