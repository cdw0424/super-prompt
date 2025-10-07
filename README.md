# Super Prompt v7

[![npm version](https://img.shields.io/npm/v/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt) [![npm downloads](https://img.shields.io/npm/dt/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Simplified Development Assistant for Cursor IDE**

Super Prompt v7 is a complete rewrite focused on simplicity and Cursor IDE integration. It provides framework-specific best practices, professional development roles, and a lightweight Spec-Driven Development workflow.

## ✨ What's New in v7

- 🎯 **Framework Selection**: Choose your stack (Next.js, React, React Router v7, Vue, Python, Django, FastAPI)
- 🚀 **Simplified Architecture**: No more MCP/Python dependencies
- 📝 **Cursor Rules & Commands**: Native `.mdc` rules and `/commands`
- 👥 **10 Professional Roles**: @architect, @frontend, @backend, and more
- ⚡ **SDD Micro-Cycle**: Lightweight spec-driven development workflow
- 🧹 **Clean Installation**: Single command setup with no legacy baggage

## 🚀 Quick Start

### Installation

```bash
# Install globally
npm install -g @cdw0424/super-prompt

# Initialize in your project
cd your-project
super-prompt super:init
```

### Interactive Setup

When you run `super:init`, you'll be prompted to select your project type:

```
📦 Select your project type:

  1. Next.js + TypeScript (React framework)
  2. React + TypeScript
  3. React Router v7 + TypeScript
  4. Vue.js + TypeScript
  5. Python
  6. Django (Python web framework)
  7. FastAPI (Python API framework)
  8. All Frameworks (install everything)

Enter your choice (1-8) [1]:
```

### What Gets Installed

After initialization, your project will have:

```
your-project/
├── .cursor/
│   ├── rules/
│   │   ├── 01-codequality.mdc      # Code quality guidelines
│   │   ├── 10-clean-code.mdc       # Clean code principles
│   │   ├── 30-typescript.mdc       # TypeScript best practices (if selected)
│   │   ├── 40-react.mdc            # React best practices (if selected)
│   │   └── roles/                  # 10 professional roles
│   │       ├── architect.mdc
│   │       ├── backend.mdc
│   │       ├── frontend.mdc
│   │       ├── devops.mdc
│   │       ├── double-check.mdc
│   │       ├── performance.mdc
│   │       ├── qa.mdc
│   │       ├── refactor.mdc
│   │       ├── security.mdc
│   │       └── troubleshooting.mdc
│   └── commands/
│       └── sdd-micro.md            # Spec-Driven Development workflow
└── ...
```

## 📚 Features

### 🎯 Cursor Rules (Auto-Applied)

These rules are automatically applied to all your code:

- **Code Quality Guidelines** - Best practices for clean, maintainable code
- **Clean Code Principles** - SOLID principles, DRY, SSOT compliance
- **Framework-Specific Rules** - Tailored to your selected framework

### 👥 Roles (Use with @)

Invoke specialized AI roles for different tasks:

| Role | Command | Description |
|------|---------|-------------|
| **Architect** | `@architect` | System architecture design and technical decisions |
| **Backend** | `@backend` | Backend & API development, scalability, security |
| **Frontend** | `@frontend` | Frontend & UI/UX development, accessibility |
| **DevOps** | `@devops` | CI/CD, infrastructure, deployment automation |
| **Double Check** | `@double-check` | Risk audit, verification, confession-driven review |
| **Performance** | `@performance` | Performance optimization, profiling, benchmarking |
| **QA** | `@qa` | Quality assurance, testing strategy, test automation |
| **Refactor** | `@refactor` | Code refactoring, technical debt reduction |
| **Security** | `@security` | Security audit, threat modeling, vulnerability analysis |
| **Troubleshooting** | `@troubleshooting` | Debugging, root-cause analysis, incident response |

### ⚡ Commands (Use with /)

Execute specialized workflows:

- **`/sdd-micro`** - Lightweight Spec-Driven Development workflow
  - Clarify requirements
  - Plan implementation
  - Implement with confidence
  - Verify completion

## 🎯 Usage Examples

### Starting a New Feature

```
/sdd-micro

> What feature are you building?
Add rate limiting to API

> Why does this matter?
Prevent abuse and ensure fair usage

> How will you know it's done?
- 100 req/min limit enforced
- 429 status on exceed
- Rate limit headers in response

✓ Created: docs/super-prompt/sdd/001-251010-add-rate-limiting/spec.md
✓ Created: docs/super-prompt/sdd/001-251010-add-rate-limiting/plan.md
```

### Getting Expert Advice

```
@architect How should I structure a microservices architecture?

@frontend What's the best way to implement dark mode in React?

@security Can you review this authentication flow for vulnerabilities?

@performance How can I optimize this database query?
```

### Code Review

```
@double-check Review this PR for potential issues

@qa What test cases should I add for this feature?

@refactor How can I improve this code's maintainability?
```

## 🔄 Upgrading from v6 to v7

v7 is a **complete rewrite** with breaking changes. Follow these steps for a clean upgrade:

### 1. Remove Old Installation

```bash
# Uninstall old version
npm uninstall -g @cdw0424/super-prompt

# Remove old global files (if they exist)
rm -rf ~/.super-prompt
rm -rf ~/.cursor/mcp.json  # Only if you used v6 MCP features
```

### 2. Clean Up Your Project

```bash
cd your-project

# Remove old Super Prompt files
rm -rf .super-prompt/
rm -rf .cursor/rules/*-sdd-*.mdc
rm -rf python-packages/
rm -rf personas/

# Remove old MCP configuration (if exists)
rm -f .cursor/mcp.json
```

### 3. Install v7

```bash
# Install new version
npm install -g @cdw0424/super-prompt

# Initialize in your project
super-prompt super:init
```

### 4. Select Your Framework

Choose the framework that matches your project when prompted.

### What Changed?

| v6 | v7 |
|----|-----|
| MCP + Python architecture | Pure JavaScript/Node.js |
| 29+ personas | 10 focused roles |
| Complex SDD workflow | Lightweight SDD micro-cycle |
| `.md` commands | `.mdc` rules + `.md` commands |
| Manual mode switching | Framework-based configuration |
| Global MCP server | Cursor-native integration |

## 🛠️ Supported Frameworks

### Frontend

- **Next.js** - React framework with server-side rendering
- **React** - React library with TypeScript
- **React Router v7** - React Router v7 with file-based routing and data loading
- **Vue.js** - Vue.js framework with TypeScript

### Backend

- **Python** - Python development best practices
- **Django** - Django web framework
- **FastAPI** - FastAPI framework for APIs

### All Frameworks

Select "All Frameworks" if you work with multiple stacks or want all rules available.

## 📖 Documentation

### SDD Micro-Cycle

The SDD (Spec-Driven Development) micro-cycle is a lightweight workflow inspired by GitHub's Spec-Kit:

1. **Clarify** (3-5 min) - Define what you're building and why
2. **Plan** (5-10 min) - Outline how you'll build it
3. **Implement** - Execute the plan with confidence
4. **Verify** - Ensure success criteria are met

Each feature gets its own folder:
```
docs/super-prompt/sdd/
├── 001-251010-add-rate-limiting/
│   ├── spec.md
│   ├── plan.md
│   └── notes.md
├── 002-251015-jwt-authentication/
│   ├── spec.md
│   └── plan.md
└── ...
```

### Role Details

Each role provides:
- **Specialized expertise** in their domain
- **Evidence-based analysis** with references
- **Actionable recommendations** with priorities
- **Risk assessment** and mitigation strategies
- **Best practices** from industry standards

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/cdw0424/super-prompt/issues)
- **Discussions**: [GitHub Discussions](https://github.com/cdw0424/super-prompt/discussions)

## 🙏 Acknowledgments

Built with ❤️ for the Cursor IDE community.

---

**Super Prompt v7** - Simplified Development Assistant for Cursor IDE