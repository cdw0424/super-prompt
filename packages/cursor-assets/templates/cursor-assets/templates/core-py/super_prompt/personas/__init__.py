"""
Personas Module - Persona management and configuration
"""

try:
    # Preferred: dedicated config module
    from .config import PersonaConfig
except Exception:  # fallback for older loader-based config
    from .loader import PersonaConfig  # type: ignore

from .loader import PersonaLoader

__all__ = ["PersonaLoader", "PersonaConfig"]
