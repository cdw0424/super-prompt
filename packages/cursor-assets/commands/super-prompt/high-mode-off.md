---
description: Disable Codex-backed high reasoning mode (default)
run: mcp
server: super-prompt
tool: sp_high_mode_off
---

## Execution Mode

# High Mode Off — Toggle

## Instructions
- Run to revert `/super-prompt/high` back to prompt-based planning without Codex
- Useful when Codex access is unavailable or you prefer lightweight reasoning
- This is the default state for fresh workspaces

## Outputs
- Confirms high reasoning mode is disabled; future `/high` calls fall back to internal planners
