"""
Personas Module - Persona management and configuration
"""

from .loader import PersonaConfig, PersonaLoader  # single source of truth

__all__ = ["PersonaLoader", "PersonaConfig"]
