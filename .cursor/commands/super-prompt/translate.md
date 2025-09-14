---
description: translate command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-translate'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

🔀 Translate
Code translation and format conversion
