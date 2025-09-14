---
description: grok command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-grok'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

🧠 Grok Session
Session-only Grok optimization
