---
description: high command - Deep reasoning and strategic problem solving
run: mcp
server: super-prompt
tool: sp_high
args:
  query: "${input}"
  persona: "high"
  force_codex: true
---

## Execution Mode

# High — Guided Execution

## Instructions
- Review the project dossier at `.super-prompt/context/project-dossier.md`; if it is missing, run `/super-prompt/init` to regenerate it.
- Provide a short, specific input describing the goal and constraints
- **Optional high mode:** run `/super-prompt/high-mode-on` first to enable Codex high-effort planning (default is off)
- When enabled, the tool updates Codex via `sudo npm install -g @openai/codex@latest` and executes `codex exec -c 'model_reasoning_effort="high"' -c 'reasoning_summaries=false' --sandbox read-only "<prompt>"`
- If Codex reports a login requirement, run `codex login` in a terminal, complete the browser flow, and retry
- Use MCP Only (MCP server call): /super-prompt/high "<your input>"
- Direct `/high` calls always force Codex execution even when high mode remains off; the toggle only controls automatic hand-offs from other workflows.

## Execution Checklist
- [ ] Define goal and scope
  - What outcome is expected? Any constraints or deadlines?
  - Run Double-Check MCP: /super-prompt/double-check "Confession review for <scope>"

- [ ] Run the tool for primary analysis
  - Use MCP Only (MCP server call): /super-prompt/high "<your input>"
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
