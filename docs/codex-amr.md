# Codex AMR (medium ↔ high)

## What’s included
- AMR router helpers: `src/amr/router.js`
- State machine helpers: `src/state-machine/index.js`
- Bootstrap prompt factory: `src/prompts/codexAmrBootstrap.en.js`
- Scaffold utility: `src/scaffold/codexAmr.js`
- Thin CLI: `codex-amr` (also routed via `super-prompt codex-amr`)

## Usage
- Print the bootstrap prompt (paste in Codex TUI):
```bash
npx codex-amr print-bootstrap
```
- Scaffold AMR assets into a repo:
```bash
npx codex-amr init --target .
# writes: AGENTS.md, prompts/codex_amr_bootstrap_prompt_en.txt,
#         bin/codex-high, bin/codex-medium, scripts/codex/router-check.sh
```
- Programmatic scaffold:
```js
const { scaffoldCodexAmr } = require('@cdw0424/super-prompt/src/scaffold/codexAmr');
await scaffoldCodexAmr({ targetDir: '.', overwrite: false });
```

## Tests
```bash
npm test    # runs node --test for AMR router
```

## Router switch (manual, if environment doesn’t auto-execute)
```
/model gpt-5 high
/model gpt-5 medium
```
