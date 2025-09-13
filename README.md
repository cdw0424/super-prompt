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

**🚀 New in v2.9.29:** Performance Optimization - Fixed infinite git output in analyzer
command by optimizing `_get_project_files()` function. Added .gitignore pattern filtering,
excluded large directories (.git, node_modules, .npm-cache), and reduced file scanning limits.

**🚀 New in v2.9.28:** NPM Cache Git Loop Fix - Automated diagnostic and repair
system for npm cache misconfiguration that causes infinite git analysis loops.
Includes `npm-cache-fix.sh` script and enhanced installation warnings.

**🚀 New in v2.9.25:** Enhanced CLI experience with optional `optimize` command,
improved Cursor usage documentation, and refined command consistency across all
interfaces.

**🚀 New in v2.9.0:** Context Engineering System - Spec Kit implementation for
conversation context preservation, stage gating workflow, and intelligent
context injection with 30-50% token optimization.

**🚀 New in v2.8.0:** Added TODO Auto-Validation System with intelligent
high-mode retry for failed tasks, ensuring reliable completion and automatic
error recovery.

Prompt Engineering toolkit supporting both Cursor and Codex CLI with Spec‑Driven
Development assist. Super Prompt generates `.cursor/rules/*.mdc` from your
SPEC/PLAN, installs slash commands for Cursor, and provides flag‑based personas
for Codex CLI - giving you flexibility to work with either IDE seamlessly.

**Dual IDE Support**: Works seamlessly with both Cursor (slash commands) and
Codex CLI (flag-based personas).

## Credits & Attribution

This project is a reconstruction that references and integrates ideas from
various open‑source tools and community snippets. In particular, it draws
inspiration from:

- speckit
- superclaude

We greatly appreciate the open‑source community. If you are a maintainer of a
referenced project and would like additional attribution or adjustments, please
open an issue.

## Features

- 🎯 **Dual IDE Support**: Cursor slash commands + Codex CLI flag-based personas
- 🧠 **AMR**: Auto Model Router (reasoning medium ↔ high) with fixed state
  machine (INTENT→CLASSIFY→PLAN→EXECUTE→VERIFY→REPORT)
- 🚀 **SDD assist**: generate lightweight rules from `specs/**/spec.md` and
  `specs/**/plan.md`
- 🎭 **Personas**: Specialized AI personalities (`--frontend`, `--backend`,
  `--architect`, etc.)
- 🗣️ **Debate (single‑model)**: Positive vs Critical self with structured
  alternation and synthesis
- 🧰 **CLI tools**: rule generation (`super:init`), persona prompting
  (`optimize`), AMR scaffold/print (`codex-amr`)

## Quick Start

### 1. Install

```bash
npm install -g @cdw0424/super-prompt
```

### 2. Initialize in your project

This sets up Cursor rules and slash commands:

```bash
super-prompt super:init
# or if not globally installed:
npx @cdw0424/super-prompt super:init
```

**What happens during initialization:**

- Creates `.cursor/rules/` with SDD workflow rules
- Sets up slash commands for Cursor IDE
- Optionally creates `.codex/` for CLI integration

**Non-interactive setup:**

```bash
SUPER_PROMPT_INIT_CODEX=1 super-prompt super:init
```

### 3. Use with your preferred IDE

**In Cursor:**

After running `super-prompt super:init`, Cursor automatically recognizes the
slash commands. Here's how to use them:

**Step-by-step usage:**

1. Open Cursor in your project
2. Start typing `/` in any prompt or chat
3. Select from available Super Prompt commands

**Available Commands:**

**Core AI Personas** (for different development tasks):

- `/frontend` — Frontend design advisor (UX-focused)
- `/frontend-ultra` — Elite UX/UI architect (top-tier design)
- `/backend` — Backend reliability engineer (99.9% uptime)
- `/analyzer` — Root cause analyst (evidence-based debugging)
- `/architect` — Systems architecture specialist
- `/high` — Deep reasoning specialist (strategic thinking)
- `/seq` — Sequential thinking (5 iterations)
- `/seq-ultra` — Advanced sequential thinking (10 iterations)
- `/debate` — AI vs AI debate system

**Enhanced Personas** (specialized tools):

- `/security` — Threat modeler & vulnerability specialist
- `/performance` — Optimization specialist (metrics-driven)
- `/wave` — Wave system orchestrator (multi-stage execution)
- `/task` — Task management mode (structured workflow)
- `/ultracompressed` — Token efficiency mode (30-50% reduction)
- `/db-refector` — Database refactoring specialist (Prisma support)
- `/db-template` — Generate Prisma schema templates
- `/db-doc` — Generate database documentation

**SDD Workflow** (Spec-Driven Development):

- `/spec` — Create detailed specifications for features
- `/plan` — Design implementation plans
- `/tasks` — Break down plans into actionable tasks
- `/implement` — Start implementation with SDD compliance checking

**Example Usage Scenarios:**

**Frontend Development:**

```
/frontend "Design a responsive login form with validation"
/frontend-ultra "Create a complete design system for our app"
/analyzer "Debug why my CSS animations aren't working"
```

**Backend Development:**

```
/backend "Design REST API for user management"
/architect "Plan database schema for e-commerce platform"
/high "Evaluate GraphQL vs REST for our use case"
```

**Full Development Workflow (SDD):**

```
/spec "Design a real-time chat feature with file uploads"
/plan "Implement chat using WebSocket and AWS S3"
/tasks "Break down chat implementation into development tasks"
/implement "Start building the chat backend"
```

**Advanced Usage:**

```
/seq "Refactor this monolithic component into smaller pieces"
/debate --rounds 8 "Should we use TypeScript or JavaScript?"
/performance "Optimize this slow database query"
/security "Review this authentication flow for vulnerabilities"
```

**💡 Pro Tips:**

- Commands work in any Cursor prompt or chat
- You can combine commands with regular text
- Use quotes around multi-word queries
- Tab completion is available for command names

**In Codex CLI:**

```bash
# Simplified persona flags (--sp-* prefix, optimize command is optional)
--sp-frontend "Design strategy"
--sp-analyzer "Debug intermittent failures"
--sp-backend "API design patterns"
--sp-architect "System architecture review"

# Original flag syntax (still supported)
--frontend "Design strategy"
--analyzer "Debug intermittent failures"

# Single‑model debate (internal Positive vs Critical selves)
--sp-debate --rounds 8 "Choose DB schema migration approach"
--sp-debate --rounds 5 "TypeScript vs JavaScript for our project"

# SDD workflow commands - simplified flag syntax
--sp-sdd-spec "user authentication system"
--sp-sdd-plan "API endpoints design"
--sp-sdd-tasks "break down into development tasks"
--sp-sdd-implement "login functionality"
```

## Commands

### 🆕 Simplified Command Syntax (v2.7.0+)

Super Prompt now offers streamlined `--sp-*` flags for both personas and SDD
workflows, making commands cleaner and more intuitive:

__Benefits of --sp-_ syntax:_*

- **Shorter commands**: `--sp-frontend` vs `--frontend`
- **Consistent naming**: All Super Prompt flags use the same `--sp-` prefix
- **Future-proof**: New features will follow this pattern
- **Backward compatible**: Original flags still work

**Quick Comparison:**

```bash
# New simplified syntax (recommended)
super-prompt --sp-frontend "Create responsive UI"
super-prompt --sp-sdd-spec "user authentication"

# Original syntax (still supported)
super-prompt optimize --frontend "Create responsive UI"
super-prompt sdd spec "user authentication"
```

### 🔄 Command Format Differences

**Cursor IDE** (uses `/tag` format):

- Type `/` followed by command name in any prompt
- Example: `/frontend "Design a login form"`
- Automatically available after `super-prompt super:init`
- Interactive and visual command selection

**Codex CLI** (uses `--sp-*` flags):

- Command-line interface with flag options
- Example: `--sp-frontend "Design a login form"`
- `optimize` command is optional since v2.9.19
- Terminal-based execution

**Both environments provide identical functionality:**

- Same AI personas and SDD workflows
- Same output quality and features
- Just different input methods for your preferred interface

__All available --sp-_ flags:_*

- **Personas**: `--sp-frontend`, `--sp-backend`, `--sp-analyzer`,
  `--sp-architect`, `--sp-high`, `--sp-seq`, `--sp-seq-ultra`, `--sp-debate`,
  `--sp-performance`, `--sp-security`, `--sp-task`, `--sp-wave`,
  `--sp-ultracompressed`
- **SDD Workflow**: `--sp-sdd-spec`, `--sp-sdd-plan`, `--sp-sdd-tasks`,
  `--sp-sdd-implement`

### Core Setup

- `super:init` — Generate SDD rule files under `.cursor/rules/`
  - Options: `--out <dir>` (default `.cursor/rules`), `--dry-run`

### Persona System

- `"<query>" [--persona|--frontend|--backend|--architect|--analyzer|--high|--seq|--seq-ultra|--debate]`
  — Execute a persona‑assisted prompt (flags for Codex, optimize command is
  optional)
- **New**: Simplified syntax with `--sp-*` prefix for cleaner commands
  (recommended)

### SDD Workflow (Available in both Cursor and Codex CLI)

**Cursor (slash commands):**

- `/spec "<description>"` — Create or edit SPEC files with architect persona
- `/plan "<description>"` — Create or edit PLAN files with architect persona
- `/tasks "<description>"` — Break down plans into actionable tasks with
  analyzer persona
- `/implement "<description>"` — Start implementation with SDD compliance
  checking

**Codex CLI (simplified flags):**

- `--sp-sdd-spec "<description>"` — Create or edit SPEC files (optimize command
  optional)
- `--sp-sdd-plan "<description>"` — Create or edit PLAN files (optimize command
  optional)
- `--sp-sdd-tasks "<description>"` — Break down plans into tasks (optimize
  command optional)
- `--sp-sdd-implement "<description>"` — Start implementation (optimize command
  optional)

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

__Codex CLI (simplified --sp-_ flags, recommended):_*

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

- `--frontend`, `--backend`, `--analyzer`, `--architect`, `--high`, `--seq`,
  `--seq-ultra`
- `--debate`, `--performance`, `--security`, `--task`, `--wave`,
  `--ultracompressed`

### Enhanced Personas (Cursor only)

- `/security` — Threat modeler & vulnerability specialist
- `/performance` — Optimization specialist (metrics-driven)
- `/wave` — Wave system orchestrator (multi-stage execution)
- `/task` — Task management mode (structured workflow)
- `/ultracompressed` — Token efficiency mode (30-50% reduction)

### Database Tools (Cursor + CLI)

- `/db-refector` — Database schema analysis and optimization
- `/db-template` — Generate Prisma schema templates
- `/db-doc` — Generate database documentation from Prisma schema

### SDD Workflow Commands (Cursor slash commands)

- `/spec` — Create detailed specifications for features and requirements
- `/plan` — Design implementation plans based on specifications
- `/tasks` — Break down plans into actionable development tasks
- `/implement` — Start implementation with SDD compliance checking

**Note**: SDD workflow is also available in Codex CLI using the `sdd` command
(see examples above)

Add your own personas in `.cursor/commands/super-prompt/**/*.{md,mdc,py}`.
Markdown with front‑matter and Python files with leading docstrings are
recognized.

## SDD Workflow

Super Prompt includes a complete Spec-Driven Development workflow available in
**both Cursor and Codex CLI**:

### 🎯 SDD Methodology

**Spec-Driven Development** ensures you build the right thing, the right way, at
the right time by following a structured approach:

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

# Or use the dedicated sdd subcommand
super-prompt sdd spec "user authentication system"
super-prompt sdd plan "OAuth2 + JWT implementation"
super-prompt sdd tasks "break down auth tasks"
super-prompt sdd implement "start development"
```

### 🎯 SDD Benefits

- **Clarity**: Everyone knows what's being built and why
- **Quality**: Architecture decisions made upfront
- **Efficiency**: Reduced rework and scope creep
- **Collaboration**: Clear handoffs between team members
- **Compliance**: Built-in validation and quality gates

Each step builds on the previous one, with automatic context sharing between
phases and intelligent validation.

## ✅ TODO Auto-Validation System

The TODO validation system automatically monitors task completion and triggers
high-reasoning mode retries for failed tasks. This ensures reliable task
completion and intelligent error recovery.

### Features

- **Automatic Validation**: Validates task completion using multiple criteria
  (file changes, syntax, tests, builds)
- **Intelligent Retry**: Failed tasks automatically retry in high-reasoning mode
  with enhanced context
- **Progress Tracking**: Real-time session management with attempt tracking and
  error logging
- **Quality Gates**: Built-in validation for syntax, testing, security, and
  documentation

### TODO Commands

```bash
# Validate current TODO session and trigger retries for failed tasks
super-prompt todo:validate

# Auto-validation mode (validates after each task completion)
super-prompt todo:validate --auto

# Show current TODO session status with progress tracking
super-prompt todo:status

# Use custom session file
super-prompt todo:validate --session-file custom_todos.json
```

**Note:** TODO commands are currently in development and may change in future
versions.

### Validation Criteria

The system automatically validates tasks using context-aware criteria:

- **File Operations**: Detects file changes via git status
- **Code Quality**: Validates Python/JavaScript syntax
- **Testing**: Runs available test suites (npm test, pytest)
- **Build Process**: Verifies build success (npm run build)
- **Documentation**: Checks README completeness and quality
- **Git Status**: Ensures repository is in clean state

### High-Mode Retry Logic

When validation fails:

1. **Failure Detection**: Task marked as failed with detailed error context
2. **Enhanced Prompt**: Creates comprehensive retry prompt with failure analysis
3. **High-Mode Execution**: Retries using `--sp-high` reasoning mode
4. **Attempt Tracking**: Monitors retry attempts (max 3 per task)
5. **Success Validation**: Re-validates after high-mode completion

### Integration with AGENTS.md

The validation system integrates with the Codex AGENTS.md TODO workflow:

- **Mandatory Planning**: All complex tasks (3+ steps) must start with TODO
  planning
- **Progress Tracking**: Real-time updates after each task completion
- **Evidence-Based**: Tasks marked complete only with validation evidence
- **Quality Assurance**: Automatic validation before final completion

This ensures reliable, high-quality task completion with intelligent error
recovery.

## 🧠 Context Engineering System

The Context Engineering System implements Spec Kit principles to maintain
conversation context across development stages, ensuring design intent
preservation and eliminating context drift.

### Core Principles

**1. Context Externalization**: All conversation context is stored as versioned
artifacts **2. Stage Gating**: Structured workflow prevents context loss through
validation gates **3. Task Minimization**: Break complex contexts into
manageable, task-specific injections **4. Organizational Integration**: Absorb
company standards and rules into project context

### Directory Structure

```
project/
├── specs/
│   └── project-id/
│       ├── spec.md      # Requirements and goals
│       ├── plan.md      # Implementation strategy  
│       └── tasks.md     # Actionable breakdown
└── memory/
    ├── constitution/    # Project principles and rules
    │   └── constitution.md
    ├── rules/          # Domain-specific guidelines
    └── sessions/       # Context session states
```

### Context Commands

```bash
# Initialize context management for a project
super-prompt context:init my-project --stage specify

# Check context status and available artifacts
super-prompt context:status --project my-project

# List all projects with context information
super-prompt context:projects

# Manage context sessions
super-prompt context:session start my-project --stage plan
super-prompt context:session switch my-project --stage tasks

# Clean up old context sessions
super-prompt context:cleanup --days 30
```

### Context Injection in SDD

The system automatically injects relevant context when using SDD commands:

```bash
# SPEC creation with constitution and rules
super-prompt sdd spec "user authentication system"
# → Automatically includes project constitution and organizational standards

# PLAN development with spec context
super-prompt sdd plan "OAuth2 + JWT implementation"  
# → Includes SPEC requirements and architectural constraints

# TASKS breakdown with full context
super-prompt sdd tasks "break down auth implementation"
# → Includes SPEC + PLAN with task-relevant sections

# Implementation with focused context
super-prompt sdd implement "start development" --validate
# → Minimal context injection focused on current task
```

### Context Injection Policies

- **FULL**: Complete context injection for comprehensive analysis
- **SELECTIVE**: Query-relevant sections only for efficiency
- **SECTIONAL**: Key sections by artifact type (architecture, requirements)
- **MINIMAL**: Essential information only for focused implementation

### Stage Gating Workflow

**specify → plan → tasks → implement**

Each stage transition validates required artifacts exist:

- **plan** requires `spec.md`
- **tasks** requires `spec.md` + `plan.md`
- **implement** requires `spec.md` + `plan.md` + `tasks.md`

### Token Optimization

- **Intelligent Compression**: 30-50% token reduction through selective
  injection
- **Priority Context**: Constitution and critical requirements loaded first
- **Content Summarization**: Automatic summarization when approaching token
  limits
- **Section Extraction**: Query-relevant content extraction for efficiency

### Integration Benefits

- **Context Preservation**: Design intent maintained across all development
  stages
- **Collaboration**: Clear handoffs between team members with persistent context
- **Quality Assurance**: Built-in validation against established requirements
- **Organizational Alignment**: Company standards automatically integrated
- **Token Efficiency**: Optimized context injection reduces token usage by
  30-50%

The Context Engineering System ensures that every interaction has access to
relevant project context, eliminating the need to repeatedly explain
requirements and maintaining consistency across development phases.

## Debate (Single‑Model, Codex)

A structured internal debate that alternates between two selves and ends with a
synthesis:

- Positive Self (Builder): constructive, solution‑oriented
- Critical Self (Skeptic): risk‑focused, assumption testing

Usage

```bash
super-prompt --sp-debate --rounds 8 "Should we use microservices or a modular monolith?"
# or: super-prompt optimize --sp-debate --rounds 8 "Should we use microservices or a modular monolith?"
# or: super-prompt --debate --rounds 8 "Should we use microservices or a modular monolith?"
```

Flow

1. Alternate Positive → Critical for N rounds
2. Keep sections: [INTENT][TASK_CLASSIFY][PLAN][EXECUTE][VERIFY][REPORT]
3. Finish with a concise synthesis and next steps

## Generated Files

- Rules: `.cursor/rules/00-organization.mdc`, `10-sdd-core.mdc`,
  `20-frontend.mdc`, `30-backend.mdc`
- Commands: `.cursor/commands/super-prompt/tag-executor.sh` and multiple `.md`
  entries

## Requirements

- macOS or Linux
- Node.js ≥ 14
- Python ≥ 3.7
- Codex CLI (optional): install/upgrade choice at install time. To auto‑install
  non‑interactively:
  `SUPER_PROMPT_CODEX_INSTALL=1 npm i -g @cdw0424/super-prompt`
- Tests: `npm test` (Node’s built‑in `node --test`)

## Troubleshooting

- “Python CLI not found” after install → re‑run `npm install` or
  `node install.js`
- Python < 3.7 → install Python ≥ 3.7 and ensure `python3` points to it
- Slash commands not visible (Cursor) → ensure `.cursor/commands/super-prompt/`
  exists, files executable (`chmod 755`), restart Cursor
 - Infinite Git churn referencing `.npm-cache/_cacache`
   - Cause: npm cache is set to a path inside the repository; installs flood `.npm-cache/` and trigger Git watchers.
   - **Automated Fix (recommended)**:
     ```bash
     npx @cdw0424/super-prompt run scripts/codex/npm-cache-fix.sh --fix
     ```
   - **Manual Fix**:
     ```bash
     npm config get cache
     npm config set cache ~/.npm --global
     echo ".npm-cache/" >> .gitignore
     git rm -r --cached .npm-cache 2>/dev/null || true
     ```
   - Our installer detects this condition and prints a warning with the recommended fix.

## Codex AMR (medium ↔ high)

This repo includes an Auto Model Router (AMR) and a strict state‑machine
bootstrap prompt to improve instruction adherence and output consistency.

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

- Generate Cursor AMR rule: `npm run amr:rules` → writes
  `.cursor/rules/05-amr.mdc`
- Print bootstrap prompt: `npm run amr:print` (copy to Codex TUI)
- Validate a transcript: `npm run amr:qa -- path/to/transcript.txt`

Router switching

- If the environment does not auto‑execute the following lines, copy‑run them in
  the TUI:
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
- Translation/backends (optional) → if you use external CLIs (`claude`,
  `codex`), ensure they’re on PATH and configured
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

This creates `.codex/agents.md`, `.codex/personas.py`,
`.codex/bootstrap_prompt_en.txt`, and `.codex/router-check.sh`.

### Using with Codex TUI

1. Open Codex:

```bash
codex
```

2. Paste the bootstrap prompt from `.codex/bootstrap_prompt_en.txt` (or print
   it: `npx codex-amr print-bootstrap`).
3. Run your workflow; when using the Super Prompt CLI alongside Codex, prefer
   simplified --sp-* flags (optimize command is optional):

```bash
super-prompt --sp-frontend "Design a responsive layout"
super-prompt --sp-backend  "Retry + idempotency strategy"
super-prompt --sp-debate --rounds 8 "Feature flags now?"
# Double-Check Auditor (self-review + confessional + remediation plan)
super-prompt --sp-double-check "Audit last changes for correctness, honesty, and provide a remediation plan" --out .codex/reports/double_check.md
super-prompt optimize --double-check "Audit last changes for correctness, honesty, and provide a remediation plan"
```

4. Router switches (if not auto‑executed by your environment), copy‑run in TUI:

```
/model gpt-5 high
/model gpt-5 medium
```

## Architecture & Why It Performs Well

### Component Map

- Router: `src/amr/router.js` — classifies tasks (L0/L1/H) and advises
  medium↔high switches
- State Machine: `src/state-machine/index.js` — fixed loop
  (INTENT→CLASSIFY→PLAN→EXECUTE→VERIFY→REPORT)
- Bootstrap Prompt: `src/prompts/codexAmrBootstrap.en.js` — AMR‑aware TUI
  starter
- Scaffold: `src/scaffold/codexAmr.js` — one‑shot bootstrap into a repo
- Python CLI: `.super-prompt/utils/cli.py` — flag personas, single‑model debate,
  project SDD helpers
- Cursor Processors: `.super-prompt/utils/cursor-processors/` — specialized
  Cursor command processors
- Codex Agent: `.codex/AGENTS.md` + `.super-prompt/utils/personas.py` —
  Codex‑specific guidance & builders

### New Modular Structure

- **`.super-prompt/utils/`**: Centralized Python utilities for better
  maintainability
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
  - Mechanism: English‑only, fixed tone, flag personas; logs prefixed with
    `--------`
  - Effect: stylistic stability; easy log parsing in scripts/CI
  - Result: repeatable outputs, fewer formatting failures
- Memory Hygiene
  - Mechanism: repo facts vs. per‑turn discoveries kept explicit (rules +
    transcripts)
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
