---
description: performance command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-performance'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

⚡ Performance
Performance optimization and bottleneck analysis
