---
description: specify command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', 'specify'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

📋 Specify
Create Feature Specification.
