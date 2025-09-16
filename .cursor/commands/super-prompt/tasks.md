---
description: tasks command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', 'tasks'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

📋 Tasks
Create Task Breakdown.
