---
description: analyzer command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-analyzer'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

🔍 Analyzer
Root cause analysis and systematic investigation
