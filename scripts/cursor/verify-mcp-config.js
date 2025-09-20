#!/usr/bin/env node
/**
 * Verify MCP config (project .cursor/mcp.json or templates/cursor/mcp.json)
 * Ensures stdio transport and expected command/env are present.
 */
const fs = require('fs');
const path = require('path');

function loadJson(p) {
  try { return JSON.parse(fs.readFileSync(p, 'utf-8')); } catch { return null; }
}

function main() {
  const root = process.cwd();
  const projectCfg = path.join(root, '.cursor', 'mcp.json');
  const templateCfg = path.join(root, 'templates', 'cursor', 'mcp.json');
  const p = fs.existsSync(projectCfg) ? projectCfg : templateCfg;
  if (!fs.existsSync(p)) {
    console.error('-------- verify-mcp-config: no config found at', projectCfg, 'or', templateCfg);
    process.exit(1);
  }
  const json = loadJson(p);
  if (!json || !json.mcpServers || !json.mcpServers['super-prompt']) {
    console.error('-------- verify-mcp-config: missing mcpServers.super-prompt');
    process.exit(1);
  }
  const sp = json.mcpServers['super-prompt'];
  const errors = [];
  if (sp.type !== 'stdio') errors.push('type must be "stdio"');
  // Accept either relative ./bin/sp-mcp or absolute path ending with /bin/sp-mcp
  const cmdOk = sp.command && (/\.\/bin\/sp-mcp$/.test(sp.command) || /\/(?:bin|\\bin)\/sp-mcp$/.test(sp.command));
  if (!cmdOk) errors.push('command must point to bin/sp-mcp (relative or absolute)');
  const env = sp.env || {};
  for (const k of ['SUPER_PROMPT_ALLOW_INIT','SUPER_PROMPT_REQUIRE_MCP','SUPER_PROMPT_PROJECT_ROOT','PYTHONUNBUFFERED','PYTHONUTF8']) {
    if (!(k in env)) errors.push(`env.${k} missing`);
  }
  if (errors.length) {
    console.error('-------- verify-mcp-config: FAILED');
    for (const e of errors) console.error(' -', e);
    process.exit(1);
  }
}

main();
