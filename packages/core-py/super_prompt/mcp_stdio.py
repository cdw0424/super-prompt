#!/usr/bin/env python3
"""Super Prompt MCP stdio server entrypoint."""

from __future__ import annotations

import asyncio
import inspect
import json
import sys
from typing import Any, Dict, Iterable, Optional

from . import __version__ as SUPER_PROMPT_VERSION

LOG_PREFIX = "-------- MCP:"


def main() -> None:
    """Start the MCP server using FastMCP when available, fallback otherwise."""
    try:
        from .mcp_server_new import _TOOL_REGISTRY, mcp
    except Exception as exc:  # pragma: no cover - import level failure is fatal
        _log_error(f"failed to import MCP server modules: {exc}")
        raise

    # Try to run the official FastMCP runtime first. When the optional dependency is
    # missing the stub implementation raises a RuntimeError that we can intercept and
    # continue with a lightweight protocol handler instead of exiting abruptly.
    try:
        if not hasattr(mcp, "run"):
            raise RuntimeError("MCP runtime missing run() API")

        run_result = mcp.run()
        if inspect.isawaitable(run_result):
            asyncio.run(run_result)  # type: ignore[func-returns-value]
        return
    except RuntimeError as exc:
        message = str(exc)
        if "MCP SDK not available" not in message and "run() API" not in message:
            raise
        _log_info("FastMCP not detected; activating fallback stdio implementation")
    except AttributeError:
        _log_info("FastMCP runtime unavailable; activating fallback stdio implementation")
    except Exception as exc:
        _log_error(f"FastMCP runtime crashed: {exc}")
        raise

    asyncio.run(_run_fallback_stdio(_TOOL_REGISTRY))


async def _run_fallback_stdio(tool_registry: Dict[str, Any]) -> None:
    """Minimal MCP stdio server implementation for environments without FastMCP."""

    loop = asyncio.get_running_loop()
    _log_info("Fallback MCP stdio server started")

    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            break

        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            _write_response(_error_response(None, -32700, "Parse error"))
            continue

        response = await _handle_message(tool_registry, message)
        if response is not None:
            _write_response(response)


async def _handle_message(tool_registry: Dict[str, Any], message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Dispatch incoming MCP messages for the fallback server."""

    method = message.get("method")
    msg_id = message.get("id")

    # Notifications carry no identifier; ignore quietly after minimal validation.
    if msg_id is None and message.get("jsonrpc") == "2.0":
        return None

    if method == "initialize":
        return _initialize_response(msg_id)
    if method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": _list_tools(tool_registry)}}
    if method == "tools/call":
        return await _call_tool(tool_registry, message, msg_id)
    if method == "prompts/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"prompts": []}}
    if method == "prompts/get":
        return _error_response(msg_id, -32601, "Prompt not found")

    return _error_response(msg_id, -32601, f"Method '{method}' not implemented")


def _initialize_response(msg_id: Any) -> Dict[str, Any]:
    """Return a minimal initialize response compliant with the MCP spec."""

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {
            "protocolVersion": "0.1.0",
            "serverInfo": {
                "name": "super-prompt",
                "version": SUPER_PROMPT_VERSION,
            },
            "capabilities": {
                "tools": {"listChanged": False},
                "prompts": {"listChanged": False},
            },
        },
    }


def _list_tools(tool_registry: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    """Build tool descriptors from the in-memory registry."""

    tools: list[Dict[str, Any]] = []
    for tool_name, tool_func in tool_registry.items():
        description = inspect.getdoc(tool_func) or f"{tool_name} tool"
        schema = _build_input_schema(tool_func)
        entry: Dict[str, Any] = {
            "name": tool_name,
            "description": description,
        }
        if schema:
            entry["inputSchema"] = schema
        tools.append(entry)
    return tools


async def _call_tool(tool_registry: Dict[str, Any], message: Dict[str, Any], msg_id: Any) -> Dict[str, Any]:
    """Execute a registry tool and serialize the response."""

    params = message.get("params") or {}
    tool_name = params.get("name")
    arguments = params.get("arguments") or {}

    if tool_name not in tool_registry:
        return _error_response(msg_id, -32602, f"Tool '{tool_name}' not found")

    tool_func = tool_registry[tool_name]

    try:
        result = tool_func(**arguments)
        if inspect.isawaitable(result):
            result = await result
    except TypeError as exc:
        return _error_response(msg_id, -32602, f"Invalid arguments for {tool_name}: {exc}")
    except Exception as exc:  # pragma: no cover - tool execution errors are propagated
        return _error_response(msg_id, -32000, f"{tool_name} failed: {exc}")

    content = _normalize_content(result)
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {"content": content},
    }


def _build_input_schema(func: Any) -> Optional[Dict[str, Any]]:
    """Derive a JSON schema from a tool callable's signature."""

    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        return {"type": "object"}

    properties: Dict[str, Dict[str, Any]] = {}
    required: list[str] = []

    for name, param in signature.parameters.items():
        if name == "self" or param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        schema: Dict[str, Any] = {"type": _python_type_to_json_type(param.annotation)}
        if param.default is not inspect._empty:
            schema["default"] = param.default
        else:
            required.append(name)
        properties[name] = schema

    schema: Dict[str, Any] = {"type": "object", "properties": properties, "additionalProperties": False}
    if required:
        schema["required"] = required
    if not properties:
        schema.pop("properties")
        schema.pop("additionalProperties", None)
    return schema


def _python_type_to_json_type(annotation: Any) -> str:
    """Map Python annotations to JSON schema types."""

    if annotation in (bool, "bool"):
        return "boolean"
    if annotation in (int, "int"):
        return "integer"
    if annotation in (float, "float"):
        return "number"
    return "string"


def _normalize_content(result: Any) -> list[Dict[str, Any]]:
    """Convert tool return values into MCP text content."""

    if result is None:
        return [{"type": "text", "text": ""}]

    if isinstance(result, list):
        if all(isinstance(item, dict) and "type" in item for item in result):
            return result  # Already in MCP content format
        if all(hasattr(item, "type") and hasattr(item, "text") for item in result):
            return [{"type": getattr(item, "type", "text"), "text": getattr(item, "text", str(item))} for item in result]
        return [{"type": "text", "text": "\n".join(str(item) for item in result)}]

    if hasattr(result, "type") and hasattr(result, "text"):
        return [{"type": getattr(result, "type", "text"), "text": getattr(result, "text", str(result))}]

    if isinstance(result, dict) and "content" in result:
        content = result["content"]
        if isinstance(content, list):
            return _normalize_content(content)

    return [{"type": "text", "text": str(result)}]


def _error_response(msg_id: Any, code: int, message: str) -> Dict[str, Any]:
    """Build a JSON-RPC error response."""

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": code, "message": message},
    }


def _write_response(payload: Dict[str, Any]) -> None:
    """Serialize and flush a JSON-RPC response."""

    print(json.dumps(payload, ensure_ascii=False), flush=True)


def _log_info(message: str) -> None:
    print(f"{LOG_PREFIX} {message}", file=sys.stderr)


def _log_error(message: str) -> None:
    print(f"{LOG_PREFIX} {message}", file=sys.stderr)


if __name__ == "__main__":
    main()
