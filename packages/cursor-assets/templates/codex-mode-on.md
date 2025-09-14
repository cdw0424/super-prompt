---
description: Enable Codex AMR mode (Cursor)
run: "./.cursor/commands/super-prompt/tag-executor.sh"
args: ["/codex-mode-on"]
---

Enable Codex Auto Model Router mode for all subsequent commands by creating `.cursor/.codex-mode`.

In this mode, planning and review steps can opt into high-effort reasoning with clear router signals while execution returns to medium-effort.

Usage
```
/codex-mode-on
```

