---
description: backend command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-backend'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

⚙️ Backend
Server-side development and API specialist
