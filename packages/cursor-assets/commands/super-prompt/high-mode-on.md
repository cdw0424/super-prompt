---
description: Enable Codex-backed high reasoning mode
run: mcp
server: super-prompt
tool: sp_high_mode_on
---

## Execution Mode

# High Mode On — Toggle

## Instructions
- Use before invoking `/super-prompt/high` when you need Codex high-effort planning
- Ensures the workspace runs `sudo npm install -g @openai/codex@latest` automatically before planning
- If Codex requests authentication, complete it with `codex login` in a terminal and rerun your command

## Outputs
- Confirms high reasoning mode is active for subsequent `/high` or `sp_high` calls
