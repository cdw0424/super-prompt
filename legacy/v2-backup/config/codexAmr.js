// Lightweight config loader for AMR; no heavy deps
const fs = require('fs');

function loadPackageJSON(cwd = process.cwd()) {
  try {
    const p = require('path').join(cwd, 'package.json');
    if (fs.existsSync(p)) return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (_) {}
  return {};
}

function loadAmrConfig(cwd = process.cwd()) {
  const pkg = loadPackageJSON(cwd) || {};
  const cfg = (pkg.superPrompt && pkg.superPrompt.router) || {};
  const def = { defaultLevel: 'medium', enableRouter: true };
  return { ...def, ...cfg };
}

module.exports = { loadAmrConfig };

