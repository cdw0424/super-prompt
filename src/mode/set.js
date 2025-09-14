#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

function projectRoot() {
  return process.env.SUPER_PROMPT_PROJECT_ROOT || process.cwd();
}

function dataDir() {
  return path.join(projectRoot(), '.super-prompt');
}

function setMode(mode) {
  const m = String(mode || '').toLowerCase();
  if (m !== 'gpt' && m !== 'grok') {
    console.error('-------- mode: invalid (use gpt|grok)');
    process.exit(2);
  }
  const dir = dataDir();
  try { fs.mkdirSync(dir, { recursive: true }); } catch (_) {}
  const file = path.join(dir, 'mode.json');
  const payload = { llm_mode: m, updatedAt: new Date().toISOString() };
  fs.writeFileSync(file, JSON.stringify(payload, null, 2));
  console.error(`-------- mode: set to ${m}`);
}

if (require.main === module) {
  setMode(process.argv[2] || 'gpt');
}

module.exports = { setMode };

