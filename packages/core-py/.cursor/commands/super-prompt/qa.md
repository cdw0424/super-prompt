---
description: qa command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-qa'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

✅ QA
Quality assurance and testing specialist
