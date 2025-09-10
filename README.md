# Super Prompt (Cursor‑first)

[![npm version](https://img.shields.io/npm/v/%40cdw0424%2Fsuper-prompt?logo=npm)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![npm downloads](https://img.shields.io/npm/dm/%40cdw0424%2Fsuper-prompt?logo=npm)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Quick install (scoped package):
```bash
npm i -g @cdw0424/super-prompt
# or just use npx
npx @cdw0424/super-prompt --help
```

Cursor‑first Prompt Engineering toolkit with Spec‑Driven Development assist. Super Prompt generates `.cursor/rules/*.mdc` from your SPEC/PLAN, installs slash commands under `.cursor/commands/super-prompt`, and lets specialized personas help you craft precise prompts inside Cursor.

Note: Super Prompt targets Cursor as the primary environment. Non‑Cursor editors are not supported beyond generating rule files.

## Credits & Attribution

This project is a reconstruction that references and integrates ideas from various open‑source tools and community snippets. In particular, it draws inspiration from:
- speckit
- superclaude

We greatly appreciate the open‑source community. If you are a maintainer of a referenced project and would like additional attribution or adjustments, please open an issue.

## Features

- 🎯 **Cursor integration**: rules under `.cursor/rules` + slash commands
- 🚀 **SDD assist**: generate lightweight rules from `specs/**/spec.md` and `specs/**/plan.md`
- 🎭 **Enhanced Personas**: SuperClaude framework integration with specialized AI personalities
- 🌊 **Wave System**: Multi-stage execution for complex operations (complexity ≥0.7)
- 🔗 **MCP Integration**: Context7, Sequential, Magic, Playwright server coordination
- ⚡ **Token Efficiency**: Intelligent compression (30-50% reduction) with quality preservation
- 📋 **Task Management**: Structured workflow execution with progress tracking
- 🧰 **CLI tools**: rule generation (`super:init`) and persona‑assisted prompting (`optimize`)
- 📋 **SDD Workflow**: complete SPEC → PLAN → TASKS → Implementation workflow via slash commands

## Cursor Quick Start

1) Install
```bash
npm install -g @cdw0424/super-prompt
```

2) Initialize in your project (sets up rules + Cursor slash commands)
```bash
super-prompt super:init
```

3) Use inside Cursor
- Open Cursor; rules from `.cursor/rules/*.mdc` are applied.
- In the prompt, use slash tags installed under `.cursor/commands/super-prompt/`:
  - **Core Personas**: `/frontend`, `/frontend-ultra`, `/backend`, `/analyzer`, `/architect`, `/high`, `/seq`, `/seq-ultra`, `/debate`
  - **Enhanced Personas**: `/security`, `/performance`, `/wave`, `/task`, `/ultracompressed`
  - **SDD Workflow**: `/spec`, `/plan`, `/tasks`, `/implement`

4) Run persona‑assisted prompts from the CLI (optional)
```bash
# Persona commands
npx @cdw0424/super-prompt optimize "design strategy /frontend"
npx @cdw0424/super-prompt optimize "debug intermittent failures /analyzer"

# Debate mode (requires `codex` CLI)
npx @cdw0424/super-prompt optimize "Choose DB schema migration approach /debate --rounds 12"

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
- `optimize "<query with /tag>"` — Execute a persona‑assisted prompt from the terminal

### SDD Workflow 
- `sdd spec "<description>"` — Create or edit SPEC files with architect persona
- `sdd plan "<description>"` — Create or edit PLAN files with architect persona  
- `sdd tasks "<description>"` — Break down plans into actionable tasks with analyzer persona
- `sdd implement "<description>"` — Start implementation with SDD compliance checking

## Available Slash Commands

### Core Persona Commands
- `/frontend` — Frontend design advisor (UX-focused, MCP: Magic + Playwright)
- `/frontend-ultra` — Elite UX/UI architect (top-tier design, WCAG 2.2 AAA)
- `/backend` — Backend reliability engineer (99.9% uptime, MCP: Context7 + Sequential)
- `/analyzer` — Root cause analyst (evidence-based, MCP: Sequential + Context7)
- `/architect` — Systems architecture specialist (long-term focus, MCP: Sequential + Context7)
- `/high` — Deep reasoning specialist (strategic thinking, MCP: Sequential + Context7)
- `/seq` — Sequential thinking (5 iterations, structured reasoning)
- `/seq-ultra` — Advanced sequential thinking (10 iterations, comprehensive analysis)

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

## Generated Files

- Rules: `.cursor/rules/00-organization.mdc`, `10-sdd-core.mdc`, `20-frontend.mdc`, `30-backend.mdc`
- Commands: `.cursor/commands/super-prompt/tag-executor.sh` and multiple `.md` entries

## Requirements

- macOS or Linux
- Node.js ≥ 14
- Python ≥ 3.7
 - Codex CLI (auto-upgraded): the tool attempts `npm install -g @openai/codex@latest` during install/run

## Troubleshooting

- “Python CLI not found” after install → re‑run `npm install` or `node install.js`
- Python < 3.7 → install Python ≥ 3.7 and ensure `python3` points to it
- Slash commands not visible → check `.cursor/commands/super-prompt/` exists and files are executable (`chmod 755`), restart Cursor
- Translation/backends (optional) → if you use external CLIs (`claude`, `codex`), ensure they’re on PATH and configured

## Roadmap (later)

- Expand execution paths that use Anthropic Claude and Codex CLIs
- Improve artifact capture and result injection back into rules/docs

## License

MIT
