---
description: seq command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-seq'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

🔍 Sequential
Sequential reasoning and step-by-step analysis
