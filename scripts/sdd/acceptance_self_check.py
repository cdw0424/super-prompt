#!/usr/bin/env python3
"""Acceptance Self-Check Script (Spec Kit v0.0.20)
Automated validation of implementation against spec requirements.
"""
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class CheckResult:
    passed: bool
    message: str
    details: List[str] = None

    def __post_init__(self):
        if self.details is None:
            self.details = []

class AcceptanceSelfCheck:
    """Automated acceptance criteria validation"""

    def __init__(self, spec_path: str = None, tasks_path: str = None):
        self.spec_path = spec_path or self._find_latest_file('spec.md')
        self.tasks_path = tasks_path or self._find_latest_file('tasks.md')
        self.results: Dict[str, CheckResult] = {}

    def _find_latest_file(self, pattern: str) -> str:
        """Find the most recently modified file matching pattern"""
        if not os.path.exists('specs'):
            return None

        candidates = []
        for root, dirs, files in os.walk('specs'):
            for file in files:
                if file.endswith(pattern):
                    path = os.path.join(root, file)
                    mtime = os.path.getmtime(path)
                    candidates.append((path, mtime))

        if not candidates:
            return None

        return max(candidates, key=lambda x: x[1])[0]

    def validate_success_criteria(self) -> CheckResult:
        """Validate that success criteria from spec are met"""
        if not self.spec_path or not os.path.exists(self.spec_path):
            return CheckResult(False, "Spec file not found", ["Run /specify command first"])

        try:
            with open(self.spec_path, 'r', encoding='utf-8') as f:
                spec_content = f.read()

            # Extract success criteria
            success_match = re.search(r'#{2,3} Success Criteria\s*\n((?:- \[.\] .*\n?)*)',
                                    spec_content, re.MULTILINE)
            if not success_match:
                return CheckResult(False, "No success criteria found in spec",
                                 ["Add measurable success criteria to spec.md"])

            criteria_text = success_match.group(1)
            criteria = re.findall(r'- \[([ x])\] (.*)', criteria_text)

            if not criteria:
                return CheckResult(False, "No valid success criteria checkboxes found",
                                 ["Use format: - [ ] Criterion description"])

            total_criteria = len(criteria)
            completed_criteria = sum(1 for status, _ in criteria if status.lower() == 'x')

            if completed_criteria == 0:
                return CheckResult(False, f"0/{total_criteria} success criteria completed",
                                 ["Mark completed criteria with [x]"])

            if completed_criteria < total_criteria:
                return CheckResult(False, f"{completed_criteria}/{total_criteria} success criteria completed",
                                 ["Complete all success criteria before implementation"])

            return CheckResult(True, f"All {total_criteria} success criteria completed")

        except Exception as e:
            return CheckResult(False, f"Error validating success criteria: {e}")

    def validate_acceptance_criteria(self) -> CheckResult:
        """Validate that acceptance criteria from spec are met"""
        if not self.spec_path or not os.path.exists(self.spec_path):
            return CheckResult(False, "Spec file not found", ["Run /specify command first"])

        try:
            with open(self.spec_path, 'r', encoding='utf-8') as f:
                spec_content = f.read()

            # Extract acceptance criteria
            acceptance_match = re.search(r'#{2,3} Acceptance Criteria\s*\n((?:- \[.\] .*\n?)*)',
                                       spec_content, re.MULTILINE)
            if not acceptance_match:
                return CheckResult(False, "No acceptance criteria found in spec",
                                 ["Add specific acceptance criteria to spec.md"])

            criteria_text = acceptance_match.group(1)
            criteria = re.findall(r'- \[([ x])\] (.*)', criteria_text)

            if not criteria:
                return CheckResult(False, "No valid acceptance criteria checkboxes found",
                                 ["Use format: - [ ] Criterion description"])

            total_criteria = len(criteria)
            completed_criteria = sum(1 for status, _ in criteria if status.lower() == 'x')

            if completed_criteria < total_criteria:
                return CheckResult(False, f"{completed_criteria}/{total_criteria} acceptance criteria validated",
                                 ["Mark validated criteria with [x]", "All criteria must pass before implementation"])

            return CheckResult(True, f"All {total_criteria} acceptance criteria validated")

        except Exception as e:
            return CheckResult(False, f"Error validating acceptance criteria: {e}")

    def validate_task_completion(self) -> CheckResult:
        """Validate that all tasks are completed"""
        if not self.tasks_path or not os.path.exists(self.tasks_path):
            return CheckResult(False, "Tasks file not found", ["Run /tasks command first"])

        try:
            with open(self.tasks_path, 'r', encoding='utf-8') as f:
                tasks_content = f.read()

            # Find all task checkboxes
            task_checkboxes = re.findall(r'- \[([ x])\] \*\*TASK-[\w-]+\*\*', tasks_content)

            if not task_checkboxes:
                return CheckResult(False, "No valid task checkboxes found",
                                 ["Tasks must follow format: - [ ] **TASK-XXX**"])

            total_tasks = len(task_checkboxes)
            completed_tasks = sum(1 for status in task_checkboxes if status.lower() == 'x')

            if completed_tasks < total_tasks:
                return CheckResult(False, f"{completed_tasks}/{total_tasks} tasks completed",
                                 ["Mark completed tasks with [x]", "All tasks must be completed"])

            return CheckResult(True, f"All {total_tasks} tasks completed")

        except Exception as e:
            return CheckResult(False, f"Error validating task completion: {e}")

    def validate_code_quality(self) -> CheckResult:
        """Validate basic code quality checks"""
        issues = []

        # Check for required files
        if not os.path.exists('pyproject.toml') and not os.path.exists('package.json'):
            issues.append("No dependency management file found (pyproject.toml or package.json)")

        # Check for test files
        test_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.startswith('test_') or file.endswith('.test.js') or file.endswith('_test.py'):
                    test_files.append(os.path.join(root, file))

        if not test_files:
            issues.append("No test files found")

        # Check for documentation
        if not os.path.exists('README.md'):
            issues.append("README.md missing")

        # Check for linting errors (basic check)
        python_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))

        # Basic syntax check for Python files
        import subprocess
        syntax_errors = []
        for py_file in python_files[:5]:  # Check first 5 files
            try:
                result = subprocess.run([sys.executable, '-m', 'py_compile', py_file],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    syntax_errors.append(f"Syntax error in {py_file}")
            except:
                pass

        if syntax_errors:
            issues.extend(syntax_errors)

        if issues:
            return CheckResult(False, f"Code quality issues found: {len(issues)}",
                             issues[:5])  # Show first 5 issues

        return CheckResult(True, "Code quality checks passed")

    def validate_security_checks(self) -> CheckResult:
        """Validate basic security checks"""
        issues = []

        # Check for secrets in code (very basic)
        sensitive_patterns = [
            r'password\s*=\s*["\'][^"\']*["\']',
            r'secret\s*=\s*["\'][^"\']*["\']',
            r'api_key\s*=\s*["\'][^"\']*["\']',
            r'token\s*=\s*["\'][^"\']*["\']'
        ]

        code_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java')):
                    code_files.append(os.path.join(root, file))

        secrets_found = []
        for code_file in code_files[:10]:  # Check first 10 files
            try:
                with open(code_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern in sensitive_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            secrets_found.append(f"Potential secret in {code_file}")
                            break
            except:
                pass

        if secrets_found:
            issues.extend(secrets_found[:3])  # Show first 3 findings

        # Check for .env files
        if os.path.exists('.env'):
            issues.append(".env file should not be committed")

        if issues:
            return CheckResult(False, f"Security issues found: {len(issues)}", issues)

        return CheckResult(True, "Security checks passed")

    def run_all_checks(self) -> Dict[str, CheckResult]:
        """Run all acceptance checks"""
        checks = {
            'success_criteria': self.validate_success_criteria,
            'acceptance_criteria': self.validate_acceptance_criteria,
            'task_completion': self.validate_task_completion,
            'code_quality': self.validate_code_quality,
            'security': self.validate_security_checks
        }

        results = {}
        for check_name, check_func in checks.items():
            try:
                result = check_func()
                results[check_name] = result
                self.results[check_name] = result
            except Exception as e:
                results[check_name] = CheckResult(False, f"Check failed with error: {e}")
                self.results[check_name] = results[check_name]

        return results

    def generate_check_report(self) -> str:
        """Generate a formatted report of all checks"""
        if not self.results:
            self.run_all_checks()

        report_lines = [
            "# Acceptance Self-Check Report",
            "",
            f"**Timestamp:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Check Results",
            ""
        ]

        all_passed = True
        for check_name, result in self.results.items():
            status = "✅ PASS" if result.passed else "❌ FAIL"
            report_lines.extend([
                f"### {check_name.replace('_', ' ').title()}",
                f"**Status:** {status}",
                f"**Message:** {result.message}",
            ])

            if result.details:
                report_lines.append("**Details:**")
                for detail in result.details:
                    report_lines.append(f"- {detail}")

            report_lines.append("")

            if not result.passed:
                all_passed = False

        # Overall status
        overall_status = "✅ ALL CHECKS PASSED" if all_passed else "❌ CHECKS FAILED"
        report_lines.insert(4, f"**Overall Status:** {overall_status}")
        report_lines.insert(5, "")

        if not all_passed:
            report_lines.extend([
                "## Next Steps",
                "",
                "1. Address all failed checks",
                "2. Re-run this script to validate fixes",
                "3. Only proceed with implementation after all checks pass",
                ""
            ])

        return "\n".join(report_lines)

def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Acceptance Self-Check Script')
    parser.add_argument('--spec', help='Path to spec file')
    parser.add_argument('--tasks', help='Path to tasks file')
    parser.add_argument('--output', '-o', help='Output file for report')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only output final status')

    args = parser.parse_args()

    checker = AcceptanceSelfCheck(args.spec, args.tasks)

    if args.quiet:
        results = checker.run_all_checks()
        all_passed = all(result.passed for result in results.values())
        print("PASS" if all_passed else "FAIL")
        sys.exit(0 if all_passed else 1)

    report = checker.generate_check_report()

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"----- Report written to {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main()
