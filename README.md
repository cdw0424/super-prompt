# Super Prompt v4.7.0: Ultimate Dual IDE Prompt Engineering Toolkit

[![npm version](https://img.shields.io/npm/v/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![npm downloads](https://img.shields.io/npm/dm/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**🚀 The Ultimate Dual IDE Prompt Engineering Toolkit with Enhanced MCP
Support**

### ❗ Important: Enable Super‑Prompt MCP in Cursor

To use Super‑Prompt inside Cursor, ensure the Super‑Prompt MCP is enabled in
Cursor after initialization.

- Open Cursor → Settings → MCP and enable the Super‑Prompt server
- If you don’t see it, restart Cursor after running project initialization
- In chat, you should see slash command autocomplete like
  `/super-prompt/architect`

See the setup guide: [Cursor MCP Setup Guide](docs/cursor-mcp-setting-guide.md)

---

Super Prompt delivers advanced MCP (Model Context Protocol) implementation with
comprehensive development tools, seamless Cursor and Codex IDE integration, and
intelligent persona system.

### 🧭 Philosophy

- **Command First**: Explicit commands/flags take precedence and are executed
  immediately.
- **SSOT**: Single Source of Truth — personas manifest → `.cursor/rules` →
  `AGENTS.md`.
- **SDD**: Spec → Plan → Implement, with Acceptance Self‑Check before merge.
- **AMR**: Default to medium reasoning; switch to high for deep planning; return
  to medium for execution.
- **Safety**: English logs start with `-----`; never print secrets (mask like
  `sk-***`).

This philosophy powers a dual‑IDE workflow (Cursor + Codex) and underpins our
model recommendation below for consistent, fast, and reliable results.

### 🔍 Confession Mode (Double‑Check)

- **What it is**: An automatic self‑audit appended to the end of every MCP tool
  response.
- **What it includes**:
  - Summary of what was done
  - Unknowns and potential risks
  - Recommended countermeasures (verification/rollback/alternatives)
  - Completion timestamp
- **Scope**: Enabled by default for all Super Prompt MCP tool outputs in
  Cursor/Codex.
- **Purpose**: Standardizes a “double‑check” step to improve reliability and
  transparency of results.

### ✅ Recommended IDE Models (Cursor)

- Use both models together for best results:
  - GPT‑5 Codex (low, fast, max context)
  - Grok Code (fast, max context)

---

## ⚡ Quick Start

### 1) Install

```bash
npm install @cdw0424/super-prompt@latest
```

### 2) Initialize project assets

```bash
npx -y @cdw0424/super-prompt@latest super:init
```

> ℹ️ **Why `npx`?** `super-prompt` isn’t installed globally by default, so
> running `super-prompt super:init` directly will usually show
> `command not found`. The one-off `npx` call (or the local npm script below) is
> the supported way to run the init command.

If you installed the package locally, you can also use the bundled npm script:

```bash
npm run sp:init
```

To make the CLI globally available, install it with `npm i -g` or add
`./node_modules/.bin` to your PATH.

### 3) Enable in Cursor (MCP)

Open Cursor → Settings → MCP and enable the Super‑Prompt server (restart Cursor
if needed). After enabling, slash commands will autocomplete in chat.

### 4) Model Modes (GPT vs Grok)

- Modes are mutually exclusive; default is GPT.
- In Cursor, toggle with slash commands (these persist the mode to
  `.super-prompt/mode.json` and switch the active provider):

```
/super-prompt/gpt-mode-on
/super-prompt/grok-mode-on
/super-prompt/gpt-mode-off
/super-prompt/grok-mode-off
```

- What happens:
  - `grok-mode-on`: sets mode to Grok (disables Codex AMR prompts), new chats
    use Grok.
  - `gpt-mode-on`: sets mode to GPT (enables Codex AMR prompts), new chats use
    GPT‑5 Codex.
  - `gpt-mode-off`/`grok-mode-off`: clear explicit mode; system will fall back
    to defaults.

- Codex CLI toggles (same behavior, affects both Cursor and Codex):

```bash
# Turn on GPT mode
sp gpt-mode-on

# Turn on Grok mode
sp grok-mode-on

# Turn off explicit GPT/Grok mode (revert to default)
sp gpt-mode-off
sp grok-mode-off
```

### 5) Use in Cursor IDE

1. Set models as recommended above (GPT‑5 Codex low fast max + Grok Code fast
   max).
2. In Cursor chat, use slash commands:

```
/super-prompt/architect "design a REST API"
/super-prompt/dev "implement authentication"
```

### 6) Use in Codex (flag commands)

In Codex, enter flags directly in chat (no `super-prompt` prefix). Recommended
flags use the `--sp-` prefix (both forms are accepted):

```
--sp-architect "design a REST API"
--sp-dev "implement authentication"
```

### 7) CLI shorthand

The package also installs a short alias `sp`, so you can run MCP personas
directly from the shell:

```bash
sp --architect "design a REST API"
sp --dev "implement authentication"
```

### Unified MCP pipeline (new in 4.7.0)

- Every `/super-prompt/<persona>` command now routes through a shared
  `sp.pipeline` helper.
- The pipeline always performs: memory lookup → prompt/context analysis →
  Codex/persona execution → plan + execution guidance → confession double-check
  → memory update.
- To call the pipeline manually you can run
  `sp --pipeline "tool=<persona>" "<query>"` or via MCP tool args.
- Existing Cursor commands are already wired to the appropriate pipeline key, so
  no action is required to benefit from the upgraded workflow.
- The helper understands Cursor-style argument payloads (`query`, `input`, `a`,
  etc.), so legacy commands keep working without changes.

---

## 🛠️ Available Tools

### Development

- `architect` - System architecture design
- `backend` - Backend development
- `frontend` - Frontend development
- `dev` - General development
- `refactorer` - Code refactoring
- `optimize` - Performance optimization

### Quality & Analysis

- `analyzer` - Code analysis
- `security` - Security review
- `performance` - Performance analysis
- `qa` - Quality assurance
- `review` - Code review

### Advanced

- `high` - Strategic analysis
- `doc-master` - Documentation
- `db-expert` - Database expertise

---

## 📚 Links

- **[Changelog](CHANGELOG.md)**: Version history
- **[Issues](https://github.com/cdw0424/super-prompt/issues)**: Report bugs

## 📄 License

MIT © [Daniel Choi](https://github.com/cdw0424)
