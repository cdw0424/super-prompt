---
description: scribe command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-scribe'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

📝 Scribe
Technical writing and developer documentation
