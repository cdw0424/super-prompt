#!/usr/bin/env node
// scripts/cursor/sync-commands-from-assets.js
// Copies packaged super-prompt command assets into .cursor/commands/super-prompt

const fs = require('fs');
const path = require('path');

function ensureDir(p) {
  if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
}

function run() {
  const root = process.cwd();
  const srcDir = path.join(root, 'packages', 'cursor-assets', 'commands', 'super-prompt');
  const dstDir = path.join(root, '.cursor', 'commands', 'super-prompt');
  if (!fs.existsSync(srcDir)) {
    console.error('-------- sync-commands: missing source dir', srcDir);
    process.exit(2);
  }
  ensureDir(dstDir);
  let copied = 0;
  for (const name of fs.readdirSync(srcDir)) {
    if (!name.endsWith('.md')) continue;
    const src = path.join(srcDir, name);
    const dst = path.join(dstDir, name);
    fs.copyFileSync(src, dst);
    copied += 1;
  }
  console.log(`-------- sync-commands: copied ${copied} files`);
}

if (require.main === module) run();
