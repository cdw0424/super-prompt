"""
Super Prompt Core Engine

A modular prompt engineering toolkit that provides:
- State machine execution (INTENT→CLASSIFY→PLAN→EXECUTE→VERIFY→REPORT)
- Auto Model Router (AMR) for complexity-based routing
- Context-aware file collection with .gitignore support
- SDD workflow (Spec→Plan→Tasks→Implement)
- YAML-based persona and rule management
"""

__version__ = "3.0.0"
__author__ = "Daniel Choi"
__email__ = "cdw0424@gmail.com"

# Module-level imports will be added as we implement each component
__all__ = [
    # Core modules
    "engine",
    "context",
    "sdd",
    "personas",
    "adapters",
    "validation",
]

