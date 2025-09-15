---
description: gpt-mode-on command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-gpt-mode-on'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

💻 GPT Mode On
Enable GPT mode for enhanced code generation
