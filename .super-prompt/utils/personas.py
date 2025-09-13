#!/usr/bin/env python3
# Codex Personas Helper — centralized persona loading and prompt building.
import os
import sys
from textwrap import dedent
from typing import Dict, Optional, List, Any

# Attempt to import yaml and provide a helpful error message if it's missing.
try:
    import yaml
except ImportError:
    print("FATAL: The 'pyyaml' package is required. Please install it by running: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

class PersonaManager:
    """
    Manages loading persona configurations from a central YAML file
    and building prompts based on them.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PersonaManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, project_root: Optional[str] = None):
        if hasattr(self, 'initialized') and self.initialized:
            return

        self.project_root = project_root or self._find_project_root()
        self.personas_path = os.path.join(self.project_root, ".super-prompt", "personas.yaml")
        self.personas = self._load_personas()
        self.initialized = True

    def _find_project_root(self, start_dir: str = '.') -> str:
        """Find the project root by looking for a .git or .super-prompt directory."""
        path = os.path.abspath(start_dir)
        while path != '/':
            if os.path.isdir(os.path.join(path, '.git')) or os.path.isdir(os.path.join(path, '.super-prompt')):
                return path
            path = os.path.dirname(path)
        return os.path.abspath(start_dir)  # Fallback to current dir

    def _load_personas(self) -> Dict[str, Any]:
        """Loads persona definitions from the personas.yaml file."""
        if not os.path.exists(self.personas_path):
            print(f"FATAL: Persona manifest not found at '{self.personas_path}'", file=sys.stderr)
            return {}
        
        try:
            with open(self.personas_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"FATAL: Failed to load or parse personas.yaml: {e}", file=sys.stderr)
            return {}

    def get_persona(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieves the configuration for a single persona."""
        return self.personas.get(name)

    def list_personas(self) -> List[Dict[str, str]]:
        """Returns a list of all available personas with their descriptions."""
        return [
            {"name": name, "description": config.get("desc", "No description.")}
            for name, config in self.personas.items()
        ]

    def build_prompt(self, name: str, query: str, context: str = "", **kwargs) -> str:
        """
        Builds a complete, ready-to-use prompt for a given persona.
        """
        persona_config = self.get_persona(name)
        
        if not persona_config:
            # Fallback for unknown or undefined personas
            return f"**[Persona]** {name}\n\n{context}\n\n**[User's Request]**\n{query}\n"
        
        # Handle special cases like 'debate' which has a unique prompt structure
        if name == 'debate':
            return self.build_debate_prompt(query, rounds=kwargs.get('rounds', 8))
        
        prompt_template = dedent(persona_config.get('prompt', '')).strip()
        
        # Combine the persona's base prompt, any provided context, and the user's query.
        full_prompt = f"{prompt_template}\n\n{context}\n\n**[User's Request]**\n{query}"
        
        return full_prompt.strip()

    def build_debate_prompt(self, topic: str, rounds: int = 8) -> str:
        """Builds the specialized prompt for the Debate persona."""
        rounds = max(2, min(int(rounds or 8), 20))
        return dedent(f'''
        You are a single model simulating a structured internal debate with two clearly separated selves:
        - Positive Self (Builder): constructive, solution-focused.
        - Critical Self (Skeptic): risk-driven, assumption-testing.

        Rules:
        - English only. Keep each turn concise (<= 6 lines).
        - Alternate strictly: Positive → Critical → Positive → ... ({rounds} rounds).
        - No repetition; each turn must add new reasoning.
        - End with a Synthesis that integrates strengths + mitigations.

        Topic: {topic}

        Output template:
        [INTENT]
        - Debate: {topic}
        [TASK_CLASSIFY]
        - Class: H (multi-step reasoning & evaluation)
        [PLAN]
        - Rounds: {rounds}
        - Criteria: correctness, risks, minimal viable path
        [EXECUTE]
        1) Positive Self: ...
        2) Critical Self: ...
        ... (continue alternating up to {rounds})
        [VERIFY]
        - Checks: factuality, feasibility, risk coverage
        [REPORT]
        - Synthesis: final position, plan, and guardrails
        ''')

# --- Backwards Compatibility Wrappers ---
# These functions allow older scripts to use the new system without modification.

persona_manager = PersonaManager()

def build_persona_prompt(name: str, query: str, context: str = "", **kwargs) -> str:
    """Builds a prompt for a given persona using the central manager."""
    return persona_manager.build_prompt(name, query, context, **kwargs)

def build_debate_prompt(topic: str, rounds: int = 8) -> str:
    """Builds the debate prompt using the central manager."""
    return persona_manager.build_debate_prompt(topic, rounds)

def build_dev_prompt(*, context: str, query: str) -> str:
    """Builds the dev prompt using the central manager for compatibility."""
    return persona_manager.build_prompt('dev', query, context)