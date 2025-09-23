# Repository Guidelines

## Project Structure & Module Organization
The CLI entry points live in `bin/super-prompt` and `bin/sp-mcp`, with `package.json` owning metadata and script wiring. JavaScript orchestration code sits under `src/`, while Python MCP core modules live in `packages/core-py/super_prompt/` and ship via `python-packages/super-prompt-core/`. Cursor assets are curated in `.cursor/commands/super-prompt/` and `.cursor/rules/`. Personas rely on `packages/cursor-assets/manifests/personas.yaml` as the source of truth; create local overrides under `personas/manifest.yaml` when experimenting. Documentation stays in `docs/`, templates in `templates/`, and integration specs in `specs/`.

## Build, Test, and Development Commands
Run `npm run sp:init` to bootstrap Cursor assets and sync AMR rules. Use `npm run sp:mcp` (or `python -m super_prompt.mcp_client`) to start the MCP server for Cursor. `npm test` executes the Node test suite via `node --test`; pair it with `npm run sp:verify:all` to lint SSOT state and ensure the build passes. Launch the CLI locally with `npm run dev` or execute targeted setup with `npm run dev:init`.

## Coding Style & Naming Conventions
Format JavaScript and JSON with 2-space indentation; Python modules use 4 spaces. Prefer snake_case in Python, camelCase for internal JavaScript variables, and kebab-case for executables (for example `bin/sp-mcp`). Keep documentation and prompts in English only. Always mask credentials in logs as `sk-***`, and prefix custom diagnostic output with `--------` to keep AMR parsing predictable.

## Testing Guidelines
Favour behaviour-driven integration coverage using native Node test files (e.g. `src/**/__tests__/*.int.test.js`). Place prompt transcripts in `docs/examples/` and validate changes with `./prompt-qa.sh` before merging. For Python surfaces, extend `test_mcp.py` or add tests beside the relevant module. Run `npm test` plus targeted `python -m pytest` invocations when Python behaviour changes.

## Commit & Pull Request Guidelines
Adopt Conventional Commits such as `feat(cli): add persona loader` or `fix: handle mcp timeout`. Each PR should include a concise summary, rationale, any Cursor screenshots for UX updates, and the commands used for verification. Keep diffs focused on a single concern and avoid sweeping refactors in the same review.

## Agent-Specific Workflow
Follow Auto Model Router policy: begin in medium mode, escalate to high for planning, reviews, or deep debugging, then revert to medium for execution. Honour config precedence `personas manifest → .cursor/rules → AGENTS.md`, preferring toggle-based overrides over ad-hoc edits. Activate only one of `/gpt-mode-on` or `/grok-mode-on` per session to keep agent routing predictable. Enable Codex-backed high reasoning only when necessary via `/super-prompt/high-mode-on`; otherwise leave it off with `/super-prompt/high-mode-off`—direct `/high` or `/sp_high` invocations always force Codex regardless of the toggle.
