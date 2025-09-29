# Super Prompt - MCP-First Cursor Integration Guide

This guide shows how to leverage **Super Prompt's 29+ specialized MCP tools** with Cursor AI for **enterprise-grade development workflows** using the **SDD (Scope → Design → Delivery) methodology**.

## 🎯 **Super Prompt SDD Workflow**

Super Prompt transforms Cursor AI into an **enterprise-grade development copilot** using:

- **29+ Specialized MCP Tools**: Each optimized for specific development tasks
- **SDD Methodology**: Scope → Design → Delivery workflow
- **LLM-Optimized Personas**: GPT, Claude, Grok modes for different task types
- **Evidence-First Approach**: All outputs include citations and validation

### 🚀 **One-Shot Setup (MCP-First Integration)**

```bash
npx @cdw0424/cursor-one-shot@latest
```

This configures:
- **MCP-First Rules**: Prioritize Super Prompt tools over manual coding
- **29+ MCP Tools**: Global access to specialized development tools
- **LLM Mode Optimization**: Automatic persona selection for task types
- **Quality Guardrails**: Evidence requirements and double-check rituals

---

## 🏗️ **Architecture: MCP-First Development**

### **29+ Specialized MCP Tools**

| Category | Tools | Purpose |
|----------|-------|---------|
| **Planning** | `sp_specify`, `sp_plan`, `sp_tasks` | SDD workflow foundation |
| **Analysis** | `sp_analyzer`, `sp_researcher`, `sp_review` | Evidence-based investigation |
| **Architecture** | `sp_architect`, `sp_backend`, `sp_frontend` | System design and structure |
| **Implementation** | `sp_implement`, `sp_refactorer`, `sp_optimize` | Code generation and improvement |
| **Quality** | `sp_qa`, `sp_security`, `sp_performance` | Testing and validation |
| **Documentation** | `sp_scribe`, `sp_doc_master`, `sp_translate` | Knowledge management |
| **Operations** | `sp_devops`, `sp_db_expert`, `sp_service_planner` | Infrastructure and deployment |

### **SDD Workflow Integration**

```
1. 📋 Specify → 2. 📝 Plan → 3. ✅ Tasks → 4. 🚀 Implement
   ↓              ↓           ↓           ↓
/specify    /plan       /tasks      /implement
```

### **LLM Mode Optimization**

- **🤖 GPT Mode**: Complex reasoning, analysis, research tasks
- **🧠 Claude Mode**: Structured planning, XML workflows, documentation
- **⚡ Grok Mode**: Rapid implementation, optimization, refactoring

### **Context Management (Super Prompt Enhanced)**

- **@Cursor Rules**: Loads MCP-First development principles
- **@codebase**: Enhanced with Super Prompt's evidence-based analysis
- **@Web**: Integrated with research tools and citation tracking
- **Project Dossier**: Automatic context at `.super-prompt/context/project-dossier.md`

### **SDD Documentation Management**

Every SDD phase generates comprehensive, traceable documentation:

#### **Phase Documentation Structure**
```
docs/sdd/projects/{project-name}/
├── 01-specification/
│   ├── spec.md              # Requirements & scope
│   ├── requirements.md       # Detailed requirements
│   └── context.md           # Background & stakeholders
├── 02-planning/
│   ├── plan.md              # Implementation strategy
│   ├── architecture.md      # System architecture
│   └── risks.md             # Risk assessment
├── 03-tasks/
│   ├── tasks.md             # Task breakdown
│   ├── timeline.md          # Project timeline
│   └── assignments.md       # Team assignments
└── 04-implementation/
    ├── implementation.md     # Implementation tracking
    ├── changes.md           # Code/configuration changes
    └── results.md           # Results & outcomes
```

#### **Documentation Automation**
- **Project Creation**: `./scripts/cursor/create-sdd-project.sh "Project Name"`
- **Status Updates**: `./scripts/cursor/update-sdd-docs.sh [project-name]`
- **Template-Driven**: Consistent structure across all projects
- **Version Tracking**: Documents evolve with code changes

## Quick Start

### One-Shot Setup

For new projects or team members, use the automated setup:

```bash
npx @cdw0424/cursor-one-shot@latest
```

This single command will:
- Create `.cursor/rules/` with core principles and guardrails
- Set up `.cursorignore` for performance and security
- Configure global MCP servers in `~/.cursor/mcp.json`
- Generate install links for team sharing

### Manual Setup

If you prefer manual configuration:

1. **Install Cursor CLI**:
   ```bash
   curl https://cursor.com/install -fsS | bash
   ```

2. **Create project rules** (already done if using the repo):
   ```bash
   mkdir -p .cursor/rules
   # Copy 00-core.mdc and 90-guardrails.mdc to .cursor/rules/
   ```

3. **Configure MCP servers**:
   ```bash
   mkdir -p ~/.cursor
   # Copy the mcp.json configuration to ~/.cursor/mcp.json
   ```

## Architecture Overview

### Rules System

The project uses a structured rules system:

- **00-core.mdc**: Universal principles for all AI interactions
- **90-guardrails.mdc**: Security and cost protection measures
- **Additional rules**: Project-specific guidance in `packages/cursor-assets/rules/`

### MCP Integration

Two MCP servers are configured globally:

1. **super-prompt-core**: Python-based core functionality
2. **super-prompt-mcp**: Node.js MCP server for tool integration

### Context Management

- **@Cursor Rules**: Access project rules in any chat
- **@codebase**: Intelligent code search and understanding
- **@Web**: Web search and documentation lookup
- **Reuse Existing Code**: Automatic code reuse policy enforcement

## Daily Workflow

### Development Tasks

1. **Start a conversation**: Open any file in Cursor
2. **Load context**: Use `@Cursor Rules` to inject project principles
3. **Code exploration**: Use `@codebase` for understanding existing code
4. **Generate code**: AI will automatically reuse existing patterns
5. **Review changes**: Use `@codebase` to verify integration

### Code Review

```bash
# Review recent changes
cursor-agent -p --output-format text \
  "Review the latest changes for correctness, security, and tests. Summarize key risks."
```

### Refactoring

```bash
# Merge duplicate utilities
cursor-agent "Refactor duplicated helpers into a single utility with tests."
```

## Configuration Details

### Rules Structure

```
.cursor/rules/
├── 00-core.mdc          # Universal principles
├── 10-style.mdc         # Coding standards
├── 20-testing.mdc       # Testing guidelines
└── 90-guardrails.mdc    # Security/cost controls
```

### MCP Server Configuration

```json
{
  "mcpServers": {
    "super-prompt-core": {
      "command": "python",
      "args": ["-m", "super_prompt.mcp_server"],
      "cwd": "/path/to/super-prompt/python-packages/super-prompt-core",
      "transport": "stdio"
    }
  }
}
```

### Cursorignore Patterns

Key exclusions for performance:
- `node_modules/`, `dist/`, `coverage/`
- `__pycache__/`, `*.pyc`, `.env*`
- Build artifacts and temporary files

## Troubleshooting

### Network Issues
1. Run `Settings → Network → Run Diagnostics`
2. Check MCP server connectivity
3. Verify global MCP configuration

### Performance Issues
1. Review `.cursorignore` for unnecessary files
2. Check indexing settings in Cursor
3. Consider using Max Mode only when necessary

### Integration Problems
1. Verify Cursor CLI installation
2. Check MCP server paths in `~/.cursor/mcp.json`
3. Ensure project rules are properly formatted

## Team Integration

### Onboarding New Members

1. Share the one-shot setup command
2. Provide install links JSON for MCP configuration
3. Include Cursor integration in team documentation

### CI/CD Integration

```bash
# Verify Cursor integration in CI
cursor-agent mcp  # Check MCP connectivity
cursor-agent -p "Verify project rules are properly loaded"
```

## Advanced Configuration

### Custom Rules

Add project-specific rules to `.cursor/rules/`:
- Use numbered prefixes (30-, 40-, etc.)
- Include `---` frontmatter with description and globs
- Set `alwaysApply: true` for critical rules

### MCP Server Development

To add new MCP tools:
1. Implement server following MCP protocol
2. Add to `~/.cursor/mcp.json`
3. Test with `cursor-agent mcp`

### Performance Optimization

- Use specific globs in rules to limit scope
- Configure indexing to focus on source directories
- Enable "Reuse Existing Code" for large codebases
- Use Max Mode sparingly for complex multi-file operations

## Security Considerations

- Rules prevent modification of production configs
- Terminal access requires explicit approval
- Network/MCP calls require argument summaries
- Large prompts need explicit Max Mode approval
- Sensitive files excluded via `.cursorignore`

## Migration from Other Tools

- Export existing configurations
- Import rules into `.cursor/rules/`
- Configure MCP servers for custom tools
- Update team documentation
- Test integration thoroughly

## Support

For issues with Cursor integration:
1. Check the troubleshooting section above
2. Review Cursor's official documentation
3. Test with minimal configuration
4. Report issues with full context and logs
