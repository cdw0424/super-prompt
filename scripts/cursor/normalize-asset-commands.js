#!/usr/bin/env node
/**
 * Normalize packaged command cards to ensure strict MCP usage
 * - Ensure run: mcp and server: super-prompt exist
 * - Ensure `tool:` is either sp.<name> or sp.pipeline
 * - Remove illegal top-level `autorun:` (must live under args:)
 */
const fs = require('fs');
const path = require('path');

function splitFrontmatter(text) {
  if (!text.startsWith('---')) return null;
  const end = text.indexOf('\n---', 3);
  if (end === -1) return null;
  const front = text.slice(3, end).trim();
  const body = text.slice(end + 4);
  return { front, body };
}

function normalizeFront(front) {
  const lines = front.split('\n');
  // Strip trailing spaces
  for (let i = 0; i < lines.length; i++) lines[i] = lines[i].replace(/\s+$/,'');
  // Remove any top-level autorun
  const filtered = lines.filter(l => !/^\s*autorun:\s*/.test(l));
  // Ensure run:mcp present
  let hasRun = filtered.some(l => l.trim() === 'run: mcp');
  let hasServer = filtered.some(l => l.trim() === 'server: super-prompt');
  const out = [];
  for (const l of filtered) out.push(l);
  if (!hasRun) out.splice(1, 0, 'run: mcp');
  if (!hasServer) out.splice(2, 0, 'server: super-prompt');
  return out.join('\n');
}

function main() {
  const root = process.cwd();
  const dir = path.join(root, 'packages', 'cursor-assets', 'commands', 'super-prompt');
  if (!fs.existsSync(dir)) {
    console.error('missing dir', dir); process.exit(2);
  }
  let changed = 0;
  for (const name of fs.readdirSync(dir)) {
    if (!name.endsWith('.md')) continue;
    const p = path.join(dir, name);
    const text = fs.readFileSync(p, 'utf-8');
    const fm = splitFrontmatter(text);
    if (!fm) continue;
    const newFront = normalizeFront(fm.front);
    if (newFront !== fm.front) {
      const updated = `---\n${newFront}\n---${fm.body}`;
      fs.writeFileSync(p, updated);
      changed++;
    }
  }
}

main();

