#!/usr/bin/env python3
"""
Audit script to detect unused modules and assets in Super Prompt packages/

This script:
1. Walks packages/ and lists all modules and assets
2. For each .py file, checks if it's imported anywhere
3. For assets (Markdown/JSON), checks if they're referenced
4. Outputs a report categorizing files as referenced/maybe-unused
"""

import os
import sys
import json
import csv
from pathlib import Path
from typing import Dict, List, Set, Tuple
import subprocess


class UsageAuditor:
    """Audit tool for finding unused modules and assets"""

    def __init__(self, root_dir: str = "packages"):
        self.root_dir = Path(root_dir)
        self.repo_root = Path(__file__).parent.parent.parent
        self.all_files: Set[str] = set()
        self.python_files: Set[str] = set()
        self.asset_files: Set[str] = set()
        self.referenced_files: Set[str] = set()
        self.import_patterns: Set[str] = set()

    def collect_files(self) -> None:
        """Collect all files in packages/ and subdirectories"""
        print(f"📁 Collecting files from {self.root_dir}...")

        # Collect from packages/core-py/
        core_py_dir = self.root_dir / "core-py" / "super_prompt"
        if core_py_dir.exists():
            for file_path in core_py_dir.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith("."):
                    rel_path = "packages/core-py/super_prompt/" + str(file_path.relative_to(core_py_dir))
                    self.all_files.add(rel_path)

                    if file_path.suffix == ".py":
                        self.python_files.add(rel_path)
                    elif file_path.suffix in [".md", ".json", ".yaml", ".yml", ".txt"]:
                        self.asset_files.add(rel_path)

        # Collect from packages/cursor-assets/
        cursor_assets_dir = self.root_dir / "cursor-assets"
        if cursor_assets_dir.exists():
            for file_path in cursor_assets_dir.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith("."):
                    rel_path = "packages/cursor-assets/" + str(file_path.relative_to(cursor_assets_dir))
                    self.all_files.add(rel_path)

                    if file_path.suffix == ".py":
                        self.python_files.add(rel_path)
                    elif file_path.suffix in [".md", ".json", ".yaml", ".yml", ".txt"]:
                        self.asset_files.add(rel_path)

        print(f"✅ Found {len(self.all_files)} files total")
        print(f"   - {len(self.python_files)} Python files")
        print(f"   - {len(self.asset_files)} asset files")

    def analyze_python_imports(self) -> None:
        """Analyze Python imports across the codebase"""
        print("🔍 Analyzing Python imports...")

        for py_file in self.python_files:
            abs_path = self.repo_root / py_file

            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Find import statements
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()

                    # from module import
                    if line.startswith('from '):
                        parts = line[5:].split(' import ')
                        if parts:
                            module_name = parts[0].split('.')[0]
                            self.import_patterns.add(module_name)

                    # import module
                    elif line.startswith('import '):
                        parts = line[7:].split(' as ')
                        if parts:
                            module_name = parts[0].split('.')[0]
                            self.import_patterns.add(module_name)

            except Exception as e:
                print(f"⚠️  Error reading {py_file}: {e}")

        print(f"✅ Found {len(self.import_patterns)} unique import patterns")

    def analyze_file_references(self) -> None:
        """Analyze references to files in the codebase"""
        print("🔍 Analyzing file references...")

        # Search for references to each file
        for file_path in self.all_files:
            if file_path.endswith(('.py', '.md', '.json', '.yaml', '.yml', '.txt')):
                # Search for filename references
                filename = Path(file_path).name
                if filename != "__init__.py":  # Skip __init__.py files
                    try:
                        result = subprocess.run(
                            ['rg', '-l', filename],
                            cwd=self.repo_root,
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            self.referenced_files.add(file_path)
                    except Exception as e:
                        print(f"⚠️  Error searching for {filename}: {e}")

        print(f"✅ Found {len(self.referenced_files)} referenced files")

    def generate_report(self) -> Dict[str, List[str]]:
        """Generate usage report"""
        print("📊 Generating usage report...")

        report = {
            "referenced": [],
            "maybe_unused": [],
            "asset_files": [],
            "python_modules": []
        }

        for file_path in sorted(self.all_files):
            if file_path in self.referenced_files:
                report["referenced"].append(file_path)
            else:
                report["maybe_unused"].append(file_path)

        report["asset_files"] = sorted([f for f in self.all_files if f.endswith(('.md', '.json', '.yaml', '.yml', '.txt'))])
        report["python_modules"] = sorted([f for f in self.all_files if f.endswith('.py')])

        return report

    def save_reports(self, report: Dict[str, List[str]]) -> None:
        """Save reports to files"""
        print("💾 Saving reports...")

        # JSON report
        with open("scripts/audit/usage_report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print("✅ Saved scripts/audit/usage_report.json")

        # CSV report
        with open("scripts/audit/usage_report.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Status", "File Path"])

            for file_path in report["referenced"]:
                writer.writerow(["referenced", file_path])

            for file_path in report["maybe_unused"]:
                writer.writerow(["maybe_unused", file_path])
        print("✅ Saved scripts/audit/usage_report.csv")

        # Summary report
        with open("scripts/audit/usage_summary.txt", 'w', encoding='utf-8') as f:
            f.write("=== SUPER PROMPT USAGE AUDIT SUMMARY ===\n\n")
            f.write(f"Total files: {len(self.all_files)}\n")
            f.write(f"Referenced files: {len(report['referenced'])}\n")
            f.write(f"Maybe unused files: {len(report['maybe_unused'])}\n")
            f.write(f"Asset files: {len(report['asset_files'])}\n")
            f.write(f"Python modules: {len(report['python_modules'])}\n\n")

            f.write("=== REFERENCED FILES ===\n")
            for file_path in report["referenced"]:
                f.write(f"✅ {file_path}\n")

            f.write("\n=== MAYBE UNUSED FILES ===\n")
            for file_path in report["maybe_unused"]:
                f.write(f"❓ {file_path}\n")

        print("✅ Saved scripts/audit/usage_summary.txt")

    def run_audit(self) -> None:
        """Run complete audit"""
        print("🚀 Starting Super Prompt usage audit...")

        self.collect_files()
        self.analyze_python_imports()
        self.analyze_file_references()
        report = self.generate_report()
        self.save_reports(report)

        print("🎉 Audit completed!")
        print("📋 Check scripts/audit/ for detailed reports")


def main():
    """Main entry point"""
    auditor = UsageAuditor()
    auditor.run_audit()


if __name__ == "__main__":
    main()
