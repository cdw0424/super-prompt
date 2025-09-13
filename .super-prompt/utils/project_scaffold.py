#!/usr/bin/env python3
"""
Project scaffold helpers for Super Prompt (fallbacks only).
These are used only when core CLI is not available. Minimal implementations.
"""
import os


def write_text(path: str, content: str, dry: bool = False):
    if dry:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_sdd_rules_files(out_dir: str = ".cursor/rules", dry: bool = False) -> str:
    os.makedirs(out_dir, exist_ok=True)
    org = """---
description: "Project organization rules"
globs: ["**/*"]
alwaysApply: true
---
# Organization
- Keep code modular and testable.
- Follow project coding standards.
"""
    sdd = """---
description: "SDD core & self-check"
globs: ["**/*"]
alwaysApply: true
---
# SDD
1) No implementation before SPEC & PLAN.
2) PLAN: architecture, constraints, NFRs, risks.
3) TASKS: small, testable units.
"""
    fe = """---
description: "Frontend conventions"
globs: ["**/*.tsx", "**/*.jsx", "**/*.css", "**/*.scss"]
---
# Frontend Rules
- Accessibility and performance first.
"""
    be = """---
description: "Backend conventions"
globs: ["**/*.py", "**/*.js", "**/*.java", "**/*.go"]
---
# Backend Rules
- Layered architecture; safe logging; no secrets.
"""
    write_text(os.path.join(out_dir, '00-organization.mdc'), org, dry)
    write_text(os.path.join(out_dir, '10-sdd-core.mdc'), sdd, dry)
    write_text(os.path.join(out_dir, '20-frontend.mdc'), fe, dry)
    write_text(os.path.join(out_dir, '30-backend.mdc'), be, dry)
    return out_dir


def generate_amr_rules_file(out_dir: str = ".cursor/rules", dry: bool = False) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, '05-amr.mdc')
    content = """---
description: "AMR policy"
globs: ["**/*"]
---
# AMR medium ↔ high; fixed state machine
[INTENT] → [TASK_CLASSIFY] → [PLAN] → [EXECUTE] → [VERIFY] → [REPORT]
"""
    write_text(path, content, dry)
    return path


def install_cursor_commands_in_project(dry: bool = False):
    base = os.path.join('.cursor', 'commands', 'super-prompt')
    os.makedirs(base, exist_ok=True)
    tag_sh = """#!/usr/bin/env bash
set -euo pipefail
if command -v super-prompt >/dev/null 2>&1; then
  exec super-prompt optimize "$@"
else
  exec npx @cdw0424/super-prompt optimize "$@"
fi
"""
    write_text(os.path.join(base, 'tag-executor.sh'), tag_sh, dry)
    for name in ['architect','frontend','backend','analyzer']:
        content = f"---\ndescription: {name} command\nrun: \"./tag-executor.sh\"\nargs: [\"${{input}} /{name}\"]\n---\n\n{name.title()} persona"
        write_text(os.path.join(base, f'{name}.md'), content, dry)


def write_codex_agent_assets(dry: bool = False):
    base = os.path.join('.codex')
    os.makedirs(base, exist_ok=True)
    agents = """# Codex Agent — Super Prompt Integration

Use flag-based personas; logs start with '--------'.
"""
    write_text(os.path.join(base, 'agents.md'), agents, dry)

