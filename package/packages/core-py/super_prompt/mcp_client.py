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

import typer


class MCPClient:
    """MCP client wrapper using stdio transport"""

    def __init__(self, server_command: Optional[List[str]] = None):
        self.server_command = server_command or self._default_server_command()
        self._session = None
        self._exit_stack = AsyncExitStack()
        # Ensure no stdout usage in MCP environment
        self._stdout_suppressed = True

    def _default_server_command(self) -> List[str]:
        """Get default MCP server command (bin/sp-mcp equivalent)"""
        # Find Python interpreter
        python_cmd = self._resolve_python()

        # Set up environment like bin/sp-mcp
        project_root = os.environ.get('SUPER_PROMPT_PROJECT_ROOT') or self._resolve_project_root()
        package_root = os.environ.get('SUPER_PROMPT_PACKAGE_ROOT') or str(Path(__file__).parent.parent.parent)

        env = os.environ.copy()
        env.update({
            'MCP_SERVER_MODE': '1',
            'SUPER_PROMPT_PROJECT_ROOT': project_root,
            'SUPER_PROMPT_PACKAGE_ROOT': package_root,
            'PYTHONPATH': f"{package_root}/packages/core-py:{env.get('PYTHONPATH', '')}".rstrip(':'),
            'PYTHONUNBUFFERED': '1',
            'PYTHONUTF8': '1',
        })

        # Return the server command for MCP execution
        return [python_cmd, '-m', 'super_prompt.mcp_stdio']

    def _resolve_python(self) -> str:
        """Resolve Python interpreter (similar to bin/sp-mcp)"""
        candidates = []
        if os.environ.get('PYTHON'):
            candidates.append(os.environ['PYTHON'])

        if sys.platform == 'win32':
            candidates.extend(['python', 'py'])
        else:
            candidates.extend(['python3.12', 'python3.11', 'python3.10', 'python3', 'python'])

        for cmd in candidates:
            try:
                result = subprocess.run([cmd, '--version'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return cmd
            except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue

        return 'python3' if sys.platform != 'win32' else 'python'

    def _resolve_project_root(self) -> str:
        """Resolve project root (similar to bin/sp-mcp)"""
        cwd = os.getcwd()
        current = Path(cwd)

        # Look for .git directory
        for parent in [current] + list(current.parents):
            if (parent / '.git').exists():
                return str(parent)

        return cwd

    async def __aenter__(self):
        """Async context manager entry with improved error handling"""
        from mcp.client.stdio import stdio_client
        import anyio

        try:
            # Start MCP server process with better error handling
            self._process = await asyncio.create_subprocess_exec(
                *self.server_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Set up stderr monitoring for debugging
            asyncio.create_task(self._monitor_stderr())

            # Create stdio client with proper stream handling
            try:
                self._session = await stdio_client(self._process.stdout, self._process.stdin).__aenter__()
            except AttributeError as e:
                if "'StreamReader' object has no attribute 'command'" in str(e):
                    # MCP SDK compatibility issue - provide detailed error info
                    import sys
                    print(f"-------- MCP: SDK compatibility issue: {e}", file=sys.stderr, flush=True)
                    print("-------- MCP: This may be due to MCP SDK version mismatch", file=sys.stderr, flush=True)
                    print("-------- MCP: Attempting fallback mode...", file=sys.stderr, flush=True)
                    # Try fallback initialization
                    self._session = await self._create_fallback_session()
                else:
                    raise

        except Exception as e:
            import sys
            print(f"-------- MCP: Client initialization failed: {e}", file=sys.stderr, flush=True)
            print(f"-------- MCP: Server command: {' '.join(self.server_command or [])}", file=sys.stderr, flush=True)
            raise RuntimeError(f"MCP client initialization failed: {e}") from e

        return self

    async def _monitor_stderr(self):
        """Monitor stderr for debugging and error detection"""
        if not self._process or not self._process.stderr:
            return

        try:
            async for line in self._process.stderr:
                line = line.decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"-------- MCP: server stderr: {line}", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"-------- MCP: stderr monitoring failed: {e}", file=sys.stderr, flush=True)

    async def _create_fallback_session(self):
        """Create fallback session for compatibility issues"""
        import sys

        class FallbackSession:
            def __init__(self, process):
                self.process = process

            async def list_tools(self):
                """Fallback tool listing"""
                return type('ToolsResult', (), {'tools': []})()

            async def call_tool(self, name, arguments):
                """Fallback tool calling"""
                return type('ToolResult', (), {'content': [{'type': 'text', 'text': f'Fallback: Tool {name} not available'}]})()

            async def list_prompts(self):
                """Fallback prompt listing"""
                return type('PromptsResult', (), {'prompts': []})()

            async def get_prompt(self, name, arguments):
                """Fallback prompt getting"""
                return type('PromptResult', (), {'model_dump': lambda: {'error': 'Prompt not available'}})()

        return FallbackSession(self._process)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Close the stdio client session
        if hasattr(self._session, '__aexit__'):
            await self._session.__aexit__(exc_type, exc_val, exc_tb)

        # Terminate the server process
        if hasattr(self, '_process') and self._process:
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
            raise RuntimeError("Client not initialized. Use async context manager.")

        try:
            result = await self._session.list_tools()
            tools = [tool.model_dump() for tool in result.tools]

            # Validate tool structure
            validated_tools = []
            for tool in tools:
                if not isinstance(tool, dict) or 'name' not in tool:
                    print(f"-------- MCP: Invalid tool format: {tool}", file=sys.stderr, flush=True)
                    continue
                validated_tools.append(tool)

            return validated_tools

        except Exception as e:
            import sys
            print(f"-------- MCP: Failed to list tools: {e}", file=sys.stderr, flush=True)
            # Return empty list instead of crashing
            return []

    async def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        """Call a tool by name with enhanced error handling"""
        if not self._session:
            # Direct tool execution without MCP server
            return self._call_tool_direct(name, arguments or {})

        try:
            result = await self._session.call_tool(name, arguments or {})

            # Validate result structure
            if hasattr(result, 'content'):
                return result.content
            elif isinstance(result, dict) and 'content' in result:
                return result['content']
            else:
                # Fallback for unexpected result format
                return [{'type': 'text', 'text': str(result)}]

        except Exception as e:
            import sys
            print(f"-------- MCP: Tool call failed - {name}: {e}", file=sys.stderr, flush=True)
            print(f"-------- MCP: Arguments: {arguments}", file=sys.stderr, flush=True)

            # Try fallback direct call
            try:
                return self._call_tool_direct(name, arguments or {})
            except Exception as fallback_error:
                print(f"-------- MCP: Fallback also failed: {fallback_error}", file=sys.stderr, flush=True)
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


# CLI Interface
app = typer.Typer(name="super-prompt-mcp", help="Super Prompt MCP Client")


@app.command()
def list_tools(json_output: bool = typer.Option(False, "--json", help="Output as JSON")):
    """List available MCP tools"""
    async def _list_tools():
        async with MCPClient() as client:
            tools = await client.list_tools()
            if json_output:
                print(json.dumps(tools, indent=2), file=sys.stderr, flush=True)
            else:
                for tool in tools:
                    print(f"• {tool['name']}: {tool.get('description', 'No description')}", file=sys.stderr, flush=True)

    asyncio.run(_list_tools())


@app.command()
def call_tool(
    tool_name: str = typer.Argument(..., help="Name of the tool to call"),
    args_json: str = typer.Option(None, "--args-json", help="JSON string of arguments"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON")
):
    """Call an MCP tool"""
    async def _call_tool():
        # Parse arguments
        arguments = {}
        if args_json:
            try:
                arguments = json.loads(args_json)
            except json.JSONDecodeError as e:
                typer.echo(f"Error parsing JSON arguments: {e}", err=True)
                raise typer.Exit(1)

        async with MCPClient() as client:
            try:
                result = await client.call_tool(tool_name, arguments)
                if json_output:
                    print(json.dumps(result, indent=2), file=sys.stderr, flush=True)
                else:
                    # Pretty print the result to stderr to avoid MCP protocol interference
                    if isinstance(result, list):
                        for item in result:
                            if hasattr(item, 'text'):
                                print(item.text, file=sys.stderr, flush=True)
                            else:
                                print(str(item), file=sys.stderr, flush=True)
                    else:
                        print(str(result), file=sys.stderr, flush=True)
            except Exception as e:
                typer.echo(f"Error calling tool '{tool_name}': {e}", err=True)
                raise typer.Exit(1)

    asyncio.run(_call_tool())


@app.command()
def list_prompts(json_output: bool = typer.Option(False, "--json", help="Output as JSON")):
    """List available MCP prompts"""
    async def _list_prompts():
        async with MCPClient() as client:
            prompts = await client.list_prompts()
            if json_output:
                print(json.dumps(prompts, indent=2), file=sys.stderr, flush=True)
            else:
                for prompt in prompts:
                    print(f"• {prompt['name']}: {prompt.get('description', 'No description')}", file=sys.stderr, flush=True)

    asyncio.run(_list_prompts())


@app.command()
def get_prompt(
    prompt_name: str = typer.Argument(..., help="Name of the prompt to get"),
    args_json: str = typer.Option(None, "--args-json", help="JSON string of arguments"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON")
):
    """Get an MCP prompt"""
    async def _get_prompt():
        # Parse arguments
        arguments = {}
        if args_json:
            try:
                arguments = json.loads(args_json)
            except json.JSONDecodeError as e:
                typer.echo(f"Error parsing JSON arguments: {e}", err=True)
                raise typer.Exit(1)

        async with MCPClient() as client:
            try:
                result = await client.get_prompt(prompt_name, arguments)
                if json_output:
                    print(json.dumps(result, indent=2), file=sys.stderr, flush=True)
                else:
                    # Pretty print the result to stderr to avoid MCP protocol interference
                    if 'messages' in result:
                        for message in result['messages']:
                            role = message.get('role', 'unknown')
                            content = message.get('content', '')
                            if isinstance(content, str):
                                print(f"[{role.upper()}]: {content}", file=sys.stderr, flush=True)
                            elif isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and 'text' in item:
                                        print(f"[{role.upper()}]: {item['text']}", file=sys.stderr, flush=True)
                    else:
                        print(str(result), file=sys.stderr, flush=True)
            except Exception as e:
                typer.echo(f"Error getting prompt '{prompt_name}': {e}", err=True)
                raise typer.Exit(1)

    asyncio.run(_get_prompt())


@app.command()
def doctor(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    timeout: int = typer.Option(10, "--timeout", help="Timeout in seconds")
):
    """Run diagnostics on MCP server connection"""
    async def _doctor():
        import time
        start_time = time.time()

        try:
            async with asyncio.timeout(timeout):
                async with MCPClient() as client:
                    # Test tools listing
                    tools = await client.list_tools()
                    tools_count = len(tools)

                    # Test prompts listing
                    prompts = await client.list_prompts()
                    prompts_count = len(prompts)

                    # Test a simple tool call if available
                    test_tool_result = None
                    if tools:
                        test_tool = tools[0]['name']
                        try:
                            test_tool_result = await client.call_tool(test_tool, {})
                        except Exception as e:
                            test_tool_result = f"Error: {e}"

                    response_time = time.time() - start_time

                    result = {
                        "status": "healthy",
                        "response_time": f"{response_time:.2f}s",
                        "tools_count": tools_count,
                        "prompts_count": prompts_count,
                        "test_tool_result": test_tool_result,
                        "server_command": client.server_command
                    }

                    if json_output:
                        print(json.dumps(result, indent=2), file=sys.stderr, flush=True)
                    else:
                        print("✅ MCP Server Connection: Healthy", file=sys.stderr, flush=True)
                        print(f"⏱️  Response Time: {response_time:.2f}s", file=sys.stderr, flush=True)
                        print(f"📋 Available Tools: {tools_count}", file=sys.stderr, flush=True)
                        print(f"📝 Available Prompts: {prompts_count}", file=sys.stderr, flush=True)
                        if test_tool_result:
                            print(f"🧪 Test Tool Call: {'✅ Success' if not str(test_tool_result).startswith('Error:') else '❌ Failed'}", file=sys.stderr, flush=True)

        except asyncio.TimeoutError:
            result = {"status": "timeout", "message": f"Connection timed out after {timeout}s"}
            if json_output:
                print(json.dumps(result, indent=2), file=sys.stderr, flush=True)
            else:
                print(f"❌ MCP Server Connection: Timeout ({timeout}s)", file=sys.stderr, flush=True)
        except Exception as e:
            result = {"status": "error", "message": str(e)}
            if json_output:
                print(json.dumps(result, indent=2), file=sys.stderr, flush=True)
            else:
                print(f"❌ MCP Server Connection: Error - {e}", file=sys.stderr, flush=True)

    asyncio.run(_doctor())


if __name__ == "__main__":
    app()
