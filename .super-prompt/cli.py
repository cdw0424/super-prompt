#!/usr/bin/env python3
"""
Project-local Super Prompt CLI launcher.
Bridges the Node wrapper to the Python package located at packages/core-py.

This thin shim avoids relative-import issues by prepending the package path
to sys.path and delegating to super_prompt.cli:main().
"""

import os
import sys


def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _ensure_core_py_on_path() -> None:
    # Try project-local packages first
    super_prompt_dir = os.path.dirname(__file__)
    core_py = os.path.join(super_prompt_dir, "packages", "core-py")

    # Fallback to project root packages
    if not os.path.exists(core_py):
        root = _project_root()
        core_py = os.path.join(root, "packages", "core-py")

    if os.path.exists(core_py) and core_py not in sys.path:
        sys.path.insert(0, core_py)


def main() -> None:
    _ensure_core_py_on_path()
    try:
        from super_prompt.cli import main as super_prompt_main  # type: ignore
    except Exception as e:
        print(f"-------- Failed to import super_prompt.cli: {e}")
        print("-------- Ensure 'packages/core-py' exists and is a valid package")
        sys.exit(1)

    # Delegate to the real CLI
    super_prompt_main()


if __name__ == "__main__":
    main()

