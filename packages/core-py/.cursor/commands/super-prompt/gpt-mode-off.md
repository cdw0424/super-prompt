---
description: gpt-mode-off command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-gpt-mode-off'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

🔴 GPT Mode Off
Disable GPT mode
