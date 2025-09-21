// scripts/cursor/ensure-mcp-banner.js
// Scans super-prompt command markdown files and inserts a standardized MCP execution banner
// after the header args block if missing.

const fs = require('fs');
const path = require('path');

const TARGET_DIRS = [
  path.resolve(__dirname, '../../.cursor/commands/super-prompt'),
  path.resolve(__dirname, '../../packages/cursor-assets/commands/super-prompt'),
];

const BANNER_IDENTIFIER = '➡️ Execution: This command executes via MCP';
const BANNER_BLOCK = [
  '## Execution Mode',
  '',
  '➡️ Execution: This command executes via MCP (server: super-prompt; tool as defined above).',
  '',
].join('\n');

function listMarkdownFiles(dir) {
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith('.md') || f.endsWith('.md.disabled'))
    .map((f) => path.join(dir, f));
}

function findInsertIndex(lines) {
  // We attempt to insert after the header args block.
  // Heuristic:
  // - Start from top; expect header lines (description/run/server/tool/args)
  // - When we pass the first blank line after any of these header lines, insert there
  let seenHeader = false;
  let seenArgs = false;
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (/^description:\s*/.test(line) || /^run:\s*/.test(line) || /^server:\s*/.test(line) || /^tool:\s*/.test(line) || /^args:\s*/.test(line)) {
      seenHeader = true;
      if (/^args:\s*/.test(line)) {
        seenArgs = true;
      }
      continue;
    }
    if (seenHeader) {
      // Track the args block indentation; end when we hit a non-indented or blank line after args
      if (seenArgs) {
        const isIndented = /^\s{2,}\S/.test(line);
        const isBlank = /^\s*$/.test(line);
        if (!isIndented) {
          // We left the indented args block; insert before this line
          return i;
        }
        // continue within args block
      } else {
        const isBlank = /^\s*$/.test(line);
        if (isBlank) {
          // End of simple header; insert after this blank
          return i + 1;
        }
      }
    } else if (/^\s*$/.test(line) && i > 0) {
      // If we somehow didn't match header but reached a blank line soon, insert here
      return i + 1;
    }
  }
  // Fallback: append near top (after first 8 lines or end)
  return Math.min(lines.length, 8);
}

function ensureBanner(filePath) {
  const original = fs.readFileSync(filePath, 'utf8');
  if (original.includes(BANNER_IDENTIFIER)) {
    return { updated: false };
  }
  const lines = original.split(/\r?\n/);
  const insertAt = findInsertIndex(lines);
  const updated = [...lines.slice(0, insertAt), BANNER_BLOCK, ...lines.slice(insertAt)].join('\n');
  fs.writeFileSync(filePath, updated, 'utf8');
  return { updated: true };
}

function run() {
  let total = 0;
  let changed = 0;
  for (const dir of TARGET_DIRS) {
    if (!fs.existsSync(dir)) continue;
    const files = listMarkdownFiles(dir);
    for (const file of files) {
      // Skip non-super-prompt subdirs if any
      if (!file.endsWith('.md') && !file.endsWith('.md.disabled')) continue;
      total += 1;
      const res = ensureBanner(file);
      if (res.updated) changed += 1;
    }
  }
  console.log(`-------- ensure-mcp-banner: processed=${total} updated=${changed}`);
}

if (require.main === module) {
  run();
}
