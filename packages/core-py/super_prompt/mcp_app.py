# packages/core-py/super_prompt/mcp_app.py
# Clean MCP application with essential tools only

def create_app():
    """Factory function that creates and configures FastMCP app"""
    try:
        from mcp.server.fastmcp import FastMCP
        app = FastMCP(name="super-prompt")
    except ImportError:
        raise RuntimeError("MCP SDK not available")

    @app.tool(name="sp_high")
    def high(query: str) -> str:
        """High-level analysis persona: Strategic thinking, big-picture analysis, and executive summaries"""
        return "High-Level Strategic Analysis Framework\n\nQuery: " + query + "\n\nStrategic analysis framework provided."

    return app
