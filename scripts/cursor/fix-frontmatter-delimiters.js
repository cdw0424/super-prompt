#!/usr/bin/env node
/**
 * Ensure each command markdown has proper frontmatter delimiters:
 * Starts with '---' and includes a closing '---' before body content.
 * If the closing delimiter is missing, insert it right before the first '## ' header
 * or before the first non-frontmatter section line.
 */
const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const TARGET_DIRS = [
  path.join(ROOT, '.cursor', 'commands', 'super-prompt'),
  path.join(ROOT, 'packages', 'cursor-assets', 'commands', 'super-prompt'),
];

function* iterMarkdown(dir) {
  if (!fs.existsSync(dir)) return;
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) yield* iterMarkdown(full);
    else if (name.endsWith('.md')) yield full;
  }
}

function fixFile(p) {
  const original = fs.readFileSync(p, 'utf-8');
  if (!original.startsWith('---')) return false;
  // If closing delimiter exists, nothing to do
  if (original.indexOf('\n---', 3) !== -1) return false;

  // Find a safe insertion point: look for first markdown header (## or #) after frontmatter keys
  // Common marker in our commands: '## Execution Mode'
  const markerIdx = original.indexOf('\n## ');
  if (markerIdx !== -1) {
    const before = original.slice(0, markerIdx);
    const after = original.slice(markerIdx);
    const fixed = before + '\n---' + after;
    fs.writeFileSync(p, fixed);
    return true;
  }

  // Fallback: insert closing delimiter after an 'args:' block if present
  const argsIdx = original.indexOf('\nargs:');
  if (argsIdx !== -1) {
    // Insert after the args block lines (assume next line starting with non-space or end)
    const lines = original.split('\n');
    let i = 0;
    // skip starting '---'
    if (lines[i].trim() === '---') i++;
    // advance to args
    while (i < lines.length && !/^\s*args:\s*$/.test(lines[i])) i++;
    if (i < lines.length) {
      i++;
      while (i < lines.length && (/^\s{2}\S/.test(lines[i]) || /^\s*$/.test(lines[i]))) i++;
      lines.splice(i, 0, '---');
      fs.writeFileSync(p, lines.join('\n'));
      return true;
    }
  }

  return false;
}

let scanned = 0, changed = 0;
for (const dir of TARGET_DIRS) {
  for (const p of iterMarkdown(dir)) {
    scanned++;
    if (fixFile(p)) changed++;
  }
}

console.error(`-------- fix-frontmatter: scanned=${scanned} changed=${changed}`);

