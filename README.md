# Super Prompt v5.2.49

**Latest Update**: MCP stdout/stderr Cleanup & Enhanced Stability

[![npm version](https://img.shields.io/npm/v/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![npm downloads](https://img.shields.io/npm/dt/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.17-brightgreen)](https://nodejs.org/)

Super Prompt is a zero-config, MCP-powered toolkit for Cursor IDE. It provides
29+ AI tools including 6 specialized personas, context management, SDD workflow
tools, and seamless slash command integration. All tools are accessible via
Cursor's slash commands (/) for instant AI assistance.

## 1) Install (one line)

```bash
npm install -g @cdw0424/super-prompt@latest
```

## 2) Quick Start

```bash
super-prompt super:init --force
```

The initializer will:

- create `.cursor/` and copy command/rule assets
- create `.super-prompt/` internal config
- register the MCP server with 29+ AI tools

Then restart Cursor (fully quit and relaunch).

**Slash Commands**: All tools are accessible via Cursor's slash commands (/) for
instant AI assistance:

```bash
/sp_analyzer "Analyze this code performance"
/sp_architect "Design a microservice architecture"
/sp_doc_master "Generate API documentation"
/sp_refactorer "Refactor this function"
/sp_frontend "Review React component"
/sp_backend "Optimize database queries"
```

**Mode Switching**:

```bash
/sp_gpt_mode_on    # Switch to GPT mode
/sp_grok_mode_on   # Switch to Grok mode
/sp_mode_get       # Check current mode
```

## 3) Modes (per language)

- **GPT mode (default)**: structured, deterministic, great for APIs, reviews,
  docs
- **Grok mode**: exploratory, creative, great for architecture, debugging,
  ideation

You can mix modes per task; the tool registry is stable during switches.

## 4) If something goes wrong

Try in order:

```bash
# Ensure latest package
npm install -g @cdw0424/super-prompt@latest

# Re-run initializer
super-prompt super:init --force

# Still odd? Use npx (bypasses PATH)
npx --yes @cdw0424/super-prompt@latest super:init --force
```

Using an older global binary? The CLI now auto-switches to the npm global binary
when it detects a Homebrew/legacy wrapper first in PATH. No manual PATH edits
needed.

## 5) What we believe (short)

- **MCP-first**: clear tool boundaries, reproducible automations
- **Zero‑config UX**: it should “just work” on first run
- **Productivity personas**: focused prompts with measurable outputs

## 6) What you get

### MCP Tools (29+ slash commands)

All tools are accessible via Cursor's slash commands (/) for instant AI
assistance:

**Persona Tools (6)**

- `/sp_analyzer` - Code analysis and performance optimization
- `/sp_architect` - System architecture design and planning
- `/sp_frontend` - Frontend development and UI/UX guidance
- `/sp_backend` - Backend development and API design
- `/sp_doc_master` - Documentation generation and technical writing
- `/sp_refactorer` - Code refactoring and improvement suggestions

**Basic Tools (4)**

- `/sp.version` - Get current version
- `/sp_health` - Check server health
- `/sp_list_commands` - List all available commands
- `/sp_list_personas` - List available personas

**Context Management (2)**

- `/sp_context_collect` - Collect relevant context for queries
- `/sp_context_clear_cache` - Clear context cache

**SDD Workflow Tools (4)**

- `/sp_specify` - Requirements specification (SDD Phase 1)
- `/sp_plan` - Implementation planning (SDD Phase 2)
- `/sp_tasks` - Task breakdown (SDD Phase 3)
- `/sp.sdd_architecture` - SDD architecture playbook

**Mode Management (6)**

- `/sp_mode_get` - Get current LLM mode
- `/sp_mode_set` - Set LLM mode
- `/sp_gpt_mode_on` - Switch to GPT mode
- `/sp_grok_mode_on` - Switch to Grok mode
- `/sp_gpt_mode_off` - Turn off GPT mode
- `/sp_grok_mode_off` - Turn off Grok mode

**Additional Tools (7+)**

- `/sp_init` - Initialize project
- `/sp_refresh` - Refresh project assets
- `/sp_memory_stats` - Memory management statistics
- `/sp_high` - High-level analysis
- `/sp_gpt` - GPT persona analysis
- `/sp_grok` - Grok persona analysis
- `/sp_troubleshooting` - Systematic problem diagnosis

### Features

- 29+ ready-to-use MCP tools accessible via slash commands
- Stable GPT/Grok mode switching
- Project memory and spec-driven scaffolding hooks
- Zero-config setup with automatic MCP server registration

## What's new in 5.2.47

### **Latest Features (v5.2.47)**

- **Robust Python Installation** – Implemented multiple fallback methods for
  Python dependency installation
- **Enhanced Auto-Installation** – More reliable Python package installation
  during npm install
- **Better User Experience** – Improved installation process for new users with
  comprehensive error handling

### **Previous Updates (v5.2.46)**

### **Previous Updates (v5.2.45)**

### **Previous Updates (v5.2.44)**

### **Previous Updates (v5.2.43)**

### **Previous Updates (v5.2.42)**

### **Previous Updates (v5.2.41)**

### **Previous Updates (v5.2.38)**

- **Auto-switch Wrapper** – If a Homebrew/old wrapper is first in PATH, the CLI
  auto re-execs to npm global binary (`~/.local/bin/super-prompt`)
- **Zero-Configuration Init** – No PATH or env setup required; `super:init`
  works out of the box
- **Improved CLI Detection** – Robust detection to ensure proper CLI operation
  across environments
- **Fixed Version Display Issue** – Version now shows correctly instead of
  "unknown"
- **Removed Venv References** – All virtual environment references removed
- **Cleaned Up Dependencies Message** – Now simply: "Using system Python"
- **Enhanced CLI Prompt Readability** – Added visual separators and clear
  formatting for user input prompts
- **Improved Interactive Initialization** – User inputs now have clear visual
  boundaries with decorative separators
- **Better Input Prompts** – Added emojis and clear formatting for project root,
  MCP server, and Python package paths
- **Enhanced CLI Mode** – All CLI commands now work without requiring
  SUPER_PROMPT_ALLOW_DIRECT=true
- **Improved CLI User Experience** – CLI mode automatically disables MCP-only
  enforcement for better usability
- **Simplified CLI Usage** – No need to set environment variables for basic CLI
  operations
- **Fixed MCP Server Python Path Issue** – MCP server now correctly uses
  .super-prompt/lib/ Python packages
- **User-Centric Python Path Resolution** – All commands prioritize user's
  project .super-prompt/lib/ over system packages
- **Enhanced Package Discovery** – Improved PYTHONPATH resolution for both MCP
  server and CLI tools
- **Fixed "no tools" Error** – MCP server can now properly find and load all
  Super Prompt tools after initialization
- **Enhanced CLI User Experience** – Improved readability by hiding debug logs
  in CLI mode
- **Cleaner Initialization Output** – User input prompts are now clearly visible
  without debug message interference
- **Better Visual Separation** – Debug logs are hidden in CLI mode for better
  user experience
- **Fixed MCP Server Interference** – Removed MCP module imports from mode
  change functions to prevent server state disruption
- **Improved Mode Switching** – Mode changes (grok/gpt) no longer affect MCP
  tool availability
- **Enhanced Stability** – MCP server remains stable during mode transitions
- **Interactive Initialization** – Added dialog-based input for project root,
  MCP server path, and Python package path
- **Enhanced MCP Path Configuration** – Users can now specify custom paths for
  MCP server and Python packages during initialization
- **Improved User Experience** – Initialization process now asks for user input
  when needed instead of using defaults
- **Flexible Path Management** – Support for custom installation paths while
  maintaining backward compatibility

## How it works (very short)

- CLI `super-prompt` initializes your project and verifies MCP
- MCP server `sp-mcp` runs under the hood to serve tools to Cursor

## Development Workflows

Super Prompt provides structured AI-assisted development workflows:

### **Spec-Driven Development (SDD)**

```bash
/super-prompt/specify "Design user authentication with OAuth2"
/super-prompt/plan "Implementation roadmap"
/super-prompt/tasks "Break down into tasks"
```

### **Problem Solving**

```bash
/super-prompt/troubleshooting "Debug complex issues"
/super-prompt/performance "Performance analysis"
/super-prompt/security "Security audit"
/super-prompt/analyzer "Root cause analysis"
```

### **Quality Assurance**

```bash
/super-prompt/review "Code review and validation"
/super-prompt/qa "Quality assurance checks"
/super-prompt/architect "Architecture design and validation"
/super-prompt/refactorer "Code quality improvements"
```

### **Development Workflows**

```bash
/super-prompt/dev "Feature development"
/super-prompt/mentor "Learning and guidance"
/super-prompt/doc-master "Documentation architecture"
/super-prompt/devops "CI/CD and deployment"
```

## Documentation

For detailed technical documentation, see the [`docs/`](./docs/) directory:

- **[Architecture Overview](./docs/architecture-v5.md)** - System design and
  technical specifications
- **[Cursor Integration Guide](./docs/cursor-mcp-setting-guide.md)** - MCP
  server setup instructions
- **[Development Workflows](./docs/codex-amr.md)** - Advanced usage patterns

## Troubleshooting

| Symptom                                                           | Resolution                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Version shows older release (e.g., v1.0.4) after installation** | `npm view @cdw0424/super-prompt version` now returns 5.2.41, so the registry is serving the new build. When you see the banner report v1.0.4 after installation, the CLI is being launched from an older copy that's still on your machine—most often a globally installed 1.0.4 or a project lockfile pinned to that number.<br><br> **Do this once to flush the stale install:**<br><br> `npm uninstall -g @cdw0424/super-prompt   # removes the old global copy`<br> `npm cache clean --force                  # optional, clears cached tarballs`<br><br> **Then reinstall the new release (pick the style you want per project):**<br><br> `# global upgrade (if you rely on the super-prompt binary in PATH)`<br> `npm install -g @cdw0424/super-prompt@latest`<br><br> `# project-local (preferred for workspace isolation)`<br> `npm install @cdw0424/super-prompt@latest`<br> `npx @cdw0424/super-prompt@latest super:init   # or ./node_modules/.bin/super-prompt super:init`<br><br> **If the project already had a package-lock.json or npm-shrinkwrap.json, make sure it doesn't pin the old version; delete the lockfile or bump the semver entry to ^5.2.41 before reinstalling.**<br><br> **After reinstalling, rerun super:init (or ./bin/super-prompt super:init) and the banner will show v5.2.41 \| @cdw0424/super-prompt, confirming the newer code is in use.**<br><br> _Note: npm will always deliver the latest tarball, but Node's install flow can't guess your intent about existing copies. If a machine already has an older global install, the shell will keep launching that binary until it's removed or upgraded. Likewise, a project's package-lock.json can legitimately pin an older release. Automatically ripping those out during install would break reproducibility, so the CLI leaves that decision to you._<br><br> _If you want to force the newest version every time, add a one-line script to your bootstrap (for example, in your project's postinstall):_<br><br> `"scripts": {`<br>&nbsp;&nbsp;`"postinstall": "npx --yes npm@latest install @cdw0424/super-prompt@latest"`<br> `}`<br><br> _Or, for global installs on shared machines:_<br><br> `npm install -g @cdw0424/super-prompt@latest`<br> `super-prompt super:init --force`<br><br> _That way each environment explicitly refreshes to 5.2.41 (or whatever's current) before initialization, without the tool destroying user-managed installations behind the scenes._ |
| Cursor reports "no tools available"                               | Check `~/.cursor/mcp.log` for `-------- MCP:` entries. If FastMCP is missing, install the runtime manually: `pip install mcp`. The fallback server will operate automatically once the CLI reconnects.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `sp_high` missing or duplicated                                   | The 5.0.5 release registers a single `sp_high` backed by the persona pipeline. Restart `sp-mcp` to reload the registry.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Stdout parse errors                                               | Ensure you never print to stdout in custom scripts. Super Prompt reserves stdout for JSON-RPC; use `--------`-prefixed logs on stderr.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |

## Release workflow

1. `npm install` – refreshes `package-lock.json`.
2. `npm run prepack` – builds the Python wheel into `dist/` (optional for local
   testing).
3. `npm publish` – publishes `@cdw0424/super-prompt@5.2.41` with synchronized
   Python assets.

Super Prompt is MIT licensed. Contributions and issues are welcome at
[https://github.com/cdw0424/super-prompt](https://github.com/cdw0424/super-prompt).
