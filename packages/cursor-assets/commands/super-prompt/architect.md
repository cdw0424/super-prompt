---
description: architect command - System design and architecture analysis with Mermaid diagrams
run: mcp
server: super-prompt
tool: sp_architect
args:
  query: "${input}"
  persona: "architect"
---

## Execution Mode

# Architect — Guided Execution with Visual Architecture Diagrams

## Instructions
- Review the project dossier at `.super-prompt/context/project-dossier.md`; if it is missing, run `/super-prompt/init` to regenerate it.
- Provide a short, specific input describing the goal and constraints
- Prefer concrete artifacts (file paths, diffs, APIs) for higher quality output
- Use MCP Only (MCP server call): /super-prompt/architect "<your input>"
- **Always includes Mermaid diagrams** in final results for visual architecture representation

## Execution Checklist
- [ ] Define goal and scope
  - What outcome is expected? Any constraints or deadlines?
  - Run Double-Check MCP: /super-prompt/double-check "Confession review for <scope>"

- [ ] Run the tool for primary analysis
  - Use MCP Only (MCP server call): /super-prompt/architect "<your input>"
  - Run Double-Check MCP: /super-prompt/double-check "Confession review for <scope>"

- [ ] Apply recommendations and produce artifacts
  - Implement changes, write tests/docs as needed
  - **Generate Mermaid diagrams** for all architecture components
  - Run Double-Check MCP: /super-prompt/double-check "Confession review for <scope>"

- [ ] Convert follow-ups into tasks
  - Use MCP Only (MCP server call): /super-prompt/tasks "Break down follow-ups into tasks"
  - Run Double-Check MCP: /super-prompt/double-check "Confession review for <scope>"

## Outputs
- **Mermaid Architecture Diagrams** (always included)
  - System component diagrams
  - Data flow diagrams
  - Deployment diagrams
  - Sequence diagrams as needed
- Prioritized findings with rationale
- Concrete fixes/refactors with examples
- Follow-up TODOs (tests, docs, monitoring)

## Mermaid Diagram Types
Based on [Cursor Mermaid Documentation](https://cursor.com/ko/docs/configuration/tools/mermaid-diagrams):
- `graph TD` - Top-down flowcharts
- `graph LR` - Left-right flowcharts
- `graph BT` - Bottom-up flowcharts
- `sequenceDiagram` - Interaction sequences
- `classDiagram` - Class relationships
- `stateDiagram-v2` - State machines
- `erDiagram` - Entity relationships
- `journey` - User journey maps

