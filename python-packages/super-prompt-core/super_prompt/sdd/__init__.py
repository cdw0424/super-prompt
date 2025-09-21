"""
SDD (Spec-Driven Development) Module
Spec, Plan, Tasks, and Implementation workflow management.
"""

from .gates import check_spec_plan, check_tasks, check_implementation_ready
from .spec_processor import SpecProcessor
from .plan_processor import PlanProcessor
from .tasks_processor import TasksProcessor
from .architecture import (
    list_sdd_sections,
    get_sdd_section,
    generate_sdd_persona_overlay,
    render_sdd_brief,
)

__all__ = [
    "check_spec_plan",
    "check_tasks",
    "check_implementation_ready",
    "SpecProcessor",
    "PlanProcessor",
    "TasksProcessor",
    "list_sdd_sections",
    "get_sdd_section",
    "generate_sdd_persona_overlay",
    "render_sdd_brief",
]
