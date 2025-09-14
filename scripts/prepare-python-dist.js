#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

function copyLatestWheel() {
  const src = path.join(__dirname, '..', 'packages', 'core-py', 'dist');
  const dst = path.join(__dirname, '..', 'dist');
  if (!fs.existsSync(src)) {
    console.log('No packages/core-py/dist found; skipping wheel copy');
    return;
  }
  const wheels = fs.readdirSync(src).filter(f => f.endsWith('.whl') && f.startsWith('super_prompt_core-'));
  if (wheels.length === 0) {
    console.log('No core-py wheel found; skipping wheel copy');
    return;
  }
  wheels.sort((a, b) => b.localeCompare(a, undefined, { numeric: true }));
  const latest = wheels[0];
  if (!fs.existsSync(dst)) fs.mkdirSync(dst, { recursive: true });
  fs.copyFileSync(path.join(src, latest), path.join(dst, latest));
  console.log(`Copied wheel to dist/: ${latest}`);
}

copyLatestWheel();
