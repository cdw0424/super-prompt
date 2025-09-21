#!/usr/bin/env python3
"""
Check for re-introduction of deleted files in Super Prompt packages/

This script:
1. Maintains a list of known-deleted files that should not reappear
2. Checks if any of these files exist in the current codebase
3. Fails CI if deleted files are found
4. Provides reporting for cleanup verification
"""

import os
import sys
from pathlib import Path
from typing import List, Set


class DeletedFilesChecker:
    """Check for re-introduction of deleted files"""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent.parent
        self.packages_dir = self.repo_root / "packages"

        # Known deleted files that should NOT reappear
        self.deleted_files = {
            # Batch 1: Pycache and cache files
            "packages/core-py/super_prompt/__pycache__",
            "packages/core-py/super_prompt/adapters/__pycache__",
            "packages/core-py/super_prompt/commands/__pycache__",
            "packages/core-py/super_prompt/context/__pycache__",
            "packages/core-py/super_prompt/core/__pycache__",
            "packages/core-py/super_prompt/mcp/__pycache__",
            "packages/core-py/super_prompt/personas/__pycache__",
            "packages/core-py/super_prompt/personas/tools/__pycache__",
            "packages/core-py/super_prompt/pipeline/__pycache__",
            "packages/core-py/super_prompt/sdd/__pycache__",
            "packages/core-py/super_prompt/tools/__pycache__",
            "packages/core-py/super_prompt/utils/__pycache__",
            "packages/core-py/super_prompt/validation/__pycache__",
            "packages/cursor-assets/__pycache__",
            "packages/cursor-assets/commands/__pycache__",
            "packages/cursor-assets/commands/super-prompt/__pycache__",
            "packages/cursor-assets/manifests/__pycache__",
            "packages/cursor-assets/rules/__pycache__",
            "packages/cursor-assets/templates/__pycache__",

            # Batch 2: DS_Store files
            "packages/.DS_Store",
            "packages/core-py/.DS_Store",
            "packages/core-py/super_prompt/.DS_Store",
            "packages/cursor-assets/.DS_Store",

            # Legacy modules that were removed
            "packages/core-py/super_prompt/analysis",
            "packages/core-py/super_prompt/codex",
            "packages/core-py/super_prompt/workflow_runner.py",
            "packages/core-py/super_prompt/personas/pipeline_manager.py",
            "packages/codex-assets",
            "scripts/codex",
            ".codex",
            "docs/codex-amr.md",
            "docs/codex-amr-usage.md",
            "docs/codex-mcp-setting-guide.md",
            "src/tools/codex-mcp.js",
            "src/config/codexAmr.js",
            "src/scaffold/codexAmr.js",
            "prompts/codex_amr_bootstrap_prompt_en.txt",
        }

    def check_deleted_files(self) -> List[str]:
        """Check if any deleted files have reappeared"""
        found_files = []

        for deleted_path in self.deleted_files:
            full_path = self.repo_root / deleted_path

            if full_path.exists():
                # Check if it's a directory or file
                if full_path.is_dir():
                    found_files.append(f"Directory: {deleted_path}")
                else:
                    found_files.append(f"File: {deleted_path}")

        return found_files

    def generate_report(self) -> str:
        """Generate a report of the check"""
        found_files = self.check_deleted_files()

        if not found_files:
            return "✅ No deleted files found. Cleanup integrity maintained."

        report = "❌ DELETED FILES REAPPEARED!\n\n"
        report += "The following files were previously deleted but have reappeared:\n\n"

        for file_path in found_files:
            report += f"🚨 {file_path}\n"

        report += "\n📋 Action Required:\n"
        report += "These files should be removed as they are:\n"
        report += "- __pycache__ directories (auto-generated)\n"
        report += "- .DS_Store files (macOS artifacts)\n"
        report += "- Legacy modules that were intentionally removed\n"

        return report

    def run_check(self) -> bool:
        """Run the check and return True if clean"""
        found_files = self.check_deleted_files()

        if found_files:
            print(self.generate_report())
            return False

        print("✅ Deleted files check passed")
        return True


def main():
    """Main entry point"""
    checker = DeletedFilesChecker()
    success = checker.run_check()

    if not success:
        print("\n💡 To fix this issue:")
        print("1. Remove the listed files/directories")
        print("2. Check git status to see what was added")
        print("3. Remove them: git rm -r <file>")
        print("4. Commit the cleanup")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
