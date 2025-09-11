#!/usr/bin/env node
/* Thin CLI entry for Codex AMR scaffold and bootstrap printing. */
const path = require('path');

async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];

  if (!cmd || cmd === '--help' || cmd === '-h') {
    console.log('Usage: codex-amr <init|print-bootstrap> [--target DIR] [--overwrite]');
    process.exit(0);
  }

  if (cmd === 'init') {
    const overwrite = args.includes('--overwrite');
    const tIdx = Math.max(args.indexOf('--target'), args.indexOf('-C'));
    const targetDir = tIdx >= 0 && args[tIdx + 1] ? args[tIdx + 1] : '.';
    const { scaffoldCodexAmr } = require('../src/scaffold/codexAmr');
    try {
      await scaffoldCodexAmr({ targetDir, overwrite });
      console.log('--------codex-amr: scaffold complete →', path.resolve(targetDir));
    } catch (e) {
      console.error('--------error:', (e && e.message) || String(e));
      process.exit(1);
    }
    return;
  }

  if (cmd === 'print-bootstrap') {
    const { createBootstrap } = require('../src/prompts/codexAmrBootstrap.en');
    process.stdout.write(createBootstrap());
    return;
  }

  console.log('Usage: codex-amr <init|print-bootstrap> [--target DIR] [--overwrite]');
}

main();

