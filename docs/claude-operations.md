# Claude Operations Playbook

This document explains how to operate Claude mode in Super Prompt, covering mode toggles, guardrails, repository layout, and evaluation workflow. Pair it with `docs/claude-persona-guide.md` for persona design details.

## Mode Management

- Enable with `/super-prompt/claude-mode-on` (or `sp.claude_mode_on`). Disables GPT/Grok guidance automatically.
- Disable with `/super-prompt/claude-mode-off` to fall back to default GPT planning.
- Check status via `/super-prompt/mode_get`.
- High reasoning remains opt-in: `/super-prompt/high` forces Codex plans; `/super-prompt/high-mode-on` delegates to Codex automatically.

## Prompt Architecture Checklist

1. **Capture meta** — version, owner, evaluations, guardrails.
2. **System role** — persona identity, safety policy, XML schema.
3. **Developer instructions** — tool limits, file hygiene, parallelization guidelines.
4. **Context tags** — inject references via `<context>`, `<data>`, `<examples>`.
5. **User task** — instructions, success criteria, constraints, and tone.
6. **Evaluation layer** — tests, rubrics, auto scoring.

## Safety & Hallucination Controls

- Always allow “I don’t know” and cite sources for numeric or policy claims.
- Require post-answer verification or TODO lists for missing evidence.
- Mask secrets (`sk-***`) and refuse regulatory or legal advice unless provided.
- Keep persona tone (mission, audience, non-goals) consistent across turns.

## Language Alignment

- Replies mirror the user’s most recent language automatically (see `packages/cursor-assets/rules/22-language.mdc`).
- Internal policies, system prompts, and rule files stay in English for SSOT consistency.

## Repository Structure

```
/prompts
  /personas/*.yml         # Persona specs with Claude model overrides
  /system/system.template # System prompt skeleton
  /user/user.template     # User prompt skeleton
  /examples/{good,bad}.md  # Few-shot samples
/docs
  claude-persona-guide.md
  claude-operations.md
/evals
  cases.csv
  rubric.md
  run_eval.py
/guardrails
  hallucination.md
  character.md
```

## Evaluation Workflow

1. Draft eval cases (`/evals/cases.csv`) with expected schema keys.
2. Run `python evals/run_eval.py` to compare outputs against rubric.
3. Track pass/fail and persona drift in `evals/rubric.md`.
4. Gate releases on eval checks when modifying personas or mode rules.

## Debugging 80/20

- **Messy format?** Confirm container tag and child schema in system prompt.
- **Tone drift?** Reinforce mission/tone in `<persona>` section and add example responses.
- **Hallucinations?** Ensure refs to policies/data are present, plus verification checklist.
- **Latency?** Use `<tool_use>` instructions for parallel tool calls and cleanup.
- **Overly long answers?** Set explicit token or section-length constraints.

## Change Control

- Version persona specs (YAML) and reference IDs in commit messages.
- Record changes in `CHANGELOG.md` and update `meta.updated` timestamps.
- Roll back by toggling modes (`*_mode_off`) and re-installing previous prompt assets.
- Keep Claude, GPT, and Grok guidance files mutually exclusive under `.cursor/rules/`.

## References

- Anthropic Prompting Tutorial & Cookbook.[5]
- Claude system prompt guide (role, guardrails).[1]
- Hallucination mitigation strategies.[2]
- XML tagging best practices.[3]
- Prompt construction best practices.[4]
- Persona stay-in-character recommendations.[7]

[1]: https://docs.anthropic.com/claude/docs/system-prompts
[2]: https://docs.anthropic.com/claude/docs/reduce-hallucinations
[3]: https://docs.anthropic.com/claude/docs/use-xml-tags
[4]: https://docs.anthropic.com/claude/docs/constructing-effective-prompts
[5]: https://github.com/anthropics/anthropic-cookbook/tree/main/prompting-with-claude
[7]: https://docs.anthropic.com/claude/docs/maintain-character
