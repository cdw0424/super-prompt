---
description: claude-mode-off command - Return to default GPT planning
run: mcp
server: super-prompt
tool: sp_claude_mode_off
---

## Execution Mode

# Claude-Mode-Off — Guided Execution

## Instructions
- Use when Claude-specific guardrails are no longer required; returns to default GPT configuration.
- Review `.super-prompt/context/project-dossier.md`; regenerate with `/super-prompt/init` if necessary.
- After disabling, re-enable another mode (`/super-prompt/gpt-mode-on` or `/super-prompt/grok-mode-on`) as needed.
- Use MCP Only: `/super-prompt/claude-mode-off`

## Execution Checklist
- [ ] Confirm no outstanding tasks depend on Claude-specific outputs.
- [ ] Call `/super-prompt/claude-mode-off`.
- [ ] Verify with `/super-prompt/mode_get`.
- [ ] Update teammates in the prompt guide or runbook if workflow expectations changed.

## Outputs
- Confirmation that Claude guidance has been removed and default GPT planning is restored.
- Reminder to select the next active mode explicitly.
