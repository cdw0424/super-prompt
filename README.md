# Super Prompt — Cursor Research & Delivery Copilot

[![npm version](https://img.shields.io/npm/v/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![npm downloads](https://img.shields.io/npm/dt/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.17-brightgreen)](https://nodejs.org/)

> **Current Release:** v5.6.2

<!-- SEO: Cursor MCP extension, AI developer productivity, evidential research workflows, zero-config install, global teams -->

Super Prompt is the zero-configuration Model Context Protocol (MCP) extension engineered for **Cursor IDE** teams that need enterprise-grade research, planning, and delivery automation. We combine abstention-first research workflows, evidence-enforced personas, and tightly-coupled Cursor slash commands so every build, review, or investigation ships with citations, tests, and follow-up guardrails.

---

## Table of Contents
1. [Product Philosophy](#product-philosophy)
2. [How Super Prompt Works](#how-super-prompt-works)
3. [Installation](#installation)
4. [Quick Start (90 seconds)](#quick-start-90-seconds)
5. [Using Super Prompt Inside Cursor](#using-super-prompt-inside-cursor)
6. [Command Catalogue](#command-catalogue)
7. [Personas & Workflows](#personas--workflows)
8. [Global & SEO Readiness](#global--seo-readiness)
9. [Operations & Troubleshooting](#operations--troubleshooting)
10. [Frequently Asked Questions](#frequently-asked-questions)

---

## Product Philosophy
We designed Super Prompt as a **service-quality extension** for developers building in Cursor:
- **MCP-first reliability** – every action runs through the MCP server so logs, retries, and guardrails are predictable.
- **Abstention over hallucination** – research personas enforce evidence thresholds, citations, and double-check rituals.
- **Delivery accountability** – development personas emit task plans, test matrices, and deployment checklists by default.
- **Cursor-native UX** – everything installs under `.cursor/` and surfaces through familiar slash commands (no extra UI).

These principles make Super Prompt suitable for regulated teams, globally distributed squads, and anyone who needs auditable AI support rather than opaque answers.

---

## How Super Prompt Works
| Layer | What It Does | Why It Exists |
| ----- | ------------- | ------------- |
| **Cursor Extension Assets** | Ships curated commands, rules, and MCP wiring into `.cursor/` | Keeps slash commands discoverable without manual configuration |
| **MCP Server (`sp-mcp`)** | Hosts 29+ tool endpoints (personas, SDD workflows, diagnostics) | Provides consistent protocol-based execution for Cursor and compatible MCP clients |
| **Personas Manifest** | Governs reasoning budgets, abstention thresholds, and tool budgets | Ensures every persona follows the same operating philosophy |
| **Double-Check Ritual** | Confessional audit command invoked by default | Forces final verification and confession before handoff |

Super Prompt is packaged on npm; the initializer copies assets, sets up `.super-prompt/` runtime state, and registers the MCP server so Cursor recognizes every tool immediately.

---

## Installation
```bash
npm install -g @cdw0424/super-prompt@latest
```

Requirements:
- Node.js ≥ 18.17
- Cursor IDE ≥ v0.42 (slash command support)
- macOS, Linux, or Windows WSL2

> **Tip:** For CI/CD or shared dev containers, add the install command to your base image. Super Prompt does not require global configuration beyond copying assets.

---

## Quick Start (90 seconds)
```bash
super-prompt super:init --force
```
The initializer will:
- Materialize `.cursor/commands/super-prompt/` and `.cursor/rules/`
- Generate `.super-prompt/` runtime state (mode, config, telemetry)
- Register `sp-mcp` (MCP server) for Cursor clients
- Seed the **Abstention-First CoVe-RAG** assets (`/resercher`, `/double-check`, etc.)
- Produce `.super-prompt/context/project-dossier.md` for personas to reference
- Prompt you for the target environment (macOS by default) so Windows shells receive correct path separators and MCP wiring

Restart Cursor after initialization so slash commands reload.

Common follow-ups:
```bash
/sp_gpt_mode_on    # Force GPT-5 medium mode
/sp_grok_mode_on   # Switch to Grok code-fast mode
/sp_claude_mode_on # Enable Claude XML/tag-driven guidance
/sp_mode_get       # Inspect active engine
/sp_high_mode_on   # Enable Codex high reasoning for downstream plans
/sp_high_mode_off  # Return to prompt-based high persona planning
```

> Responses automatically mirror the language of your latest message; switch languages simply by changing the language you type in.

Claude-specific persona design and runbooks live under `docs/claude-persona-guide.md` and `docs/claude-operations.md`.

---

## Using Super Prompt Inside Cursor
1. **Trigger the command palette** (`/`) and type `sp_` to filter Super Prompt commands.
2. Provide focused prompts (include file paths, acceptance criteria, risk notes).
3. Observe the persona rubric in the response; most workflows will automatically:
   - Propose phased plans (Scopes, Design, Build, Handoff)
   - Emit testing commands and monitoring hooks
   - Call `/double-check` before finalizing
4. For research-heavy tasks, use `/resercher` first, then hand results to `/dev`, `/review`, or `/doc-master`.
5. Consult `.super-prompt/context/project-dossier.md` before acting; if it’s missing, run `/super-prompt/init` to regenerate.

Every persona returns Markdown optimized for Cursor’s diff view, making it easy to copy into PRs, design docs, or CLI tasks.

---

## Command Catalogue
Below is the canonical list of Super Prompt slash commands (also available via `COMMANDS.md`).

### Core Development Personas
- `/sp_dev` – Feature delivery pipeline with task breakdowns and test matrices
- `/sp_architect` – System design, trade-off mapping, ADR-ready briefs
- `/sp_backend` / `/sp_frontend` – Implementation guidance per stack, with observability hooks
- `/sp_refactorer` – Technical debt reduction playbooks and regression safety nets
- `/sp_doc_master` – Information architecture, documentation workflows, review gates

### Research & Verification
- `/sp_resercher` – Abstention-first CoVe-RAG research with enforced citations
- `/sp_double_check` – Confessional audit before merge/deploy handoffs
- `/sp_analyzer` – Root-cause investigations with evidence tracking
- `/sp_review` – Code review specialist aligned with specs and plans
- `/sp_high` – High-effort strategic reasoning (plan/review mode)

### Operations & Quality
- `/sp_security` – Threat modeling, compliance guardrails
- `/sp_performance` – Performance analysis, SLO alignment
- `/sp_qa` – Test strategy, automation coverage
- `/sp_devops` – CI/CD, infra rollout, observability upgrades

### Workflow Automation
- `/sp_specify`, `/sp_plan`, `/sp_tasks`, `/sp_implement` – Full Software Design Doc (SDD) pipeline
- `/sp_seq`, `/sp_seq_ultra` – Sequential reasoning loops (5 or 10 iterations)
- `/sp_optimize`, `/sp_wave`, `/sp_service_planner` – Optimization and phased delivery support

### Utilities & Toggles
- `/sp_translate`, `/sp_tr` – Code and language translation
- `/sp_ultracompressed` – Executive-summary compression
- `/sp_gpt_mode_on` / `/sp_grok_mode_on` / `/sp_claude_mode_on` / `/sp_mode_get` – Engine management
- `/sp_high_mode_on` / `/sp_high_mode_off` – Codex high-reasoning delegation

All commands are also callable via the CLI (`super-prompt dev "Implement onboarding"`), which is useful for scripts and CI hooks.

---

## Personas & Workflows
Super Prompt ships personas tuned for different delivery phases:

| Persona | Primary Output | Core Principles |
| ------- | -------------- | --------------- |
| **Dev** | Task plan, test matrix, release handoff | Clarify scope → design → plan → build → confess |
| **Resercher** | Evidence-backed research briefs | Self-RAG retrieval, Chain-of-Verification, abstain when unsure |
| **Double Check** | Confessional audit + next steps | Confession intake → integrity audit → gap resolution → information request |
| **Doc Master** | Documentation IA & governance | Structure-first writing with review cadences |
| **Security / Performance / QA** | Risk registers & validation plans | KPIs, observability hooks, thresholds |

Each persona is defined in `packages/cursor-assets/manifests/personas.yaml` and mirrored into `personas/manifest.yaml` for project-level overrides. If you need custom behavior, edit the override manifest, rerun `super:init`, and restart Cursor.

---

## Global & SEO Readiness
- **International Usage**: Super Prompt works across North America, EMEA, APAC, and LATAM teams. Prompts and doc outputs stay in English by default, while Claude mode mirrors the user’s latest language automatically for responses.
- **Geo Awareness**: Research workflows encourage citing local regulations and standards. Use `/sp_resercher` to gather region-specific insights before implementation.
- **Search Discoverability**: We publish npm metadata (`keywords`, `homepage`, `repository`) to improve SEO for phrases such as *Cursor MCP extension*, *AI pair programmer*, and *Chain-of-Verification research*. Linking this README in your internal wiki helps reinforce search ranking.

---

## Operations & Troubleshooting
**Reinstall or refresh assets**
```bash
npm install -g @cdw0424/super-prompt@latest
super-prompt super:init --force
```

**Start MCP server manually**
```bash
npx --yes --package=@cdw0424/super-prompt sp-mcp
```

**Verify assets**
```bash
node ./scripts/ssot/verify-ssot.js | cat
node ./scripts/cursor/verify-commands.js | cat
```

Common resolutions:
- **Slash commands missing:** rerun `super:init`, restart Cursor, confirm `.cursor/commands/super-prompt` contents.
- **Mode confusion:** run `/sp_mode_get`, then toggle `/sp_gpt_mode_on`, `/sp_grok_mode_on`, or `/sp_claude_mode_on` as needed.
- **CI usage:** call `super-prompt <tool> "query"` directly; the MCP server is optional outside Cursor.

---

## Frequently Asked Questions

**Does Super Prompt phone home?**  
No. MCP communication stays on `stdin/stdout`. We log only to `.super-prompt/` for local telemetry (optional).

**Can I customize personas?**  
Yes. Edit `personas/manifest.yaml`, then rerun the initializer. Your overrides remain in repo, so teammates share the same guidance.

**How does abstention scoring work?**  
Research personas enforce a configurable threshold `t` (default 0.75). If evidence fails or contradictions exceed 0.2, the assistant returns "I don't know" with follow-up requests.

**Is this production ready?**  
Super Prompt is used internally across multiple geo-distributed teams. We treat it as service software—every release ships with changelog entries, and MCP assets are validated before publish.

**Where can I learn more about Cursor MCP?**  
See the [Cursor MCP announcement](https://www.cursor.com/mcp) and [Model Context Protocol Spec](https://modelcontextprotocol.io/).

---

### Stay Updated
- npm: [`@cdw0424/super-prompt`](https://www.npmjs.com/package/@cdw0424/super-prompt)
- Changelog: `CHANGELOG.md`
- Issues & feedback: open a GitHub issue or reach the maintainers on Cursor Discord

Let Super Prompt handle the research, planning, and verification routine so your team can ship production-quality software faster—with evidence, global context, and zero manual setup.
