from __future__ import annotations
import json
from pathlib import Path
from .paths import project_data_dir

MODE_FILE = project_data_dir() / 'mode.json'

def get_mode(default: str = 'gpt') -> str:
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
    return default

def set_mode(mode: str) -> str:
    m = str(mode or '').lower()
    if m == 'default':
        m = 'gpt'
    if m not in ('gpt','grok','claude'):
        raise ValueError('mode must be one of: gpt, grok, claude')
    MODE_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = { 'llm_mode': m }
    MODE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return m
