"""
Tool registration and metadata management
"""

import inspect
import json
from typing import Dict, Any, List, Optional


# Tool metadata registry
TOOL_METADATA: Dict[str, Dict[str, Any]] = {
    "sp.version": {"category": "system", "tags": ["system", "diagnostics"]},
    "sp.init": {"category": "system", "tags": ["system", "setup"], "destructive": True},
    "sp.refresh": {"category": "system", "tags": ["system", "setup"], "destructive": True},
    "sp.list_commands": {"category": "system", "tags": ["system", "introspection"]},
    "sp.list_personas": {"category": "system", "tags": ["system", "personas"]},
    "sp.mode_get": {"category": "system", "tags": ["system", "mode"]},
    "sp.mode_set": {"category": "system", "tags": ["system", "mode"], "destructive": True},
    "sp.grok_mode_on": {"category": "system", "tags": ["system", "mode"], "destructive": True},
    "sp.gpt_mode_on": {"category": "system", "tags": ["system", "mode"], "destructive": True},
    "sp.grok_mode_off": {"category": "system", "tags": ["system", "mode"], "destructive": True},
    "sp.gpt_mode_off": {"category": "system", "tags": ["system", "mode"], "destructive": True},
    "sp.architect": {
        "category": "persona",
        "persona": "Architect",
        "tags": ["persona", "architecture"],
    },
    "sp.frontend": {"category": "persona", "persona": "Frontend", "tags": ["persona", "frontend"]},
    "sp.backend": {"category": "persona", "persona": "Backend", "tags": ["persona", "backend"]},
    "sp.security": {"category": "persona", "persona": "Security", "tags": ["persona", "security"]},
    "sp.performance": {
        "category": "persona",
        "persona": "Performance",
        "tags": ["persona", "performance"],
    },
    "sp.analyzer": {"category": "persona", "persona": "Analyzer", "tags": ["persona", "analysis"]},
    "sp.qa": {"category": "persona", "persona": "QA", "tags": ["persona", "quality"]},
    "sp.refactorer": {
        "category": "persona",
        "persona": "Refactorer",
        "tags": ["persona", "refactoring"],
    },
    "sp.devops": {"category": "persona", "persona": "DevOps", "tags": ["persona", "devops"]},
    "sp.debate": {"category": "persona", "persona": "Debate", "tags": ["persona", "analysis"]},
    "sp.mentor": {"category": "persona", "persona": "Mentor", "tags": ["persona", "guidance"]},
    "sp.scribe": {"category": "persona", "persona": "Scribe", "tags": ["persona", "documentation"]},
    "sp.doc-master": {
        "category": "persona",
        "persona": "Doc Master",
        "tags": ["persona", "documentation"],
    },
    "sp.docs-refector": {
        "category": "persona",
        "persona": "Docs Refector",
        "tags": ["persona", "documentation", "refactor"],
    },
    "sp.service-planner": {
        "category": "persona",
        "persona": "Service Planner",
        "tags": ["persona", "strategy"],
    },
    "sp.dev": {"category": "persona", "persona": "Dev", "tags": ["persona", "development"]},
    "sp.review": {"category": "persona", "persona": "Review", "tags": ["persona", "review"]},
    "sp.optimize": {
        "category": "persona",
        "persona": "Optimize",
        "tags": ["persona", "optimization"],
    },
    "sp.grok": {"category": "persona", "persona": "Grok", "tags": ["persona", "grok"]},
    "sp.db-expert": {
        "category": "persona",
        "persona": "DB Expert",
        "tags": ["persona", "database"],
    },
    "sp.specify": {"category": "sdd", "tags": ["sdd", "spec"]},
    "sp.plan": {"category": "sdd", "tags": ["sdd", "plan"]},
    "sp.tasks": {"category": "sdd", "tags": ["sdd", "tasks"]},
    "sp.sdd_architecture": {"category": "sdd", "tags": ["sdd", "architecture"]},
    "sp.implement": {"category": "sdd", "tags": ["sdd", "implement"]},
    "sp.seq": {"category": "reasoning", "tags": ["reasoning", "sequential"]},
    "sp.seq-ultra": {"category": "reasoning", "tags": ["reasoning", "sequential", "advanced"]},
    "sp_high": {"category": "reasoning", "tags": ["reasoning", "high-effort"]},
    "sp.tr": {"category": "utility", "tags": ["utility", "translation"]},
    "sp.ultracompressed": {"category": "utility", "tags": ["utility", "compression"]},
    "sp.high_mode_on": {"category": "mode", "tags": ["mode", "codex"]},
    "sp.high_mode_off": {"category": "mode", "tags": ["mode", "codex"]},
}


# Registered tool annotations
REGISTERED_TOOL_ANNOTATIONS: Dict[str, Dict[str, Any]] = {}


def _short_description(doc: Optional[str]) -> str:
    """Extract short description from docstring"""
    if not doc:
        return ""
    lines = [line.strip() for line in doc.strip().splitlines() if line.strip()]
    return lines[0] if lines else ""


def register_tool(tool_name: str):
    """Tool registration decorator"""
    meta = TOOL_METADATA.get(tool_name, {})

    def decorator(fn):
        description = _short_description(fn.__doc__)
        annotations: Dict[str, Any] = {
            "name": tool_name,
            "description": description,
            "destructive": bool(meta.get("destructive", False)),
        }

        if "category" in meta:
            annotations["category"] = meta["category"]
        if meta.get("tags"):
            annotations["tags"] = list(meta["tags"])
        if meta.get("persona"):
            annotations["persona"] = meta["persona"]
        if meta.get("examples"):
            annotations["examples"] = meta["examples"]

        input_schema: Optional[Dict[str, Any]] = None
        try:
            fn_sig = inspect.signature(fn)
        except Exception:
            fn_sig = None

        if fn_sig:
            properties: Dict[str, Any] = {}
            required: List[str] = []
            for param_name, param in fn_sig.parameters.items():
                if param_name == "self":
                    continue
                schema: Dict[str, Any] = {}
                annotation = param.annotation
                schema_type = "string"
                if annotation in (bool, "bool"):
                    schema_type = "boolean"
                elif annotation in (int, "int"):
                    schema_type = "integer"
                elif annotation in (float, "float"):
                    schema_type = "number"
                schema["type"] = schema_type
                if param.default is not inspect._empty:
                    schema["default"] = param.default
                properties[param_name] = schema
                if param.default is inspect._empty:
                    required.append(param_name)
            if properties:
                input_schema = {
                    "type": "object",
                    "properties": properties,
                    "additionalProperties": False,
                }
                if required:
                    input_schema["required"] = required

        if input_schema:
            annotations["input_schema"] = input_schema

        REGISTERED_TOOL_ANNOTATIONS[tool_name] = annotations
        setattr(fn, "_sp_annotations", annotations)
        return fn

    return decorator
