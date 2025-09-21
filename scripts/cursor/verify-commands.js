#!/usr/bin/env node
/**
 * Verify that all project Cursor commands call MCP correctly.
 * Checks frontmatter for: run: mcp, server: super-prompt, tool: sp_<name> or sp.<name>
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

function* iterMarkdown(dir) {
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      yield* iterMarkdown(full);
    } else if (name.endsWith('.md')) {
      yield full;
    }
  }
}

function verify() {
  const root = process.cwd();
  const dir = path.join(root, '.cursor', 'commands');
  if (!fs.existsSync(dir)) {
    console.error('-------- verify-commands: directory missing:', dir);
    process.exit(2);
  }
  let ok = true;
  const problems = [];
  for (const p of iterMarkdown(dir)) {
    const lines = readFrontmatter(p);
    if (!lines) { problems.push({file: path.relative(root, p), reason: 'missing frontmatter'}); ok = false; continue; }
    const hasRun = lines.some(l => /^run:\s*mcp$/.test(l));
    const hasServer = lines.some(l => /^server:\s*super-prompt$/.test(l));
    const toolLine = lines.find(l => /^tool:\s*/.test(l));
    const hasTool = !!toolLine;
    const toolOk = hasTool && /^(tool:\s*)(sp[._][A-Za-z0-9_-]+)$/.test(toolLine);
    if (!(hasRun && hasServer && toolOk)) {
      const miss = [];
      if (!hasRun) miss.push('run:mcp');
      if (!hasServer) miss.push('server:super-prompt');
      if (!toolOk) miss.push('tool:sp_<name> or sp.<name>');
      problems.push({file: path.relative(root, p), reason: 'missing keys', missing: miss});
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
    console.error('-------- verify-commands: OK (all commands use MCP correctly)');
  }
}

verify();

