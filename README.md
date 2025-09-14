# Super Prompt v4.0.0: The MCP Revolution

[![npm version](https://img.shields.io/npm/v/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![npm downloads](https://img.shields.io/npm/dm/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 💡 Project Philosophy

**Maximum Efficiency Through Model Optimization** - We pursue the utmost efficiency in both time and cost by leveraging fast, affordable models like Grok Code Fast and providing optimized modes tailored to each LLM model's strengths. Our approach maximizes productivity while minimizing resource consumption.

**A powerful prompt engineering toolkit, now rebuilt from the ground up as a FastMCP server for seamless IDE integration.**

Super Prompt v4 marks a fundamental shift from a command-line utility to a robust, programmatic backend for your IDE. It exposes its powerful persona-based prompt optimization engine as a set of MCP tools, enabling a fluid and integrated development experience.

---

### 🚀 The Core Concepts of v4

1.  **👑 MCP-First Architecture**: Super Prompt is now a server. All functionality, including the specialized personas, is exposed as MCP tools that your IDE can call directly. This means faster, more reliable, and more deeply integrated interactions.

2.  **🧠 Fused Intelligent Memory**: A groundbreaking dual-memory system that makes the assistant smarter over time.
    - **EvolKV Optimization**: Persists and evolves task-aware KV-cache profiles to optimize LLM inference performance.
    - **Context-Aware Memory**: Maintains task context across sessions for seamless continuity.

3.  **🕵️‍♂️ Confession Mode (Double Check)**: Radical transparency for every action. All MCP tools automatically append a self-audit to their output, detailing what is known, what is unknown (potential side-effects, edge cases), and proposing countermeasures to ensure reliability.

---

## ⚡ Quick Start

1.  **Install as a Dev Dependency (Recommended)**
    This is the modern, recommended way to use CLI tools. It installs `super-prompt` locally into your project, avoiding all permission issues.
    ```bash
    cd your-project
    npm install --save-dev @cdw0424/super-prompt@latest
    ```

2.  **Initialize Your Project**
    Use `npx` to run the locally installed `super-prompt`. This command generates the necessary `.cursor/` files for IDE integration.
    ```bash
    npx super-prompt init
    ```

3.  **Configure and Run the MCP Server in Your IDE**
    For Super Prompt to work, your IDE (e.g., Cursor) must be configured to run its MCP server. Since `super-prompt` is installed locally, the command should also use `npx`.

    - **Example Cursor MCP Server Configuration**:
        - **Name**: `super-prompt (local)`
        - **Command**: `npx`
        - **Arguments**: `["super-prompt", "mcp:serve"]`

4.  **Use Personas in Your IDE**
    With the server running, you can now use the slash commands in your IDE's chat to invoke the persona tools.
    ```
    /frontend "Build a responsive login form using React and Tailwind CSS."
    /architect "Design a scalable microservices architecture for an e-commerce platform."
    /backend "Write a NodeJS endpoint to handle user registration."
    ```

---

## 🔧 How It Works: The MCP Server

The heart of Super Prompt v4 is the MCP server. You run it, and your IDE connects to it.

-   **Start the server**: `super-prompt mcp:serve`
-   **Transport**: The server uses `stdio` for communication, so no network ports are required.
-   **Logs**: All diagnostic logs are sent to `stderr` (prefixed with `-----`), while `stdout` is reserved for clean MCP communication.

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

## 🔄 Migration from v3.x

### 🚨 **Clean Migration Required**

**IMPORTANT**: To avoid conflicts, you **MUST** delete old Super Prompt directories before upgrading.

```bash
# 1. REQUIRED: Clean up old versions first
rm -rf .super-prompt/        # Delete project-local Super Prompt directory
rm -rf .cursor/commands/super-prompt/  # Delete old Cursor commands
rm -rf .cursor/rules/*-sdd*.mdc        # Delete old SDD rules

# 2. Uninstall old global package (if installed)
npm uninstall -g @cdw0424/super-prompt

# 3. Install the latest version locally in your project
cd your-project
npm install --save-dev @cdw0424/super-prompt@latest

# 4. Initialize with all new features
npx super-prompt init
```

### ✅ **What Gets Automatically Installed**

After running `npx super-prompt init`, you'll have:

- **🎯 25+ Persona Commands**: All specialist AI personas ready to use
  - `/architect`, `/frontend`, `/backend`, `/security`, `/performance`
  - `/grok-mode-on`, `/gpt-mode-on`, `/seq`, `/ultracompressed`
  - And many more!

  - Model‑specific guidance is auto‑installed with mode toggles:
    - `/gpt-mode-on` installs GPT‑5 guidance rules for all personas
    - `/grok-mode-on` installs Grok guidance rules for all personas
    - Turning a mode off removes its guidance rules

  - Persona manifest (canonical): `packages/cursor-assets/manifests/personas.yaml`
    - Use `super-prompt personas-init` to copy a project-local editable copy to `personas/manifest.yaml` if needed.

### 🧠 AMR (Global) via MCP

- AMR applies to all LLM interactions and all commands. Use these MCP tools to operationalize the flow:
  - `amr_repo_overview(project_root)` → Lightweight repo map (languages, frameworks, tests, important files)
  - `amr_handoff_brief(project_root, query)` → Concise brief for handing off to a high‑reasoning model
  - `amr_qa(file_path)` → Validate transcript for AMR/state-machine conformance
  - Model toggles: `gpt_mode_on/off`, `grok_mode_on/off`

- Recommended AMR flow:
  1) Small/medium model calls `amr_repo_overview` → organizes context
  2) Call `amr_handoff_brief` → produce a compact brief
  3) Escalate for reasoning/execution if heavy: `/model gpt-5 high` (exec); otherwise stay medium
  4) After high execution, return to medium; continue implementation
  5) Use `amr_qa` to validate transcript

- **⚙️ MCP Server Ready**: Configure your IDE to use the MCP server:
  - **Command**: `npx super-prompt mcp:serve`
  - **Transport**: `stdio`

- **📁 Clean Project Structure**: No conflicting old files or configurations

### ⚠️ **Why Clean Installation is Required**

- **Architecture Change**: v4 uses a completely new MCP-first architecture
- **File Conflicts**: Old `.super-prompt/` files can interfere with new functionality
- **Command Updates**: Persona commands have been completely rewritten
- **Database Migration**: New memory system uses different database schemas

The new installation script automatically sets up the encapsulated Python virtual environment and all MCP components.

---

## 🛠️ Installation

### Requirements
- **Node.js**: v14+
- **Python**: v3.10+ (A dedicated virtual environment is created and managed automatically).

### Command (Recommended: Local Install)
```bash
npm install --save-dev @cdw0424/super-prompt@latest
```
The installer handles the creation of a self-contained Python virtual environment and all necessary dependencies within your project's `node_modules`. No manual Python package management or `sudo` is required.

---

## 🧩 Architecture

- Core Principles
  - MCP-first: All functionality is exposed as MCP tools over stdio.
  - AMR everywhere: Auto Model Router rules apply to all LLM interactions and commands.
  - Model-optimized personas: Guidance rules auto-install per model mode (GPT‑5, Grok) with strict mutual exclusivity.
  - Minimal, focused code changes: Diff-first execution with clear VERIFY and REPORT.
  - SSOT first: Single Source of Truth is personas manifest → .cursor/rules → AGENTS.md; avoid drift and duplication.

- Components
  - Node Wrapper (`bin/super-prompt`)
    - Launches Python entry via isolated venv, ensures consistent runtime.
  - Python Core (`packages/core-py/super_prompt/`)
    - `mcp_srv/server.py`: FastMCP server exposing all tools.
    - `modes.py`: Model mode toggles + guidance rule management (mutual exclusivity).
    - `commands/`: MCP-first tool modules
      - `amr_repo_tools.py`: Repo overview, handoff brief (small→large model)
      - `amr_tools.py`: AMR QA (state machine/regression checks)
      - `context_tools.py`: Context collect/stats/clear
      - `validate_tools.py`: Validation (todo/check)
      - `personas_tools.py`: Personas init/build
      - `codex_tools.py`: Codex assets init
    - `adapters/`: Cursor/Codex adapters for project assets
  - Cursor Assets
    - Rules: `.cursor/rules/12-amr.mdc` (global), plus GPT‑5/Grok guidance rules when modes are toggled.
    - Commands: `.cursor/commands/super-prompt/*.md` for quick access.
  - Personas Manifest
    - Canonical: `packages/cursor-assets/manifests/personas.yaml`
    - Optionally copy to project via `super-prompt personas-init`.
    - Supports per‑model overrides under `model_overrides` (e.g., `gpt`, `grok`). Mode toggles materialize these into `.cursor/rules/21-persona-overrides.mdc`.
    - Personas are pre‑defined. Dynamic persona generation is disabled; commands are created strictly from the manifest/templates for consistency.

- AMR Routing
  - Default medium reasoning; classify tasks L0/L1/H.
  - Heavy reasoning → switch to `gpt-5 high` for PLAN/REVIEW or EXECUTION as needed, then return to medium.
  - Small model organizes repo context via MCP tools; passes concise handoff brief to high reasoning.

### Model Modes
- GPT Mode (`/gpt-mode-on`)
  - Installs global GPT‑5 guidance and materializes persona `model_overrides.gpt` into `.cursor/rules/21-persona-overrides.mdc`.
  - Avoid conflicting instructions; use XML-like structure; calibrate reasoning effort; self‑reflection; persistence; SSOT first.

- Grok Mode (`/grok-mode-on`)
  - Installs Grok guidance and materializes persona `model_overrides.grok`.
  - Provide necessary, scoped context; explicit goals; iterate rapidly; prefer native tool-calling; structure context; optimize for cache hits; SSOT first.

- Mode Management
  - `/gpt-mode-on` installs GPT‑5 guidance and removes Grok guidance.
  - `/grok-mode-on` installs Grok guidance and removes GPT‑5 guidance.
  - Modes are strictly mutually exclusive and persisted under `.cursor`.

- Installation Behavior
  - `install.js` sets up a venv and installs `super_prompt` from wheel if present, else from source, ensuring CLI/MCP availability.

## 🧠 Memory System

- Context Cache
  - File cache under `.super-prompt/cache/context_cache.json` speeds up context collection.
  - Tools: `context_stats`, `context_clear`.

- Persistent Memory (SQLite)
  - DB path: `.super-prompt/data/context_memory.db`
  - Key‑Value store and Event log for lightweight state.
  - MCP tools:
    - `memory_set(key, value)`, `memory_get(key)`
    - `memory_set_task(tag)`, `memory_get_task()`
    - `memory_append_event(type, payloadJSON)`, `memory_recent(limit)`

- AMR Integration
  - `amr_persona_orchestrate` includes the current `task_tag` from memory and returns a suggested flow (with high/medium reasoning guidance).
  - You can set `task_tag` at the start of a session to keep context across turns.

## ✅ SSOT (Single Source of Truth)
- Order of authority:
  1) Personas manifest (canonical or project override)
  2) `.cursor/rules/*.mdc` (materialized guidance, modes, overrides)
  3) `AGENTS.md` and related docs
- Do not duplicate configuration; reference SSOT to avoid drift.
- Mode toggles write overrides to rules; do not inline divergent copies.

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
