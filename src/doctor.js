#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

function projectRoot() {
  // INIT_CWD points to the user's project when running npm scripts
  const init = process.env.INIT_CWD;
  if (init && fs.existsSync(path.join(init, 'package.json'))) return init;
  return process.cwd();
}

function pkgRoot() {
  return path.resolve(__dirname, '..');
}

function log(msg) {
  process.stdout.write(`-------- ${msg}\n`);
}

function checkFile(p, note) {
  const ok = fs.existsSync(p);
  log(`${ok ? 'OK' : 'MISS'}: ${note} (${p})`);
  return ok;
}

function ensureMode(pr) {
  const dir = path.join(pr, '.super-prompt');
  const file = path.join(dir, 'mode.json');
  try {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    if (!fs.existsSync(file)) {
      fs.writeFileSync(file, JSON.stringify({ llm_mode: 'gpt', updatedAt: new Date().toISOString() }, null, 2));
      log(`created: default mode file at ${file}`);
    }
    return true;
  } catch (e) {
    log(`ERROR: cannot write mode file (${e.message})`);
    return false;
  }
}

function runMcp(tool, args = []) {
  const root = pkgRoot();
  const cmd = process.execPath; // node
  const cli = path.join(root, 'src', 'mcp-client.js');
  const a = [cli, 'call', tool, ...args];
  const env = {
    ...process.env,
    SUPER_PROMPT_PACKAGE_ROOT: root,
    SUPER_PROMPT_ALLOW_INIT: 'true',
    PYTHONPATH: `${path.join(root, 'packages', 'core-py')}:${process.env.PYTHONPATH || ''}`,
  };
  const r = spawnSync(cmd, a, { encoding: 'utf8', env });
  return r;
}

function main() {
  const pr = projectRoot();
  log(`doctor: projectRoot=${pr}`);

  // 1) Core locations
  const cursorDir = path.join(pr, '.cursor');
  const rulesDir = path.join(cursorDir, 'rules');
  const codexDir = path.join(pr, '.codex');

  // 2) Check mode
  ensureMode(pr);

  // 3) Asset presence
  const baseRules = [
    '10-sdd-core.mdc',
    '11-ssot.mdc',
    '12-amr.mdc',
    '15-personas.mdc',
  ];
  let rulesOk = fs.existsSync(rulesDir);
  for (const f of baseRules) {
    const ok = checkFile(path.join(rulesDir, f), `.cursor/rules/${f}`);
    rulesOk = rulesOk && ok;
  }
  const codexOk = checkFile(path.join(codexDir, 'agents.md'), '.codex/agents.md');

  if (!rulesOk || !codexOk) {
    log('SUGGEST: run `super-prompt super:init` to materialize assets');
  }

  // 4) Verify MCP tool bridge responds
  const r = runMcp('sp.list_commands');
  if (r.status === 0) {
    log('MCP bridge: OK (sp.list_commands succeeded)');
  } else {
    log(`MCP bridge: FAIL (exit=${r.status})`);
    if (r.stderr) log(`stderr: ${r.stderr.trim()}`);
    log('SUGGEST: ensure Python v3.10+ available and reinstall package to recreate venv');
  }

  // 5) Memory write check (.super-prompt writable)
  try {
    const dataDir = path.join(pr, '.super-prompt');
    fs.mkdirSync(dataDir, { recursive: true });
    const probe = path.join(dataDir, 'doctor.probe');
    fs.writeFileSync(probe, String(Date.now()));
    fs.unlinkSync(probe);
    log('Memory dir: writable (.super-prompt)');
  } catch (e) {
    log(`Memory dir: NOT WRITABLE (${e.message})`);
  }

  // 6) Personas manifest reachable
  const localPersona = path.join(pr, 'personas', 'manifest.yaml');
  const pkgPersona = path.join(pkgRoot(), 'packages', 'cursor-assets', 'manifests', 'personas.yaml');
  if (fs.existsSync(localPersona)) {
    log('Personas manifest: project override present (personas/manifest.yaml)');
  } else if (fs.existsSync(pkgPersona)) {
    log('Personas manifest: using packaged defaults');
  } else {
    log('Personas manifest: MISSING');
  }

  // 7) Mode flags in .cursor (optional)
  if (fs.existsSync(path.join(cursorDir, '.codex-mode'))) log('Mode flag: .cursor/.codex-mode present');
  if (fs.existsSync(path.join(cursorDir, '.grok-mode'))) log('Mode flag: .cursor/.grok-mode present');

  log('doctor: done');
}

if (require.main === module) {
  main();
}

module.exports = { main };

