---
description: claude-mode-on command - Enable Claude-native prompt discipline
run: mcp
server: super-prompt
tool: sp_claude_mode_on
---

## Execution Mode

# Claude-Mode-On — Guided Execution

## Instructions
- Run this before Claude personas should take over; it installs Claude guidance and disables GPT/Grok rules.
- Review `.super-prompt/context/project-dossier.md`; if missing, call `/super-prompt/init` first.
- Pair this toggle with the design notes in `docs/claude-persona-guide.md` and `docs/claude-operations.md`.
- Use MCP Only: `/super-prompt/claude-mode-on`
- Responses will mirror the language of the latest user message; switch languages by changing user input.

## Execution Checklist
- [ ] Confirm that Claude mode is required (XML-structured output, Korean-first tone, etc.).
- [ ] Call `/super-prompt/claude-mode-on`.
- [ ] Re-run `/super-prompt/mode_get` to verify the mode switch.
- [ ] Rerun `/super-prompt/tasks` if follow-up planning is needed under Claude guidance.

## Outputs
- Confirmation that Claude mode is active and Claude guidance rules are installed.
- Reminder to consult the Claude persona guide and operations playbook.
