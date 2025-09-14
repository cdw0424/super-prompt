---
description: security command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-security'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

🛡️ Security
Security analysis and threat modeling
