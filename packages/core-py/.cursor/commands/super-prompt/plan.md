---
description: plan command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', 'plan'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

📋 Plan
Create Implementation Plan.