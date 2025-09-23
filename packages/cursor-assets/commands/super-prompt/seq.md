---
description: seq command
run: mcp
server: super-prompt
tool: sp_seq
args:
  query: "${input}"
  persona: "seq"
---

## Execution Mode

# Seq — Guided Execution

## Instructions
- Review the project dossier at `.super-prompt/context/project-dossier.md`; if it is missing, run `/super-prompt/init` to regenerate it.
- Provide a short, specific input describing the goal and constraints
- Prefer concrete artifacts (file paths, diffs, APIs) for higher quality output
- Use MCP Only (MCP server call): /super-prompt/seq "<your input>"

## Execution Checklist
- [ ] Define goal and scope
  - What outcome is expected? Any constraints or deadlines?
  - Run Double-Check MCP: /super-prompt/double-check "Confession review for <scope>"

- [ ] Run the tool for primary analysis
  - Use MCP Only (MCP server call): /super-prompt/seq "<your input>"
  - Run Double-Check MCP: /super-prompt/double-check "Confession review for <scope>"

- [ ] Apply recommendations and produce artifacts
  - Implement changes, write tests/docs as needed
  - Run Double-Check MCP: /super-prompt/double-check "Confession review for <scope>"

- [ ] Convert follow-ups into tasks
  - Use MCP Only (MCP server call): /super-prompt/tasks "Break down follow-ups into tasks"
  - Run Double-Check MCP: /super-prompt/double-check "Confession review for <scope>"

## Outputs
- Prioritized findings with rationale
- Concrete fixes/refactors with examples
- Follow-up TODOs (tests, docs, monitoring)

