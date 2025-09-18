"""Project virtual environment management utilities."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union

from .paths import package_root

PathLike = Union[str, Path]


def _select_python() -> str:
    """Select a Python interpreter for venv creation."""
    if os.name == "nt":
        return "python"

    for candidate in ("python3.12", "python3.11", "python3.10", "python3"):
        if shutil.which(candidate):
            return candidate
    return "python3"


def ensure_project_venv(project_root: PathLike, force: bool = False, offline: Optional[bool] = None) -> Optional[Path]:
    """Ensure the project has a ready-to-use Python virtual environment.

    Parameters
    ----------
    project_root: PathLike
        The project directory where `.super-prompt/venv` will live.
    force: bool
        If True, recreate the virtual environment from scratch.
    offline: Optional[bool]
        Explicit offline toggle. Defaults to reading SUPER_PROMPT_OFFLINE / SP_NO_PIP_INSTALL.
    """
    project_root = Path(project_root).resolve()
    data_dir = project_root / ".super-prompt"
    venv_dir = data_dir / "venv"

    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        if force and venv_dir.exists():
            print(f"-------- venv: removing existing venv at {venv_dir}", file=sys.stderr, flush=True)
            shutil.rmtree(venv_dir)

        if not venv_dir.exists():
            python_cmd = _select_python()
            print(f"-------- venv: creating with {python_cmd} at {venv_dir}", file=sys.stderr, flush=True)
            subprocess.check_call([python_cmd, "-m", "venv", str(venv_dir)])

        if os.name == "nt":
            bin_dir = venv_dir / "Scripts"
            python_bin = bin_dir / "python.exe"
            pip_bin = bin_dir / "pip.exe"
        else:
            bin_dir = venv_dir / "bin"
            python_bin = bin_dir / "python"
            pip_bin = bin_dir / "pip"

        if offline is None:
            offline_env = os.environ.get("SUPER_PROMPT_OFFLINE") or os.environ.get("SP_NO_PIP_INSTALL")
            offline = str(offline_env or "").lower() in ("1", "true", "yes")

        if offline:
            print("-------- venv: offline mode (skip pip installs)", file=sys.stderr, flush=True)
        else:
            try:
                print("-------- venv: upgrading pip", file=sys.stderr, flush=True)
                subprocess.check_call([str(python_bin), "-m", "pip", "install", "--upgrade", "pip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as exc:
                print(f"-------- WARN: pip upgrade failed: {exc}", file=sys.stderr, flush=True)

            deps = [
                "typer>=0.9.0",
                "pyyaml>=6.0",
                "pathspec>=0.11.0",
                "mcp>=0.4.0",
            ]
            try:
                print("-------- venv: installing python deps", file=sys.stderr, flush=True)
                subprocess.check_call([str(pip_bin), "install", *deps], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as exc:
                print(f"-------- WARN: dependency install failed: {exc}", file=sys.stderr, flush=True)

        # Install bundled core wheel if available
        try:
            pkg_root = package_root()
            dist_dirs = [pkg_root / "packages" / "core-py" / "dist", pkg_root / "dist"]
            wheel_path: Optional[Path] = None
            for dist_dir in dist_dirs:
                if not dist_dir.exists():
                    continue
                wheels = sorted(dist_dir.glob("*.whl"), reverse=True)
                if wheels:
                    wheel_path = wheels[0]
                    break
            if wheel_path:
                print(f"-------- venv: installing {wheel_path.name}", file=sys.stderr, flush=True)
                subprocess.check_call([str(pip_bin), "install", str(wheel_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                print("-------- venv: no core wheel found; relying on PYTHONPATH", file=sys.stderr, flush=True)
        except Exception as exc:
            print(f"-------- WARN: core wheel install failed: {exc}", file=sys.stderr, flush=True)

        return venv_dir
    except Exception as exc:
        print(f"-------- WARN: venv setup failed: {exc}", file=sys.stderr, flush=True)
        return None


def _parse_bool(value: str) -> bool:
    return value.lower() in ("1", "true", "yes", "on")


def main(argv: Optional[list[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Ensure Super Prompt project venv")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--force", action="store_true", help="Recreate the venv")
    parser.add_argument("--offline", help="Force offline mode", choices=["true", "false"], default=None)

    args = parser.parse_args(argv)
    offline = None
    if args.offline is not None:
        offline = _parse_bool(args.offline)

    result = ensure_project_venv(args.project_root, force=args.force, offline=offline)
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
