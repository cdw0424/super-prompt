# Super Prompt Commands Reference (SSOT)

This document reflects the Single Source of Truth for commands, aligned with the personas manifest and rules.

## 🚀 Quick Start

After running `npx super-prompt init`:
- `.cursor/commands/super-prompt/` contains all persona commands
- `.cursor/rules/` contains global rules (SSOT/AMR); model guidance installs on toggle

Start MCP server: `npx super-prompt mcp:serve`
Use slash commands in your IDE.

---

## 🏗️ Core Personas

### `/architect` - Systems Architecture Specialist
**Best for:** System design, scalability planning, architectural decisions
```
/architect "Design a microservices architecture for e-commerce platform"
/architect "Review current system architecture and suggest improvements"
```

### `/frontend` - UI/UX & Accessibility Specialist
**Best for:** React/Vue components, responsive design, accessibility
```
/frontend "Build a responsive login form with proper accessibility"
/frontend "Create a modern dashboard layout with Tailwind CSS"
```

### `/frontend-ultra` - Elite Design Systems Architect
**Best for:** Advanced UI patterns, design systems, complex interactions
```
/frontend-ultra "Design a comprehensive component library"
/frontend-ultra "Create advanced data visualization components"
```

### `/backend` - Server-Side & API Specialist
**Best for:** APIs, databases, server architecture, performance
```
/backend "Create a user authentication system with JWT"
/backend "Design a scalable database schema for social media app"
```

### `/dev` - Feature Development Specialist
**Best for:** Minimal, testable implementations, rapid prototyping
```
/dev "Implement user profile editing feature"
/dev "Add search functionality to the product catalog"
```

### `/devops` - Infrastructure & CI/CD Specialist
**Best for:** Deployment, containers, monitoring, automation
```
/devops "Set up CI/CD pipeline with GitHub Actions"
/devops "Create Docker configuration for Node.js application"
```

---

## 🔬 Analysis & Quality Commands

### `/analyzer` - Root Cause Investigation Specialist
**Best for:** Debugging, performance issues, system investigation
```
/analyzer "Investigate why API response times are slow"
/analyzer "Debug memory leak in React application"
```

### `/security` - Security & Threat Modeling Expert
**Best for:** Security audits, vulnerability assessment, compliance
```
/security "Audit authentication system for vulnerabilities"
/security "Review API endpoints for security best practices"
```

### `/performance` - Optimization Specialist
**Best for:** Performance tuning, bottleneck identification, metrics
```
/performance "Optimize database queries for faster load times"
/performance "Analyze bundle size and suggest optimizations"
```

### `/qa` - Quality Assurance & Testing Expert
**Best for:** Test strategies, quality gates, validation processes
```
/qa "Create comprehensive test plan for user registration flow"
/qa "Review code quality and suggest testing improvements"
```

### `/review` - Code Review Specialist
**Best for:** Code quality review, best practices validation
```
/review "Review this pull request for best practices"
/review "Analyze code changes and suggest improvements"
```

### `/double-check` - Confessional Integrity Auditor
**Best for:** Post-task confession, gap surfacing, targeted follow-up questions
```
/double-check "Review my latest changes and list what still needs proof"
/double-check "Confession: implemented signup flow; what evidence is missing?"
```

### `/init` - Project Bootstrap & Asset Sync
**Best for:** Refreshing Super Prompt assets after upgrades or repo setup
```
/init
/init "Refresh workspace assets"
```

### `/resercher` - Abstention-First Research Analyst
**Best for:** Evidence-backed investigations, citation-heavy synthesis, hallucination-sensitive topics
```
/resercher "Investigate regulatory changes for fintech lending in 2024"
/resercher "Synthesize climate risk metrics with sources and confidence tags"
```

---

## 🎓 Knowledge & Documentation Commands

### `/mentor` - Educational Guidance Expert
**Best for:** Learning, explanations, best practices teaching
```
/mentor "Explain React hooks and when to use each one"
/mentor "Teach me about database normalization with examples"
```

### `/scribe` - Technical Writing Specialist
**Best for:** Documentation, technical writing, process documentation
```
/scribe "Write API documentation for user management endpoints"
/scribe "Create onboarding guide for new developers"
```

### `/doc-master` - Documentation Architecture Expert
**Best for:** Large-scale documentation projects, information architecture
```
/doc-master "Restructure entire project documentation"
/doc-master "Create documentation standards and templates"
```

---

## ⚡ Advanced Reasoning Commands

### `/seq` - Sequential Thinking (5 iterations)
**Best for:** Complex problems requiring step-by-step analysis
```
/seq "Analyze the root cause of this performance bottleneck"
/seq "Plan the migration from monolith to microservices"
```

### `/seq-ultra` - Advanced Sequential Thinking (10 iterations)
**Best for:** Extremely complex problems requiring deep analysis
```
/seq-ultra "Design enterprise-scale system architecture"
/seq-ultra "Analyze complex security vulnerabilities and create fix strategy"
```

### `/high` - Deep Reasoning Specialist
**Best for:** High-effort planning and review tasks
```
/high "Create comprehensive project roadmap with risk analysis"
/high "Review system architecture for enterprise scalability"
```

---

## 🔧 Utility & Enhancement Commands

### `/refactorer` - Code Quality Specialist
**Best for:** Code cleanup, technical debt reduction, refactoring
```
/refactorer "Clean up this legacy codebase and improve maintainability"
/refactorer "Refactor these components to reduce duplication"
```

### `/implement` - SDD-Aligned Implementation Specialist
**Best for:** Implementing features following specifications
```
/implement "Build the user dashboard based on the provided wireframes"
/implement "Create the API endpoints according to the specification"
```

### `/optimize` - Generic Optimization Expert
**Best for:** General optimization tasks, efficiency improvements
```
/optimize "Improve application startup time"
/optimize "Reduce memory usage in data processing pipeline"
```

### `/ultracompressed` - Token-Optimized Responses
**Best for:** Getting concise, efficient responses to save time/cost
```
/ultracompressed "Explain microservices architecture"
/ultracompressed "Review this code and suggest improvements"
```

---

## 🧠 Reasoning & Compression

### `/seq` — Step-by-step reasoning
### `/seq-ultra` — Deep sequential reasoning
### `/high` — High reasoning (planning/review)
### `/ultracompressed` — Concise, token-optimized responses

---

## 📋 Workflow & Planning Commands

### `/spec` - Specification Writer (SDD)
**Best for:** Writing detailed technical specifications
```
/spec "Create specification for user authentication system"
/spec "Document API requirements for mobile app integration"
```

### `/plan` - Implementation Planning (SDD)
**Best for:** Breaking down specifications into implementation plans
```
/plan "Create implementation plan for e-commerce checkout flow"
/plan "Plan the migration strategy for legacy system modernization"
```

### `/tasks` - Task Breakdown Specialist
**Best for:** Breaking large projects into manageable tasks
```
/tasks "Break down social media platform development into sprints"
/tasks "Create task list for implementing real-time chat feature"
```

### `/wave` - Phased Delivery Planning
**Best for:** Multi-phase project planning, incremental delivery
```
/wave "Plan phased rollout of new user interface"
/wave "Create incremental delivery strategy for system migration"
```

---

## 🎛️ Mode Control

- `/gpt-mode-on` / `/gpt-mode-off` — GPT‑5 guidance and persona overrides (materialized)
- `/grok-mode-on` / `/grok-mode-off` — Grok guidance and persona overrides (materialized)
- `/high-mode-on` / `/high-mode-off` — Toggle Codex-backed high reasoning for `/high` and `sp_high`
- Aliases: `/codex-mode-on`, `/codex-mode-off`

---

## 🧰 MCP Tools

- `amr_repo_overview(project_root)` — Repo map (languages, frameworks, tests)
- `amr_handoff_brief(project_root, query)` — Brief for high reasoning
- `amr_persona_orchestrate(persona, project_root, query)` — One‑shot orchestration (includes task_tag, suggested next)
- `context_collect|stats|clear` — Context tools (with cache)
- `validate_todo|validate_check` — Validation gates
- `memory_set|get`, `memory_set_task|get_task`, `memory_append_event`, `memory_recent`

## 💡 Usage Tips

### 🎯 **Command Combination Strategy**
1. **Start with analysis:** `/analyzer` or `/seq` to understand the problem
2. **Get specialized help:** Choose domain expert (`/frontend`, `/backend`, etc.)
3. **Quality check:** Use `/review` or `/qa` to validate solutions
4. **Document:** Use `/scribe` for documentation

### ⚡ **Efficiency Modes**
- Use `/ultracompressed` when you need quick, concise answers
- Use `/seq` or `/seq-ultra` for complex problem-solving
- Switch modes (`/gpt-mode-on` / `/grok-mode-on`) based on your active model

### 🔄 **Iterative Development**
- Start with `/spec` for requirements
- Use `/plan` for implementation strategy
- Apply `/implement` for execution
- Validate with `/review` and `/qa`

### 🚨 **Emergency Debugging**
```
/analyzer "Debug production issue: users can't login"
/security "Check for security vulnerabilities in auth flow"
/performance "Why is the login process taking 10+ seconds?"
```

---

## 📚 Further Resources

- **[Main README](README.md)** — Setup and installation guide
- **[Changelog](CHANGELOG.md)** — Version history and updates
- **[AGENTS.md](AGENTS.md)** — Repository rules and conventions (SSOT)
- **[GitHub Issues](https://github.com/cdw0424/super-prompt/issues)** — Report bugs and request features

---

**Pro Tip:** All commands work with natural language - be specific about your needs and context for best results!
