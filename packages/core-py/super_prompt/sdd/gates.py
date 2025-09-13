"""SDD gates (v3 scaffold)
Spec/Plan/Tasks/Implement stage checks.
"""
from dataclasses import dataclass
from typing import List

@dataclass
class GateReport:
    ok: bool
    missing: List[str]

def check_spec_plan() -> GateReport:
    miss = []
    import os
    if not os.path.exists('specs'):
        miss.append('specs/')
    if not any(p.endswith('/spec.md') for p in _glob('specs')):
        miss.append('spec.md')
    if not any(p.endswith('/plan.md') for p in _glob('specs')):
        miss.append('plan.md')
    return GateReport(ok=not miss, missing=miss)

def _glob(root: str):
    for dirpath, _, files in __import__('os').walk(root):
        for f in files:
            yield f"{dirpath}/{f}"

