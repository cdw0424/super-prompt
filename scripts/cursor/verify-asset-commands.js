#!/usr/bin/env node
/**
 * Verify packaged Cursor command assets under packages/cursor-assets/commands/super-prompt
 * Ensures frontmatter has: run: mcp, server: super-prompt, tool: sp.* (or sp.pipeline)
 * Also flags illegal top-level `autorun:` keys (must be inside args:)
 */
const fs = require('fs');
const path = require('path');

function* iterFiles(dir) {
  for (const name of fs.readdirSync(dir)) {
    if (!name.endsWith('.md')) continue;
    yield path.join(dir, name);
  }
}

function splitFrontmatter(text) {
  if (!text.startsWith('---')) return null;
  const end = text.indexOf('\n---', 3);
  if (end === -1) return null;
  const front = text.slice(3, end).trim();
  const body = text.slice(end + 4);
  return { front, body };
}

function main() {
  const root = process.cwd();
  const dir = path.join(root, 'packages', 'cursor-assets', 'commands', 'super-prompt');
  if (!fs.existsSync(dir)) {
    console.error('-------- verify-asset-commands: directory missing:', dir);
    process.exit(2);
  }
  let ok = true;
  const issues = [];
  for (const file of iterFiles(dir)) {
    const text = fs.readFileSync(file, 'utf-8');
    const fm = splitFrontmatter(text);
    if (!fm) { issues.push({file, msg:'missing frontmatter'}); ok=false; continue; }
    const lines = fm.front.split('\n').map(s => s.trimEnd());
    const hasRun = lines.some(l => l.trim() === 'run: mcp');
    const hasServer = lines.some(l => l.trim() === 'server: super-prompt');
    const toolLine = lines.find(l => l.trim().startsWith('tool: '));
    const hasTool = !!toolLine;
    const hasValidTool = hasTool && (/^tool:\s+sp\.[A-Za-z0-9_-]+$/.test(toolLine.trim()) || /^tool:\s+sp\.pipeline$/.test(toolLine.trim()));

    // illegal top-level autorun (must be nested under args:)
    const topLevelAutorun = lines.some(l => /^autorun:\s*/.test(l.trim()));

    if (!(hasRun && hasServer && hasValidTool) || topLevelAutorun) {
      ok = false;
      const miss = [];
      if (!hasRun) miss.push('run:mcp');
      if (!hasServer) miss.push('server:super-prompt');
      if (!hasValidTool) miss.push('tool:sp.* or sp.pipeline');
      if (topLevelAutorun) miss.push('top-level autorun (must be under args)');
      issues.push({file, msg: 'invalid frontmatter', details: miss});
    }
  }

  if (!ok) {
    console.error('-------- verify-asset-commands: FAILED');
    for (const i of issues) {
      console.error(' -', path.relative(root, i.file), '=>', i.msg, i.details ? `(${i.details.join(', ')})` : '');
    }
    process.exit(1);
  }
  console.log('-------- verify-asset-commands: OK');
}

main();

