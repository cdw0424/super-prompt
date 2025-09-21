# Super Prompt v5.0.0: Pure Python MCP Dual IDE Prompt Engineering Toolkit

## 🚀 **v5.0.0 Major Architecture Revolution**

**Complete transformation to prompt-based workflow architecture with stateless MCP design!**

### ✨ **What's New in v5.0.0**
- **🔄 Prompt-Based Workflow**: All 20+ persona functions converted to prompt-based architecture
- **🎯 Mode-Specific Optimization**: Specialized GPT/Grok prompt templates for enhanced reasoning
- **🧹 Architecture Cleanup**: Removed unnecessary pipeline code, optimized for performance
- **⚡ Performance Enhancement**: Simplified architecture delivers faster response times
- **🏗️ Stateless MCP Server**: Refactored MCP server with modular design and improved reliability

[![PyPI version](https://img.shields.io/pypi/v/super-prompt-core.svg)](https://pypi.org/project/super-prompt-core/)
[![Python versions](https://img.shields.io/pypi/pyversions/super-prompt-core.svg)](https://pypi.org/project/super-prompt-core/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**🚀 The Ultimate Dual IDE Prompt Engineering Toolkit with Pure Python MCP Implementation**

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

### 🏗️ **New Architecture: Prompt-Based Workflow v5.0.0**

#### **🔄 Complete Prompt-Based Transformation**
- **Before**: Complex `_run_persona_pipeline` + `_PIPELINE_CONFIGS` architecture
- **After**: Simple `run_prompt_based_workflow` + specialized prompt templates
- **Impact**: All 20+ persona functions now use streamlined prompt-based execution

#### **🎯 Mode-Specific Optimization**
- **GPT Mode**: Structured analysis, practical solutions, systematic approaches
- **Grok Mode**: Maximum truth-seeking analysis, realistic considerations, innovative thinking

#### **📈 Performance & Efficiency Gains**
- Eliminated unnecessary pipeline logic and complex routing
- Template-based execution for rapid response times
- Reduced memory footprint and improved resource utilization
- **40 specialized prompt templates** (20 GPT + 20 Grok) for optimal performance

### 🧭 Philosophy

- **Command First**: Explicit commands/flags take precedence and are executed immediately.
- **SSOT**: Single Source of Truth — personas manifest → `.cursor/rules` → `AGENTS.md`.
- **SDD**: Spec → Plan → Implement, with Acceptance Self-Check before merge.
- **AMR**: Default to medium reasoning; switch to high for deep planning; return to medium for execution.
- **Safety**: English logs start with `-----`; never print secrets (mask like `sk-***`).
- **Prompt-Based Architecture**: All persona functions converted to prompt-based workflow for optimal performance.
- **Stateless MCP Design**: Modular MCP server architecture with improved reliability and maintainability.

This philosophy powers a dual‑IDE workflow (Cursor + Codex) and underpins our model recommendation below for consistent, fast, and reliable results.

### 🗂️ **Legacy Files Removal Guide (v5.0.0 Upgrade)**

#### **Safe to Remove Legacy Files**
After upgrading to v5.0.0, these legacy files can be safely removed:

```bash
# Remove legacy pipeline and infrastructure files
rm -rf packages/core-py/super_prompt/engine/pipeline/  # Old pipeline code
rm -rf packages/core-py/super_prompt/core/pipeline.py  # Legacy pipeline configs
rm -f packages/core-py/super_prompt/mcp/mcp_server.py # Old server with PID management
rm -f packages/core-py/super_prompt/mcp_server_new.py # Deprecated server version
rm -f bin/sp-mcp-legacy                              # Legacy MCP launcher

# Remove obsolete CLI wrappers
rm -f bin/sp                                        # Old wrapper script
rm -f bin/codex-*                                    # Legacy codex commands
```

#### **Files to Keep (Still Required)**
```bash
# Core Python MCP server (refactored)
packages/core-py/super_prompt/mcp_app.py          # New modular MCP app
packages/core-py/super_prompt/mcp_stdio.py        # Minimal wrapper

# Prompt templates (new architecture)
packages/core-py/super_prompt/prompts/            # All 40 prompt templates
packages/core-py/super_prompt/personas/           # Updated persona configs

# Configuration and assets
.cursor/commands/                                  # Cursor command definitions
.cursor/rules/                                     # Rules and templates
personas/manifest.yaml                            # SSOT persona manifest
```

### 🚀 **Post-Upgrade Commands & Usage**

#### **1. Update Installation**
```bash
# Update to v5.0.0
npm install @cdw0424/super-prompt@latest

# Or install fresh (recommended)
npm install @cdw0424/super-prompt@5.0.0
```

#### **2. Initialize Project Assets**
```bash
# Clean initialization with new architecture
super-prompt super:init --force

# Verify MCP server health
super-prompt mcp doctor
```

#### **3. New Command Usage Patterns**
```bash
# All personas now use prompt-based execution
/super-prompt/architect "design API system"     # Faster, streamlined
/super-prompt/dev "implement authentication"    # Optimized templates
/super-prompt/high "analyze system requirements" # Enhanced reasoning

# Mode switching (persisted to .super-prompt/mode.json)
/super-prompt/gpt-mode-on                        # GPT mode activation
/super-prompt/grok-mode-on                       # Grok mode activation
```

#### **4. MCP Server Commands**
```bash
# List all available tools (24 comprehensive tools)
super-prompt mcp list-tools

# Interactive tool execution
super-prompt mcp call sp.architect --interactive

# Direct tool calls with JSON arguments
super-prompt mcp call sp.dev --args-json '{"query": "optimize database queries"}'
```

#### **5. Legacy Command Migration**
```bash
# Old → New command mapping
super-prompt --persona-analyzer "..."   →   /super-prompt/analyzer "..."
super-prompt --sp-architect "..."       →   /super-prompt/architect "..."
super-prompt codex-mode-on             →   /super-prompt/gpt-mode-on
```

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
# ⭐ Recommended: Python-only installation (Pure Python MCP implementation)
pip install super-prompt-core

# Installation verification
super-prompt --help
super-prompt mcp --help
```

### 2) Initialize project assets

```bash
# Project initialization (automatic asset configuration)
super-prompt super:init

# Or run Python module directly
python -m super_prompt super:init
```

### 3) MCP Client Usage

```bash
# MCP server health check
super-prompt mcp doctor

# List available tools
super-prompt mcp list-tools

# Tool calls (interactive mode)
super-prompt mcp call sp.list_commands --interactive

# Tool calls (JSON arguments)
super-prompt mcp call sp.architect --args-json '{"query": "design user auth system"}'
```

### 4) Enable in Cursor (MCP)

Open Cursor → Settings → MCP and enable the Super‑Prompt server (restart Cursor
if needed). After enabling, slash commands will autocomplete in chat.

MCP details (stdio)
- Transport: stdio (local child process). Cursor also supports HTTP/SSE, but stdio is recommended for local development. citeturn0search1
- Config locations: project `.cursor/mcp.json` (recommended) or global `~/.cursor/mcp.json`. Same schema in both. citeturn0search1turn0search2
- Minimal config:

```
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

Programmatic registration: Cursor exposes an Extension API (`vscode.cursor.mcp.registerServer`) for dynamic registration from extensions, useful in enterprise setups. citeturn0search3

### 4.1) MCP Inspector for Local STDIO Server Debugging (Optional)

```
# Run from project root
npx @modelcontextprotocol/inspector node ./bin/sp-mcp

# Access http://localhost:6274 in browser → Test tool calls
```

Inspector is a browser-based debugger for visually inspecting stdio MCP server interactions. Requires Node 22+. citeturn0search3

### 5) Model Modes (GPT vs Grok)

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

### 6) Codex Dependencies (for High Reasoning)

The `sp_high` tool uses **CLI-only execution** with automatic setup and authentication. It always starts with `sudo npm install` and handles login automatically.

#### Prerequisites
- **OpenAI CLI**: Install via `pip install openai`
- **Codex CLI**: Will be installed automatically via `sudo npm install -g @openai/codex@latest`
- **OpenAI Login**: Will be prompted automatically if not logged in
- **sudo access**: Required for npm global installation

#### How It Works
1. **Always Update CLI**: `sudo npm install -g @openai/codex@latest` (runs every time)
2. **Check Login Status**: `openai api keys.list`
3. **Auto Login**: If not logged in, launches `openai login` interactively
4. **Retry After Login**: If login succeeds, retries the entire process
5. **Execute Query**: Runs `openai codex high-plan` with your query

#### Execution Flow
```bash
# Every time you run /high:
sudo npm install -g @openai/codex@latest  # Always first
openai api keys.list                      # Check login
# If not logged in:
openai login                             # Interactive login
# Then retry from step 1
openai codex high-plan                   # Execute query
```

#### Troubleshooting sp_high Errors

If you encounter errors:

```bash
# Manual setup (if automatic fails)
pip install openai
sudo npm install -g @openai/codex@latest
openai login

# Check status
python -c "from super_prompt.codex.client import get_codex_status; import json; print(json.dumps(get_codex_status(), indent=2))"
```

Common error messages and solutions:
- **"sudo: command not found"**: Install sudo or run as root
- **"npm: command not found"**: Install Node.js and npm
- **"Codex login failed"**: Run `openai login` manually
- **"Permission denied"**: Ensure you have sudo access or run as root

**Note**: The tool always updates the CLI first and handles authentication automatically.

The enhanced error handling provides actionable hints to resolve dependency issues quickly.

### 7) Use in Cursor IDE

1. Set models as recommended above (GPT‑5 Codex low fast max + Grok Code fast
   max).
2. In Cursor chat, use slash commands:

```
 /super-prompt/architect "design a REST API"
/super-prompt/dev "implement authentication"
```

### 8) Use in Codex (flag commands)

In Codex, enter flags directly in chat (no `super-prompt` prefix). Recommended
flags use the `--sp-` prefix (both forms are accepted):

```
--sp-architect "design a REST API"
--sp-dev "implement authentication"
```

### 9) CLI usage

#### Python MCP Client (Recommended)

```bash
# List tools
python -m super_prompt.mcp_client list-tools

# Tool calls
python -m super_prompt.mcp_client call sp.architect --args-json '{"query": "design a REST API"}'

# List prompts
python -m super_prompt.mcp_client list-prompts

# Health diagnostics
python -m super_prompt.mcp_client doctor
```

#### Typer CLI (Python Package Installation)

```bash
super-prompt --version
super-prompt mcp-serve
super-prompt super:init
super-prompt doctor
super-prompt mcp list-tools
super-prompt mcp call sp.architect --args-json '{"query": "design a REST API"}'
```

#### NPM CLI (Legacy Method - Still Supported)

```bash
npx super-prompt --version
npx super-prompt mcp-serve
super-prompt --version  # For global installation
```

### 📦 Architecture (v5.0.0)

Super Prompt v5.0.0 adopts **Python-first architecture** with complete npm ecosystem support:

```
super-prompt/
├── bin/
│   ├── super-prompt        # Bash CLI (npm compatible)
│   └── sp-mcp             # Python MCP server launcher
├── packages/core-py/
│   ├── super_prompt/      # Python MCP server (core logic)
│   │   ├── mcp_app.py     # 🆕 Modular MCP application
│   │   ├── mcp_stdio.py   # 🆕 Minimal STDIO wrapper
│   │   └── cli.py         # Typer CLI with MCP commands
│   └── tests/             # Unit tests
├── packages/cursor-assets/  # IDE integration files
└── install.js             # Python environment auto-configuration
```

**Architecture Design Principles (v5.0.0):**
- 🐍 **Python First**: Pure Python MCP client implementation
- ⚡ **Performance Optimized**: Leveraging Python's high-performance MCP SDK
- 🔧 **Auto-Configuration**: Automatic Python MCP client setup during npm installation
- 🚀 **Prompt-Based Workflow**: Complete transition to template-based execution
- 🏗️ **Stateless MCP Server**: Modular design with improved reliability

### Unified MCP pipeline

- Every `/super-prompt/<persona>` command now routes through a shared
  `sp.pipeline` helper.
- The pipeline always performs: memory lookup → prompt/context analysis →
  Codex/persona execution → plan + execution guidance → confession double-check
  → memory update.

---

## 🛠️ Available Tools (v5.0.0 - All Complete!)

### Core Development (완전 구현 ✅)

- `architect` - System architecture design and technical planning
- `backend` - Backend development, APIs, databases, security
- `frontend` - Frontend development, UI/UX, responsive design
- `dev` - Full-stack development and implementation planning
- `refactorer` - Code refactoring and quality improvement
- `optimize` - Performance optimization and bottleneck analysis
- `implement` - Implementation planning and execution strategy

### Quality & Analysis (완전 구현 ✅)

- `analyzer` - Systematic root cause analysis and problem solving
- `security` - Security analysis, threat modeling, compliance
- `performance` - Performance optimization and monitoring
- `qa` - Quality assurance, testing strategies, automation
- `review` - Code review, quality assessment, improvement recommendations
- `db-expert` - Database design, optimization, and scalability

### Advanced & Specialized (완전 구현 ✅)

- `high` - Strategic analysis, executive summaries, big-picture thinking
- `doc-master` - Documentation architecture and technical writing
- `mentor` - Developer mentoring and skill development
- `scribe` - Technical writing and content creation
- `debate` - Strategic debate and critical analysis
- `seq` - Sequential reasoning and step-by-step analysis
- `seq-ultra` - Ultra-detailed sequential reasoning and optimization
- `ultracompressed` - Maximum insight with minimum words
- `wave` - Trend analysis and market forecasting
- `service-planner` - Service design and customer experience planning
- `tr` - Translation and localization
- `docs-refector` - Documentation organization and maintenance

### DevOps & Infrastructure (완전 구현 ✅)

- `devops` - DevOps engineering, CI/CD, infrastructure automation

---

## 📚 Links

- **[Changelog](CHANGELOG.md)**: Version history
- **[Issues](https://github.com/cdw0424/super-prompt/issues)**: Report bugs

## 📄 License

MIT © [Daniel Choi](https://github.com/cdw0424)
