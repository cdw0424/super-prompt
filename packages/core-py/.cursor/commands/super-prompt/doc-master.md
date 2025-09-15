---
description: doc-master command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-doc-master'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

📚 Doc Master
Documentation architecture, writing, and verification
