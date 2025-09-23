"""
Prompt-Based Workflow Executor for Super Prompt v5.0.5
Executes persona-specific prompts based on mode selection
"""

import os
from typing import Dict, Any, Optional
from .gpt_prompts import GPT_PROMPTS
from .grok_prompts import GROK_PROMPTS
from ..paths import project_root, project_data_dir
from ..personas.tools.system_tools import ensure_project_dossier


class PromptWorkflowExecutor:
    """Executes prompt-based workflows for Super Prompt personas"""

    def __init__(self):
        self.gpt_prompts = GPT_PROMPTS
        self.grok_prompts = GROK_PROMPTS

    def get_current_mode(self) -> str:
        """Get current LLM mode from environment or config"""
        # Check for mode override in environment
        mode = os.getenv('SUPER_PROMPT_MODE', '').lower()
        if mode in ['gpt', 'grok']:
            return mode

        # Check for mode file
        mode_file = os.path.join(os.getcwd(), '.super-prompt', 'mode.json')
        if os.path.exists(mode_file):
            try:
                import json
                with open(mode_file, 'r') as f:
                    mode_data = json.load(f)
                    saved_mode = mode_data.get('mode', '').lower()
                    if saved_mode in ['gpt', 'grok']:
                        return saved_mode
            except Exception:
                pass

        # Default to GPT mode
        return 'gpt'

    def get_prompt_template(self, persona: str, mode: Optional[str] = None) -> Optional[str]:
        """Get the appropriate prompt template for a persona and mode (strict matching)."""
        if mode is None:
            mode = self.get_current_mode()

        prompts = self.gpt_prompts if mode == 'gpt' else self.grok_prompts
        key = persona.lower()
        # Strict: Only exact key match; do not auto-fallback or transform
        return prompts.get(key)

    def execute_workflow(self, persona: str, query: str, mode: Optional[str] = None) -> str:
        """Execute a prompt-based workflow for the given persona"""
        # Get the prompt template (strict persona; no cross-persona fallback)
        try:
            ensure_project_dossier(project_root(), project_data_dir())
        except Exception:
            pass

        template = self.get_prompt_template(persona, mode)

        if not template:
            return f"Error: No prompt template found for persona '{persona}' in mode '{mode or self.get_current_mode()}'"

        # Format the prompt with the query
        try:
            formatted_prompt = template.format(query=query)
        except KeyError as e:
            return f"Error: Missing required parameter in prompt template: {e}"

        # For now, return the formatted prompt
        # In a real implementation, this would call the LLM API
        return formatted_prompt

    def list_available_personas(self, mode: Optional[str] = None) -> Dict[str, str]:
        """List all available personas with descriptions"""
        if mode is None:
            mode = self.get_current_mode()

        prompts = self.gpt_prompts if mode == 'gpt' else self.grok_prompts

        descriptions = {}
        for persona in prompts.keys():
            # Extract first line of prompt as description
            prompt = prompts[persona]
            first_line = prompt.split('\n')[0] if '\n' in prompt else prompt[:100]
            descriptions[persona] = first_line

        return descriptions


# Global executor instance
executor = PromptWorkflowExecutor()


def run_prompt_based_workflow(persona: str, query: str, mode: Optional[str] = None) -> str:
    """Main entry point for prompt-based workflow execution"""
    return executor.execute_workflow(persona, query, mode)
