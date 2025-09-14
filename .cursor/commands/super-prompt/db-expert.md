---
description: db-expert command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-db-expert'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

🗄️ DB Expert
Database design and query optimization
