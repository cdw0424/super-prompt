---
description: service-planner command
run: "python3"
args: ["-c", "import subprocess; subprocess.run(['super-prompt', '--persona-service-planner'] + __import__('sys').argv[1:], input='${input}', text=True, check=False)"]
---

🧭 Service Planner
Service planning expert (product strategy from discovery → delivery → growth)
