#!/usr/bin/env node
/**
 * SSOT verifier
 * - Ensures personas are defined only in:
 *   packages/cursor-assets/manifests/personas.yaml (canonical) or personas/manifest.yaml (project override)
 * - Flags other files containing a top-level `personas:` key
 * - Validates .cursor/commands/* front matter (run: mcp, server: super-prompt)
 */
const fs = require('fs');
const path = require('path');

function listFiles(dir, exts, max=5000) {
  const out = [];
  function walk(d) {
    for (const name of fs.readdirSync(d, { withFileTypes: true })) {
      const p = path.join(d, name.name);
      if (name.isDirectory()) {
        if (name.name === 'node_modules' || name.name.startsWith('.git')) continue;
        walk(p);
        if (out.length > max) return;
      } else if (exts.some(e => name.name.endsWith(e))) {
        out.push(p);
      }
    }
  }
  walk(dir);
  return out;
}

function hasTopLevelPersonas(yamlText) {
  // naive check: start of line 'personas:' with no leading spaces
  return /^personas:\s*$/m.test(yamlText) || /^personas:\s*\n/m.test(yamlText);
}

function verifyPersonasSSOT(root) {
  const allowed = new Set([
    path.join(root, 'packages', 'cursor-assets', 'manifests', 'personas.yaml'),
    path.join(root, 'personas', 'manifest.yaml'),
  ].map(p=>path.normalize(p)));

  const yamlFiles = listFiles(root, ['.yaml', '.yml']);
  const offenders = [];
  for (const f of yamlFiles) {
    try {
      const text = fs.readFileSync(f, 'utf-8');
      if (hasTopLevelPersonas(text)) {
        const norm = path.normalize(f);
        if (!allowed.has(norm)) offenders.push(norm);
      }
    } catch {}
  }
  return offenders;
}

function verifyCursorCommands(root) {
  const dir = path.join(root, '.cursor', 'commands');
  if (!fs.existsSync(dir)) return [];
  const mdFiles = listFiles(dir, ['.md']);
  const errors = [];
  for (const f of mdFiles) {
    try {
      const t = fs.readFileSync(f, 'utf-8');
      if (!t.startsWith('---')) continue; // skip files without FM
      const end = t.indexOf('\n---');
      if (end === -1) continue;
      const fm = t.slice(3, end).split(/\r?\n/).map(s=>s.trim());
      const hasRun = fm.some(l=>/^run:\s*mcp$/.test(l));
      const hasServer = fm.some(l=>/^server:\s*super-prompt$/.test(l));
      if (!hasRun || !hasServer) errors.push(f);
    } catch {}
  }
  return errors;
}

function main() {
  const root = process.cwd();
  const offenders = verifyPersonasSSOT(root);
  const cmdErrors = verifyCursorCommands(root);

  if (offenders.length === 0 && cmdErrors.length === 0) {
    return;
  }

  console.error('-------- SSOT verify: FAILED');
  if (offenders.length) {
    console.error(' - Unexpected persona manifest(s):');
    offenders.forEach(f=>console.error('   •', path.relative(root,f)));
  }
  if (cmdErrors.length) {
    console.error(' - Command cards missing run: mcp or server: super-prompt:');
    cmdErrors.forEach(f=>console.error('   •', path.relative(root,f)));
  }
  process.exit(1);
}

if (require.main === module) main();

