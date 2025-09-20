"""
Pipeline system for persona-based workflows
"""

from .config import (
    PersonaPipelineConfig,
    PipelineState,
    PIPELINE_LABELS,
    PIPELINE_ALIASES,
    DEFAULT_PLAN_LINES,
    DEFAULT_EXEC_LINES
)

__all__ = [
    "PersonaPipelineConfig",
    "PipelineState", 
    "PIPELINE_LABELS",
    "PIPELINE_ALIASES",
    "DEFAULT_PLAN_LINES",
    "DEFAULT_EXEC_LINES"
]
