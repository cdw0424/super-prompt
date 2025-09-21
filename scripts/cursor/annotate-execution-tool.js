#!/usr/bin/env node
/**
 * Annotate the Execution line with the mapped MCP tool name.
 * Example:
 *   Before: ➡️ Execution: This command executes via MCP (server: super-prompt; tool as defined above).
 *   After:  ➡️ Execution: sp_high MCP (server: super-prompt; tool as defined above).
 *
 * Applies to both .cursor commands and packaged assets.
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

function parseTool(text) {
  if (!text.startsWith('---')) return null;
  const end = text.indexOf('\n---', 3);
  if (end === -1) return null;
  const fm = text.slice(3, end);
  const m = fm.match(/\n\s*tool:\s*([\w\.-]+)\s*/);
  return m ? m[1] : null;
}

function annotateExecution(text, toolName) {
  // Replace the first occurrence of the Execution line to include tool name
  const pattern = /(➡️ Execution:\s*)(?:This command executes via MCP|.*?)\s*\(server:\s*super-prompt;\s*tool as defined above\)\./;
  const replacement = `$1${toolName} MCP (server: super-prompt; tool as defined above).`;
  if (pattern.test(text)) {
    return text.replace(pattern, replacement);
  }
  return null;
}

let scanned = 0, changed = 0;
for (const dir of TARGET_DIRS) {
  for (const p of iterMarkdown(dir)) {
    scanned++;
    const text = fs.readFileSync(p, 'utf-8');
    const tool = parseTool(text);
    if (!tool) continue;
    const updated = annotateExecution(text, tool);
    if (updated && updated !== text) {
      fs.writeFileSync(p, updated);
      changed++;
    }
  }
}

console.error(`-------- annotate-exec: scanned=${scanned} changed=${changed}`);

