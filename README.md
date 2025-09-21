# Super Prompt v5.2.22

[![npm version](https://img.shields.io/npm/v/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.17-brightgreen)](https://nodejs.org/)

## Installation

```bash
# For regular users - install globally
npm install -g @cdw0424/super-prompt@latest

# For developers working on this project - use local version
# DO NOT run npm install in the project root - use ./bin/super-prompt directly
```

> **⚠️ Version Management Note**: This project has both development and published versions. When developing, always use `./bin/super-prompt` from the project root. The `node_modules/.bin/super-prompt` is the published npm package version.

> **🛠️ For Developers**: If you're working on Super Prompt itself, NEVER run `npm install` in the project root. This creates version conflicts between `./bin/super-prompt` (development) and `node_modules/.bin/super-prompt` (published). Always use `./bin/super-prompt` directly for development work.

Super Prompt enables Cursor to apply language-specific optimized personas and guidelines, maximizing development performance. It provides a pure Python MCP server with specialized personas, model routing rules, and command-line tooling in a single npm package, allowing you to install, initialize, and register the MCP server in one step.

## Quick Start

### Step-by-Step Setup Guide

> **Note:** If you haven't installed Super Prompt yet, see the [Installation](#installation) section above.

#### 1. Initialize Project Assets

```bash
# Initialize Super Prompt assets in your workspace
super-prompt super:init --force
```

> **For developers**: If you're working on the Super Prompt project itself, use `./bin/super-prompt super:init --force` instead.

This command:
- ✅ Creates `.cursor/` directory with command assets
- ✅ Sets up `.super-prompt/` configuration directory
- ✅ Copies all persona command files (24 total)
- ✅ Initializes MCP server configuration
- ✅ Prepares project for persona usage

> **Important:** After initialization, you must **fully quit and relaunch Cursor** to load the new MCP configuration.
> - On macOS: `Cursor → Quit Cursor` (Cmd+Q) - window close is not enough
> - On Windows/Linux: Fully exit Cursor and restart

#### 2. Configure Cursor MCP Integration

1. **Open MCP Settings**: `Cursor → Settings → MCP`
2. **Add Server Configuration**:

```json
{
  "mcpServers": {
    "super-prompt": {
      "type": "stdio",
      "command": "./bin/sp-mcp",
      "args": [],
      "env": {
        "SUPER_PROMPT_ALLOW_INIT": "true",
        "SUPER_PROMPT_REQUIRE_MCP": "1",
        "SUPER_PROMPT_PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONUNBUFFERED": "1",
        "PYTHONUTF8": "1"
      }
    }
  }
}
```

3. **Verify Configuration**: Restart Cursor and check that Super Prompt commands appear in the command palette

#### 3. Choose Your AI Mode

Super Prompt supports both **GPT** and **Grok** modes. Choose one:

**For Grok Mode (Recommended for creative tasks):**
```bash
/super-prompt/grok-mode-on
```

**For GPT Mode (Recommended for structured tasks):**
```bash
/super-prompt/gpt-mode-on
```

> **Note:** You can switch between modes anytime using `/super-prompt/grok-mode-on` or `/super-prompt/gpt-mode-on`

#### 4. Start Using Personas

You're now ready to use all 24 Super Prompt personas! Try these examples:

```bash
# Architecture design with Mermaid diagrams
/super-prompt/architect "Design a microservices architecture for an e-commerce platform"

# Backend API development
/super-prompt/backend "Create REST API endpoints for user management"

# Frontend component design
/super-prompt/frontend "Design a responsive dashboard UI with dark mode"

# Code review and optimization
/super-prompt/dev "Review and optimize this React component for performance"

# Database schema design
/super-prompt/db-expert "Design a PostgreSQL schema for a social media app"
```

### Troubleshooting

**MCP Commands Not Appearing:**
- Ensure Cursor is fully restarted after initialization
- Check that the MCP configuration is saved in Cursor settings
- Verify the `.bin/sp-mcp` file exists in `node_modules/.bin/`

**Python Errors:**
- Super Prompt includes its own Python runtime
- No additional Python installation required
- All dependencies are bundled with the package

**Permission Issues:**
- On macOS/Linux, ensure executable permissions: `chmod +x ./bin/sp-mcp`
- On Windows, run terminal as administrator if needed

## Model Mode Configuration

Super Prompt supports different AI models with specialized capabilities:

### GPT Mode (Default)
- **Best for**: Structured reasoning, code generation, and technical documentation
- **When to use**: General development tasks, API design, code reviews
- **Commands**:
  ```bash
  /super-prompt/gpt-mode-on   # Enable GPT mode
  /super-prompt/gpt-mode-off  # Disable GPT mode
  ```

### Grok Mode
- **Best for**: Creative problem-solving, innovative approaches, and complex reasoning
- **When to use**: Architecture decisions, debugging complex issues, innovative solutions
- **Commands**:
  ```bash
  /super-prompt/grok-mode-on   # Enable Grok mode
  /super-prompt/grok-mode-off  # Disable Grok mode
  ```

### Mode-Specific Personas

| Persona | GPT Mode Focus | Grok Mode Focus |
|---------|---------------|-----------------|
| **Architect** | Structured design patterns | Creative architectural solutions |
| **Backend** | Standard frameworks & patterns | Innovative backend approaches |
| **Frontend** | UI/UX best practices | Creative user experiences |
| **Analyzer** | Systematic code analysis | Deep insight generation |
| **Doc Master** | Technical documentation | Creative content structure |

### Recommended Model Configuration

For optimal performance in Cursor, we recommend using **max mode** with these AI models:

#### **Primary Recommendation: Grok Code Fast**
```bash
# In Cursor Settings → AI → Model Configuration
Model: Grok Code Fast
Mode: Max
```

**Why Grok Code Fast?**
- **Superior reasoning**: Advanced logical reasoning capabilities
- **Creative solutions**: Generates innovative approaches to complex problems
- **Context awareness**: Better understanding of project context and dependencies
- **Performance optimized**: Fast response times with high-quality output

#### **Alternative: GPT-5 Low Fast**
```bash
# In Cursor Settings → AI → Model Configuration
Model: GPT-5 Low Fast
Mode: Max
```

**When to use GPT-5 Low Fast:**
- **Structured tasks**: API design, documentation, code reviews
- **Consistency needed**: Following established patterns and best practices
- **Large codebases**: Better handling of extensive context windows
- **Enterprise environments**: Familiar interface for team collaboration

### Automatic Mode Detection

Super Prompt automatically detects your project's context and applies the most appropriate mode:

- **New Projects**: Starts in GPT mode for structured planning
- **Complex Debugging**: Switches to Grok mode for creative problem-solving
- **Documentation**: Uses GPT mode for clear, structured writing
- **Innovation Tasks**: Applies Grok mode for breakthrough thinking

### Mode Selection Guidelines

| **Task Type** | **Recommended Model** | **Mode** |
|---------------|----------------------|----------|
| **Architecture Design** | Grok Code Fast | Max |
| **Code Generation** | Grok Code Fast | Max |
| **Debugging** | Grok Code Fast | Max |
| **Code Review** | GPT-5 Low Fast | Max |
| **Documentation** | GPT-5 Low Fast | Max |
| **API Design** | GPT-5 Low Fast | Max |
| **Refactoring** | Grok Code Fast | Max |

## What's new in 5.1.7

- **Command Standardization** – All Super Prompt commands now feature standardized bodies with clear directives, actionable checklists, and mandatory double-check steps using sp_high (confession review mode).
- **MCP Tool Mapping Clarity** – Execution lines now explicitly show the mapped MCP tool (e.g., "sp_analyzer MCP") for transparent debugging and usage.
- **Installation Consistency** – Ensured super:init applies .cursor/ folder contents identically across fresh installations, with comprehensive asset syncing.
- **MCP Server Conflict Resolution** – Added logic to prevent global/local MCP server conflicts, ensuring only one runtime instance executes per project.
- **Command Frontmatter Automation** – New scripts for bulk updating command metadata, persona args, and frontmatter delimiters across all assets.
- **Documentation Architecture** – Enhanced command documentation with guided execution checklists and MCP tool integration guidance.
- **SDD Workflow Integration** – Strengthened Spec-Driven Development integration with plan delegation for specialized commands (wave, ultracompressed).

## How It Works

Super Prompt provides two core entry points for Cursor integration:

- **`super-prompt`** – Command-line tool for project initialization and diagnostics
- **`sp-mcp`** – MCP server that powers AI persona capabilities in Cursor

### Key Principles

- **Language-Specific Intelligence** – Automatically detects your project's tech stack and applies optimized AI personas
- **Single Source of Truth** – Centralized persona configurations and rules
- **Performance-First Design** – Minimal latency with context-aware optimizations

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
```

### **Quality Assurance**

```bash
/super-prompt/review "Code review and validation"
/super-prompt/qa "Quality assurance checks"
/super-prompt/architect "Architecture design and validation"
```

## Documentation

For detailed technical documentation, see the [`docs/`](./docs/) directory:

- **[Architecture Overview](./docs/architecture-v5.md)** - System design and technical specifications
- **[Cursor Integration Guide](./docs/cursor-mcp-setting-guide.md)** - MCP server setup instructions
- **[Development Workflows](./docs/codex-amr.md)** - Advanced usage patterns

## Troubleshooting

| Symptom | Resolution |
| --- | --- |
| **Version shows older release (e.g., v1.0.4) after installation** | `npm view @cdw0424/super-prompt version` now returns 5.1.6, so the registry is serving the new build. When you see the banner report v1.0.4 after installation, the CLI is being launched from an older copy that's still on your machine—most often a globally installed 1.0.4 or a project lockfile pinned to that number.<br><br>**Do this once to flush the stale install:**<br><br>`npm uninstall -g @cdw0424/super-prompt   # removes the old global copy`<br>`npm cache clean --force                  # optional, clears cached tarballs`<br><br>**Then reinstall the new release (pick the style you want per project):**<br><br>`# global upgrade (if you rely on the super-prompt binary in PATH)`<br>`npm install -g @cdw0424/super-prompt@latest`<br><br>`# project-local (preferred for workspace isolation)`<br>`npm install @cdw0424/super-prompt@latest`<br>`npx @cdw0424/super-prompt@latest super:init   # or ./node_modules/.bin/super-prompt super:init`<br><br>**If the project already had a package-lock.json or npm-shrinkwrap.json, make sure it doesn't pin the old version; delete the lockfile or bump the semver entry to ^5.1.6 before reinstalling.**<br><br>**After reinstalling, rerun super:init (or ./bin/super-prompt super:init) and the banner will show v5.1.6 \| @cdw0424/super-prompt, confirming the newer code is in use.**<br><br>*Note: npm will always deliver the latest tarball, but Node's install flow can't guess your intent about existing copies. If a machine already has an older global install, the shell will keep launching that binary until it's removed or upgraded. Likewise, a project's package-lock.json can legitimately pin an older release. Automatically ripping those out during install would break reproducibility, so the CLI leaves that decision to you.*<br><br>*If you want to force the newest version every time, add a one-line script to your bootstrap (for example, in your project's postinstall):*<br><br>`"scripts": {`<br>&nbsp;&nbsp;`"postinstall": "npx --yes npm@latest install @cdw0424/super-prompt@latest"`<br>`}`<br><br>*Or, for global installs on shared machines:*<br><br>`npm install -g @cdw0424/super-prompt@latest`<br>`super-prompt super:init --force`<br><br>*That way each environment explicitly refreshes to 5.1.6 (or whatever's current) before initialization, without the tool destroying user-managed installations behind the scenes.* |
| Cursor reports "no tools available" | Check `~/.cursor/mcp.log` for `-------- MCP:` entries. If FastMCP is missing, install the runtime manually: `pip install mcp`. The fallback server will operate automatically once the CLI reconnects. |
| `sp_high` missing or duplicated | The 5.0.5 release registers a single `sp_high` backed by the persona pipeline. Restart `sp-mcp` to reload the registry. |
| Stdout parse errors | Ensure you never print to stdout in custom scripts. Super Prompt reserves stdout for JSON-RPC; use `--------`-prefixed logs on stderr. |

## Release workflow

1. `npm install` – refreshes `package-lock.json`.
2. `npm run prepack` – builds the Python wheel into `dist/` (optional for local testing).
3. `npm publish` – publishes `@cdw0424/super-prompt@5.1.6` with synchronized Python assets.

Super Prompt is MIT licensed. Contributions and issues are welcome at [https://github.com/cdw0424/super-prompt](https://github.com/cdw0424/super-prompt).
