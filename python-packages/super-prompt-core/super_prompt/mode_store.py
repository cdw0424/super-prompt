from __future__ import annotations
import json
import os
from pathlib import Path
from .paths import project_data_dir

MODE_FILE = project_data_dir() / 'mode.json'

def get_mode(default: str = 'gpt') -> str:
    """Get current LLM mode with automatic detection and caching."""
    try:
        if MODE_FILE.exists():
            data = json.loads(MODE_FILE.read_text(encoding='utf-8'))
            mode = str(data.get('llm_mode') or '').lower()
            if mode == 'default':
                return 'gpt'
            if mode in ('gpt','grok','claude'):
                return mode
    except Exception:
        pass

    # Fallback to environment variable
    env_mode = os.getenv('SUPER_PROMPT_MODE', '').lower()
    if env_mode in ('gpt', 'grok', 'claude'):
        return env_mode

    return default


def is_grok_mode() -> bool:
    """Check if Grok mode is currently active."""
    return get_mode() == 'grok'


def is_gpt_mode() -> bool:
    """Check if GPT mode is currently active."""
    return get_mode() == 'gpt'


def is_claude_mode() -> bool:
    """Check if Claude mode is currently active."""
    return get_mode() == 'claude'


def get_optimized_model_for_mode() -> str:
    """Get the optimized model for the current mode."""
    mode = get_mode()
    if mode == 'grok':
        return 'grok-code-fast-1'
    elif mode == 'gpt':
        return 'gpt-4o'  # or whatever the default GPT model should be
    elif mode == 'claude':
        return 'claude-3-5-sonnet-20241022'  # or whatever the default Claude model should be
    return 'gpt-4o'

def set_mode(mode: str) -> str:
    m = str(mode or '').lower()
    if m == 'default':
        m = 'gpt'
    if m not in ('gpt','grok','claude'):
        raise ValueError('mode must be one of: gpt, grok, claude')
    MODE_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {'llm_mode': m}
    MODE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    # Keep process environment in sync so subsequent calls respect the new mode immediately.
    os.environ['SUPER_PROMPT_MODE'] = m

    return m
