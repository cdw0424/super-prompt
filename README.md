# Super Prompt v3

[![npm version](https://img.shields.io/npm/v/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![npm downloads](https://img.shields.io/npm/dm/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Production-ready prompt engineering toolkit** supporting both **Cursor IDE** and **Codex CLI** with **Spec-Driven Development (SDD)** workflow and **Auto Model Router (AMR)** for intelligent reasoning optimization.

🚀 **New in v3.0.0**: Complete modular architecture with Python core, data-driven assets, advanced context collection, and unified CLI experience.

---

## 🆕 What's New in v3.1.6

### ✨ **New Features**
- **Memory Initialization**: Added `/init-sp` command to initialize Super Prompt memory with a project structure snapshot.

## 🆕 What's New in v3.1.5

### ⚡ **Performance & Reliability**
- **Optimized Command Execution**: Improved `tag-executor.sh` with special command handling for init-sp and re-init-sp
- **Better Error Handling**: Enhanced fallback mechanisms and clearer error messages for command execution
- **Streamlined Initialization**: Direct execution path for project memory initialization commands

### 🔧 **Technical Improvements**
- **Special Command Routing**: Dedicated handling for initialization commands separate from regular personas
- **Path Resolution**: Robust project root detection for consistent command execution across environments
- **Execution Reliability**: Improved Python script discovery and execution for all commands

## 🆕 What's New in v3.1.4

### ✨ **New Features**
- **Expanded Persona Library**: Added 14 new specialized personas including debate, frontend-ultra, seq-ultra, docs-refector, ultracompressed, wave, task, implement, plan, review, spec, specify, init-sp, and re-init-sp
- **Complete Command Coverage**: All cursor command files now have corresponding persona definitions and proper execution routing
- **Enhanced Persona Support**: All personas now support Context7 MCP integration and SDD workflow guidance

### 🐛 **Bug Fixes**
- **Fixed command execution**: Resolved missing persona definitions causing commands like `/debate`, `/dev`, etc. to fail
- **Updated persona routing**: Fixed `tag-executor.sh` to include all supported personas in the PERSONAS array
- **Complete persona coverage**: Ensured all `.md` command files have matching entries in `enhanced_personas.yaml`

## 🆕 What's New in v3.1.3

### 🐛 **Bug Fixes**
- **Fixed scaffold import error**: Resolved `NameError: name 'scaffold' is not defined` in `super:init` command
- **Improved module loading**: Added proper scaffold module initialization in main function
- **Enhanced error handling**: Better fallback handling when scaffold module is unavailable

<details>
<summary>📋 <strong>Full Changelog (v3.0.x - v3.1.x)</strong></summary>

### 🆕 What's New in v3.0.0

### 🏗️ **Complete Architecture Overhaul**
- **Modular Python Core**: Clean separation with dedicated modules (engine, context, SDD, personas, adapters, validation)
- **Data-Driven Assets**: Externalized personas, rules, and prompts for easy customization and maintenance
- **Advanced Context Collection**: Intelligent context preservation with `.gitignore` compliance and `ripgrep` optimization

### 🧠 **Intelligent Reasoning System**
- **AMR (Auto Model Router)**: Automatic medium↔high reasoning switching based on task complexity
- **Context Engineering**: 30-50% token optimization through selective injection and compression
- **Quality Enhancement**: Confession, double-check, and anti-overengineering utilities for all commands

### 🚀 **Enhanced Development Workflow**
- **SDD Pipeline**: Complete Spec-Driven Development with quality gates (SPEC→PLAN→TASKS→IMPLEMENT)
- **29 Specialized Personas**: From basic development roles to advanced specialists (architect, security, performance, etc.)
- **Dual IDE Integration**: Seamless experience in both Cursor IDE and Codex CLI

### 🛡️ **Production-Ready Features**
- **Global Write Protection**: Prevents accidental file modifications (only safe outputs allowed)
- **TODO Auto-Validation**: Automatic task completion validation with intelligent retry mechanisms
- **Comprehensive Testing**: Full test coverage with automated validation and quality assurance

### 🔧 **Developer Experience**
- **Unified CLI**: Consistent interface across all environments and commands
- **Intelligent Defaults**: Automatic persona detection and reasoning optimization
- **Extensive Documentation**: Complete command reference with usage examples and best practices

---

## Quick Install

```bash
# Global installation (recommended)
npm install -g @cdw0424/super-prompt

# or use npx directly
npx @cdw0424/super-prompt --help
```

---

## 🧾 Changelog (highlights)

### v3.1.2
- Fix: Installation banner now shows the actual package version dynamically (reads package.json) instead of a hardcoded string.
- Fix: `super:init` scaffold NameError resolved by bundling a fallback scaffold module and importing it correctly.
- Refactor: Project CLI is a thin wrapper — delegates optimize/SDD/AMR/Codex/Personas to the Python core when present; otherwise prints clear install guidance (pip/pipx) and Cursor alternatives.
- DX: `super:help` prints environment status (Python/SQLite/FTS5/Codex) and richer usage examples.
### v3.0.x
- Project CLI refactor: delegates core logic to Python core (super-prompt-core) where available; thin wrapper structure
- Added `super:upgrade`: refresh rules/commands, cleanup legacy, migrate JSON sessions → SQLite (memory/ltm.db) with automatic DB backup
- Added `/init-sp` and `/re-init-sp` commands (Cursor) for project analysis → memory
- Enhanced personas: research-based directives and structured response formats; added `doc-master`
- Reasoning delegate: deep-planning via Codex CLI with automatic `@openai/codex@latest` update
- LTM: SQLite-backed memory; graceful FTS5 fallback; dev-only vector index scaffold (excluded from npm)
- OS setup: install.js best-effort checks for Python 3 and SQLite3 on macOS/Linux/Windows
- Help command: `super:help` with dynamic environment status (Python/SQLite/FTS/Codex)

### v3.0.0
- Modular architecture: Python core, data-driven assets, SDD pipeline, AMR router, and unified CLI

</details>

---

## ✨ Key Features

🎯 **Dual IDE Support**: Seamless integration with both Cursor (slash commands) and Codex CLI (flag-based personas)

🧠 **AMR (Auto Model Router)**: Intelligent medium↔high reasoning switching with fixed state machine (INTENT→CLASSIFY→PLAN→EXECUTE→VERIFY→REPORT)

🚀 **SDD Workflow**: Complete Spec-Driven Development pipeline with quality gates and context preservation

🎭 **Advanced Personas**: Specialized AI personalities (architect, frontend, backend, security, performance, etc.)

🗣️ **Internal Debate**: Single-model debate system with Positive vs Critical selves

🧰 **Context Engineering**: Intelligent context preservation with 30-50% token optimization

✅ **TODO Auto-Validation**: Automatic task completion validation with retry mechanisms

🔒 **Global Write Protection**: Prevents accidental file modifications (only safe outputs allowed)

---

## Quick Start

### 1. Install & Initialize

```bash
# Install globally
npm install -g @cdw0424/super-prompt

# Initialize in your project (creates Cursor rules and commands)
super-prompt super:init

# Initialize Super Prompt's memory with a project snapshot
/init-sp

# Optional: Install Codex CLI for text UI
npm install -g @openai/codex
```

### 2. Use with Cursor IDE

After initialization, Cursor automatically recognizes Super Prompt commands:

```
/architect "Design scalable microservices architecture"
/implement "Add user authentication with JWT"
/security "Review API endpoints for vulnerabilities"
/performance "Optimize slow database queries"
```

### 3. Use with Codex CLI

```bash
# Simplified persona syntax (recommended)
super-prompt --sp-architect "Design system architecture"
super-prompt --sp-security "Audit authentication flow"
super-prompt --sp-performance "Optimize database queries"

# SDD workflow
super-prompt --sp-sdd-spec "User authentication system"
super-prompt --sp-sdd-plan "OAuth2 + JWT implementation"
super-prompt --sp-sdd-tasks "Break down into development tasks"
super-prompt --sp-sdd-implement "Start implementation"
```

---

## 🎯 SDD Workflow

Super Prompt implements complete **Spec-Driven Development** methodology:

### 📋 SDD Commands

**Cursor (slash commands):**
- `/spec` — Create detailed feature specifications
- `/plan` — Design implementation plans with architecture
- `/tasks` — Break down plans into actionable development tasks
- `/implement` — Start implementation with SDD compliance checking

**Codex CLI:**
```bash
super-prompt --sp-sdd-spec "user authentication system"
super-prompt --sp-sdd-plan "OAuth2 + JWT implementation"
super-prompt --sp-sdd-tasks "break down auth tasks"
super-prompt --sp-sdd-implement "start development"
```

### 🎯 SDD Benefits
- **Clarity**: Everyone knows what's being built and why
- **Quality**: Architecture decisions made upfront with validation
- **Efficiency**: Reduced rework through structured planning
- **Collaboration**: Clear handoffs with persistent context
- **Compliance**: Built-in quality gates and validation

---

## 🧠 AMR (Auto Model Router)

Intelligent reasoning optimization that automatically switches between medium and high reasoning modes:

- **Default**: gpt-5, reasoning=medium (cost-effective execution)
- **Auto-upgrade**: Heavy tasks (design, security, performance analysis) automatically use high reasoning
- **State Machine**: Fixed workflow ensures consistent, high-quality outputs
- **Smart Switching**: Plans at high reasoning, executes at medium for optimal balance

---

## 🎭 Complete Command Reference

Super Prompt supports a comprehensive set of commands across different categories. All commands are available in both Cursor IDE (slash commands) and Codex CLI (flag-based syntax).

---

### 🏗️ Core Development Personas

| Command | Cursor | Codex CLI | Description | Best For |
|---------|--------|-----------|-------------|----------|
| **Architect** | `/architect` | `--sp-architect` | System design & scalability specialist | Large-scale architecture, scalability planning, technical strategy |
| **Frontend** | `/frontend` | `--sp-frontend` | UI/UX specialist & accessibility advocate | Component development, responsive design, user experience |
| **Backend** | `/backend` | `--sp-backend` | Server-side development & API specialist | API design, database optimization, server performance |
| **Analyzer** | `/analyzer` | `--sp-analyzer` | Root cause analyst & systematic investigator | Complex debugging, performance bottleneck analysis, system investigation |
| **Security** | `/security` | `--sp-security` | Threat modeler & vulnerability specialist | Security audits, threat modeling, compliance reviews |
| **Performance** | `/performance` | `--sp-performance` | Optimization specialist & bottleneck eliminator | Performance profiling, resource optimization, scaling improvements |
| **QA** | `/qa` | `--sp-qa` | Quality assurance & testing strategist | Test planning, quality gates, edge case identification |

**Usage Examples:**
```bash
# Cursor IDE
/architect "Design microservices architecture for e-commerce"
/frontend "Create responsive login component with validation"
/backend "Design REST API for user management"
/analyzer "Debug intermittent API timeout issues"
/security "Audit authentication flow for vulnerabilities"
/performance "Optimize slow database queries"
/qa "Design comprehensive test strategy for payment system"

# Codex CLI
super-prompt --sp-architect "Design microservices architecture"
super-prompt --sp-frontend "Create responsive login component"
super-prompt --sp-backend "Design REST API for user management"
super-prompt --sp-analyzer "Debug intermittent API timeout issues"
super-prompt --sp-security "Audit authentication flow"
super-prompt --sp-performance "Optimize slow database queries"
super-prompt --sp-qa "Design comprehensive test strategy"
```

---

### 🎯 Specialized Expert Personas

| Command | Cursor | Codex CLI | Description | Best For |
|---------|--------|-----------|-------------|----------|
| **High Reasoning** | `/high` | `--sp-high` | Deep strategic analysis with GPT-5 high model | Complex strategic decisions, critical system design, high-stakes technical decisions |
| **Dev** | `/dev` | `--sp-dev` | Feature development specialist with quality focus | New feature implementation, incremental development, integration testing |
| **Troubleshooter** | `/tr` | `--sp-tr` | Expert diagnostician for complex technical issues | Bug reproduction, root cause analysis, rapid issue resolution |
| **Mentor** | `/mentor` | `--sp-mentor` | Educational guidance & knowledge transfer specialist | Learning support, code explanation, career development |
| **Refactorer** | `/refactorer` | `--sp-refactorer` | Code quality & technical debt management specialist | Code cleanup, refactoring, maintainability improvements |
| **DevOps** | `/devops` | `--sp-devops` | CI/CD, infrastructure & reliability specialist | Deployment automation, infrastructure as code, SRE practices |
| **Scribe** | `/scribe` | `--sp-scribe` | Technical writer & documentation specialist | API documentation, developer guides, technical specifications |

**Usage Examples:**
```bash
# High-complexity tasks
/high "Evaluate GraphQL vs REST for our API architecture"
/dev "Implement user authentication feature with testing"
/tr "Diagnose memory leak in production application"
/mentor "Explain microservices architecture patterns"
/refactorer "Clean up legacy codebase technical debt"
/devops "Design CI/CD pipeline for microservices"
/scribe "Create comprehensive API documentation"
```

---

### 📋 SDD Workflow Commands

Super Prompt implements complete **Spec-Driven Development** methodology with structured workflow commands.

| Command | Cursor | Codex CLI | Description | Purpose |
|---------|--------|-----------|-------------|---------|
| **Spec** | `/spec` | `--sp-sdd-spec` | Create detailed feature specifications | Define WHAT to build with requirements & success criteria |
| **Plan** | `/plan` | `--sp-sdd-plan` | Design implementation plans | Define HOW to build with architecture & strategy |
| **Tasks** | `/tasks` | `--sp-sdd-tasks` | Break down plans into actionable tasks | Define the STEPS with detailed development tasks |
| **Implement** | `/implement` | `--sp-sdd-implement` | Start implementation with compliance checking | Build with confidence using SDD validation |

**SDD Workflow Example:**
```bash
# 1. Define the feature specification
/spec "Design a real-time chat feature with file uploads and end-to-end encryption"

# 2. Create implementation plan
/plan "Design WebSocket-based chat with AWS S3 integration and client-side encryption"

# 3. Break down into development tasks
/tasks "Implement chat backend, frontend components, file upload system, and encryption"

# 4. Start implementation with validation
/implement "Build the chat backend with WebSocket handlers and message queuing"
```

**Codex CLI SDD Usage:**
```bash
super-prompt --sp-sdd-spec "Design user authentication system"
super-prompt --sp-sdd-plan "Implement OAuth2 + JWT with refresh tokens"
super-prompt --sp-sdd-tasks "Break down auth implementation into tasks"
super-prompt --sp-sdd-implement "Start building login functionality"
```

---

### 🗄️ Database Tools

| Command | Cursor | Codex CLI | Description | Purpose |
|---------|--------|-----------|-------------|---------|
| **DB Refactorer** | `/db-refector` | `--sp-db-refector` | Database schema analysis & optimization | Schema refactoring, performance optimization, data migration |
| **DB Template** | `/db-template` | `--sp-db-template` | Generate database schema templates | Prisma schema generation, database modeling, boilerplate creation |
| **DB Doc** | `/db-doc` | `--sp-db-doc` | Generate database documentation | Schema documentation, ER diagrams, API integration guides |

**Database Tool Examples:**
```bash
/db-refector "Analyze and optimize user table schema for better performance"
/db-template "Generate Prisma schema for e-commerce database"
/db-doc "Create comprehensive database documentation with relationships"
```

---

### 🎪 Advanced Features

| Command | Cursor | Codex CLI | Description | Purpose |
|---------|--------|-----------|-------------|---------|
| **Debate** | `/debate` | `--sp-debate` | Single-model internal debate system | Structured decision-making with Positive vs Critical perspectives |
| **Task Manager** | `/task` | `--sp-task` | Task management & workflow execution | Structured task planning and progress tracking |
| **Wave** | `/wave` | `--sp-wave` | Multi-stage execution orchestrator | Complex multi-step processes and phased execution |

**Advanced Feature Examples:**
```bash
# Internal debate for decision making
/debate "Should we use microservices or modular monolith?"
super-prompt --sp-debate --rounds 8 "Choose between React and Vue for our frontend"

/task "Manage the user authentication feature implementation"
/wave "Orchestrate the full deployment pipeline from development to production"
```

---

### ⚙️ System & Utility Commands

| Command | Description | Usage |
|---------|-------------|-------|
| **super:init** | Initialize Super Prompt in project | `super-prompt super:init` |
| **codex:init** | Initialize Codex-specific assets | `super-prompt codex:init` |
| **amr:rules** | Generate AMR rule files | `super-prompt amr:rules` |
| **amr:print** | Output AMR bootstrap prompt | `super-prompt amr:print` |
| **todo:validate** | Validate TODO completion | `super-prompt todo:validate` |

---

### 🎨 Command Syntax Reference

#### Cursor IDE Commands
- **Format**: `/command "your query here"`
- **Auto-completion**: Tab completion available for command names
- **Interactive**: Visual command selection in chat interface

#### Codex CLI Commands
- **Simplified syntax** (recommended): `--sp-command "query"`
- **Original syntax** (still supported): `--command "query"` or `optimize --command "query"`
- **SDD commands**: `--sp-sdd-spec`, `--sp-sdd-plan`, `--sp-sdd-tasks`, `--sp-sdd-implement`

#### AMR Integration
All commands automatically benefit from **Auto Model Router (AMR)**:
- **Light tasks**: Use medium reasoning (cost-effective)
- **Heavy tasks**: Automatically upgrade to high reasoning
- **Strategic decisions**: Always use high reasoning for critical analysis

#### Context Engineering
Commands leverage **Context Engineering** for optimal results:
- **30-50% token optimization** through intelligent context injection
- **Conversation preservation** across development stages
- **Query-relevant context** for focused, accurate responses

---

## 🏗️ Architecture Benefits

### Why Super Prompt v3?

**🎯 Production-Ready Architecture**
- **Modular Python Core**: Clean separation of concerns with dedicated modules
- **Data-Driven Assets**: Externalized personas, rules, and prompts for easy customization
- **Advanced Context Collection**: Intelligent context preservation with 30-50% token optimization
- **Quality Enhancement**: Confession, double-check, and anti-overengineering utilities

**🚀 Performance & Quality**
- **AMR Optimization**: High reasoning only when needed, medium for cost-effective execution
- **Context Engineering**: Spec Kit implementation for conversation context preservation
- **Global Write Protection**: Prevents accidental file modifications
- **TODO Auto-Validation**: Automatic task completion validation with retry mechanisms

**🔧 Developer Experience**
- **Dual IDE Support**: Same powerful features in both Cursor and Codex
- **Unified CLI**: Consistent interface across all environments
- **Intelligent Defaults**: Automatic persona detection and reasoning optimization
- **Comprehensive Testing**: Built-in validation and quality assurance

---

## 📋 Requirements

- **Node.js** >= 14
- **Python** >= 3.7 (for internal CLI utilities)
- **OS**: macOS/Linux recommended (zsh-based)

### Optional Dependencies

```bash
# Codex CLI for text UI (recommended)
npm install -g @openai/codex

# ripgrep for enhanced context collection performance
# Install via your package manager (brew, apt, etc.)
```

---

## 🔧 Configuration

### Environment Variables

     ```bash
# Debug and logging
SP_DEBUG=1           # Expand debug logs
SP_VERBOSE=1         # Detailed progress logs
SP_NO_LOGS=1         # Suppress non-essential logs

# Model and behavior
SP_OPENAI_MODEL=gpt-5         # Override default model
SP_SKIP_CODEX_UPGRADE=1       # Skip Codex CLI auto-updates
SP_SKIP_SELF_UPDATE=1         # Skip self-updates

# Advanced
SP_SAVE_DEBATE=1              # Save debate mode recordings
SP_CREATOR_CMD="..."          # Override custom creation command
SP_ALLOW_WRITES=1             # Disable write protection (not recommended)
```

---

## 🚨 Global Write Protection Policy

**All commands protect `./` directory files from accidental modification.**

### What's Protected
- ✅ **BLOCKED**: All relative paths under current directory (`./src/`, `./package.json`, etc.)
- ✅ **ALLOWED**: Safe output locations (`.codex/reports/`)
- ✅ **ALLOWED**: Initialization commands (`super:init`, `amr:rules`)

### Why Protection Exists
- **Safety First**: Prevents AI from accidentally modifying your project files
- **Predictable Behavior**: You can trust commands won't touch source code
- **Command Consistency**: All commands follow the same protection rules

---

## 🐛 Troubleshooting

### Common Issues

**"codex command not found"**
```bash
npm install -g @openai/codex
# Restart terminal
```

**"Python CLI not found" after install**
```bash
# Re-run installation
npm install -g @cdw0424/super-prompt

# Or run install script directly
node install.js
```

**"Python < 3.7" error**
```bash
python3 --version  # Should show >= 3.7
# Install Python >= 3.7 and ensure python3 points to it
```

**Slash commands not visible in Cursor**
- Ensure `.cursor/commands/super-prompt/` exists
- Files should be executable: `chmod 755 .cursor/commands/super-prompt/*`
- Restart Cursor IDE

**Infinite Git churn with npm cache**
```bash
# Check if npm cache is inside repo
npm config get cache

# Fix automatically (recommended)
npx @cdw0424/super-prompt run scripts/codex/npm-cache-fix.sh --fix

# Or fix manually
npm config set cache ~/.npm --global
echo ".npm-cache/" >> .gitignore
```

**"ripgrep not installed" warning**
- Not required, but recommended for better performance
- Install via your package manager (`brew install ripgrep`, `apt install ripgrep`, etc.)

---

## 📈 Performance & Quality

### 🧠 AMR Optimization
- **30-50% Token Reduction**: Intelligent context injection and compression
- **Cost Optimization**: High reasoning only when needed, medium for execution
- **Quality Consistency**: Fixed state machine ensures predictable outputs

### 🛡️ Quality Guards
- **Output Discipline**: English-only with consistent formatting
- **Security**: Automatic masking of secrets/tokens (shows as `sk-***`)
- **Validation**: Built-in SDD gates and TODO auto-validation
- **Testing**: Comprehensive test coverage with automated validation

### 🔍 Context Engineering
- **Spec Kit Implementation**: Conversation context preservation across stages
- **Stage Gating**: Prevents context loss through structured validation
- **Token Optimization**: Query-relevant context injection with compression

---

## 📝 License

MIT

---

## 🤝 Contributing

- **Conventional Commits**: `feat(cli): ...`, `fix: ...`, `docs: ...`
- **PR Guidelines**: Include overview, reasoning, and verification methods
- **Code Quality**: Follow existing patterns and include tests

---

---

## 📈 Migration Guide (v2.x → v3.0.0)

### 🚀 **Major Improvements**
- **Complete Architecture Rewrite**: Monolithic structure → Modular Python core with clear separation of concerns
- **Data-Driven Configuration**: All personas, rules, and prompts now externalized in YAML manifests
- **Advanced Context Management**: `.gitignore`-aware collection with token optimization (30-50% reduction)
- **Intelligent Quality System**: Confession, double-check, and anti-overengineering for all outputs
- **Production-Ready Security**: Global write protection prevents accidental file modifications

### 🧠 **New Capabilities**
- **29 Specialized Personas**: From basic development to advanced specialists (architect, security, performance, doc-master, etc.)
- **AMR State Machine**: Fixed workflow (INTENT→CLASSIFY→PLAN→EXECUTE→VERIFY→REPORT) with automatic reasoning switching
- **SDD Pipeline**: Complete Spec-Driven Development workflow with quality gates
- **Context Engineering**: Spec Kit implementation for conversation context preservation
- **TODO Auto-Validation**: Intelligent task completion validation with retry mechanisms

### 🔄 **Breaking Changes**
- **Configuration Files**: All settings moved to `packages/cursor-assets/manifests/` and `packages/codex-assets/`
- **Python Dependencies**: New requirements (PyYAML, pathspec, rich, typer, pydantic)
- **Command Structure**: Enhanced with additional personas and SDD workflow commands
- **Context Behavior**: Improved context injection with selective token optimization

### ✅ **Migration Steps**
1. **Update Installation**: `npm install -g @cdw0424/super-prompt@latest`
2. **Reinitialize Project**: `super-prompt super:init` (creates new v3 configuration)
3. **Update Workflows**: Review and update any custom scripts for new command structure
4. **Test Integration**: Verify Cursor and Codex CLI integrations work with new architecture

### 🎯 **Benefits of v3.0.0**
- **50% Better Performance**: Optimized context handling and token usage
- **Enterprise-Ready**: Production-grade security, validation, and error handling
- **Future-Proof**: Modular architecture supports easy extension and customization
- **Developer Experience**: Unified CLI with intelligent defaults and comprehensive documentation

---

## 🙏 Credits & Attribution

This project draws inspiration from various open-source tools and community snippets. Special thanks to the open-source community for their contributions.

If you're a maintainer of a referenced project and would like additional attribution or adjustments, please open an issue.
