# Super Prompt v3 — Architecture Plan (Scaffolded)

## Goals
- Single source of truth in Python core (engine/context/SDD/personas/validation).
- Adapters for Cursor/Codex as thin layers.
- Data-driven personas/rules (YAML/MD) with loaders.
- Performance: git-aware, ignore-aware, incremental context collection.

## Layout (monorepo-style)
```
super-prompt/
├─ packages/
│  └─ core-py/
│     └─ super_prompt/
│        ├─ engine/        # state_machine.py, amr.py
│        ├─ context/       # collector.py (ignore-aware)
│        ├─ sdd/           # gates.py (stage checks)
│        ├─ personas/      # loader.py (YAML)
│        ├─ adapters/      # cursor.py, codex.py (thin)
│        └─ validation/    # todo.py (validators)
└─ scripts/migration/v3/scaffold.py
```

## State Machine & AMR
- Steps: INTENT→TASK_CLASSIFY→PLAN→EXECUTE→VERIFY→REPORT
- AMR: classify (L0/L1/H) → decide switch medium↔high

## Context & SDD
- collector.py: basic .gitignore awareness (pathspec optional in future).
- gates.py: presence checks for specs/plan; expand with tasks/implement.

## Migration Command
- `super-prompt scaffold:v3` — ensures skeleton directories/files exist.

## Next Steps
- Move personas to YAML manifests.
- Replace collector with RG + cache + token budget.
- Add CI (Python/Node matrix) and E2E sample repo tests.

