---
description: architect command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-architect'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

🏗️ Architect
System design and architecture specialist
