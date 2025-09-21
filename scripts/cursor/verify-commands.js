#!/usr/bin/env node
/**
 * Verify that all project Cursor commands call MCP correctly.
 * Checks frontmatter for: run: mcp, server: super-prompt, tool: sp_<name> or sp.<name>
 * Also validates persona commands include args: query + persona, while allowing mode tools without args.
 */
const fs = require('fs');
const path = require('path');

function readFrontmatter(p) {
  const text = fs.readFileSync(p, 'utf-8');
  if (!text.startsWith('---')) return null;
  const end = text.indexOf('\n---', 3);
  if (end === -1) return null;
  const fm = text.slice(3, end); // preserve indentation for reliable matching
  return fm.split('\n');
}

function* iterMarkdown(dir) {
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      yield* iterMarkdown(full);
    } else if (name.endsWith('.md')) {
      yield full;
    }
  }
}

function verify() {
  const root = process.cwd();
  const dirs = [
    path.join(root, '.cursor', 'commands', 'super-prompt'),
    path.join(root, 'packages', 'cursor-assets', 'commands', 'super-prompt'),
  ];
  for (const d of dirs) {
    if (!fs.existsSync(d)) {
      console.error('-------- verify-commands: directory missing:', d);
      process.exit(2);
    }
  }
  let ok = true;
  const problems = [];
  const MODE_TOOL_SET = new Set([
    'sp_gpt_mode_on','sp_grok_mode_on','sp_gpt_mode_off','sp_grok_mode_off',
    'sp_mode_get','sp_mode_set','sp_list_commands','sp_list_personas','sp.version'
  ]);

  for (const dir of dirs) {
    for (const p of iterMarkdown(dir)) {
      const rel = path.relative(root, p);
      const lines = readFrontmatter(p);
      if (!lines) { problems.push({file: rel, reason: 'missing frontmatter'}); ok = false; continue; }
      const hasRun = lines.some(l => /^\s*run:\s*mcp\s*$/.test(l));
      const hasServer = lines.some(l => /^\s*server:\s*super-prompt\s*$/.test(l));
      const toolLine = lines.find(l => /^\s*tool:\s*/.test(l));
      const hasTool = !!toolLine;
      const toolOk = hasTool && /^(\s*tool:\s*)(sp[._][A-Za-z0-9_-]+)\s*$/.test(toolLine);

      let argsOk = true;
      if (toolOk) {
        const m = toolLine.match(/^(\s*tool:\s*)(sp[._][A-Za-z0-9_-]+)\s*$/);
        const toolName = m && m[2].replace('sp.', 'sp_');
        if (toolName && !MODE_TOOL_SET.has(toolName)) {
          const hasArgsHeader = lines.some(l => /^\s*args:\s*$/.test(l));
          const hasQueryArg = lines.some(l => /^\s*query:\s*"\$\{input\}"\s*$/.test(l));
          const hasPersonaArg = lines.some(l => /^\s*persona:\s*"[A-Za-z0-9_-]+"\s*$/.test(l));
          argsOk = hasArgsHeader && hasQueryArg && hasPersonaArg;
        }
      }

      if (!(hasRun && hasServer && toolOk && argsOk)) {
        const miss = [];
        if (!hasRun) miss.push('run:mcp');
        if (!hasServer) miss.push('server:super-prompt');
        if (!toolOk) miss.push('tool:sp_<name> or sp.<name>');
        if (!argsOk) miss.push('args:{ query:"${input}", persona:"<persona>" }');
        problems.push({file: rel, reason: 'missing keys', missing: miss});
        ok = false;
      }
    }
  }

  if (!ok) {
    console.error('-------- verify-commands: FAILED');
    for (const p of problems) {
      console.error(` - ${p.file}: ${p.reason}${p.missing ? ' ('+p.missing.join(', ')+')' : ''}`);
    }
    process.exit(1);
  } else {
    console.error('-------- verify-commands: OK (all commands use MCP correctly)');
  }
}

verify();

