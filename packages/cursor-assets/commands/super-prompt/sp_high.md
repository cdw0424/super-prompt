---
description: sp_high command - Explicit Codex high reasoning entrypoint
run: mcp
server: super-prompt
tool: sp_high
args:
  query: "${input}"
  persona: "high"
  force_codex: true
---

## Execution Mode

# SP_High — Guided Execution

## Instructions
- Use this alias when workflows require an explicit `sp_high` MCP invocation
- Provide a concise objective plus constraints; reference concrete files or systems when possible
- Enable Codex planning via `/super-prompt/high-mode-on` (default is disabled)
- When enabled, the tool updates Codex via `sudo npm install -g @openai/codex@latest` and runs `codex exec -c 'model_reasoning_effort="high"' -c 'reasoning_summaries=false' --sandbox read-only "<prompt>"`
- Complete `codex login` in a terminal if prompted before retrying the command
- For regular usage you can also trigger `/super-prompt/high "<your input>"`
- Direct `/sp_high` invocations always force Codex execution even when high mode remains off; the toggle only affects automatic delegations from other commands.

## Execution Checklist
- [ ] Clarify goal and constraints
  - Capture desired outcome, deadlines, and blocking dependencies
  - Run Double-Check MCP: /super-prompt/double-check "Confession review for <scope>"

- [ ] Request the high-effort plan
  - Invoke `/super-prompt/sp_high "<your input>"`
  - Run Double-Check MCP: /super-prompt/double-check "Confession review for <scope>"

- [ ] Execute according to the plan
  - Apply recommended changes, tests, and documentation updates
  - Run Double-Check MCP: /super-prompt/double-check "Confession review for <scope>"

- [ ] Capture follow-ups
  - Use: /super-prompt/tasks "Break down follow-ups into tasks"
  - Run Double-Check MCP: /super-prompt/double-check "Confession review for <scope>"

## Outputs
- Detailed Codex-generated implementation plan
- Enumerated risks, validation steps, and MCP follow-up recommendations
- Actionable TODOs scoped for downstream tools or human review
