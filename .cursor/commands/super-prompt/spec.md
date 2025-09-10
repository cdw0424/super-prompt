---
description: spec command
run: "./tag-executor.py"
args: ["sdd spec ${{input}}"]
---
# 📋 SPEC Creator (SDD)

This command generates SDD-compliant specifications.

Output includes:
- Goals, user value, success criteria
- Scope boundaries (what's included/excluded)
- Key assumptions and constraints
- Acceptance criteria checklist

Principles:
- Avoid premature stack/vendor choices
- Focus on user outcomes and business value