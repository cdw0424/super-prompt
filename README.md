# Super Prompt v4.0.58: Production Ready MCP Architecture

[![npm version](https://img.shields.io/npm/v/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![npm downloads](https://img.shields.io/npm/dm/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A powerful prompt engineering toolkit, now rebuilt from the ground up as a FastMCP server for seamless IDE integration.**

Super Prompt v4 marks a fundamental shift from a command-line utility to a robust, programmatic backend for your IDE. It exposes its powerful persona-based prompt optimization engine as a set of MCP tools, enabling a fluid and integrated development experience.

---

### 🚀 The Core Concepts of v4

1.  **👑 MCP-First Architecture**: Super Prompt is now a server. All functionality, including the specialized personas, is exposed as MCP tools that your IDE can call directly. This means faster, more reliable, and more deeply integrated interactions.

2.  **🧠 Fused Intelligent Memory**: A groundbreaking dual-memory system that makes the assistant smarter over time.
    - **EvolKV Optimization**: Persists and evolves task-aware KV-cache profiles to optimize LLM inference performance.
    - **Context-Aware Memory**: Maintains task context across sessions for seamless continuity.

3.  **🕵️‍♂️ Confession Mode (double‑check)**: Radical transparency for every action. All MCP tools automatically append a self-audit to their output, detailing what is known, what is unknown (potential side-effects, edge cases), and proposing countermeasures to ensure reliability.

4.  **🔄 Mode Toggle System**: Seamless switching between GPT and Grok models with environment variables, CLI flags, and automatic resource management.

5.  **🧠 MCP Memory System**: Comprehensive span-based memory tracking across all commands with automatic error handling and health checks.

---

## 🚨 **CRITICAL PROTECTION NOTICE**

**ALL COMMANDS AND PERSONAS ARE STRICTLY PROHIBITED FROM MODIFYING:**
- `.cursor/` - Cursor IDE configuration files
- `.super-prompt/` - Super Prompt internal system files
- `.codex/` - Codex CLI configuration files

**These directories are PROTECTED and can ONLY be modified by official installation processes (`npx -y @cdw0424/super-prompt@latest super:init`). This protection is absolute and overrides any other instructions.**

---

## ⚡ Quick Start

### Install
```bash
npm i @cdw0424/super-prompt@latest
```

### Initialize (one-time)
```bash
npx -y @cdw0424/super-prompt@latest super:init
# Output:
# -------- MCP memory: healthcheck OK
# -------- init: completed
```
This command also auto‑generates `.cursor/mcp.json` so Cursor can spawn Super Prompt via stdio. No manual MCP configuration is required.

### Mode switching
```bash
# GPT
npx super-prompt --gpt --version
# Grok
npx super-prompt --grok --version
# On switch (stderr)
# -------- mode: disposed previous provider
# -------- mode: resolved to grok
```

Preferred: use `grok-mode-on` / `gpt-mode-on` commands to switch modes; they persist per‑project and take precedence over any `LLM_MODE` environment variable during project sessions.

No external API keys are required. All tools run internally within the MCP server.
The initializer sets `SUPER_PROMPT_ALLOW_INIT=true` automatically for setup tasks.

---

## 🔧 How It Works: The MCP Server

The heart of Super Prompt v4 is the MCP server. You run it, and your IDE connects to it.

-   **Spawn (Cursor)**: via `.cursor/mcp.json` using `npx -y @cdw0424/super-prompt sp-mcp`
-   **Spawn (Codex)**: via `~/.codex/config.toml` using the same `npx` + `sp-mcp` pattern
-   **Transport**: stdio only; no TCP ports
-   **Logs**: All diagnostic logs go to `stderr` (prefixed with `--------`). `stdout` is reserved for JSON‑RPC frames only.

### LLM Mode Commands (auto)
- Switch on the fly using local commands:
  - `npx -y @cdw0424/super-prompt@latest grok-mode-on`
  - `npx -y @cdw0424/super-prompt@latest gpt-mode-on`
- These persist the mode in `.super-prompt/mode.json` for project‑wide use. The MCP server also exposes tools `sp.grok_mode_on`, `sp.gpt_mode_on`, `sp.mode_get`, and `sp.mode_set`.

### Available MCP Tools

The server exposes all personas and utilities as tools. Here are a few examples:

| Tool Name         | Description                                                               |
| ----------------- | ------------------------------------------------------------------------- |
| `frontend`        | Runs the expert UI/UX persona for frontend development.                   |
| `backend`         | Runs the expert reliability engineer persona for backend tasks.           |
| `architect`       | Runs the systems architecture specialist.                                 |
| `security`        | Runs the threat modeling and vulnerability analysis persona.              |
| `set_task_context`| Sets the current task tag for the Context-Aware Memory system.            |
| `super_init`      | Initializes the `.cursor` command files in a project.                     |
| ...and 25+ more!  | All personas from v3 are available as dedicated tools.                    |


---

## 🔄 Mode Toggle System

Super Prompt v4 supports seamless switching between GPT and Grok models with comprehensive resource management.

### Environment Variables
```bash
# Set default mode
export LLM_MODE=gpt     # or 'grok'

# Enable specific modes
export ENABLE_GPT=true
export ENABLE_GROK=true

# Disable MCP client (NOOP mode)
export MCP_CLIENT_DISABLED=true
```

### CLI Flags
```bash
# Use GPT mode
npx -y @cdw0424/super-prompt@latest --gpt --version
npx -y @cdw0424/super-prompt@latest --mode=gpt super:init

# Use Grok mode
npx -y @cdw0424/super-prompt@latest --grok --version
npx -y @cdw0424/super-prompt@latest --mode=grok super:init
```

### Safety Features
- **Mutual Exclusion**: Cannot enable both GPT and Grok simultaneously
- **Resource Cleanup**: Automatic disposal of previous provider resources
- **Graceful Fallback**: NOOP mode for environments without full MCP setup

---

## 🧠 MCP Memory System

Comprehensive span-based memory tracking with automatic error handling and health checks.

### Features
- **Span Tracking**: Every command creates memory spans with start/write/end lifecycle
- **Error Handling**: Automatic error capture and span marking
- **Health Checks**: Built-in system validation spans
- **Event Logging**: Detailed event recording with timestamps

### Example Output
```
-------- memory: span started span_0 for sp.init
-------- MCP memory: healthcheck OK
-------- memory: span ended span_0 status=ok duration=1.23s
```

---

## 🔄 Migration from v3.x

Migrating from older versions is seamless. If you previously installed globally, we recommend uninstalling the global version and installing locally in your project.

```bash
# 1. Uninstall the old global package (if it exists)
npm uninstall -g @cdw0424/super-prompt

# 2. Install locally in your project
cd your-project
npm install --save-dev @cdw0424/super-prompt@latest
```
The new installation script automatically sets up the encapsulated Python virtual environment within your project's `node_modules`.

**Note**: Old files from previous versions located in your project's `.super-prompt` directory are no longer used and can be safely deleted. The new v4 databases (`evol_kv_memory.db`, `context_memory.db`) will be created in your project's `.super-prompt` directory on first use.

---

## 🛠️ Installation

### Requirements
- **Node.js**: v18.17+
- **Python**: v3.10+ (A dedicated virtual environment is created and managed automatically).

### Command (Recommended: Local Install)
```bash
npm install --save-dev @cdw0424/super-prompt@latest
```
The installer handles the creation of a self-contained Python virtual environment and all necessary dependencies within your project's `node_modules`. No manual Python package management or `sudo` is required.

### Cursor mcp.json (reference)
The initializer writes this for you under `.cursor/mcp.json`:

```
{
  "mcpServers": {
    "super-prompt": {
      "command": "npx",
  "args": ["-y", "@cdw0424/super-prompt@<installed-version>", "sp-mcp"],
  "env": {
    "SUPER_PROMPT_ALLOW_INIT": "true",
    "SUPER_PROMPT_PROJECT_ROOT": "${workspaceFolder}"
  }
    }
  }
}
```

After setup, restart Cursor and check Output → “MCP Logs”. Initialization/handshake logging appears on stderr only.

---

## 🆘 Troubleshooting

**`command not found: super-prompt` when using `npx`**

This is rare, but can happen if npm's environment is not configured correctly.
1. Ensure you are in the same directory where you ran `npm install`.
2. Try deleting `node_modules` and `package-lock.json` and running `npm install` again.

### **Using Global Install (Advanced)**
If you still prefer to install globally, you may encounter `EACCES` permission errors. **Do not use `sudo` to fix this.** The official and safest solution is to tell npm to use a directory you own.

**1. Create a directory for global packages:**
```bash
mkdir -p ~/.npm-global
```

**2. Configure npm to use the new directory path:**
```bash
npm config set prefix '~/.npm-global'
```

**3. Add the new directory to your shell's `PATH`:**
Open your shell configuration file (`.zshrc`, `.bash_profile`, or `.profile`).
```bash
# For macOS Catalina (10.15) or later (using zsh)
open ~/.zshrc

# For older macOS or most Linux distros (using bash)
open ~/.bash_profile
```
Then, add the following line to the end of the file:
```bash
export PATH=~/.npm-global/bin:$PATH
```

**4. Update your shell:**
Either restart your terminal or run the source command on your config file.
```bash
# For zsh
source ~/.zshrc

# For bash
source ~/.bash_profile
```

**5. Try installing again (without `sudo`):**
```bash
npm install -g @cdw0424/super-prompt@latest
```

---

## 📚 Documentation & Resources

-   **[Changelog](CHANGELOG.md)**: View detailed version history and updates.
-   **[Issues & Support](https://github.com/cdw0424/super-prompt/issues)**: Report bugs and request features.

## 📄 License

MIT © [Daniel Choi](https://github.com/cdw0424)


### Offline installation
- If your environment has no internet access during install or init, Super Prompt will still work using source imports.
- To explicitly skip pip activity during install/init, set one of:
  - `SUPER_PROMPT_OFFLINE=true`
  - `SP_NO_PIP_INSTALL=true`
  - Or `npm_config_offline=true` for npm postinstall
These flags create the venv without attempting network installs; the runtime falls back to `PYTHONPATH` source imports.
