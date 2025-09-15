---
description: review command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-review'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

📋 Review
Code review and best practices validation
