"""Context collector (v3 scaffold)
- Git-aware file selection
- .gitignore awareness (basic; optional pathspec)
"""
from __future__ import annotations
from typing import Iterable, List, Set
import os

def _load_gitignore_patterns() -> Set[str]:
    pats: Set[str] = set()
    if os.path.exists('.gitignore'):
        try:
            with open('.gitignore','r',encoding='utf-8') as f:
                for line in f:
                    line=line.strip()
                    if line and not line.startswith('#'):
                        pats.add(line)
        except Exception:
            pass
    return pats

def collect_candidates(limit: int = 50) -> List[str]:
    """Collect a small set of representative files respecting .gitignore.
    Intended to be replaced by a ripgrep+cache-based collector in v3 proper.
    """
    excluded = {'.git','node_modules','.next','.npm-cache','.cache','dist','build','__pycache__','.pytest_cache','.vscode','.idea'}
    ig = _load_gitignore_patterns()
    out: List[str] = []
    for root, dirs, files in os.walk('.', topdown=True):
        dirs[:] = [d for d in dirs if d not in excluded]
        # very basic ignore
        if any(root.startswith(p.strip('/') ) for p in ig if p.endswith('/')):
            continue
        for fn in files:
            if len(out) >= limit:
                return out
            path = os.path.join(root, fn)
            out.append(path)
    return out

