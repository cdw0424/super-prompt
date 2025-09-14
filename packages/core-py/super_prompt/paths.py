"""
Path utilities for Super Prompt
Centralized path resolution with typo correction
"""

import os
from pathlib import Path


def package_root() -> Path:
    """
    Get the package root directory.
    Priority: SUPER_PROMPT_PACKAGE_ROOT env var > file-based search
    """
    env = os.environ.get("SUPER_PROMPT_PACKAGE_ROOT")
    if env and Path(env).exists():
        return Path(env).resolve()

    # File-based search from current file location
    p = Path(__file__).resolve()
    while p != p.parent:
        if (p / "packages" / "cursor-assets").exists() or (p / "package.json").exists():
            return p
        p = p.parent

    # Fallback to conservative estimate
    return Path(__file__).parent.parent.parent


def project_root() -> Path:
    """
    Get the project root directory.
    Uses SUPER_PROMPT_PROJECT_ROOT env var if set, otherwise cwd
    """
    env = os.environ.get("SUPER_PROMPT_PROJECT_ROOT")
    return Path(env).resolve() if env else Path.cwd().resolve()


def project_data_dir() -> Path:
    """
    Get the project data directory (.super-prompt).
    Automatically corrects typo from .super-promp to .super-prompt
    """
    pr = project_root()
    correct = pr / ".super-prompt"
    wrong = pr / ".super-promp"  # common typo

    # Auto-correct: if only wrong exists and correct doesn't, rename
    if wrong.exists() and not correct.exists():
        try:
            wrong.rename(correct)
            print(f"----- DEBUG: Corrected typo folder: {wrong} -> {correct}")
        except Exception as e:
            print(f"----- DEBUG: Could not correct typo folder: {e}")

    return correct


def assets_root() -> Path:
    """Get the assets root directory"""
    return package_root() / "packages"


def cursor_assets_root() -> Path:
    """Get the Cursor assets root directory"""
    return assets_root() / "cursor-assets"


def codex_assets_root() -> Path:
    """Get the Codex assets root directory"""
    return assets_root() / "codex-assets"
