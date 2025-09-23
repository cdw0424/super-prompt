---
description: gpt-mode-on command
run: mcp
server: super-prompt
tool: sp_gpt_mode_on
---

## Execution Mode

# Gpt-Mode-On — Guided Execution

## Instructions
- Provide a short, specific input describing the goal and constraints
- Prefer concrete artifacts (file paths, diffs, APIs) for higher quality output
- Use MCP Only: /super-prompt/gpt-mode-on "<your input>"

## Execution Checklist
- [ ] Define goal and scope
  - What outcome is expected? Any constraints or deadlines?
  - Run Double-Check: /super-prompt/double-check "Confession review for <scope>"

- [ ] Run the tool for primary analysis
  - Use MCP Only: /super-prompt/gpt-mode-on "<your input>"
  - Run Double-Check: /super-prompt/double-check "Confession review for <scope>"

- [ ] Apply recommendations and produce artifacts
  - Implement changes, write tests/docs as needed
  - Run Double-Check: /super-prompt/double-check "Confession review for <scope>"

- [ ] Convert follow-ups into tasks
  - Use MCP Only: /super-prompt/tasks "Break down follow-ups into tasks"
  - Run Double-Check: /super-prompt/double-check "Confession review for <scope>"

## Outputs
- Prioritized findings with rationale
- Concrete fixes/refactors with examples
- Follow-up TODOs (tests, docs, monitoring)

