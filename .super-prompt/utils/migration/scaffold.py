#!/usr/bin/env python3
"""Scaffold v3 architecture (non-destructive).
Creates packages/core-py with core skeleton modules.
"""
import os
from pathlib import Path

def scaffold_v3(root: str = ".") -> None:
    # skeleton already vendored in this package; just ensure dirs exist
    paths = [
        "packages/core-py/super_prompt/engine",
        "packages/core-py/super_prompt/context",
        "packages/core-py/super_prompt/sdd",
        "packages/core-py/super_prompt/personas",
        "packages/core-py/super_prompt/adapters",
        "packages/core-py/super_prompt/validation",
    ]
    for p in paths:
        Path(os.path.join(root, p)).mkdir(parents=True, exist_ok=True)
    print("--------v3: scaffold ensured under packages/core-py")

if __name__ == "__main__":
    scaffold_v3(".")
