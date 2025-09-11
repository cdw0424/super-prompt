# Super Prompt (Cursor, Codex CLI)

[![npm version](https://img.shields.io/npm/v/%40cdw0424%2Fsuper-prompt?logo=npm)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![npm downloads](https://img.shields.io/npm/dm/%40cdw0424%2Fsuper-prompt?logo=npm)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Quick install (scoped package):
```bash
npm i -g @cdw0424/super-prompt
# or just use npx
npx @cdw0424/super-prompt --help
```

Prompt Engineering toolkit for Cursor and Codex CLI with Spec‑Driven Development assist. Super Prompt generates `.cursor/rules/*.mdc` from your SPEC/PLAN, installs slash commands under `.cursor/commands/super-prompt` (Cursor), and lets specialized personas help you craft precise prompts inside Cursor or via flag‑based personas in Codex.

Note: Super Prompt targets Cursor and Codex CLI. For Codex, use flag‑based personas (no slash commands).

## Credits & Attribution

This project is a reconstruction that references and integrates ideas from various open‑source tools and community snippets. In particular, it draws inspiration from:
- speckit
- superclaude

We greatly appreciate the open‑source community. If you are a maintainer of a referenced project and would like additional attribution or adjustments, please open an issue.

## Features

- 🎯 **Cursor integration**: rules under `.cursor/rules` + slash commands (Cursor)
- 🧠 **AMR**: Auto Model Router (reasoning medium ↔ high) with fixed state machine (INTENT→CLASSIFY→PLAN→EXECUTE→VERIFY→REPORT)
- 🚀 **SDD assist**: generate lightweight rules from `specs/**/spec.md` and `specs/**/plan.md`
- 🎭 **Personas**: Flag‑based personas for Codex (`--frontend`, `--backend`, `--architect`, etc.)
- 🗣️ **Debate (single‑model)**: Positive vs Critical self with structured alternation and synthesis
- 🧰 **CLI tools**: rule generation (`super:init`), persona prompting (`optimize`), AMR scaffold/print (`codex-amr`)

## Cursor Quick Start

1) Install
```bash
npm install -g @cdw0424/super-prompt
```

2) Initialize in your project (sets up rules + Cursor slash commands)
```bash
super-prompt super:init
```
 - During init you will be asked to extend Codex CLI integration; answering Yes creates `.codex/` with `agent.md` and `personas.py`. Non‑interactive opt‑in: `SUPER_PROMPT_INIT_CODEX=1 super-prompt super:init`.

3) Use inside Cursor
- Open Cursor; rules from `.cursor/rules/*.mdc` are applied.
- In the prompt, use slash tags installed under `.cursor/commands/super-prompt/`:
  - **Core Personas**: `/frontend`, `/frontend-ultra`, `/backend`, `/analyzer`, `/architect`, `/high`, `/seq`, `/seq-ultra`, `/debate`
  - **Enhanced Personas**: `/security`, `/performance`, `/wave`, `/task`, `/ultracompressed`
  - **SDD Workflow**: `/spec`, `/plan`, `/tasks`, `/implement`

4) Run persona‑assisted prompts from the CLI (Codex‑friendly flags)
```bash
# Persona commands (flags; no slash tags needed)
npx @cdw0424/super-prompt optimize --frontend "Design strategy"
npx @cdw0424/super-prompt optimize --analyzer "Debug intermittent failures"

# Single‑model debate (Codex; internal Positive vs Critical selves)
npx @cdw0424/super-prompt optimize --debate --rounds 8 "Choose DB schema migration approach"
npx @cdw0424/super-prompt optimize --debate --rounds 5 "TypeScript vs JavaScript for our project"

# SDD workflow commands
npx @cdw0424/super-prompt sdd spec "user authentication system"
npx @cdw0424/super-prompt sdd plan "API endpoints design"
npx @cdw0424/super-prompt sdd tasks "break down into development tasks"
npx @cdw0424/super-prompt sdd implement "login functionality"
```

## Commands

### Core Setup
- `super:init` — Generate SDD rule files under `.cursor/rules/`
  - Options: `--out <dir>` (default `.cursor/rules`), `--dry-run`

### Persona System
- `optimize "<query> [--persona|--frontend|--backend|--architect|--analyzer|--high|--seq|--seq-ultra|--debate]"` — Execute a persona‑assisted prompt (flags for Codex)

### SDD Workflow 
- `sdd spec "<description>"` — Create or edit SPEC files with architect persona
- `sdd plan "<description>"` — Create or edit PLAN files with architect persona  
- `sdd tasks "<description>"` — Break down plans into actionable tasks with analyzer persona
- `sdd implement "<description>"` — Start implementation with SDD compliance checking

## Available Slash Commands (Cursor only)

### Core Persona Commands
- `/frontend` — Frontend design advisor (UX-focused, MCP: Magic + Playwright)
- `/frontend-ultra` — Elite UX/UI architect (top-tier design, WCAG 2.2 AAA)
- `/backend` — Backend reliability engineer (99.9% uptime, MCP: Context7 + Sequential)
- `/analyzer` — Root cause analyst (evidence-based, MCP: Sequential + Context7)
- `/architect` — Systems architecture specialist (long-term focus, MCP: Sequential + Context7)
- `/high` — Deep reasoning specialist (strategic thinking, MCP: Sequential + Context7)
- `/seq` — Sequential thinking (5 iterations, structured reasoning)
- `/seq-ultra` — Advanced sequential thinking (10 iterations, comprehensive analysis)
- `/debate` — Enhanced AI vs AI debate system (Current Cursor model ↔ Codex with `model_reasoning_effort=high`)

### Enhanced SuperClaude Personas
- `/security` — Threat modeler & vulnerability specialist (zero trust, defense in depth)
- `/performance` — Optimization specialist (metrics-driven, MCP: Playwright + Sequential)
- `/wave` — Wave system orchestrator (multi-stage execution, compound intelligence)
- `/task` — Task management mode (structured workflow, progress tracking)
- `/ultracompressed` — Token efficiency mode (30-50% reduction, quality preservation)

### SDD Workflow Commands
- `/spec` — Create detailed specifications for features and requirements
- `/plan` — Design implementation plans based on specifications
- `/tasks` — Break down plans into actionable development tasks  
- `/implement` — Start implementation with SDD compliance checking

Add your own personas in `.cursor/commands/super-prompt/**/*.{md,mdc,py}`. Markdown with front‑matter and Python files with leading docstrings are recognized.

## SDD Workflow

Super Prompt includes a complete Spec-Driven Development workflow:

1. **SPEC** (`/spec`) — Define what you're building
   - Problem statement and goals
   - Success criteria and constraints
   - System overview and components

2. **PLAN** (`/plan`) — Design how you'll build it  
   - Technical architecture
   - Implementation approach
   - Dependencies and risks

3. **TASKS** (`/tasks`) — Break it down
   - Actionable development tasks
   - Priority and dependencies
   - Acceptance criteria

4. **IMPLEMENT** (`/implement`) — Build it
   - SDD compliance checking
   - Framework-aware implementation
   - Best practice guidance

Each step builds on the previous one, with automatic context sharing between phases.

## Debate (Single‑Model, Codex)

A structured internal debate that alternates between two selves and ends with a synthesis:

- Positive Self (Builder): constructive, solution‑oriented
- Critical Self (Skeptic): risk‑focused, assumption testing

Usage
```bash
super-prompt optimize --debate --rounds 8 "Should we use microservices or a modular monolith?"
```

Flow
1) Alternate Positive → Critical for N rounds; 2) keep sections: [INTENT][TASK_CLASSIFY][PLAN][EXECUTE][VERIFY][REPORT]; 3) finish with a concise synthesis and next steps.

## Generated Files

- Rules: `.cursor/rules/00-organization.mdc`, `10-sdd-core.mdc`, `20-frontend.mdc`, `30-backend.mdc`
- Commands: `.cursor/commands/super-prompt/tag-executor.sh` and multiple `.md` entries

## Requirements

- macOS or Linux
- Node.js ≥ 14
- Python ≥ 3.7
- Codex CLI (optional): install/upgrade choice at install time. To auto‑install non‑interactively: `SUPER_PROMPT_CODEX_INSTALL=1 npm i -g @cdw0424/super-prompt`
- Tests: `npm test` (Node’s built‑in `node --test`)

## Troubleshooting

- “Python CLI not found” after install → re‑run `npm install` or `node install.js`
- Python < 3.7 → install Python ≥ 3.7 and ensure `python3` points to it
- Slash commands not visible (Cursor) → ensure `.cursor/commands/super-prompt/` exists, files executable (`chmod 755`), restart Cursor

## Codex AMR (medium ↔ high)

This repo includes an Auto Model Router (AMR) and a strict state‑machine bootstrap prompt to improve instruction adherence and output consistency.

Quick start
- TUI boot:
  ```bash
  codex
  # Paste the bootstrap prompt:
  # prompts/codex_amr_bootstrap_prompt_en.txt
  ```
- Wrappers:
  ```bash
  ./bin/codex-high   "Design migration plan (no edits; PLAN only)"
  ./bin/codex-medium "Apply approved plan and run tests"
  ```
- Node scripts:
  ```bash
  npm run codex:plan
  npm run codex:exec
  ```

codex-amr CLI
```bash
# Print bootstrap prompt
npx codex-amr print-bootstrap
# Scaffold AMR assets (AGENTS.md, prompt, wrappers, router-check)
npx codex-amr init --target .
```

AMR utilities
- Generate Cursor AMR rule: `npm run amr:rules` → writes `.cursor/rules/05-amr.mdc`
- Print bootstrap prompt: `npm run amr:print` (copy to Codex TUI)
- Validate a transcript: `npm run amr:qa -- path/to/transcript.txt`

Router switching
- If the environment does not auto‑execute the following lines, copy‑run them in the TUI:
  ```
  /model gpt-5 high
  /model gpt-5 medium
  ```

Validate the router assets
```bash
--------run: scripts/codex/router-check.sh
# Expect: "--------router-check: OK"
```

Read more
- Policy and rules: `AGENTS.md`
- Usage details: `docs/codex-amr-usage.md`
- Translation/backends (optional) → if you use external CLIs (`claude`, `codex`), ensure they’re on PATH and configured
 - AMR internals and CLI: `docs/codex-amr.md`

## Codex CLI Setup & Usage

### Setup (create .codex assets)
Pick one of the following:
- Super Prompt init (asks interactively):
  ```bash
  super-prompt super:init
  # Answer Y to: Extend Codex CLI integration now (.codex assets)? [Y/n]
  ```
- Non‑interactive opt‑in:
  ```bash
  SUPER_PROMPT_INIT_CODEX=1 super-prompt super:init
  ```
- Codex‑only quick setup (no Cursor files):
  ```bash
  super-prompt codex:init
  # or
  npx codex-amr init           # defaults to .codex
  ```

This creates `.codex/agents.md`, `.codex/personas.py`, `.codex/bootstrap_prompt_en.txt`, and `.codex/router-check.sh`.

### Using with Codex TUI
1) Open Codex:
```bash
codex
```
2) Paste the bootstrap prompt from `.codex/bootstrap_prompt_en.txt` (or print it: `npx codex-amr print-bootstrap`).
3) Run your workflow; when using the Super Prompt CLI alongside Codex, prefer flag‑based personas:
```bash
super-prompt optimize --frontend "Design a responsive layout"
super-prompt optimize --backend  "Retry + idempotency strategy"
super-prompt optimize --debate --rounds 8 "Feature flags now?"
```
4) Router switches (if not auto‑executed by your environment), copy‑run in TUI:
```
/model gpt-5 high
/model gpt-5 medium
```

## Architecture & Why It Performs Well

### Component Map
- Router: `src/amr/router.js` — classifies tasks (L0/L1/H) and advises medium↔high switches
- State Machine: `src/state-machine/index.js` — fixed loop (INTENT→CLASSIFY→PLAN→EXECUTE→VERIFY→REPORT)
- Bootstrap Prompt: `src/prompts/codexAmrBootstrap.en.js` — AMR‑aware TUI starter
- Scaffold: `src/scaffold/codexAmr.js` — one‑shot bootstrap into a repo
- Python CLI: `scripts/super_prompt/cli.py` — flag personas, single‑model debate, project SDD helpers
- Codex Agent: `.codex/agents.md` + `.codex/personas.py` — Codex‑specific guidance & builders

### Mechanisms → Effects → Performance
- Fixed Loop (structured decoding)
  - Mechanism: always follow INTENT→CLASSIFY→PLAN→EXECUTE→VERIFY→REPORT
  - Effect: smaller search space; consistent turn shape; easy verification
  - Result: lower variance, higher instruction adherence
- AMR (medium↔high with explicit switching)
  - Mechanism: heavy tasks plan at high reasoning; execution at medium
  - Effect: deep planning where needed; faster/cheaper execution otherwise
  - Result: better plans without runaway verbosity
- Language & Persona Closure
  - Mechanism: English‑only, fixed tone, flag personas; logs prefixed with `--------`
  - Effect: stylistic stability; easy log parsing in scripts/CI
  - Result: repeatable outputs, fewer formatting failures
- Memory Hygiene
  - Mechanism: repo facts vs. per‑turn discoveries kept explicit (rules + transcripts)
  - Effect: reduced hallucination; easier auditability and rollbacks
  - Result: long‑run consistency and safer automation
- Templates & Guards
  - Mechanism: minimal diffs; mandatory commands; router checks; prompt QA
  - Effect: deterministic patches; quick CI validation; predictable UX
  - Result: faster iteration and fewer regressions

## Roadmap (later)

- Expand execution paths that use Anthropic Claude and Codex CLIs
- Improve artifact capture and result injection back into rules/docs

## License

MIT
