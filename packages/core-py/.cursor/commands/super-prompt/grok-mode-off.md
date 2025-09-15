---
description: grok-mode-off command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-grok-mode-off'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

🔴 Grok Mode Off
Disable Grok mode
