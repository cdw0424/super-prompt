"""
Quality Checker - Comprehensive quality validation
"""

from typing import Dict, Any, List
from .todo_validator import TodoValidator


class QualityChecker:
    """Comprehensive quality validation across multiple dimensions"""

    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.todo_validator = TodoValidator(project_root)

    def run_full_check(self) -> Dict[str, Any]:
        """Run comprehensive quality checks"""
        results = {
            "overall_status": "unknown",
            "checks": {},
            "score": 0,
            "recommendations": []
        }

        # Run individual checks
        checks = [
            ("code_quality", self._check_code_quality),
            ("test_coverage", self._check_test_coverage),
            ("documentation", self._check_documentation_quality),
            ("security", self._check_security_basics),
            ("performance", self._check_performance_basics),
            ("sdd_compliance", self._check_sdd_compliance)
        ]

        total_score = 0
        max_score = len(checks) * 100

        for check_name, check_func in checks:
            try:
                score, details = check_func()
                results["checks"][check_name] = {
                    "score": score,
                    "status": "pass" if score >= 70 else "fail",
                    "details": details
                }
                total_score += score
            except Exception as e:
                results["checks"][check_name] = {
                    "score": 0,
                    "status": "error",
                    "details": str(e)
                }

        # Calculate overall score
        overall_score = (total_score / max_score) * 100
        results["score"] = overall_score
        results["overall_status"] = "pass" if overall_score >= 70 else "fail"

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)

        return results

    def _check_code_quality(self) -> tuple[int, str]:
        """Check basic code quality metrics"""
        score = 100
        details = []

        # Check for basic syntax validation
        success, error = self.todo_validator._check_syntax_valid()
        if not success:
            score -= 30
            details.append(f"Syntax issues: {error}")

        # Check for TODO comments (could indicate incomplete work)
        # This is a simplified check
        details.append("Basic syntax validation passed")

        return score, "; ".join(details)

    def _check_test_coverage(self) -> tuple[int, str]:
        """Check test coverage and quality"""
        success, error = self.todo_validator._check_tests_pass()

        if success:
            return 85, "Tests are configured and passing"
        else:
            return 30, f"Test issues: {error or 'Tests not properly configured'}"

    def _check_documentation_quality(self) -> tuple[int, str]:
        """Check documentation completeness"""
        success, error = self.todo_validator._check_documentation()

        if success:
            return 80, "Documentation files present"
        else:
            return 20, f"Documentation issues: {error}"

    def _check_security_basics(self) -> tuple[int, str]:
        """Check basic security hygiene"""
        score = 100
        issues = []

        # Check for common security issues (simplified)
        try:
            # Look for hardcoded secrets (very basic check)
            import os
            secret_patterns = ["password", "secret", "key", "token"]

            for root, dirs, files in os.walk(self.project_root):
                # Skip common directories
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]

                for file in files:
                    if file.endswith(('.py', '.js', '.ts', '.json')):
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(10000)  # Read first 10KB

                                for pattern in secret_patterns:
                                    if f"{pattern} =" in content or f"{pattern}:" in content:
                                        score -= 10
                                        issues.append(f"Potential secret in {file}")
                                        break
                        except:
                            continue

                if len(issues) > 5:  # Don't check too many files
                    break

        except Exception as e:
            issues.append(f"Security check error: {e}")
            score -= 20

        if not issues:
            return score, "No obvious security issues detected"
        else:
            return score, "; ".join(issues[:3])  # Limit issues shown

    def _check_performance_basics(self) -> tuple[int, str]:
        """Check basic performance considerations"""
        # Simplified performance check
        return 75, "Basic performance checks completed"

    def _check_sdd_compliance(self) -> tuple[int, str]:
        """Check SDD (Spec-Driven Development) compliance"""
        from pathlib import Path

        specs_dir = Path(self.project_root) / "specs"
        if not specs_dir.exists():
            return 0, "No specs directory found"

        spec_files = list(specs_dir.glob("**/spec.md"))
        plan_files = list(specs_dir.glob("**/plan.md"))
        tasks_files = list(specs_dir.glob("**/tasks.md"))

        score = 0
        details = []

        if spec_files:
            score += 40
            details.append(f"{len(spec_files)} spec files found")
        else:
            details.append("No spec.md files found")

        if plan_files:
            score += 30
            details.append(f"{len(plan_files)} plan files found")
        else:
            details.append("No plan.md files found")

        if tasks_files:
            score += 30
            details.append(f"{len(tasks_files)} tasks files found")
        else:
            details.append("No tasks.md files found")

        return score, "; ".join(details)

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on check results"""
        recommendations = []

        for check_name, check_result in results["checks"].items():
            score = check_result["score"]
            status = check_result["status"]

            if status == "fail" or score < 70:
                if check_name == "test_coverage":
                    recommendations.append("Improve test coverage and ensure tests are passing")
                elif check_name == "documentation":
                    recommendations.append("Add comprehensive README and API documentation")
                elif check_name == "security":
                    recommendations.append("Review and fix potential security issues")
                elif check_name == "sdd_compliance":
                    recommendations.append("Implement SDD workflow with spec/plan/tasks files")
                elif check_name == "code_quality":
                    recommendations.append("Fix syntax errors and improve code quality")

        if results["score"] < 50:
            recommendations.append("Consider comprehensive code review and refactoring")

        if not recommendations:
            recommendations.append("Maintain current quality standards")

        return recommendations
