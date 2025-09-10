---
description: tasks command
run: "./tag-executor.py"
args: ["sdd tasks ${{input}}"]
---
# ✅ TASKS Breakdown (SDD)

This command breaks down PLAN into actionable tasks.

Format:
- [TASK-ID] Title
  - Description / Deliverables (files/results)
  - Acceptance criteria
  - Estimates/priority/dependencies

Guidelines:
- Minimal changes/small commits oriented, independently verifiable
