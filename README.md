---
title: Super Prompt — Zero‑config MCP toolkit for Cursor & Codex
description: Super Prompt is a zero-config, MCP-powered toolkit for Cursor IDE and Codex, providing 29+ AI tools, personas, SDD workflow, and slash commands.
keywords:
  - Super Prompt
  - MCP
  - Cursor IDE
  - Codex
  - AI tools
  - Personas
  - SDD
  - Slash commands
  - Documentation tooling
last_updated_utc: 2025-09-23T00:00:00Z
---

# Super Prompt

> 한국어 요약: Super Prompt는 Cursor와 Codex에서 바로 쓸 수 있는 MCP 기반 툴킷입니다. 설치 한 줄로 29개+ 도구와 6개 페르소나, SDD 워크플로, 슬래시 커맨드를 제공합니다. 프롬프트/문서/작업은 영어를 기준으로 하며, 비밀값은 항상 `sk-***` 형태로 마스킹하세요.

[![npm version](https://img.shields.io/npm/v/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![npm downloads](https://img.shields.io/npm/dt/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.17-brightgreen)](https://nodejs.org/)

Super Prompt is a zero-config, MCP-powered toolkit for Cursor IDE and Codex. It provides
29+ AI tools including 6 specialized personas, context management, SDD workflow
tools, and seamless slash command integration. All tools are accessible via
Cursor's slash commands (/) for instant AI assistance.

## 1) Install (one line)

```bash
npm install -g @cdw0424/super-prompt@latest
```

## 2) Quick Start

```bash
super-prompt super:init --force
```

The initializer will:

- create `.cursor/` and copy command/rule assets
- create `.super-prompt/` internal config
- register the MCP server with 29+ AI tools

Then restart Cursor (fully quit and relaunch).

**Slash Commands**: All tools are accessible via Cursor's slash commands (/) for
instant AI assistance:

```bash
/sp_analyzer "Analyze this code performance"
/sp_architect "Design a microservice architecture"
/sp_doc_master "Generate API documentation"
/sp_refactorer "Refactor this function"
/sp_frontend "Review React component"
/sp_backend "Optimize database queries"
```

You can also call documentation tooling directly:

```bash
/super-prompt/doc-master "Create API documentation structure"
```

**Mode Switching**:

```bash
/sp_gpt_mode_on    # Switch to GPT mode
/sp_grok_mode_on   # Switch to Grok mode
/sp_mode_get       # Check current mode
```

## 3) Modes (per language)

- **GPT mode (default)**: structured, deterministic, great for APIs, reviews,
  docs
- **Grok mode**: exploratory, creative, great for architecture, debugging,
  ideation

You can mix modes per task; the tool registry is stable during switches.

## 4) MCP Server (Cursor/Codex)

After initialization, the MCP server configuration is placed at `.cursor/mcp.json` (Cursor) and `.codex/mcp.json` (Codex, if used). You can also start the server directly for diagnostics:

```bash
# Start MCP server directly
npx --yes --package=@cdw0424/super-prompt sp-mcp
```

To verify MCP assets and rules (SSOT):

```bash
# Verify SSOT materialization
node ./scripts/ssot/verify-ssot.js | cat

# Verify Cursor command assets
node ./scripts/cursor/verify-commands.js | cat
```

## 5) If something goes wrong

Try in order:

```bash
# Ensure latest package
npm install -g @cdw0424/super-prompt@latest

# Re-run initializer
super-prompt super:init --force

# Still odd? Use npx (bypasses PATH)
npx --yes @cdw0424/super-prompt@latest super:init --force
```

Using an older global binary? The CLI now auto-switches to the npm global binary
when it detects a Homebrew/legacy wrapper first in PATH. No manual PATH edits
needed.

## 6) What we believe (short)

- **MCP-first**: clear tool boundaries, reproducible automations
- **Zero‑config UX**: it should "just work" on first run
- **Productivity personas**: focused prompts with measurable outputs

## 7) What you get

### MCP Tools (29+ slash commands)

All tools are accessible via Cursor's slash commands (/) for instant AI
assistance:

**Persona Tools (6)**

- `/sp_analyzer` - Code analysis and performance optimization
- `/sp_architect` - System architecture design and planning
- `/sp_frontend` - Frontend development and UI/UX guidance
- `/sp_backend` - Backend development and API design
- `/sp_refactorer` - Code refactoring and cleanup
- `/sp_doc_master` - Documentation generation and organization

**Specialized Tools**

- `/sp_security` - Security analysis and threat modeling
- `/sp_performance` - Performance optimization and profiling
- `/sp_qa` - Quality assurance and testing strategies
- `/sp_devops` - DevOps and infrastructure guidance
- `/sp_mentor` - Educational guidance and code reviews
- `/sp_scribe` - Professional writing and content creation

**Database & Optimization**

- `/sp_db_expert` - Database design and query optimization
- `/sp_optimize` - Code optimization suggestions

**Creative & Strategic**

- `/sp_grok` - Creative problem solving with Grok AI
- `/sp_debate` - Structured technical debates
- `/sp_service_planner` - Service architecture planning
- `/sp_wave` - Advanced service planning

**Development Workflow (SDD)**

- `/sp_specify` - Create detailed technical specifications
- `/sp_plan` - Generate implementation plans from specs
- `/sp_tasks` - Break down plans into actionable tasks
- `/sp_implement` - Implementation guidance

**Advanced Analysis**

- `/sp_seq` - Sequential thinking and analysis
- `/sp_seq_ultra` - Deep sequential analysis
- `/sp_high` - High-level thinking and abstraction

**Utilities**

- `/sp_translate` - Code translation between languages
- `/sp_tr` - Quick translation tool
- `/sp_ultracompressed` - Ultra-compressed responses
- `/sp_gpt_mode_on` / `/sp_gpt_mode_off` - GPT mode control
- `/sp_grok_mode_on` / `/sp_grok_mode_off` - Grok mode control
- `/sp_mode_get` - Check current mode

## 8) MCP Server Configuration

After running `super:init`, the MCP server is automatically configured at
`.cursor/mcp.json`. Each tool is independently callable through Cursor's slash
commands.

## 9) Advanced Usage

### Direct Command Line Usage

For debugging or direct tool usage:

```bash
# Run any tool directly
super-prompt analyzer "analyze this code pattern"
super-prompt architect "design a microservice"
super-prompt doc-master "create API documentation"
```

### Project-Specific Configuration

Super Prompt stores configuration in `.super-prompt/` directory:

- `config.json` - Main configuration
- `mode.json` - Current mode (GPT/Grok)

## 10) Troubleshooting

| Issue | Solution |
| --- | --- |
| **Tools not showing in Cursor** | Restart Cursor completely (quit and relaunch) |
| **"Command failed" error** | Run `super-prompt super:init --force` to reinitialize |
| **Python errors during install** | Ensure Python 3.8+ is installed: `python3 --version` |
| **Permission errors** | Use `sudo npm install -g @cdw0424/super-prompt@latest` |
| **Version shows older release after installation** | Run `npm uninstall -g @cdw0424/super-prompt` to remove old versions, then reinstall with `npm install -g @cdw0424/super-prompt@latest` |

## 11) Documentation

- **[CHANGELOG](./CHANGELOG.md)** - Version history and updates
- **[Architecture Overview](./docs/architecture-v5.md)** - System design and
  implementation details

## 12) SEO metadata and anchors

- Prefer clean, descriptive H2/H3 headings.
- Use stable anchors in docs and link to them from issues/PRs.
- Include a metadata/frontmatter block with `title`, `description`, `keywords`, and `last_updated_utc` (UTC).

Frontmatter template for docs pages:

```yaml
---
title: <Page Title>
description: <Short description (≤160 chars)>
keywords:
  - Super Prompt
  - <Topic>
last_updated_utc: 2025-09-23T00:00:00Z
---
```

## 13) GEO and localization guidance

- Primary documentation language is English. Keep prompts/docs in English.
- Add concise Korean summaries when helpful; avoid diverging content.
- Use region-neutral examples and UTC timestamps.
- Never print secrets or tokens; mask like `sk-***`.
- Prefer absolute paths in examples when clarity matters, e.g., `/Users/<you>/project/.cursor/mcp.json`.

Localization snippet template:

```md
> 한국어 요약: <1–2 lines summary. English remains canonical.>
```

## 14) SDD & SSOT verification checklist

- Align with SSOT order:
  1) `packages/cursor-assets/manifests/personas.yaml` (or `personas/manifest.yaml`)
  2) `.cursor/rules/*.mdc`
  3) `AGENTS.md`
- Ensure SPEC/PLAN/TASKS exist for new features under `specs/`.
- Run acceptance self-check before PR:
  - Validate success criteria
  - Verify non-functional constraints
  - Safe logging (no secrets/PII)
  - Regression tests added
  - Documentation updated

Helpful scripts:

```bash
bash ./scripts/codex/router-check.sh | cat
python3 ./scripts/sdd/acceptance_self_check.py | cat
```

## License

MIT © Daniel Choi

## Contributing

Issues and PRs welcome at
[GitHub](https://github.com/cdw0424/super-prompt/issues).