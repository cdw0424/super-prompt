"""Personas loader (v3 scaffold)
Loads personas from YAML files if PyYAML is available, else returns None.
"""
from typing import Any, Dict, Optional

def load_yaml(path: str) -> Optional[Dict[str, Any]]:
    try:
        import yaml  # type: ignore
        with open(path,'r',encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception:
        return None

