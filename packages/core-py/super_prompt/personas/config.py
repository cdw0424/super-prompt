"""
Persona configuration model
"""

from dataclasses import dataclass
from typing import List


@dataclass
class PersonaConfig:
    """Configuration for a persona"""
    name: str
    role_type: str
    expertise_level: str
    goal_orientation: str
    interaction_style: str
    specializations: List[str]
    auto_activate_patterns: List[str]
    description: str = ""

