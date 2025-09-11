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

**🚀 New in v2.6.0:** Full SDD (Spec-Driven Development) workflow now available in Codex CLI alongside Cursor support. Complete SPEC→PLAN→TASKS→IMPLEMENT workflow for both IDEs.

Prompt Engineering toolkit supporting both Cursor and Codex CLI with Spec‑Driven Development assist. Super Prompt generates `.cursor/rules/*.mdc` from your SPEC/PLAN, installs slash commands for Cursor, and provides flag‑based personas for Codex CLI - giving you flexibility to work with either IDE seamlessly.

**Dual IDE Support**: Works seamlessly with both Cursor (slash commands) and Codex CLI (flag-based personas).

## Credits & Attribution

This project is a reconstruction that references and integrates ideas from various open‑source tools and community snippets. In particular, it draws inspiration from:
- speckit
- superclaude

We greatly appreciate the open‑source community. If you are a maintainer of a referenced project and would like additional attribution or adjustments, please open an issue.

## Features

- 🎯 **Dual IDE Support**: Cursor slash commands + Codex CLI flag-based personas
- 🧠 **AMR**: Auto Model Router (reasoning medium ↔ high) with fixed state machine (INTENT→CLASSIFY→PLAN→EXECUTE→VERIFY→REPORT)
- 🚀 **SDD assist**: generate lightweight rules from `specs/**/spec.md` and `specs/**/plan.md`
- 🎭 **Personas**: Specialized AI personalities (`--frontend`, `--backend`, `--architect`, etc.)
- 🗣️ **Debate (single‑model)**: Positive vs Critical self with structured alternation and synthesis
- 🧰 **CLI tools**: rule generation (`super:init`), persona prompting (`optimize`), AMR scaffold/print (`codex-amr`)

## Quick Start

1) Install
```bash
npm install -g @cdw0424/super-prompt
```

2) Initialize in your project (sets up rules + Cursor slash commands)
```bash
super-prompt super:init
```
 - During init you will be asked to extend Codex CLI integration; answering Yes creates `.codex/` with `agent.md` and `personas.py`. Non‑interactive opt‑in: `SUPER_PROMPT_INIT_CODEX=1 super-prompt super:init`.

3) Use with your preferred IDE

**In Cursor:**
- Open Cursor; rules from `.cursor/rules/*.mdc` are applied.
- Use slash commands in your prompt:
  - **Core Personas**: `/frontend`, `/frontend-ultra`, `/backend`, `/analyzer`, `/architect`, `/high`, `/seq`, `/seq-ultra`, `/debate`
  - **Enhanced Personas**: `/security`, `/performance`, `/wave`, `/task`, `/ultracompressed`
  - **SDD Workflow**: `/spec`, `/plan`, `/tasks`, `/implement`

**In Codex CLI:**
```bash
# Simplified persona flags with --sp-* prefix (recommended)
npx @cdw0424/super-prompt optimize --sp-frontend "Design strategy"
npx @cdw0424/super-prompt optimize --sp-analyzer "Debug intermittent failures"
npx @cdw0424/super-prompt optimize --sp-backend "API design patterns"
npx @cdw0424/super-prompt optimize --sp-architect "System architecture review"

# Original flag syntax (still supported)
npx @cdw0424/super-prompt optimize --frontend "Design strategy"
npx @cdw0424/super-prompt optimize --analyzer "Debug intermittent failures"

# Single‑model debate (internal Positive vs Critical selves)
npx @cdw0424/super-prompt optimize --sp-debate --rounds 8 "Choose DB schema migration approach"
npx @cdw0424/super-prompt optimize --sp-debate --rounds 5 "TypeScript vs JavaScript for our project"

# SDD workflow commands - simplified flag syntax
npx @cdw0424/super-prompt optimize --sp-sdd-spec "user authentication system"
npx @cdw0424/super-prompt optimize --sp-sdd-plan "API endpoints design"
npx @cdw0424/super-prompt optimize --sp-sdd-tasks "break down into development tasks"
npx @cdw0424/super-prompt optimize --sp-sdd-implement "login functionality"
```

## Commands

### 🆕 Simplified Command Syntax (v2.7.0+)

Super Prompt now offers streamlined `--sp-*` flags for both personas and SDD workflows, making commands cleaner and more intuitive:

**Benefits of --sp-* syntax:**
- **Shorter commands**: `--sp-frontend` vs `--frontend`
- **Consistent naming**: All Super Prompt flags use the same `--sp-` prefix
- **Future-proof**: New features will follow this pattern
- **Backward compatible**: Original flags still work

**Quick Comparison:**
```bash
# New simplified syntax (recommended)
super-prompt optimize --sp-frontend "Create responsive UI"
super-prompt optimize --sp-sdd-spec "user authentication"

# Original syntax (still supported)
super-prompt optimize --frontend "Create responsive UI"
super-prompt sdd spec "user authentication"
```

**All available --sp-* flags:**
- **Personas**: `--sp-frontend`, `--sp-backend`, `--sp-analyzer`, `--sp-architect`, `--sp-high`, `--sp-seq`, `--sp-seq-ultra`, `--sp-debate`, `--sp-performance`, `--sp-security`, `--sp-task`, `--sp-wave`, `--sp-ultracompressed`
- **SDD Workflow**: `--sp-sdd-spec`, `--sp-sdd-plan`, `--sp-sdd-tasks`, `--sp-sdd-implement`

### Core Setup
- `super:init` — Generate SDD rule files under `.cursor/rules/`
  - Options: `--out <dir>` (default `.cursor/rules`), `--dry-run`

### Persona System
- `optimize "<query> [--persona|--frontend|--backend|--architect|--analyzer|--high|--seq|--seq-ultra|--debate]"` — Execute a persona‑assisted prompt (flags for Codex)
- **New**: Simplified syntax with `--sp-*` prefix for cleaner commands (recommended)

### SDD Workflow (Available in both Cursor and Codex CLI)
**Cursor (slash commands):**
- `/spec "<description>"` — Create or edit SPEC files with architect persona
- `/plan "<description>"` — Create or edit PLAN files with architect persona  
- `/tasks "<description>"` — Break down plans into actionable tasks with analyzer persona
- `/implement "<description>"` — Start implementation with SDD compliance checking

**Codex CLI (simplified flags):**
- `optimize --sp-sdd-spec "<description>"` — Create or edit SPEC files
- `optimize --sp-sdd-plan "<description>"` — Create or edit PLAN files
- `optimize --sp-sdd-tasks "<description>"` — Break down plans into tasks  
- `optimize --sp-sdd-implement "<description>"` — Start implementation

**Example SDD Workflow (Codex CLI simplified syntax):**
```bash
# 1. Create specification
super-prompt optimize --sp-sdd-spec "user authentication system"

# 2. Design implementation plan
super-prompt optimize --sp-sdd-plan "OAuth2 + JWT authentication"

# 3. Break down into tasks
super-prompt optimize --sp-sdd-tasks "authentication implementation"

# 4. Get implementation guidance
super-prompt optimize --sp-sdd-implement "start authentication development" --validate
```

## Available Commands

### Core Persona Commands

**Cursor (slash commands):**
- `/frontend` — Frontend design advisor (UX-focused)
- `/frontend-ultra` — Elite UX/UI architect (top-tier design)
- `/backend` — Backend reliability engineer (99.9% uptime)
- `/analyzer` — Root cause analyst (evidence-based)
- `/architect` — Systems architecture specialist
- `/high` — Deep reasoning specialist (strategic thinking)
- `/seq` — Sequential thinking (5 iterations)
- `/seq-ultra` — Advanced sequential thinking (10 iterations)
- `/debate` — AI vs AI debate system

**Codex CLI (simplified --sp-* flags, recommended):**
- `--sp-frontend` — Frontend design advisor
- `--sp-frontend-ultra` — Elite UX/UI architect
- `--sp-backend` — Backend reliability engineer
- `--sp-analyzer` — Root cause analyst
- `--sp-architect` — Systems architecture specialist
- `--sp-high` — Deep reasoning specialist
- `--sp-seq` — Sequential thinking (5 iterations)
- `--sp-seq-ultra` — Advanced sequential (10 iterations)
- `--sp-debate` — Single-model internal debate
- `--sp-performance` — Optimization & bottleneck elimination
- `--sp-security` — Threat modeling & vulnerability assessment
- `--sp-task` — Task management & workflow execution
- `--sp-wave` — Multi-stage execution orchestration
- `--sp-ultracompressed` — Token efficiency (30-50% reduction)

**Codex CLI (original flags, still supported):**
- `--frontend`, `--backend`, `--analyzer`, `--architect`, `--high`, `--seq`, `--seq-ultra`
- `--debate`, `--performance`, `--security`, `--task`, `--wave`, `--ultracompressed`

### Enhanced Personas (Cursor only)
- `/security` — Threat modeler & vulnerability specialist
- `/performance` — Optimization specialist (metrics-driven)
- `/wave` — Wave system orchestrator (multi-stage execution)
- `/task` — Task management mode (structured workflow)
- `/ultracompressed` — Token efficiency mode (30-50% reduction)

### SDD Workflow Commands (Cursor slash commands)
- `/spec` — Create detailed specifications for features and requirements
- `/plan` — Design implementation plans based on specifications
- `/tasks` — Break down plans into actionable development tasks  
- `/implement` — Start implementation with SDD compliance checking

**Note**: SDD workflow is also available in Codex CLI using the `sdd` command (see examples above)

Add your own personas in `.cursor/commands/super-prompt/**/*.{md,mdc,py}`. Markdown with front‑matter and Python files with leading docstrings are recognized.

## SDD Workflow

Super Prompt includes a complete Spec-Driven Development workflow available in **both Cursor and Codex CLI**:

### 🎯 SDD Methodology

**Spec-Driven Development** ensures you build the right thing, the right way, at the right time by following a structured approach:

1. **SPEC** — Define WHAT to build (Requirements & Success Criteria)
2. **PLAN** — Define HOW to build it (Architecture & Implementation Strategy)
3. **TASKS** — Define the STEPS (Actionable Development Tasks)
4. **IMPLEMENT** — Build it with confidence (Guided Implementation)

### 📋 SDD Commands

**In Cursor** (slash commands):
- `/spec` — Create detailed specifications
- `/plan` — Design implementation plans  
- `/tasks` — Break down into tasks
- `/implement` — Start implementation

**In Codex CLI** (simplified flag commands):
```bash
# Complete SDD workflow
super-prompt optimize --sp-sdd-spec "user authentication system"
super-prompt optimize --sp-sdd-plan "OAuth2 + JWT implementation"  
super-prompt optimize --sp-sdd-tasks "break down auth tasks"
super-prompt optimize --sp-sdd-implement "start development" --validate
```

### 🔄 SDD Workflow Example

```bash
# 1. SPEC: Define requirements
super-prompt optimize --sp-sdd-spec "real-time chat system with file sharing"
# → Creates comprehensive specification document
# → Defines user stories, success criteria, constraints

# 2. PLAN: Design architecture  
super-prompt optimize --sp-sdd-plan "WebSocket-based chat with S3 file storage"
# → Creates technical implementation plan
# → Defines architecture, data design, security approach

# 3. TASKS: Break down work
super-prompt optimize --sp-sdd-tasks "implement chat system components" 
# → Creates actionable task list with priorities
# → Includes estimates, dependencies, acceptance criteria

# 4. IMPLEMENT: Build with guidance
super-prompt optimize --sp-sdd-implement "start chat backend development" --validate
# → Provides implementation guidance
# → Validates compliance with SPEC and PLAN
```

### 🎯 SDD Benefits

- **Clarity**: Everyone knows what's being built and why
- **Quality**: Architecture decisions made upfront
- **Efficiency**: Reduced rework and scope creep
- **Collaboration**: Clear handoffs between team members
- **Compliance**: Built-in validation and quality gates

Each step builds on the previous one, with automatic context sharing between phases and intelligent validation.

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
- Python CLI: `.super-prompt/utils/cli.py` — flag personas, single‑model debate, project SDD helpers
- Cursor Processors: `.super-prompt/utils/cursor-processors/` — specialized Cursor command processors
- Codex Agent: `.codex/AGENTS.md` + `.super-prompt/utils/personas.py` — Codex‑specific guidance & builders

### New Modular Structure
- **`.super-prompt/utils/`**: Centralized Python utilities for better maintainability
  - `cli.py`: Main CLI implementation with all personas and SDD workflows
  - `personas.py`: Codex-specific persona helpers and debate builders
  - `cursor-processors/`: Specialized processors for Cursor slash commands
  - `templates/`: Template files for code generation

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
