#!/usr/bin/env python3
# packages/core-py/super_prompt/mcp_stdio.py
# MCP STDIO Server - Clean integration with mcp_server_new.py

import sys
import os
import json
from pathlib import Path

def main():
    """Entry point for MCP STDIO server"""
    try:
        # Import the main MCP server
        from .mcp_server_new import mcp

        # Run the MCP server with proper error handling
        if hasattr(mcp, 'run'):
            mcp.run()
        elif hasattr(mcp, '__call__'):
            mcp()
        else:
            # Fallback to basic stdio server
            _run_basic_stdio_server(mcp)

    except Exception as err:
        import sys
        print(f"Error starting MCP server: {err}", file=sys.stderr)
        sys.exit(1)

def _run_basic_stdio_server(mcp_instance):
    """Basic stdio server implementation"""
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break

            try:
                message = json.loads(line.strip())
                response = _handle_message(mcp_instance, message)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"}
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id") if 'message' in locals() else None,
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(error_response), flush=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr, flush=True)

def _handle_message(mcp_instance, message):
    """Handle MCP protocol messages"""
    method = message.get("method")
    id = message.get("id")

    if method == "tools/list":
        return _handle_tools_list(mcp_instance, id)
    elif method == "tools/call":
        return _handle_tools_call(mcp_instance, message, id)
    else:
        return {
            "jsonrpc": "2.0",
            "id": id,
            "error": {"code": -32601, "message": "Method not found"}
        }

def _handle_tools_list(mcp_instance, id):
    """Handle tools/list request"""
    try:
        if hasattr(mcp_instance, 'list_tools'):
            tools = mcp_instance.list_tools()
        elif hasattr(mcp_instance, '_tools'):
            tools = list(mcp_instance._tools.keys())
        else:
            tools = []

        return {"jsonrpc": "2.0", "id": id, "result": {"tools": tools}}
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": id,
            "error": {"code": -32603, "message": str(e)}
        }

def _handle_tools_call(mcp_instance, message, id):
    """Handle tools/call request"""
    try:
        params = message.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})

        if hasattr(mcp_instance, 'call_tool'):
            result = mcp_instance.call_tool(name, arguments)
        elif hasattr(mcp_instance, '_tools') and name in mcp_instance._tools:
            result = mcp_instance._tools[name](**arguments)
        else:
            raise ValueError(f"Tool '{name}' not found")

        return {
            "jsonrpc": "2.0",
            "id": id,
            "result": {"content": [{"type": "text", "text": str(result)}]}
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": id,
            "error": {"code": -32603, "message": str(e)}
        }

if __name__ == "__main__":
    main()
