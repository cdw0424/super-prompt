# Super Prompt v3

[![npm version](https://img.shields.io/npm/v/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![npm downloads](https://img.shields.io/npm/dm/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Production-ready prompt engineering toolkit** supporting both **Cursor IDE** and **Codex CLI** with **Spec-Driven Development (SDD)** workflow and **Auto Model Router (AMR)** for intelligent reasoning optimization.

- [x] **Latest**: v3.1.65 - Flag-only mode + minimal `sp`.
- [ ] **Next**: v3.1.66 - Enhanced error handling and user experience improvements.

<br>

## v3.1.60 - Canonical tag executor across all paths
- Fixed: `super:init` now writes the same canonical tag-executor wrapper as templates/installer (no newline/comment drift).
- Verified: Generated command files point to the canonical wrapper consistently.

## v3.1.61 - Rules from templates + pkg fix
- Fixed: All rule files under `.cursor/rules` are now copied from packaged templates for perfect consistency; no more dynamic drift in `super:init`.
- Chore: Ran `npm pkg fix` to normalize `bin` entries and tidy package metadata.

## v3.1.62 - Exact tag-executor byte match
- Fixed: `super:init` now writes `tag-executor.sh` without a trailing newline to exactly match the shipped template (byte-for-byte).

## v3.1.63 - Persona flag reliability
- Fixed: `--sp-<persona>` flags (e.g., `--sp-analyzer`) now work on clean systems by auto‑ensuring PyYAML before executing the enhanced persona processor.

## v3.1.64 - Works without global super-prompt
- Feature: Cursor tag executor prefers project-local Python CLI (`.super-prompt/cli.py`), then falls back to global binary or `npx`. This enables fully offline, no-global install usage.

## v3.1.59 - CANONICAL TAG EXECUTOR & DRIFT FIX
- Fixed: Eliminated file drift between published package and project-generated assets (Cursor tag-executor).
- Fixed: `install.js` and `super:init` now install the same canonical tag executor wrapper.
- Refactor: Simplified `tag-executor.sh` to delegate to `super-prompt optimize` (or `npx` fallback) to avoid future divergence.

## v3.1.58 - UNIFIED CLI EXECUTOR & VERSION FIX
- **🐛 FIXED**: `super-prompt init` now correctly displays the latest dynamic version instead of the outdated `v2.9.1`.
- **🛠️ REFACTORED**: Unified all CLI command executions to a single, consistent entry point, eliminating architectural debt and preventing future version drift.
- **🧹 CLEANED**: Removed obsolete legacy files and redundant code from the installation process, resulting in a cleaner and more reliable package.

## v3.1.56 - DYNAMIC VERSION DISPLAY & ENHANCED ANALYZER COMMAND
- **📊 DYNAMIC VERSION DISPLAY**: Added automatic version detection from package.json for accurate version display in CLI
- **🔍 ENHANCED ANALYZER COMMAND**: Improved analyzer command description with more detailed capabilities and expertise areas

## 📜 Overview

## ⚡ Quick Start (No global install required)

```bash
# 1) Initialize in your project (recommended, no global install)
cd your-project
npx -y @cdw0424/super-prompt@latest super:init

# Optional: initialize Codex CLI assets (AGENTS.md, bootstrap, wrappers)
npm run codex:init

# 2) Use Cursor IDE slash commands
/grok-on (or /grok-mode-on)
/codex-on (or /codex-mode-on)
/architect "design user authentication system"
/frontend "create responsive dashboard"

# 3) CLI flags (optional)
# After init, tag executor prefers the project-local Python CLI automatically
super-prompt --sp-architect "design microservices architecture" || \
  npx @cdw0424/super-prompt --sp-architect "design microservices architecture"

# 4) Codex CLI pairing (optional)
# Plan at high effort, execute at medium
npm run codex:plan -- "Plan complex refactor across modules"
npm run codex:exec -- "Apply patch and run tests"
```

## ✨ Key Features

🎯 **Dual IDE Support**: Seamless integration with both Cursor (slash commands) and Codex CLI (flag-based personas)

🧠 **AMR (Auto Model Router)**: Intelligent medium↔high reasoning switching with fixed state machine

🚀 **SDD Workflow**: Complete Spec-Driven Development pipeline with quality gates

🎭 **29+ Specialized Personas**: Domain experts (architect, frontend, backend, security, performance, etc.)

🛡️ **Production Ready**: Global write protection, validation, testing, and quality assurance

⚡ **Performance Optimized**: 30-50% token reduction through intelligent context engineering

🤖 **Grok-Optimized**: Specially optimized for [grok-code-fast-1 MAX mode] in Cursor IDE

🔧 **Codex AMR Mode**: Toggle codex-amr mode for intelligent task classification and reasoning level switching

🔄 **Exclusive Mode Switching**: Grok and Codex modes are mutually exclusive - enabling one automatically disables the other
🧭 **Codex CLI Integration**: Scaffold `.codex/` assets (AGENTS.md, bootstrap prompt, router checks) and wrappers for high/medium execution

## 🎭 Popular Personas

| Persona | Description | Use Case |
|---------|-------------|----------|
| **`/architect`** | Systems architecture specialist | System design, scalability planning |
| **`/frontend`** | UI/UX specialist, accessibility advocate | React components, responsive design |
| **`/backend`** | Reliability engineer, API specialist | Server-side development, APIs |
| **`/security`** | Threat modeler, vulnerability specialist | Security audits, threat analysis |
| **`/analyzer`** | Root cause specialist | Debugging, investigation |
| **`/doc-master`** | Documentation specialist | Comprehensive documentation creation |
| **`/qa`** | Quality advocate, testing specialist | Test strategies, quality assurance |

## 🚀 Quick Examples

### Cursor IDE Integration
```bash
# Architecture & Planning
/architect "design user authentication system"
/specify "user registration workflow"

# Development
/frontend "create responsive dashboard component"
/backend "implement REST API for user management"

# Quality & Analysis
/analyzer "investigate performance bottleneck"
/doc-master "create comprehensive API documentation"
/security "audit authentication implementation"
```

### CLI Usage
```bash
# Development workflow
--sp-sdd-spec "user authentication"
--sp-sdd-plan "user registration workflow"
--sp-sdd-implement "authentication system"

# Direct persona consultation
# Preferred minimal command for Codex: just use flags with `sp`
sp --sp-architect "design microservices architecture"
sp --sp-doc-master "create comprehensive project documentation"
sp --sp-security  "review API security"
sp --sp-tr         "triage failing CI job and propose fix"

# Also works with global/local super-prompt
super-prompt --sp-architect "design microservices architecture"
super-prompt --sp-doc-master "create comprehensive project documentation"
super-prompt --sp-security  "review API security"

# Codex CLI helpers
npm run codex:init   # writes .codex/AGENTS.md, bootstrap prompt, router-check
npm run codex:plan -- "deep planning (high)"
npm run codex:exec -- "execute steps (medium)"

# Flag‑only mode (no 'sp' or 'super-prompt' prefix)
# This makes "--sp-analyzer \"...\"" work as a command in your shell
sp-setup-shell   # run once, then restart your terminal (bash/zsh)
--sp-analyzer "investigate CPU usage spikes in logs"
```

## 🏗️ SDD Workflow

**Spec-Driven Development** with automated quality gates:

```bash
# 1. Create specification
super-prompt --sp-sdd-spec "feature description"

# 2. Generate implementation plan
super-prompt --sp-sdd-plan "feature description"

# 3. Break down into tasks
super-prompt --sp-sdd-tasks "feature description"

# 4. Implement with quality gates
super-prompt --sp-sdd-implement "feature description"
```

## 🔧 Installation & Setup

### Requirements
- **Node.js** 14+
- **Python** 3.10+ (auto-installed via virtual environment)

### Installation
```bash
# Option A (recommended): No global install
cd your-project
npx -y @cdw0424/super-prompt@latest super:init

# Option B: Local devDependency
npm install -D @cdw0424/super-prompt@latest
./node_modules/.bin/super-prompt super:init

# Option C: Global install (optional)
npm install -g @cdw0424/super-prompt@latest
super-prompt super:init
```

### What gets installed?
- **Project**: All files go into `.super-prompt/` folder only
- **Python**: Isolated virtual environment in `.super-prompt/venv/`
- **Databases**: SQLite and data files in `.super-prompt/venv/data/`
- **Global (optional)**: The `super-prompt` CLI command

### ⚠️ Important: Run in Your Project Directory
**Always run `super-prompt super:init` in your project's root directory** where you want to add Super Prompt integration.

### 🔄 Automatic Migration
Super Prompt v3.1.19+ automatically handles legacy installations:
- **✅ Detects** old Homebrew symlinks and configurations
- **✅ Migrates** to user-owned npm global directory (no sudo needed)
- **✅ Configures** shell PATH automatically
- **✅ Works** immediately after `npm install -g @cdw0424/super-prompt@latest`

### IDE Integration

**Cursor IDE** (Automatic):
- Run `super-prompt init` to generate slash commands
- Use `/architect`, `/frontend`, `/backend`, etc.

**Codex CLI** (Manual):
```bash
# Install Codex CLI
npm install -g @openai/codex

# Use with Super Prompt
super-prompt --sp-high "analyze this codebase"
```

## 🆘 Troubleshooting

### Common Issues

**Command not found: `super-prompt`**
```bash
# 1. Check if installed
which super-prompt
npm list -g @cdw0424/super-prompt

# 2. If not found, reinstall
npm install -g @cdw0424/super-prompt@latest

# 3. On some systems, you may need sudo
sudo npm install -g @cdw0424/super-prompt@latest

# 4. Restart terminal after installation
```

**Alternative installation methods:**
```bash
# Use npx (no global install needed) - RUN IN YOUR PROJECT DIRECTORY
cd your-project
npx @cdw0424/super-prompt@latest super:init

# Or install locally in project
npm install @cdw0424/super-prompt@latest
./node_modules/.bin/super-prompt super:init
```

**npm EEXIST/EACCES during global install (cache permission):**
```bash
# Best: Avoid global install — use npx or local devDependency (see above)

# If you still want global install, set a user cache and retry
npm config set cache "$HOME/.npm-cache" --global
npm cache clean --force
npm install -g @cdw0424/super-prompt@latest

# One‑shot alternative
npm_config_cache="$HOME/.npm-cache" npm install -g @cdw0424/super-prompt@latest

# If /tmp/.npm-cache is corrupted and you have permissions
rm -rf /tmp/.npm-cache
```

**Python dependencies & environment issues:**
```bash
# Super Prompt automatically creates virtual environment
# If you see "externally-managed-environment" error:

# Method 1: Use the built-in virtual environment (recommended)
super-prompt super:init  # Creates .super-prompt/venv automatically

# Method 2: If issues persist, check venv setup
cd your-project/.super-prompt/venv/bin
python -c "import typer, yaml, pathspec; print('Dependencies OK')"

# Method 3: Manual venv setup (if needed)
cd your-project/.super-prompt
python3 -m venv venv
source venv/bin/activate
pip install typer>=0.9.0 pyyaml>=6.0 pathspec>=0.11.0
```

**For macOS Homebrew users:**
```bash
# If you get externally-managed-environment errors
# Super Prompt handles this automatically with virtual environments
# Just run super-prompt super:init and it will set everything up
```

## 📚 Documentation

📖 **[Complete Documentation](https://github.com/cdw0424/super-prompt/blob/main/ARCHITECTURE.md)** - Detailed architecture and advanced usage

📋 **[Changelog](https://github.com/cdw0424/super-prompt/blob/main/CHANGELOG.md)** - Version history and updates

🐛 **[Issues & Support](https://github.com/cdw0424/super-prompt/issues)** - Bug reports and feature requests

## 📄 License

MIT © [Daniel Choi](https://github.com/cdw0424)

---

<div align="center">

**🚀 Ready to supercharge your development workflow?**

[Install Now](#-installation--setup) • [View Documentation](https://github.com/cdw0424/super-prompt/blob/main/ARCHITECTURE.md) • [Report Issues](https://github.com/cdw0424/super-prompt/issues)

</div>
