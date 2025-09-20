#!/usr/bin/env node
/**
 * Verify that all project Cursor commands call MCP correctly.
 * Checks frontmatter for: run: mcp, server: super-prompt, tool: sp.*
 */
const fs = require('fs');
const path = require('path');

function readFrontmatter(p) {
  const text = fs.readFileSync(p, 'utf-8');
  if (!text.startsWith('---')) return null;
  const end = text.indexOf('\n---', 3);
  if (end === -1) return null;
  const fm = text.slice(3, end).trim();
  return fm.split('\n').map(s => s.trim());
}

function verify() {
  const root = process.cwd();
  const dir = path.join(root, '.cursor', 'commands');
  const files = fs.existsSync(dir) ? fs.readdirSync(dir).filter(f => f.endsWith('.md')) : [];
  let ok = true;
  const problems = [];
  for (const name of files) {
    const p = path.join(dir, name);
    const lines = readFrontmatter(p);
    if (!lines) { problems.push({file: name, reason: 'missing frontmatter'}); ok = false; continue; }
    const hasRun = lines.some(l => /^run:\s*mcp$/.test(l));
    const hasServer = lines.some(l => /^server:\s*super-prompt$/.test(l));
    const hasTool = lines.some(l => /^tool:\s*sp\.[A-Za-z0-9_-]+$/.test(l));
    if (!(hasRun && hasServer && hasTool)) {
      const miss = [];
      if (!hasRun) miss.push('run:mcp');
      if (!hasServer) miss.push('server:super-prompt');
      if (!hasTool) miss.push('tool:sp.*');
      problems.push({file: name, reason: 'missing keys', missing: miss});
      ok = false;
    }
  }

  if (!ok) {
    console.error('-------- verify-commands: FAILED');
    for (const p of problems) {
      console.error(` - ${p.file}: ${p.reason}${p.missing ? ' ('+p.missing.join(', ')+')' : ''}`);
    }
    process.exit(1);
  } else {
    console.log('-------- verify-commands: OK (all commands use MCP correctly)');
  }
}

verify();

