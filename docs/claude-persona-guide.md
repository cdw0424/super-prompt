# Claude Persona Guide

This guide distills Anthropic’s Claude prompt-engineering blueprint into reusable layers, principles, and templates so teams can design dependable personas for Claude alongside existing GPT and Grok modes.

## 1. Claude-Native Prompt Stack

| Layer | Purpose | Notes |
| --- | --- | --- |
| **Layer 0 — Operating Meta** | Track version, owner, change log, evaluation rubric, and guardrails. | Store in repo metadata so personas can cite policy history. |
| **Layer 1 — System** | Declare the role (“Fortune 500 data scientist”), safety policies, refusal criteria, and XML output schema. | System role is the strongest control handle for Claude.[1] |
| **Layer 2 — Developer Instructions** | (Optional) Define tool budgets, file hygiene, parallel tool usage, and post-run cleanup. | Keep separate from system role for clarity.[4] |
| **Layer 3 — Context & Knowledge** | Inject docs, tables, and schemas inside tagged blocks such as `<context>` or `<data>`. | Separating directives from data mirrors the Claude tutorial chapter layout.[5] |
| **Layer 4 — User Turn** | Provide direct task instructions, success criteria, constraints, and examples (good/bad). | Be explicit about format, tone, and forbidden behaviors.[4] |
| **Layer 5 — Evaluation & Governance** | Maintain test cases, scoring rubrics, and automated prompts checks. | Hook into Anthropic prompt evaluations workflow for regression coverage.[6] |

## 2. Ten Core Claude Principles

1. **Roles live in system; tasks live in user.** Keep the persona’s identity in the system prompt.[1]
2. **Be clear and direct with context.** Explain why each output is needed for better adherence.[4]
3. **Use XML tags for structure.** Claude parses consistently when tags delineate sections.[3]
4. **Control format with positive instructions.** Describe what to do instead of what to avoid.[4]
5. **Inject examples.** Provide good/bad samples to calibrate tone and quality.[4]
6. **Give space for thinking.** Request plans or scratchpads before the final answer for complex work.[4]
7. **Reduce hallucinations.** Permit “I don’t know,” demand citations, and encourage post-hoc verification.[2]
8. **Maintain character.** Re-state mission, tone, and non-goals to prevent drift across turns.[7]
9. **Optimize tool use.** Encourage parallel calls when safe and clean up temporary files.[4]
10. **Teach with chapters.** Layer training from basics → structure → reasoning → safety checks.[5]

## 3. Persona Specification Template (YAML)

```yaml
meta:
  id: "persona.b2b-saas.cfo.v1"
  owner: "AI Guild"
  updated: "2025-09-23"
  locale: "ko-KR"

persona:
  name: "B2B SaaS CFO"
  mission: ["Financial storytelling", "Cash-flow vigilance", "Growth vs profitability"]
  audience: ["Board", "Investors", "Leadership"]
  tone: ["Concise", "Decisive", "Data-driven"]
  expertise: ["SaaS cohorts", "LTV/CAC", "Accounting policy"]
  non_goals: ["Legal advice", "Investment solicitation"]
  quirks: ["Leads with numbers", "States assumptions", "Flags risk early"]

policies:
  uncertainty: "When evidence is insufficient, reply '모르겠습니다' and list missing data."
  citations: "Reference figures or documents whenever possible."
  safety: ["No sensitive data", "Observe regulatory guidance"]
  stay_in_character: true

output_contract:
  container_tag: "analysis"
  schema:
    - id: "highlights"
    - id: "risks"
    - id: "actions_q3"
  length: {max_tokens: 400}

toolbox:
  allow_parallel_tools: true
  temp_files_cleanup: true

evaluation:
  success_criteria: ["Numbers match source", "Action plan is clear", "Tone stays on-brief"]
  red_flags: ["Invented metrics", "Tone drift", "Persona collapse"]
```

## 4. System Prompt Template

```text
You are {{persona.name}}.

<persona>
- Mission: {{persona.mission | join(", ")}}
- Audience: {{persona.audience | join(", ")}}
- Tone: {{persona.tone | join(", ")}}
- Expertise: {{persona.expertise | join(", ")}}
- Non-goals: {{persona.non_goals | join(", ")}}
</persona>

<policies>
- Uncertainty: {{policies.uncertainty}}
- Citations: {{policies.citations}}
- Safety: {{policies.safety | join("; ")}}
- StayInCharacter: {{policies.stay_in_character}}
</policies>

<output_format>
- Container tag: <{{output_contract.container_tag}}>
- Schema: {{output_contract.schema | map(attribute="id") | join(", ")}}
- Length limit: {{output_contract.length.max_tokens}} tokens (approx)
</output_format>

<tool_use>
- Allow parallel tools: {{toolbox.allow_parallel_tools}}
- Cleanup temp files on completion: {{toolbox.temp_files_cleanup}}
</tool_use>
```

## 5. User Prompt Template

```text
<instructions>
Task: {{task_summary}}
Success Criteria:
1) {{criterion_1}}
2) {{criterion_2}}
Format: <{{output_contract.container_tag}}> containing {{output_contract.schema | map(attribute="id") | join(", ")}}
Constraints: tone=concise, forbidden=overpromising, language=Korean
If evidence is missing, reply "모르겠다" and list required data.
</instructions>

<data>
{{structured_or_raw_inputs}}
</data>

<examples>
<good>{{few_shot.good}}</good>
<bad>{{few_shot.bad}}</bad>
</examples>

<thinking>
High complexity — sketch a step-by-step plan before the final answer, but reveal only the final output.
</thinking>
```

## 6. Example: Korean Customer Support Persona

**System excerpt**
```
You are "K-전자 고객지원 스페셜리스트".
<persona>tone=polite, concise; audience=general consumers; non-goals=policy overrides</persona>
<policies>Allow uncertainty; cite handbook sections; stay in character.</policies>
<output_format>Container=<answer>; schema=summary, next_steps, references.</output_format>
```

**User turn**
```
<instructions>
Task: Decide exchange/refund eligibility using only the manual and ticket log.
Success: (1) Quote policy clause, (2) Give step-by-step customer guidance, (3) Distinguish certainty.
</instructions>
<data>
<manual>…policy excerpt…</manual>
<ticket>…latest tickets…</ticket>
</data>
<examples>
<good>Reference clause numbers and exception conditions.</good>
<bad>Vague statements without citations.</bad>
</examples>
```

## 7. Example: B2B Finance Briefing

```
<instructions>
Task: Summarise Q2 results and propose 3–5 actions (CFO tone).
Success: Accurate metrics, risk flags, actionable guidance.
Format: <analysis> with highlights/risks/actions_q3.
</instructions>
<data>
<financials>…Q2 table…</financials>
<cohorts>…cohort report…</cohorts>
</data>
<thinking>
Reflect on tool outputs, choose best option, output only the final answer.
</thinking>
```

## 8. Prompt Guide Structure (Team Wiki)

1. Purpose & scope
2. Persona specs library
3. System prompt template
4. User prompt template
5. Data-injection rules (XML tags)
6. Output contract & schema
7. Good/bad examples and antipatterns
8. Safety & hallucination mitigation (“I don’t know”, citations, retractions)
9. Character preservation checklists
10. Tool usage rules (parallelism, cleanup)
11. Evaluation rubric and automation pipeline
12. Change management (versioning, experiments, rollback)

## 9. Repository Scaffolding Example

```
/prompts
  /personas
    persona.b2b-cfo.v1.yml
    persona.support-ko.v1.yml
  /system/system.template.txt
  /user/user.template.txt
  /examples/{good.md,bad.md}
/docs
  PROMPT_GUIDE.md
  STYLE_GUIDE.md
/evals
  cases.csv
  rubric.md
  run_eval.py
/guardrails
  hallucination.md
  character.md
```

## 10. 80/20 Debugging Checklist

- Output noisy? Ensure XML schema and container tag are specified. [3]
- Tone drift? Reinforce role and tone directives in system plus scenario scaffolding. [1]
- Incorrect facts? Enable “I don’t know,” require citations, and run verification loops. [2]
- Hallucinated tests? Clarify “generalise rather than overfit to tests.” [4]
- Tool latency? Encourage parallel calls and enforce cleanup instructions. [4]

## 11. Style Guide Snapshot

- **Sentence length:** target 15–25 characters; kill filler adjectives.
- **Tone:** business personas = concise and decisive; support personas = courteous and actionable.
- **Format:** one container tag with fixed child sections for predictable parsing. [3]

## 12. Further Reading

- Anthropic Interactive Tutorial (9 chapters, foundational → advanced).[5]
- Claude 4 Prompting Best Practices: clarity, structure, thinking, tooling.[4]
- Use XML Tags for Claude-specific formatting advantages.[3]
- System Prompts and role definition guidance.[1]
- Reduce Hallucinations with uncertainty, citation, and verification workflows.[2]
- Prompt Evaluations & Real-world Prompting course materials.[6]
- Maintain persona voice with stay-in-character checklists.[7]

---

[1]: https://docs.anthropic.com/claude/docs/system-prompts
[2]: https://docs.anthropic.com/claude/docs/reduce-hallucinations
[3]: https://docs.anthropic.com/claude/docs/use-xml-tags
[4]: https://docs.anthropic.com/claude/docs/constructing-effective-prompts
[5]: https://github.com/anthropics/anthropic-cookbook/tree/main/prompting-with-claude
[6]: https://github.com/anthropics/anthropic-cookbook/tree/main/prompt-evaluations
[7]: https://docs.anthropic.com/claude/docs/maintain-character
