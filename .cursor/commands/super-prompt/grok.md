---
description: Grok Code Fast 1 optimized execution (Cursor)
run: "./.cursor/commands/super-prompt/tag-executor.sh"
args: ["${input}"]
---

Start a session optimized for Grok Code Fast 1. This command:
- Uses native tool-calling patterns (no XML wrappers)
- Encourages explicit GOALS/CONTEXT/PLAN/EXECUTE/VERIFY sections
- Keeps prompts stable to maximize Grok cache hits

Usage
```
/grok [your request]
```

