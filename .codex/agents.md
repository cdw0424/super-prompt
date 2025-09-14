# Codex Agent — Super Prompt Integration

Use flag-based personas (no slash commands in Codex). Each persona supports a long flag and an `--sp-` alias.

## Available Personas

### Core Development
- `architect` - Systems architecture and scalability specialist
- `dev` - Feature development specialist (minimal, testable diffs)
- `backend` - Server-side development and API specialist
- `frontend` - UI/UX and accessibility-focused development
- `frontend-ultra` - Elite UX/UI architect and design systems specialist
- `refactorer` - Code quality improvement and technical debt reduction
- `implement` - Implementation specialist (SDD-aligned execution)
- `review` - Code review against SPEC/PLAN and best practices
- `devops` - CI/CD, IaC, reliability and observability

### Analysis Quality
- `analyzer` - Root cause analysis and systematic investigation
- `qa` - Comprehensive quality assurance and testing
- `performance` - Performance optimization and bottleneck analysis
- `security` - Threat modeling and security audits
- `high` - Deep reasoning specialist (plan/review at high effort)

### Knowledge Guidance
- `mentor` - Educational guidance and knowledge transfer
- `scribe` - Technical scribe for decisions and processes
- `doc-master` - Documentation architecture, writing, and verification
- `docs-refector` - Documentation consolidation and refactoring

### Sdd Workflow
- `spec` - Specification writer (SDD)
- `specify` - Specification writer (alias of spec)
- `plan` - Implementation planning (SDD)
- `tasks` - Task breakdown specialist (SDD)
- `task` - Task breakdown assistant (single)

### Database
- `db-expert` - Database expert (Prisma + 3NF)

### Utilities
- `optimize` - Generic optimizer (aggregator entry point)
- `tr` - Translator & transformer (lang/format)
- `wave` - Wave planning (phased delivery)
- `ultracompressed` - Ultra-compressed output (token saving)

### Sequences
- `seq` - Sequential thinking (5 iterations)
- `seq-ultra` - Advanced sequential thinking (10 iterations)

### Experimental
- `debate` - Single-model internal debate (positive vs critical)
- `grok` - Session-only Grok optimization (Cursor-oriented)

### Mode Toggles
- `grok-mode-on` - Enable Grok mode (disables Codex AMR)
- `grok-mode-off` - Disable Grok mode
- `codex-mode-on` - Enable Codex AMR mode (disables Grok)
- `codex-mode-off` - Disable Codex AMR mode

## Usage Examples

```bash
# Architecture planning
super-prompt --architect "Propose modular structure for feature X"
super-prompt --sp-architect "Propose modular structure for feature X"

# Root cause analysis
super-prompt --analyzer "Audit error handling and logging"
super-prompt --sp-analyzer --out .codex/reports/analysis.md "Audit error handling and logging"
```

## SDD Workflow (flag-based)

```bash
super-prompt --sp-sdd-spec "User authentication"
```

```bash
super-prompt --sp-sdd-plan "User registration workflow"
```

```bash
super-prompt --sp-sdd-tasks "Authentication system"
```

```bash
super-prompt --sp-sdd-implement "Authentication system"
```

## Tag Command Priority System

**CRITICAL EXECUTION RULES**:
1. **First Priority**: Tag commands (personas) execute BEFORE any prompt processing
2. **Position Independent**: Tag commands work regardless of position in prompt
3. **Context Separation**: Tag commands upgrade persona/prompt WITHOUT affecting user context
4. **Guaranteed Execution**: Tag command activation is ALWAYS guaranteed

**Tag Command Behavior**:
- Tag commands are TOOLS, not context modifiers
- They enhance persona capabilities for the given prompt
- They execute at highest priority, before any other processing
- User prompt context remains completely unchanged

## Tips
- Logs MUST start with `--------`
- Keep all content in English
- Auto Model Router switches between medium/high reasoning based on complexity

## MCP Integration (Context7)
- Auto-detects Context7 MCP (env `CONTEXT7_MCP=1`)
- Planning personas include MCP usage block for real-source grounding
