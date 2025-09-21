"""
Persona Loader - Load and manage persona configurations
"""

try:
    import yaml  # type: ignore
except Exception:  # degrade gracefully if PyYAML is missing
    yaml = None  # type: ignore
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import os
import sys
from ..paths import package_root, cursor_assets_root


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

        if yaml is None:
            print("-------- Warning: PyYAML not installed; skipping persona manifest load", file=sys.stderr, flush=True)
            return 0

        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            loaded_count = 0
            for persona_name, persona_data in data.get('personas', {}).items():
                # Convert YAML structure to PersonaConfig format
                try:
                    # Extract fields that match PersonaConfig
                    config_data = {
                        'name': persona_data.get('name', persona_name),
                        'role_type': persona_data.get('role_type', persona_data.get('category', 'specialist')),
                        'expertise_level': persona_data.get('expertise_level', 'expert'),
                        'goal_orientation': persona_data.get('goal_orientation', 'quality'),
                        'interaction_style': persona_data.get('interaction_style', 'professional'),
                        'specializations': persona_data.get('best_for', []),
                        'auto_activate_patterns': persona_data.get('flags', []),
                        'description': persona_data.get('description', '')
                    }

                    # Ensure lists are properly formatted
                    if isinstance(config_data['specializations'], str):
                        config_data['specializations'] = [config_data['specializations']]
                    if isinstance(config_data['auto_activate_patterns'], str):
                        config_data['auto_activate_patterns'] = [config_data['auto_activate_patterns']]

                    persona = PersonaConfig(**config_data)
                    self.personas[persona.name] = persona
                    loaded_count += 1

                    print(f"-------- persona: loaded '{persona.name}' ({persona.role_type})", file=sys.stderr, flush=True)

                except Exception as persona_error:
                    print(f"-------- persona: failed to load '{persona_name}': {persona_error}", file=sys.stderr, flush=True)
                    continue

            print(f"-------- persona: total {loaded_count} personas loaded successfully", file=sys.stderr, flush=True)
            return loaded_count

        except Exception as e:
            print(f"-------- Error loading persona manifest: {e}", file=sys.stderr, flush=True)
            return 0

    def _create_default_manifest(self):
        """Create a default persona manifest by copying the canonical SSOT manifest."""
        # SSOT: copy from packages/cursor-assets/manifests/personas.yaml if available
        try:
            canonical = cursor_assets_root() / "manifests" / "personas.yaml"
            self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
            if canonical.exists():
                self.manifest_path.write_text(canonical.read_text(encoding='utf-8'), encoding='utf-8')
            else:
                # Last resort: write an empty scaffold to encourage init
                self.manifest_path.write_text("personas:\n", encoding='utf-8')
        except Exception:
            # Best-effort; write minimal scaffold
            self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
            self.manifest_path.write_text("personas:\n", encoding='utf-8')

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
