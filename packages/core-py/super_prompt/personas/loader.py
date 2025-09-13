"""
Persona Loader - Load and manage persona configurations
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


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


class PersonaLoader:
    """
    Load persona configurations from YAML manifests
    """

    def __init__(self, manifest_path: Optional[Path] = None):
        self.manifest_path = manifest_path or self._find_default_manifest()
        self.personas: Dict[str, PersonaConfig] = {}

    def _find_default_manifest(self) -> Path:
        """Find default persona manifest"""
        # Look in standard locations
        search_paths = [
            Path.cwd() / "personas" / "manifest.yaml",
            Path.cwd() / "personas" / "manifest.yml",
            Path(__file__).parent / "manifest.yaml",
        ]

        for path in search_paths:
            if path.exists():
                return path

        # Create default manifest path
        return Path.cwd() / "personas" / "manifest.yaml"

    def load_manifest(self) -> int:
        """Load personas from manifest file"""
        if not self.manifest_path.exists():
            # Create default manifest if it doesn't exist
            self._create_default_manifest()
            return 0

        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            loaded_count = 0
            for persona_data in data.get('personas', []):
                persona = PersonaConfig(**persona_data)
                self.personas[persona.name] = persona
                loaded_count += 1

            return loaded_count

        except Exception as e:
            print(f"Error loading persona manifest: {e}")
            return 0

    def _create_default_manifest(self):
        """Create a default persona manifest"""
        default_personas = [
            {
                "name": "architect",
                "role_type": "technical_lead",
                "expertise_level": "expert",
                "goal_orientation": "system_design",
                "interaction_style": "structured",
                "specializations": ["system_design", "scalability", "architecture"],
                "auto_activate_patterns": ["architect", "design", "system", "scale"],
                "description": "Senior System Architect specializing in large-scale distributed systems"
            },
            {
                "name": "frontend",
                "role_type": "ui_engineer",
                "expertise_level": "senior",
                "goal_orientation": "user_experience",
                "interaction_style": "collaborative",
                "specializations": ["react", "ui", "ux", "accessibility"],
                "auto_activate_patterns": ["frontend", "ui", "component", "react"],
                "description": "Senior Frontend Engineer specializing in modern web development"
            },
            {
                "name": "backend",
                "role_type": "server_engineer",
                "expertise_level": "senior",
                "goal_orientation": "reliability",
                "interaction_style": "pragmatic",
                "specializations": ["api", "database", "performance", "security"],
                "auto_activate_patterns": ["backend", "api", "database", "server"],
                "description": "Senior Backend Engineer specializing in scalable server systems"
            }
        ]

        manifest_data = {
            "version": "1.0",
            "personas": default_personas
        }

        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            yaml.dump(manifest_data, f, default_flow_style=False, sort_keys=False)

    def get_persona(self, name: str) -> Optional[PersonaConfig]:
        """Get a specific persona by name"""
        return self.personas.get(name)

    def list_personas(self) -> List[Dict[str, Any]]:
        """List all available personas"""
        return [
            {
                "name": persona.name,
                "description": persona.description,
                "role_type": persona.role_type,
                "expertise_level": persona.expertise_level
            }
            for persona in self.personas.values()
        ]

    def find_matching_personas(self, query: str) -> List[PersonaConfig]:
        """Find personas that match a query"""
        matches = []
        query_lower = query.lower()

        for persona in self.personas.values():
            # Check name match
            if persona.name.lower() in query_lower:
                matches.append(persona)
                continue

            # Check specializations
            if any(spec.lower() in query_lower for spec in persona.specializations):
                matches.append(persona)
                continue

            # Check auto-activate patterns
            if any(pattern.lower() in query_lower for pattern in persona.auto_activate_patterns):
                matches.append(persona)
                continue

        return matches