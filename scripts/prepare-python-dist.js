#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

function copyLatestWheel() {
  const src = path.join(__dirname, '..', 'packages', 'core-py', 'dist');
  const dst = path.join(__dirname, '..', 'dist');

  // Clean up existing dist directory first
  if (fs.existsSync(dst)) {
    console.log('Cleaning up existing dist directory...');
    fs.rmSync(dst, { recursive: true, force: true });
  }

  if (!fs.existsSync(src)) {
    console.log('No packages/core-py/dist found; skipping wheel copy');
    return;
  }

  const wheels = fs.readdirSync(src).filter(f => f.endsWith('.whl') && f.startsWith('super_prompt_core-'));
  if (wheels.length === 0) {
    console.log('No core-py wheel found; skipping wheel copy');
    return;
  }

  // Sort by version (newest first)
  wheels.sort((a, b) => b.localeCompare(a, undefined, { numeric: true }));
  const latest = wheels[0];

  // Create fresh dist directory
  fs.mkdirSync(dst, { recursive: true });

  // Copy only the latest wheel
  fs.copyFileSync(path.join(src, latest), path.join(dst, latest));
  console.log(`Copied latest wheel to dist/: ${latest}`);

  // Optional: Also copy the latest tar.gz if it exists
  const tars = fs.readdirSync(src).filter(f => f.endsWith('.tar.gz') && f.startsWith('super_prompt_core-'));
  if (tars.length > 0) {
    tars.sort((a, b) => b.localeCompare(a, undefined, { numeric: true }));
    const latestTar = tars[0];
    fs.copyFileSync(path.join(src, latestTar), path.join(dst, latestTar));
    console.log(`Copied latest tar.gz to dist/: ${latestTar}`);
  }
}

copyLatestWheel();
