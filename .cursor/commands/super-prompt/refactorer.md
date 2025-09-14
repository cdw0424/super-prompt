---
description: refactorer command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-refactorer'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

🔧 Refactorer
Code quality and technical debt management
