#!/usr/bin/env node
// scripts/cursor/strip-inline-scripts.js
// Removes top-level `script:` blocks from packaged super-prompt command assets

const fs = require('fs');
const path = require('path');

function* iterFiles(dir) {
  for (const name of fs.readdirSync(dir)) {
    if (!name.endsWith('.md')) continue;
    yield path.join(dir, name);
  }
}

function stripScriptBlock(text) {
  // Only strip top-level `script:` blocks, not code fences
  // Strategy: find a line that starts with `script:` optionally followed by `|` or nothing,
  // then remove until the next unindented frontmatter/body section marker or blank line sequence.
  const lines = text.split(/\r?\n/);
  let start = -1;
  for (let i = 0; i < lines.length; i += 1) {
    if (/^script:\s*(\|.*)?\s*$/.test(lines[i])) { start = i; break; }
  }
  if (start === -1) return { changed: false, text };

  // Determine indentation level for the block (usually 2 spaces for YAML literal)
  // We remove from the script: line through all subsequent indented lines until a line
  // that is blank or not more indented than column 0 and not part of YAML block.
  let end = start + 1;
  while (end < lines.length) {
    const line = lines[end];
    // Stop when two conditions: a YAML key appears at column 0 (e.g., /^(\w|#|---)/) OR we hit a markdown section marker like /^## / OR frontmatter delimiter
    if (/^(description:|run:|server:|tool:|args:|---|##\s|#\s|\S)/.test(line) && !/^\s/.test(line)) {
      break;
    }
    // Continue if line is indented or blank (YAML block or continuation)
    if (/^\s/.test(line) || /^\s*$/.test(line)) {
      end += 1;
      continue;
    }
    end += 1;
  }

  const newLines = [...lines.slice(0, start), ...lines.slice(end)];
  return { changed: true, text: newLines.join('\n') };
}

function run() {
  const root = process.cwd();
  const dir = path.join(root, 'packages', 'cursor-assets', 'commands', 'super-prompt');
  if (!fs.existsSync(dir)) {
    console.error('-------- strip-inline-scripts: directory missing:', dir);
    process.exit(2);
  }
  let total = 0;
  let changed = 0;
  for (const file of iterFiles(dir)) {
    const orig = fs.readFileSync(file, 'utf-8');
    const { changed: didChange, text } = stripScriptBlock(orig);
    total += 1;
    if (didChange) {
      fs.writeFileSync(file, text, 'utf-8');
      changed += 1;
    }
  }
  console.log(`-------- strip-inline-scripts: processed=${total} changed=${changed}`);
}

if (require.main === module) run();
