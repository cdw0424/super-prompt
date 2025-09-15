---
description: optimize command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-optimize'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

🎯 Optimize
Generic optimization and efficiency improvements
