---
description: grok-mode-on command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-grok-mode-on'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

🤖 Grok Mode On
Enable Grok mode for advanced AI capabilities
