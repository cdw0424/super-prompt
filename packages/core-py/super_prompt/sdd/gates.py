"""SDD gates (v4 - Spec Kit Enhanced)
Spec/Plan/Tasks/Implement stage checks with constitution compliance and quality validation.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from pathlib import Path


PathLike = Union[str, Path]


@dataclass
class GateReport:
    ok: bool
    missing: List[str]
    warnings: List[str] = None
    score: Optional[int] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class ConstitutionCheck:
    compliant: bool
    violations: List[str]
    recommendations: List[str]


# Required sections for each document type
SPEC_REQUIRED_SECTIONS = [
    "REQ-ID",
    "Overview",
    "Success Criteria",
    "Acceptance Criteria",
    "Scope & Boundaries",
    "Business Value",
]

PLAN_REQUIRED_SECTIONS = [
    "REQ-ID",
    "Architecture Overview",
    "Technical Stack",
    "Security Architecture",
    "Testing Strategy",
    "Deployment Strategy",
    "Success Metrics",
]

TASKS_REQUIRED_SECTIONS = ["REQ-ID", "Task Breakdown Strategy", "Acceptance Self-Check Template"]


def check_spec_plan(
    project_id: Optional[str] = None, project_root: PathLike = "."
) -> GateReport:
    """Enhanced spec/plan check with quality validation.

    Parameters
    ----------
    project_id: Optional identifier for the feature being validated (unused, reserved for
        future filtering of multi-feature specs).
    project_root: Base directory to evaluate. Defaults to the current working directory.
    """
    miss = []
    warnings = []

    root_path = Path(project_root or ".").expanduser()
    spec_dir = root_path / "specs"

    # Basic structure checks
    if not spec_dir.exists():
        miss.append("specs/ directory")
        return GateReport(ok=False, missing=miss)

    spec_files = list(_find_files(spec_dir, "spec.md"))
    plan_files = list(_find_files(spec_dir, "plan.md"))

    if not spec_files:
        miss.append("at least one spec.md file")
    if not plan_files:
        miss.append("at least one plan.md file")

    if miss:
        return GateReport(ok=False, missing=miss)

    # Quality checks for latest spec and plan
    latest_spec = max(spec_files, key=lambda p: p.stat().st_mtime)
    latest_plan = max(plan_files, key=lambda p: p.stat().st_mtime)

    spec_quality = _validate_spec_quality(latest_spec)
    plan_quality = _validate_plan_quality(latest_plan)

    if not spec_quality.ok:
        miss.extend(spec_quality.missing)
    if not plan_quality.ok:
        miss.extend(plan_quality.missing)

    warnings.extend(spec_quality.warnings)
    warnings.extend(plan_quality.warnings)

    # Constitution compliance check
    constitution_check = _check_constitution_compliance(
        latest_spec, latest_plan, root_path
    )
    if not constitution_check.compliant:
        miss.extend(constitution_check.violations)
        warnings.extend(constitution_check.recommendations)

    # Calculate overall quality score
    score = _calculate_quality_score(spec_quality, plan_quality, constitution_check)

    return GateReport(ok=not miss, missing=miss, warnings=warnings, score=score)


def check_tasks(
    project_id: Optional[str] = None, project_root: PathLike = "."
) -> GateReport:
    """Check tasks implementation readiness."""
    miss = []
    warnings = []

    root_path = Path(project_root or ".").expanduser()
    tasks_dir = root_path / "specs"

    tasks_files = list(_find_files(tasks_dir, "tasks.md"))
    if not tasks_files:
        miss.append("tasks.md file (run /tasks command first)")
        return GateReport(ok=False, missing=miss)

    latest_tasks = max(tasks_files, key=lambda p: p.stat().st_mtime)
    tasks_quality = _validate_tasks_quality(latest_tasks)

    if not tasks_quality.ok:
        miss.extend(tasks_quality.missing)
    warnings.extend(tasks_quality.warnings)

    return GateReport(ok=not miss, missing=miss, warnings=warnings)


def check_implementation_ready(
    project_id: Optional[str] = None, project_root: PathLike = "."
) -> GateReport:
    """Final gate before implementation - validates all SDD requirements."""
    miss = []
    warnings = []

    root_path = Path(project_root or ".").expanduser()

    # Check all previous gates
    spec_plan_check = check_spec_plan(project_id, root_path)
    tasks_check = check_tasks(project_id, root_path)

    if not spec_plan_check.ok:
        miss.extend(spec_plan_check.missing)
    if not tasks_check.ok:
        miss.extend(tasks_check.missing)

    warnings.extend(spec_plan_check.warnings)
    warnings.extend(tasks_check.warnings)

    # Check acceptance self-check script availability
    acceptance_check = _validate_acceptance_self_check(root_path)
    if not acceptance_check.ok:
        miss.extend(acceptance_check.missing)
    warnings.extend(acceptance_check.warnings)

    # Run acceptance self-check validation
    if acceptance_check.ok:
        self_check_result = _run_acceptance_self_check(root_path)
        if not self_check_result.ok:
            miss.extend(self_check_result.missing)
        warnings.extend(self_check_result.warnings)

    return GateReport(ok=not miss, missing=miss, warnings=warnings)


def _find_files(root: PathLike, pattern: str):
    """Find files matching pattern recursively"""
    root_path = Path(root)
    if not root_path.exists():
        return

    yield from root_path.rglob(pattern)


def _validate_spec_quality(spec_path: PathLike) -> GateReport:
    """Validate spec file quality and completeness"""
    miss = []
    warnings = []

    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check required sections
        for section in SPEC_REQUIRED_SECTIONS:
            if not re.search(rf"^## {re.escape(section)}", content, re.MULTILINE):
                miss.append(f"Spec missing required section: {section}")

        # Check REQ-ID format
        req_id_match = re.search(r"## REQ-ID:\s*([^\n]+)", content)
        if not req_id_match or not re.match(r"REQ-[\w-]+", req_id_match.group(1).strip()):
            miss.append("Invalid or missing REQ-ID format (should be REQ-XXX)")

        # Check for measurable success criteria
        if not re.search(r"Success Criteria.*- \[ \]", content, re.DOTALL):
            warnings.append("Consider adding measurable success criteria")

        # Check for acceptance criteria
        if not re.search(r"Acceptance Criteria.*- \[ \]", content, re.DOTALL):
            warnings.append("Consider adding specific acceptance criteria")

    except Exception as e:
        miss.append(f"Error reading spec file: {e}")

    return GateReport(ok=not miss, missing=miss, warnings=warnings)


def _validate_plan_quality(plan_path: PathLike) -> GateReport:
    """Validate plan file quality and completeness"""
    miss = []
    warnings = []

    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check required sections
        for section in PLAN_REQUIRED_SECTIONS:
            if not re.search(rf"^## {re.escape(section)}", content, re.MULTILINE):
                miss.append(f"Plan missing required section: {section}")

        # Check for technical stack specification
        if not re.search(r"Technical Stack", content):
            miss.append("Plan must specify technical stack")

        # Check for security considerations
        if not re.search(r"Security|Authorization|Authentication", content):
            warnings.append("Consider adding security architecture details")

        # Check for testing strategy
        if not re.search(r"Testing Strategy|Unit Tests|Integration Tests", content):
            warnings.append("Consider adding comprehensive testing strategy")

        # Check for success metrics
        if not re.search(r"Success Metrics|Performance|Coverage", content):
            warnings.append("Consider defining success metrics")

    except Exception as e:
        miss.append(f"Error reading plan file: {e}")

    return GateReport(ok=not miss, missing=miss, warnings=warnings)


def _validate_tasks_quality(tasks_path: PathLike) -> GateReport:
    """Validate tasks file quality and completeness"""
    miss = []
    warnings = []

    try:
        with open(tasks_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check required sections
        for section in TASKS_REQUIRED_SECTIONS:
            if not re.search(rf"^## {re.escape(section)}", content, re.MULTILINE):
                miss.append(f"Tasks missing required section: {section}")

        # Check for task breakdown
        if not re.search(r"TASK-[\w-]+.*Description.*Acceptance Criteria", content, re.DOTALL):
            miss.append(
                "Tasks must follow proper TASK-ID format with descriptions and acceptance criteria"
            )

        # Check for acceptance self-check template
        if not re.search(r"Acceptance Self-Check.*- \[ \]", content, re.DOTALL):
            warnings.append("Consider adding acceptance self-check template")

        # Check for effort estimation
        if not re.search(r"Estimated Effort.*hours", content):
            warnings.append("Consider adding effort estimates for tasks")

    except Exception as e:
        miss.append(f"Error reading tasks file: {e}")

    return GateReport(ok=not miss, missing=miss, warnings=warnings)


def _check_constitution_compliance(
    spec_path: PathLike, plan_path: PathLike, project_root: Path
) -> ConstitutionCheck:
    """Check compliance with project constitution"""
    violations = []
    recommendations = []

    constitution_path = project_root / "memory" / "constitution" / "constitution.md"
    if not constitution_path.exists():
        return ConstitutionCheck(
            compliant=False,
            violations=["Constitution file not found"],
            recommendations=["Create memory/constitution/constitution.md"],
        )

    try:
        with open(constitution_path, "r", encoding="utf-8") as f:
            constitution = f.read()

        # Read spec and plan content
        with open(spec_path, "r", encoding="utf-8") as f:
            spec_content = f.read()
        with open(plan_path, "r", encoding="utf-8") as f:
            plan_content = f.read()

        combined_content = spec_content + plan_content

        # Check constitution requirements
        if "SPEC → PLAN → TASKS → IMPLEMENT" in constitution:
            if not ("Success Criteria" in spec_content and "Acceptance Criteria" in spec_content):
                violations.append(
                    "Spec must include success and acceptance criteria per constitution"
                )

        if "Quality Gates" in constitution:
            if not "Acceptance Criteria" in combined_content:
                violations.append("Missing acceptance criteria validation gate")

        if "Security: secure by default" in constitution:
            if not ("Security" in plan_content or "Authorization" in plan_content):
                violations.append("Plan must address security requirements per constitution")

        if "Accessibility: WCAG 2.1 AA" in constitution:
            if not ("Accessibility" in spec_content or "Accessibility" in plan_content):
                recommendations.append("Consider adding accessibility requirements")

        if "Performance: optimize for user experience" in constitution:
            if not ("Performance" in plan_content):
                recommendations.append("Consider adding performance requirements")

    except Exception as e:
        violations.append(f"Error checking constitution compliance: {e}")

    return ConstitutionCheck(
        compliant=len(violations) == 0, violations=violations, recommendations=recommendations
    )


def _validate_acceptance_self_check(project_root: Path) -> GateReport:
    """Validate that acceptance self-check is properly configured"""
    miss = []
    warnings = []

    # Check for acceptance self-check template file
    check_file = project_root / "scripts" / "sdd" / "acceptance_self_check.py"
    if not check_file.exists():
        miss.append("Acceptance self-check script missing")
        return GateReport(ok=False, missing=miss)

    # Basic validation of the check script
    try:
        with open(check_file, "r", encoding="utf-8") as f:
            content = f.read()

        required_functions = [
            "validate_success_criteria",
            "validate_acceptance_criteria",
            "generate_check_report",
        ]
        for func in required_functions:
            if f"def {func}" not in content:
                miss.append(f"Acceptance self-check missing function: {func}")

    except Exception as e:
        miss.append(f"Error validating acceptance self-check: {e}")

    return GateReport(ok=not miss, missing=miss, warnings=warnings)


def _run_acceptance_self_check(project_root: Path) -> GateReport:
    """Run the acceptance self-check script and parse results"""
    miss = []
    warnings = []

    try:
        import subprocess

        script_path = project_root / "scripts" / "sdd" / "acceptance_self_check.py"
        result = subprocess.run(
            ["python3", str(script_path), "--quiet"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=30,
        )

        if result.returncode != 0:
            # Script returned failure - parse output for details
            output_lines = result.stdout.strip().split("\n") + result.stderr.strip().split("\n")
            for line in output_lines:
                line = line.strip()
                if line.startswith("-----"):
                    continue  # Skip log prefixes
                elif "failed" in line.lower() or "error" in line.lower():
                    miss.append(line)
                elif "warning" in line.lower():
                    warnings.append(line)

            if not miss:
                miss.append("Acceptance self-check failed (check script output for details)")

        # If script succeeds, no additional issues
        return GateReport(ok=result.returncode == 0, missing=miss, warnings=warnings)

    except subprocess.TimeoutExpired:
        miss.append("Acceptance self-check timed out")
        return GateReport(ok=False, missing=miss)
    except FileNotFoundError:
        miss.append("Acceptance self-check script not found")
        return GateReport(ok=False, missing=miss)
    except Exception as e:
        miss.append(f"Error running acceptance self-check: {e}")
        return GateReport(ok=False, missing=miss)


def _calculate_quality_score(
    spec_quality: GateReport, plan_quality: GateReport, constitution_check: ConstitutionCheck
) -> int:
    """Calculate overall quality score (0-100)"""
    score = 100

    # Deduct for missing required sections
    score -= len(spec_quality.missing) * 15
    score -= len(plan_quality.missing) * 15

    # Deduct for constitution violations
    score -= len(constitution_check.violations) * 20

    # Deduct for warnings
    score -= len(spec_quality.warnings) * 5
    score -= len(plan_quality.warnings) * 5

    return max(0, min(100, score))
