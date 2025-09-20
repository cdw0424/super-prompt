Cursor MCP Setup Guide (English Only)

Overview
- Super Prompt runs as an MCP server. Cursor spawns it via stdio and calls tools directly.
- Initialization creates all required Cursor config automatically; no manual edits needed.

Automatic Setup
- Run: `super-prompt super:init`
- This generates `.cursor/mcp.json` with a safe default that spawns the server using the Python MCP server and exports required environment variables. It also installs Cursor rules/commands for Super Prompt.

Manual Reference (optional)
If you need to inspect or customize, `.cursor/mcp.json` follows this structure:

```
{
  "mcpServers": {
    "super-prompt": {
      "command": "python",
      "args": ["-m", "super_prompt.mcp_server"],
      "env": {
        "SUPER_PROMPT_ALLOW_INIT": "true",
        "SUPER_PROMPT_PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/packages/core-py"
      }
    }
  }
}
```

STDIO Discipline
- MCP uses stdout exclusively for JSON‑RPC frames; all diagnostics must go to stderr.
- Super Prompt prints logs to stderr with the `--------` prefix; stdout remains protocol‑only.

Where to Validate
- In Cursor: View → Output → “MCP Logs” to see server spawn, initialize, and tool registration.

LLM Mode Switching (auto)
- Use slash commands: `/grok-mode-on` or `/gpt-mode-on`.
- These commands run `super-prompt` locally to persist the LLM mode in `.super-prompt/mode.json` and expose it to the MCP server.
- You can also call MCP tools directly: `sp.grok_mode_on`, `sp.gpt_mode_on`, `sp.mode_get`, `sp.mode_set`.
