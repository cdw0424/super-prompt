# Super Prompt v3

[![npm version](https://img.shields.io/npm/v/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![npm downloads](https://img.shields.io/npm/dm/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Production-ready prompt engineering toolkit** supporting both **Cursor IDE** and **Codex CLI** with **Spec-Driven Development (SDD)** workflow and **Auto Model Router (AMR)** for intelligent reasoning optimization.

🚀 **Latest**: v3.1.30 - Enhanced persona system with mandatory core development principles including SOLID, TDD/BDD, Clean Architecture, confession & double-check methodology, and quality assurance standards.

## ⚡ Quick Start

```bash
# Install globally (always use @latest for automatic updates)
npm install -g @cdw0424/super-prompt@latest

# Go to your project directory and initialize
cd your-project
super-prompt super:init

# Use with Cursor IDE
/architect "design user authentication system"
/frontend "create responsive dashboard"

# Use with CLI flags
super-prompt --sp-architect "design microservices architecture"
super-prompt --sp-frontend "optimize React performance"
```

## ✨ Key Features

🎯 **Dual IDE Support**: Seamless integration with both Cursor (slash commands) and Codex CLI (flag-based personas)

🧠 **AMR (Auto Model Router)**: Intelligent medium↔high reasoning switching with fixed state machine

🚀 **SDD Workflow**: Complete Spec-Driven Development pipeline with quality gates

🎭 **29+ Specialized Personas**: Domain experts (architect, frontend, backend, security, performance, etc.)

🛡️ **Production Ready**: Global write protection, validation, testing, and quality assurance

⚡ **Performance Optimized**: 30-50% token reduction through intelligent context engineering

## 🎭 Popular Personas

| Persona | Description | Use Case |
|---------|-------------|----------|
| **`/architect`** | Systems architecture specialist | System design, scalability planning |
| **`/frontend`** | UI/UX specialist, accessibility advocate | React components, responsive design |
| **`/backend`** | Reliability engineer, API specialist | Server-side development, APIs |
| **`/security`** | Threat modeler, vulnerability specialist | Security audits, threat analysis |
| **`/analyzer`** | Root cause specialist | Debugging, investigation |
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
/security "audit authentication implementation"
```

### CLI Usage
```bash
# Development workflow
super-prompt --sp-sdd-spec "user authentication"
super-prompt --sp-sdd-plan "user registration workflow"
super-prompt --sp-sdd-implement "authentication system"

# Direct persona consultation
super-prompt --sp-architect "design microservices architecture"
super-prompt --sp-security "review API security"
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
# Install globally (always use @latest for automatic updates)
npm install -g @cdw0424/super-prompt@latest

# Go to YOUR PROJECT directory and initialize (creates .super-prompt folder only)
cd your-project
super-prompt super:init

# Verify installation
super-prompt --help
```

### What gets installed?
- **Global**: Only the `super-prompt` CLI command
- **Project**: All files go into `.super-prompt/` folder only
- **Python**: Isolated virtual environment in `.super-prompt/venv/`
- **Databases**: SQLite and data files in `.super-prompt/venv/data/`

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

**Python dependencies:**
```bash
# Automatically handled via virtual environment in your project
# No manual Python installation needed!
```

## 📚 Documentation

📖 **[Complete Documentation](https://github.com/cdw0424/super-promt/blob/main/ARCHITECTURE.md)** - Detailed architecture and advanced usage

📋 **[Changelog](https://github.com/cdw0424/super-promt/blob/main/CHANGELOG.md)** - Version history and updates

🐛 **[Issues & Support](https://github.com/cdw0424/super-promt/issues)** - Bug reports and feature requests

## 📄 License

MIT © [Daniel Choi](https://github.com/cdw0424)

---

<div align="center">

**🚀 Ready to supercharge your development workflow?**

[Install Now](#-installation--setup) • [View Documentation](https://github.com/cdw0424/super-promt/blob/main/ARCHITECTURE.md) • [Report Issues](https://github.com/cdw0424/super-promt/issues)

</div>