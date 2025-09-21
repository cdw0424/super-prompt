#!/usr/bin/env node
/**
 * Ensure all super-prompt commands include args: { query: "${input}", persona: "<persona>" }
 * Applies to both .cursor/commands and packages/cursor-assets/commands.
 */
const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const TARGET_DIRS = [
  path.join(ROOT, '.cursor', 'commands', 'super-prompt'),
  path.join(ROOT, 'packages', 'cursor-assets', 'commands', 'super-prompt'),
];

const MODE_TOOLS = new Set([
  'sp_gpt_mode_on','sp_grok_mode_on','sp_gpt_mode_off','sp_grok_mode_off',
  'sp_mode_get','sp_mode_set','sp_list_commands','sp_list_personas','sp.version'
]);

function readFile(p) { return fs.readFileSync(p, 'utf-8'); }
function writeFile(p, c) { fs.writeFileSync(p, c); }

function getFrontmatter(text) {
  if (!text.startsWith('---')) return null;
  const endIdx = text.indexOf('\n---', 3);
  if (endIdx === -1) return null;
  return { start: 0, end: endIdx + 4, body: text.slice(3, endIdx), rest: text.slice(endIdx + 4) };
}

function detectTool(frontmatter) {
  const m = frontmatter.match(/\n\s*tool:\s*(sp[._][A-Za-z0-9_-]+)\s*/);
  return m ? m[1].replace('sp.', 'sp_') : null;
}

function toolToPersona(tool) {
  if (!tool) return null;
  // normalize: strip sp_
  const key = tool.startsWith('sp_') ? tool.slice(3) : tool;
  // special mappings
  const map = {
    'db_expert': 'db-expert',
    'docs_refector': 'docs-refector',
    'service_planner': 'service-planner',
    'seq_ultra': 'seq-ultra',
  };
  if (map[key]) return map[key];
  return key; // default persona equals tool suffix
}

function ensureArgs(frontmatter, persona) {
  // If mode tool, skip
  const toolName = detectTool(frontmatter);
  if (MODE_TOOLS.has(toolName || '')) return { updated: false, fm: frontmatter };

  // Has args block?
  const hasArgs = /\n\s*args:\s*\n/.test(frontmatter);
  const hasQuery = /\n\s*query:\s*"\$\{input\}"\s*/.test(frontmatter);
  const hasPersona = /\n\s*persona:\s*"[A-Za-z0-9_-]+"\s*/.test(frontmatter);

  if (hasArgs && hasQuery && hasPersona) return { updated: false, fm: frontmatter };

  // Insert or repair args block after tool line
  const lines = frontmatter.split('\n');
  const idxTool = lines.findIndex(l => /\s*tool:\s*/.test(l));
  if (idxTool === -1) return { updated: false, fm: frontmatter };

  // Build args block with 2-space indent entries
  const argsBlock = ['args:', '  query: "${input}"', `  persona: "${persona}"`];

  // Remove any existing args header+immediate entries (simple heuristic: up to next non-indented or blank line)
  let i = idxTool + 1;
  if (i < lines.length && /^\s*args:\s*$/.test(lines[i])) {
    const start = i;
    i++;
    while (i < lines.length && (/^\s{2}\S/.test(lines[i]) || /^\s*$/.test(lines[i]))) i++;
    lines.splice(start, i - start, ...argsBlock);
  } else {
    lines.splice(idxTool + 1, 0, ...argsBlock);
  }

  return { updated: true, fm: lines.join('\n') };
}

function processFile(p) {
  const text = readFile(p);
  const fm = getFrontmatter(text);
  if (!fm) return { changed: false };
  const tool = detectTool(fm.body);
  const persona = toolToPersona(tool);
  if (!tool || !persona) return { changed: false };

  const { updated, fm: newFmBody } = ensureArgs(fm.body, persona);
  if (!updated) return { changed: false };

  const newText = '---' + newFmBody + '\n---' + fm.rest;
  writeFile(p, newText);
  return { changed: true };
}

function* iterMarkdown(dir) {
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) yield* iterMarkdown(full);
    else if (name.endsWith('.md')) yield full;
  }
}

let changed = 0, scanned = 0;
for (const dir of TARGET_DIRS) {
  if (!fs.existsSync(dir)) continue;
  for (const p of iterMarkdown(dir)) {
    scanned++;
    const res = processFile(p);
    if (res.changed) changed++;
  }
}

console.error(`-------- add-persona: scanned=${scanned} changed=${changed}`);

