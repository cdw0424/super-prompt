---
description: debate command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-debate'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

💬 Debate
Internal debate (positive vs critical analysis)
