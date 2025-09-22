"""
Python MCP Client for Super Prompt
Provides a pure Python interface to the MCP server using stdio transport.
"""

import asyncio
import json
import os
import subprocess
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any, Dict, List, Optional


# Disable typer completely
class MockTyper:
    def command(self, func=None):
        return func

    def __call__(self, *args, **kwargs):
        return self


typer = MockTyper()

# Disable CLI completely for direct execution
app = None


class MCPClient:
    """MCP client wrapper using stdio transport"""

    def __init__(self, server_command: Optional[List[str]] = None):
        if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
            print("DEBUG: MCPClient.__init__ started", file=sys.stderr)
        try:
            self.server_command = server_command or self._default_server_command()
            if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                print(f"DEBUG: server_command set to {self.server_command}", file=sys.stderr)
        except Exception as e:
            if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                print(f"DEBUG: Exception in _default_server_command: {e}", file=sys.stderr)
            import traceback

            if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                traceback.print_exc()
            raise
        self._session = None
        self._exit_stack = AsyncExitStack()
        # Ensure no stdout usage in MCP environment
        self._stdout_suppressed = True
        if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
            print("DEBUG: MCPClient.__init__ completed", file=sys.stderr)

    def _default_server_command(self) -> List[str]:
        """Get default MCP server command (bin/sp-mcp equivalent)"""
        # Find Python interpreter
        python_cmd = self._resolve_python()

        # Set up environment like bin/sp-mcp
        project_root = os.environ.get("SUPER_PROMPT_PROJECT_ROOT") or self._resolve_project_root()
        # Calculate package root correctly
        current_file = Path(__file__)
        package_root = str(current_file.parent.parent.parent)

        env = os.environ.copy()
        env.update(
            {
                "MCP_SERVER_MODE": "1",
                "SUPER_PROMPT_PROJECT_ROOT": project_root,
                "SUPER_PROMPT_PACKAGE_ROOT": package_root,
                "PYTHONPATH": f"{package_root}/packages/core-py:{project_root}:{env.get('PYTHONPATH', '')}".rstrip(
                    ":"
                ),
                "PYTHONUNBUFFERED": "1",
                "PYTHONUTF8": "1",
            }
        )

        # Return the server command for MCP execution
        # Note: PYTHONPATH will be set in the environment when subprocess is created
        return [python_cmd, "-m", "super_prompt.mcp_stdio"]

    def _resolve_python(self) -> str:
        """Resolve Python interpreter (use current Python executable)"""
        if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
            print(f"DEBUG: _resolve_python: sys.executable = {sys.executable}", file=sys.stderr)
        # Use the same Python executable that's running this script
        return sys.executable

    def _resolve_project_root(self) -> str:
        """Resolve project root (similar to bin/sp-mcp)"""
        if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
            print("DEBUG: _resolve_project_root called", file=sys.stderr)
        cwd = os.getcwd()
        current = Path(cwd)
        if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
            print(f"DEBUG: _resolve_project_root: cwd = {cwd}", file=sys.stderr)

        # Look for .git directory
        for parent in [current] + list(current.parents):
            if (parent / ".git").exists():
                return str(parent)

        return cwd

    async def __aenter__(self):
        """Async context manager entry - use direct import instead of subprocess"""
        try:
            # Import MCP server directly instead of using subprocess
            import super_prompt.mcp_server_new as mcp_server

            mcp = mcp_server.mcp

            # Create a simple session that directly calls MCP server methods
            class DirectMCPSession:
                def __init__(self, mcp_instance):
                    self.mcp = mcp_instance

                async def list_tools(self):
                    # Call MCP server list_tools directly
                    try:
                        tools = await self.mcp.list_tools()
                        return type("ToolsResult", (), {"tools": tools})()
                    except:
                        # Fallback to synchronous call
                        import asyncio

                        loop = asyncio.get_event_loop()
                        tools = loop.run_until_complete(self.mcp.list_tools())
                        return type("ToolsResult", (), {"tools": tools})()

                async def call_tool(self, name, arguments):
                    # Call MCP server tool directly
                    try:
                        result = await self.mcp.call_tool(name, arguments)
                        return result
                    except:
                        # Fallback to synchronous call
                        import asyncio

                        loop = asyncio.get_event_loop()
                        result = loop.run_until_complete(self.mcp.call_tool(name, arguments))
                        return result

                async def list_prompts(self):
                    try:
                        prompts = await self.mcp.list_prompts()
                        return type("PromptsResult", (), {"prompts": prompts})()
                    except:
                        return type("PromptsResult", (), {"prompts": []})()

                async def get_prompt(self, name, arguments):
                    try:
                        result = await self.mcp.get_prompt(name, arguments)
                        return result
                    except:
                        return type(
                            "PromptResult", (), {"model_dump": lambda: {"error": "Not available"}}
                        )()

                async def __aenter__(self):
                    return self

                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    pass

            # Create direct session
            if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                print(f"DEBUG: Creating DirectMCPSession with mcp: {mcp}", file=sys.stderr)
            self._session = await DirectMCPSession(mcp).__aenter__()
            if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                print(f"DEBUG: DirectMCPSession created successfully", file=sys.stderr)
            self._process = None  # No subprocess

        except Exception as e:
            if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                print(f"DEBUG: Exception in MCP client initialization: {e}", file=sys.stderr)
            import traceback

            if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                traceback.print_exc()
            # Re-raise for debugging
            raise RuntimeError(f"MCP client initialization failed: {e}") from e

        return self

    async def _monitor_stderr(self):
        """Monitor stderr for debugging and error detection"""
        if not self._process or not self._process.stderr:
            return

        try:
            async for line in self._process.stderr:
                line = line.decode("utf-8", errors="ignore").strip()
                if line:
                    # Silent stderr monitoring for clean MCP operation
                    pass
        except Exception as e:
            # Silent stderr monitoring failure for clean MCP operation
            pass

    async def _create_fallback_session(self):
        """Create fallback session for compatibility issues"""

        class FallbackSession:
            def __init__(self, process):
                self.process = process

            async def list_tools(self):
                """Fallback tool listing"""
                return type("ToolsResult", (), {"tools": []})()

            async def call_tool(self, name, arguments):
                """Fallback tool calling"""
                return type(
                    "ToolResult",
                    (),
                    {"content": [{"type": "text", "text": f"Fallback: Tool {name} not available"}]},
                )()

            async def list_prompts(self):
                """Fallback prompt listing"""
                return type("PromptsResult", (), {"prompts": []})()

            async def get_prompt(self, name, arguments):
                """Fallback prompt getting"""
                return type(
                    "PromptResult", (), {"model_dump": lambda: {"error": "Prompt not available"}}
                )()

        return FallbackSession(self._process)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Close the stdio client session
        if hasattr(self._session, "__aexit__"):
            await self._session.__aexit__(exc_type, exc_val, exc_tb)

        # Terminate the server process
        if hasattr(self, "_process") and self._process:
            try:
                self._process.terminate()
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except (asyncio.TimeoutError, ProcessLookupError):
                try:
                    self._process.kill()
                    await asyncio.wait_for(self._process.wait(), timeout=2.0)
                except (asyncio.TimeoutError, ProcessLookupError):
                    pass  # Process already terminated

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools with enhanced error handling"""
        if not self._session:
            if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                print(f"DEBUG: MCP client not initialized - _session is None", file=sys.stderr)
            raise RuntimeError("Client not initialized. Use async context manager.")

        try:
            if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                print(f"DEBUG: Calling _session.list_tools()", file=sys.stderr)
            result = await self._session.list_tools()
            if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                print(f"DEBUG: Got result: {result}", file=sys.stderr)
            tools = [tool.model_dump() for tool in result.tools]
            if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                print(f"DEBUG: Converted {len(tools)} tools", file=sys.stderr)

            # Validate tool structure
            validated_tools = []
            for tool in tools:
                if not isinstance(tool, dict) or "name" not in tool:
                    if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                        print(f"DEBUG: Invalid tool format: {tool}", file=sys.stderr)
                    continue
                validated_tools.append(tool)

            if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                print(f"DEBUG: Returning {len(validated_tools)} validated tools", file=sys.stderr)
            return validated_tools

        except Exception as e:
            if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
                print(f"DEBUG: Exception in list_tools: {e}", file=sys.stderr)
            import traceback

            traceback.print_exc()
            # Re-raise exception for debugging
            raise e

    async def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        """Call a tool by name with enhanced error handling"""
        if not self._session:
            # Direct tool execution without MCP server
            return self._call_tool_direct(name, arguments or {})

        try:
            result = await self._session.call_tool(name, arguments or {})

            # Validate result structure
            if hasattr(result, "content"):
                return result.content
            elif isinstance(result, dict) and "content" in result:
                return result["content"]
            else:
                # Fallback for unexpected result format
                return [{"type": "text", "text": str(result)}]

        except Exception as e:
            # Silent tool call failure for clean MCP operation
            # Try fallback direct call
            try:
                return self._call_tool_direct(name, arguments or {})
            except Exception as fallback_error:
                # Silent fallback failure for clean MCP operation
                raise RuntimeError(f"Tool call failed: {e}") from e

    def _call_tool_direct(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Direct tool execution without MCP server"""
        # Simple tool implementations for testing
        if name == "sp_high":
            query = arguments.get("query", "")
            return [{"type": "text", "text": f"High-level analysis of: {query}"}]
        elif name == "sp_grok":
            query = arguments.get("query", "")
            return [{"type": "text", "text": f"Grok analysis of: {query}"}]
        elif name == "sp_gpt":
            query = arguments.get("query", "")
            return [{"type": "text", "text": f"GPT analysis of: {query}"}]
        else:
            raise ValueError(f"Tool '{name}' not found")

    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List available prompts"""
        if not self._session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        result = await self._session.list_prompts()
        return [prompt.model_dump() for prompt in result.prompts]

    async def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        """Get a prompt by name"""
        if not self._session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        result = await self._session.get_prompt(name, arguments or {})
        return result.model_dump()


# CLI Interface - Simple version without typer
def list_tools():
    """List available MCP tools"""
    try:
        # Direct MCP server access
        from super_prompt.mcp_server_new import mcp
        import asyncio

        async def get_tools():
            tools = await mcp.list_tools()
            return tools

        # Get tools directly
        tools = asyncio.run(get_tools())

        # Display tools for CLI users (only when not in MCP environment)
        if os.environ.get("MCP_SERVER_MODE") != "1":
            print("Available MCP Tools:")
            for tool in tools:
                tool_name = tool.name
                tool_description = tool.description
                print(f"  • {tool_name}: {tool_description}")
            print(f"\nTotal: {len(tools)} tools available")

    except Exception as e:
        if os.environ.get("MCP_SERVER_MODE") != "1":
            print(f"Error listing MCP tools: {e}")
        import traceback

        if os.environ.get("SUPER_PROMPT_DEBUG") == "1":
            traceback.print_exc()


def main():
    """Main CLI entry point"""
    if os.environ.get("SUPER_PROMPT_DEBUG") == "1" and os.environ.get("MCP_SERVER_MODE") != "1":
        print("DEBUG: main() called", file=sys.stderr)
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if os.environ.get("SUPER_PROMPT_DEBUG") == "1" and os.environ.get("MCP_SERVER_MODE") != "1":
            print(f"DEBUG: command = {command}", file=sys.stderr)
        if command == "list-tools":
            list_tools()
        else:
            if os.environ.get("MCP_SERVER_MODE") != "1":
                print(f"Unknown command: {command}")
    else:
        if os.environ.get("MCP_SERVER_MODE") != "1":
            print("Usage: python -m super_prompt.mcp_client <command>")
            print("Available commands: list-tools")


# CLI commands removed for direct execution


# CLI commands removed for direct execution


# CLI commands removed for direct execution


if __name__ == "__main__":
    # Simple direct execution for testing
    try:
        print("Starting MCP client...")
        # Direct MCP server access
        from super_prompt.mcp_server_new import mcp
        import asyncio

        async def get_tools():
            tools = await mcp.list_tools()
            return tools

        # Get tools directly
        tools = asyncio.run(get_tools())

        # Display tools for CLI users
        print("Available MCP Tools:")
        for tool in tools:
            tool_name = tool.name
            tool_description = tool.description
            print(f"  • {tool_name}: {tool_description}")
        print(f"\nTotal: {len(tools)} tools available")

    except Exception as e:
        print(f"Error listing MCP tools: {e}")
        import traceback

        traceback.print_exc()
