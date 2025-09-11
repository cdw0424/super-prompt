const fs = require('fs').promises;
const path = require('path');
const { createBootstrap } = require('../prompts/codexAmrBootstrap.en');

/**
 * @typedef {{ targetDir?: string, overwrite?: boolean }} ScaffoldOpts
 */

const AGENTS_MD = `# AGENTS.md — Super-Prompt × Codex: Auto Model Router (medium ↔ high)
## Policy: Language & Logs
- Output language: English. Tone: precise, concise, production-oriented.
- All debug/console lines MUST start with \`--------\`.
## Router Rules (AMR)
- Start: gpt-5, reasoning=medium.
- L0/L1 stay medium. H → switch to high for PLAN/REVIEW, then back to medium for EXECUTION.
- To high: first line \`/model gpt-5 high\` → log \`--------router: switch to high (reason=deep_planning)\`
- Back to medium: first line \`/model gpt-5 medium\` → log \`--------router: back to medium (reason=execution)\`
- Failures/flaky/unclear → analyze at high, execute at medium.
- User override respected.
`;

const BIN_HIGH = `#!/usr/bin/env zsh
exec codex --model gpt-5 -c model_reasoning_effort="high" "$@"`;
const BIN_MED = `#!/usr/bin/env zsh
exec codex --model gpt-5 -c model_reasoning_effort="medium" "$@"`;

const ROUTER_CHECK = `#!/usr/bin/env zsh
set -euo pipefail
root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
AGENTS_PATH="$root/AGENTS.md"
if [ ! -f "$AGENTS_PATH" ]; then
  AGENTS_PATH="$root/.codex/AGENTS.md"
fi
missing=0
grep -q "Auto Model Router" "$AGENTS_PATH" || { echo "AGENTS.md missing AMR marker ($AGENTS_PATH)"; missing=1; }
grep -q "medium ↔ high" "$AGENTS_PATH" || { echo "AGENTS.md missing medium↔high ($AGENTS_PATH)"; missing=1; }
if [ "$missing" -ne 0 ]; then echo "--------router-check: FAIL"; exit 1; fi
echo "--------router-check: OK"`;

/**
 * Scaffold AMR assets into a target repository (idempotent).
 * @param {ScaffoldOpts} opts
 */
async function scaffoldCodexAmr(opts = {}) {
  const dir = path.resolve(opts.targetDir || '.');
  const files = [
    ['AGENTS.md', AGENTS_MD],
    ['prompts/codex_amr_bootstrap_prompt_en.txt', createBootstrap()],
    ['bin/codex-high', BIN_HIGH, 0o755],
    ['bin/codex-medium', BIN_MED, 0o755],
    ['scripts/codex/router-check.sh', ROUTER_CHECK, 0o755],
  ];
  for (const [rel, content, mode] of files) {
    const abs = path.join(dir, rel);
    await fs.mkdir(path.dirname(abs), { recursive: true });
    if (!opts.overwrite) {
      try { await fs.access(abs); continue; } catch {}
    }
    await fs.writeFile(abs, content, 'utf8');
    if (mode) await fs.chmod(abs, mode);
  }
  return true;
}

module.exports = { scaffoldCodexAmr };
