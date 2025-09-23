---
description: init command - Bootstrap Super Prompt assets for the current project
run: mcp
server: super-prompt
tool: sp_init
args:
  force: true
---

## Execution Mode

# Init — Project Bootstrap

## Instructions
- Review the project dossier at `.super-prompt/context/project-dossier.md`; if it is missing, run `/super-prompt/init` to regenerate it.
- Run from the project root to sync `.cursor/` and `.super-prompt/` assets
- Use MCP Only (MCP server call): /super-prompt/init "<optional notes>"
- The CLI equivalent is `super-prompt super:init --force`

## Phases & Checklist
### Phase 0 — Preflight
- [ ] Confirm you are inside the repository that should receive Super Prompt assets
- [ ] (Optional) Back up local `.cursor/` customizations if you maintained manual edits
- [ ] Ensure the MCP server points to the latest `sp-mcp` binary (`super-prompt/bin/sp-mcp`)

### Phase 1 — Asset Sync
- [ ] Copy Cursor commands/rules from the npm package into `.cursor/`
- [ ] Refresh MCP configuration (`.cursor/mcp.json`, `.super-prompt/config.json`)
- [ ] Install/update Python dependencies for `sp-mcp`

### Phase 2 — Verification
- [ ] Run `/super-prompt/list-commands` to confirm every tool, including `/super-prompt/double-check` and `/super-prompt/resercher`, is registered
- [ ] Inspect `.cursor/commands/super-prompt/` to ensure the latest markdown guides are present
- [ ] Check `sp_list_personas` output for the expected persona catalog

### Phase 3 — Post-Init Tasks
- [ ] Restart Cursor (fully quit and relaunch) so slash commands reload
- [ ] Re-run any workspace-specific setup (e.g., environment variables, adapters)
- [ ] Communicate changes to teammates so they run init after pulling updates

## Outputs
- Fresh `.cursor/commands/super-prompt/` and `.cursor/rules/` assets
- Updated MCP server configuration referencing the latest `sp-mcp`
- Verified persona/tool registry aligned with the npm release
- Project dossier at `.super-prompt/context/project-dossier.md`
