# AGENTS.md — Super-Prompt × Codex: Auto Model Router (medium ↔ high)

## Policy: Language & Logs
- Output language: English. Tone: precise, concise, production-oriented.
- All debug/console lines MUST start with `--------`.

## Router Rules (AMR)
- Start: gpt-5, reasoning=medium.
- L0/L1 stay medium. H → switch to high for PLAN/REVIEW, then back to medium for EXECUTION.
- To high: first line `/model gpt-5 high` → log `--------router: switch to high (reason=deep_planning)`
- Back to medium: first line `/model gpt-5 medium` → log `--------router: back to medium (reason=execution)`
- Failures/flaky/unclear → analyze at high, execute at medium.
- User override respected.

## Fixed State Machine (per turn)
- `[INTENT] → [TASK_CLASSIFY] → [PLAN] → [EXECUTE] → [VERIFY] → [REPORT]`
- H tasks: produce a short PLAN first (Goal, Plan, Risks, Test/Verify, Rollback) before EXECUTE.
- EXECUTE: minimal diffs only; include exact macOS zsh commands with `--------run:` prefix.
- VERIFY: show commands and a brief pass/fail summary (smallest failing snippet if any).

## Personas (Codex‑friendly flags)
- Use CLI flags (no slash commands in Codex):

### Simplified Syntax (--sp-* flags, recommended)
  - `super-prompt optimize --sp-frontend  "Design responsive layout"`
  - `super-prompt optimize --sp-frontend-ultra "Elite UX/UI architecture"`
  - `super-prompt optimize --sp-backend   "Retry + idempotency strategy"`
  - `super-prompt optimize --sp-analyzer  "Debug intermittent failures"`
  - `super-prompt optimize --sp-architect "Modular structure for feature X"`
  - `super-prompt optimize --sp-high      "Strategic architectural decision"`
  - `super-prompt optimize --sp-seq       "Sequential analysis (5 iterations)"`
  - `super-prompt optimize --sp-seq-ultra "Advanced sequential (10 iterations)"`
  - `super-prompt optimize --sp-performance "Bottleneck elimination & optimization"`
  - `super-prompt optimize --sp-security    "Threat modeling & vulnerability assessment"`
  - `super-prompt optimize --sp-task        "Task management & workflow execution"`
  - `super-prompt optimize --sp-wave        "Multi-stage execution orchestration"`
  - `super-prompt optimize --sp-ultracompressed "Token efficiency (30-50% reduction)"`
  - `super-prompt optimize --sp-debate --rounds 8 "Should we adopt feature flags?"`

### Original Syntax (still supported)
  - `super-prompt optimize --frontend`, `--backend`, `--analyzer`, `--architect`
  - `super-prompt optimize --high`, `--seq`, `--seq-ultra`, `--debate`
  - `super-prompt optimize --performance`, `--security`, `--task`, `--wave`, `--ultracompressed`

### Available Personas Summary
**All Personas**: frontend, frontend-ultra, backend, analyzer, architect, high, seq, seq-ultra, debate, performance, security, task, wave, ultracompressed
**Simplified Syntax**: Add `--sp-` prefix to any persona flag (recommended for cleaner commands)

## Python Utils Structure
- All Python utilities are organized in `.super-prompt/utils/`:
  - `.super-prompt/utils/cli.py` - Main CLI implementation
  - `.super-prompt/utils/personas.py` - Persona helpers for Codex
  - `.super-prompt/utils/cursor-processors/` - Cursor-specific processors
  - `.super-prompt/utils/templates/` - Template files

## SDD Workflow (Simplified Flag Syntax for Codex CLI)
- `super-prompt optimize --sp-sdd-spec "feature description"` - Create SPEC documents
- `super-prompt optimize --sp-sdd-plan "implementation approach"` - Create PLAN documents
- `super-prompt optimize --sp-sdd-tasks "break down implementation"` - Create TASKS documents
- `super-prompt optimize --sp-sdd-implement "start development" --validate` - Implementation guidance

### SDD Examples
```bash
# Complete SDD workflow with simplified syntax
super-prompt optimize --sp-sdd-spec "user authentication system"
super-prompt optimize --sp-sdd-plan "OAuth2 + JWT implementation"
super-prompt optimize --sp-sdd-tasks "break down auth tasks"
super-prompt optimize --sp-sdd-implement "start development" --validate
```

## Codex Tips
- File search: type `@` and select a path.
- Image input: `codex -i img.png "Explain this error"`
- Edit previous message: press Esc when composer is empty, then Esc again to backtrack.
- Shell completions: `codex completion bash|zsh|fish`
- Use `--cd`/`-C` to set Codex working root.

## Expectations
- Keep diffs minimal; avoid unrelated changes.
- Always provide verification commands and a short result summary.
- Prioritize clarity, reproducibility, and low noise.
