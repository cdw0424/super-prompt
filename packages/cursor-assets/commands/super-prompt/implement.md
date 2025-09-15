---
description: implement command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', 'implement'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

📋 Implement
Execute Implementation.