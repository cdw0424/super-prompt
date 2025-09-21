#!/usr/bin/env node
// scripts/cursor/fix-asset-frontmatter.js
// Ensures each packaged command asset has a properly closed frontmatter block

const fs = require('fs');
const path = require('path');

function* iterFiles(dir) {
  for (const name of fs.readdirSync(dir)) {
    if (!name.endsWith('.md')) continue;
    yield path.join(dir, name);
  }
}

function hasClosedFrontmatter(text) {
  if (!text.startsWith('---')) return false;
  const end = text.indexOf('\n---', 3);
  return end !== -1;
}

function ensureClosedFrontmatter(file) {
  const text = fs.readFileSync(file, 'utf-8');
  if (hasClosedFrontmatter(text)) return false;

  // Try to find the header section end by detecting the first line that doesn't look like key: value
  const lines = text.split(/\r?\n/);
  let endIdx = -1;
  for (let i = 1; i < Math.min(lines.length, 100); i += 1) {
    const line = lines[i];
    if (/^\s*$/.test(line)) { // blank after header
      endIdx = i;
      break;
    }
    if (!/^([A-Za-z0-9_.-]+):/.test(line)) { // first non key: value
      endIdx = i;
      break;
    }
  }
  if (endIdx === -1) endIdx = Math.min(lines.length, 100);

  const front = lines.slice(0, endIdx).join('\n');
  const body = lines.slice(endIdx).join('\n');
  const fixed = `${front}\n---\n${body}`;
  fs.writeFileSync(file, fixed, 'utf-8');
  return true;
}

function run() {
  const root = process.cwd();
  const dir = path.join(root, 'packages', 'cursor-assets', 'commands', 'super-prompt');
  if (!fs.existsSync(dir)) {
    console.error('-------- fix-asset-frontmatter: directory missing');
    process.exit(2);
  }
  let total = 0;
  let fixed = 0;
  for (const file of iterFiles(dir)) {
    total += 1;
    if (ensureClosedFrontmatter(file)) fixed += 1;
  }
  console.log(`-------- fix-asset-frontmatter: processed=${total} fixed=${fixed}`);
}

if (require.main === module) run();
