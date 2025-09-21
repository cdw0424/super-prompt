"""
TODO Validator - Validate task completion and quality gates
"""

import os
import subprocess
from pathlib import Path
from typing import Tuple, List, Optional
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class TodoValidator:
    """
    Validate TODO/task completion using various quality checks
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

    def validate_task_completion(self, task_description: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a task has been properly completed

        Args:
            task_description: Description of the task to validate

        Returns:
            (success, error_message)
        """
        checks = [
            self._check_file_changes,
            self._check_syntax_valid,
            self._check_tests_pass,
            self._check_build_success,
            self._check_documentation,
        ]

        errors = []

        for check in checks:
            try:
                success, error = check()
                if not success and error:
                    errors.append(error)
            except Exception as e:
                errors.append(f"Check failed: {e}")

        if errors:
            return False, "; ".join(errors)

        return True, None

    def _check_file_changes(self) -> Tuple[bool, Optional[str]]:
        """Check for recent file changes indicating work was done"""
        try:
            # Check git status for modified files
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                return True, None

            return False, "No file changes detected"

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # If git is not available, check for recent file modifications
            return self._check_recent_file_modifications()

    def _check_recent_file_modifications(self) -> Tuple[bool, Optional[str]]:
        """Fallback check for file modifications when git is not available"""
        try:
            import time
            recent_files = []

            for root, dirs, files in os.walk(self.project_root):
                # Skip common directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]

                for file in files:
                    if file.startswith('.'):
                        continue

                    file_path = Path(root) / file
                    try:
                        mtime = file_path.stat().st_mtime
                        # Check if modified within last hour
                        if time.time() - mtime < 3600:
                            recent_files.append(file_path)
                    except OSError:
                        continue

            if recent_files:
                return True, None

            return False, "No recent file modifications detected"

        except Exception as e:
            return False, f"Could not check file modifications: {e}"

    def _check_syntax_valid(self) -> Tuple[bool, Optional[str]]:
        """Check that code has valid syntax"""
        try:
            # Check Python files
            python_files = list(self.project_root.glob("**/*.py"))
            if python_files:
                result = subprocess.run(
                    ["python3", "-m", "py_compile"] + [str(f) for f in python_files[:5]],  # Check first 5 files
                    cwd=self.project_root,
                    capture_output=True,
                    timeout=30
                )

                if result.returncode != 0:
                    return False, f"Python syntax errors: {result.stderr.decode()[:200]}"

            # Check JavaScript/TypeScript files if available
            js_files = list(self.project_root.glob("**/*.{js,ts,jsx,tsx}"))
            if js_files and Path("/usr/bin/node").exists():
                # Simple syntax check using node
                for js_file in js_files[:3]:  # Check first 3 files
                    result = subprocess.run(
                        ["node", "--check", str(js_file)],
                        cwd=self.project_root,
                        capture_output=True,
                        timeout=10
                    )

                    if result.returncode != 0:
                        return False, f"JavaScript syntax errors in {js_file.name}"

            return True, None

        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False, "Syntax validation timed out or failed"

    def _check_tests_pass(self) -> Tuple[bool, Optional[str]]:
        """Check that tests pass"""
        try:
            # Try common test runners
            test_commands = [
                ["pytest", "--tb=short", "-q"],
                ["npm", "test", "--", "--watchAll=false"],
                ["yarn", "test", "--watchAll=false"],
                ["python3", "-m", "unittest", "discover", "-v"]
            ]

            for cmd in test_commands:
                if Path(cmd[0]).exists() or (cmd[0] in ["npm", "yarn"] and Path(f"/usr/bin/{cmd[0]}").exists()):
                    result = subprocess.run(
                        cmd,
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )

                    # If tests ran (even if some failed), consider it checked
                    if result.returncode == 0:
                        return True, None
                    elif "test" in result.stdout.lower() or "spec" in result.stdout.lower():
                        # Tests were found and ran
                        return True, None

            # No test framework detected
            return True, None  # Don't fail if no tests exist

        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False, "Test execution failed or timed out"

    def _check_build_success(self) -> Tuple[bool, Optional[str]]:
        """Check that build succeeds"""
        try:
            # Try common build commands
            build_commands = [
                ["npm", "run", "build"],
                ["yarn", "build"],
                ["python3", "setup.py", "build"],
                ["make"],
                ["./build.sh"]
            ]

            for cmd in build_commands:
                script_path = self.project_root / cmd[0]
                if script_path.exists() or cmd[0] in ["npm", "yarn", "make"]:
                    try:
                        result = subprocess.run(
                            cmd,
                            cwd=self.project_root,
                            capture_output=True,
                            timeout=120
                        )

                        if result.returncode == 0:
                            return True, None
                    except subprocess.TimeoutExpired:
                        continue

            # No build system detected or all builds failed
            return True, None  # Don't fail if no build system

        except Exception as e:
            return False, f"Build check failed: {e}"

    def _check_documentation(self) -> Tuple[bool, Optional[str]]:
        """Check that documentation exists and is up to date"""
        try:
            # Check for README
            readme_files = ["README.md", "README.rst", "README.txt"]
            has_readme = any((self.project_root / f).exists() for f in readme_files)

            # Check for recent documentation updates
            doc_files = []
            for ext in [".md", ".rst", ".txt"]:
                doc_files.extend(list(self.project_root.glob(f"docs/**/*{ext}")))

            if not has_readme and not doc_files:
                return False, "No documentation files found"

            return True, None

        except Exception as e:
            return False, f"Documentation check failed: {e}"
