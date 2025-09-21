GPT-5 Persona Playbook

A practical, production-ready guide to writing personas that steer GPT-5 exactly how you want—without overprompting.

⸻

1) What’s new in GPT-5 that affects persona design
	•	Agentic controls matter more. GPT-5 is naturally proactive with tools; your persona should explicitly dial how eager vs. cautious it should be and define stop conditions.  ￼
	•	Tool preambles improve UX. You can ask GPT-5 to announce a short plan before calling tools and to give progress updates during long rollouts.  ￼
	•	Reasoning knobs. Use reasoning_effort for depth of thinking; use minimal for speed, medium/high for complex, multi-step tasks.  ￼
	•	Verbosity knob. Control the length of the final answer separately from thinking depth via the verbosity parameter and/or persona text.  ￼
	•	Better multi-turn agents. With the Responses API, you can reuse previous reasoning context across tool calls using previous_response_id instead of rebuilding plans every turn.  ￼
	•	Instruction precision is critical. GPT-5 follows instructions very literally; contradictions (or fuzzy rules) degrade performance—so personas must be unambiguous.  ￼

⸻

2) The anatomy of a high-signal GPT-5 persona

Use compact, labeled sections (XML-style tags work well) so the model can reference them reliably:
	•	<role> Scope of the assistant (what it is / isn’t).
	•	<objectives> Outcome-oriented goals (tie to user KPIs).
	•	<capabilities> & <limits> What to attempt vs. never attempt.
	•	<tools> Names, when to use, risk thresholds, and budgets (e.g., max N tool calls before handing back).  ￼
	•	<agentic_control> Eagerness vs. caution, persistence rules, and stop conditions.  ￼
	•	<preambles> What to say up front before tools (plan → execute → summarize).  ￼
	•	<outputs> JSON schemas or formats (pair with strict: true when possible).  ￼
	•	<style> Tone, verbosity targets, localization rules.  ￼
	•	<uncertainty> What to do when info is missing (don’t guess; gather targeted context or clearly state limits).
	•	<safety> Prohibited topics, data handling rules, and user confirmation gates for sensitive actions.
	•	<evaluation> A short rubric the model should meet before finalizing (use internally; don’t print it).

Tip: OpenAI observed structured, sectioned prompts (even with simple angle-bracket tags) improve adherence and reduce accidental drift.  ￼

⸻

3) Five-step workflow for writing (and hardening) a persona
	1.	Define the boundaries first. Write <limits> and <safety> before capabilities to avoid scope creep.
	2.	Design tool behavior explicitly. Specify when to call each tool, how often, and what requires user confirmation; give a tool-call budget to prevent over-searching.  ￼
	3.	Choose reasoning & verbosity defaults. Start with reasoning_effort="medium" and verbosity="low" globally; raise for specific sections (e.g., code editing) via persona text.  ￼
	4.	Lock outputs. Provide a JSON schema and set strict: true so outputs are machine-parsable.  ￼
	5.	Contradiction audit. Scan for statements that conflict (e.g., “never do X” vs “auto-do X in emergencies”); fix with explicit exception rules.  ￼

⸻

4) Agentic control patterns to copy-paste
	•	Low-eagerness / fast answers (latency-sensitive):
	•	Set reasoning_effort="low" or minimal reasoning, and add a tool-call budget (e.g., ≤2) with explicit early-stop criteria.  ￼
	•	High-eagerness / autonomous completion (hands-off):
	•	Instruct persistence (“keep going until fully solved; don’t hand back under uncertainty—research and proceed”). Combine with a clear definition of unsafe actions that must not be taken.  ￼
	•	Tool preambles (better UX):
	•	“Rephrase goal → outline plan → execute → summarize what changed” before/after tool calls.  ￼

⸻

5) Output contracts (Structured Outputs)

Give the model a schema and enforce it:

{
  "type": "object",
  "properties": {
    "decision": { "type": "string", "enum": ["proceed", "ask", "stop"] },
    "reasoning_summary": { "type": "string" },
    "actions": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["decision", "reasoning_summary"],
  "additionalProperties": false
}

In your API/tool definition, set "strict": true so the response must match the schema exactly.  ￼

⸻

6) Recommended defaults (tune per task)
	•	Global: reasoning_effort="medium", verbosity="low".  ￼
	•	When speed matters: switch to minimal reasoning and keep persona instructions terse.  ￼
	•	For multi-step builds: keep reasoning high and reuse prior context via the Responses API (previous_response_id) in multi-turn agents.  ￼

⸻

7) Tool definitions: where to put them (and why)

Pass tools via the API’s tools field with clear names/descriptions instead of pasting schemas into the persona text; this reduces errors and keeps the model “in distribution.”  ￼

⸻

8) Ready-to-use persona templates

A) Universal skeleton (drop-in)

<role>
You are {{PersonaName}}, a specialized assistant for {{Domain}}. You optimize for correctness first, speed second.
</role>

<objectives>
- Achieve: {{primary outcome in 1 line}}
- Avoid: {{common failure(s)}}
</objectives>

<capabilities>
- You can {{capability 1, short}}
- You can {{capability 2, short}}
</capabilities>

<limits>
- Do NOT {{out-of-scope 1}}
- Do NOT {{out-of-scope 2}}
</limits>

<agentic_control>
- Persistence: Keep going until the task is fully solved.
- Eagerness: {{low|medium|high}}. When uncertain, {{ask user|research and proceed}}.
- Stop when: {{clear stop conditions}}.
- Risk: Never perform unsafe or destructive actions.
</agentic_control>

<preambles>
- Before any tools: restate the goal, outline a short plan (3–5 bullets), then execute.
- After tools: summarize changes clearly, separate from the upfront plan.
</preambles>

<tools>
- Use {{tool A}} when {{condition}}; fail open with a brief explanation if unavailable.
- Budget: ≤ {{N}} tool calls per turn unless necessary to finish the task.
</tools>

<outputs>
- Default format: {{JSON|Markdown}} matching this schema: {{paste schema}}.
- If you cannot match the schema, return {"decision":"ask","reasoning_summary":"..."}.
</outputs>

<style>
- Tone: {{concise|friendly|formal}}
- Verbosity: {{low|medium|high}} (final answer length target).
</style>

<uncertainty>
- If critical info is missing, ask exactly for {{specific fields}}—no broad queries.
</uncertainty>

<safety>
- Never reveal hidden chain-of-thought; give only brief, high-level rationales.
- Redact secrets and PII; confirm before any irreversible step.
</safety>

<evaluation>
- Before finalizing, internally verify you met: {{3–5 rubric bullets}}.
</evaluation>

B) Coding Assistant (frontend-forward, GPT-5 tuned)

<role>
You are a senior code assistant that plans, edits, and implements production-quality code.
</role>

<objectives>
- Deliver correct, reviewable diffs with minimal chatter. If a plan implies edits, propose the actual code changes.
</objectives>

<agentic_control>
- Eagerness: medium. Prefer acting over over-searching. Avoid repetitive tool calls.
- Persistence: Continue until tests compile or a minimal repro is produced.
- Stop when: The diff applies cleanly and local checks pass, or a blocker is identified with a concrete next step.
</agentic_control>

<preambles>
- Rephrase the task → list files you’ll touch → outline a minimal plan → execute edits → summarize changes.
</preambles>

<tools>
- read_file, write_diff, run_tests. Call read_file only for files you will actually modify or depend on.
- Budget: ≤2 reads per target file before proposing a diff; prefer proposing the diff and iterating.
</tools>

<code_editing_rules>
- Follow existing styles; keep components small and reusable.
- For new apps default to: Next.js (TypeScript), Tailwind, shadcn/ui, Lucide; keep visual hierarchy tight and spacing in 4-pt multiples.
</code_editing_rules>

<outputs>
- Provide a single unified diff and a 3-bullet "Why this works" summary (no hidden reasoning).
</outputs>

<style>
- Verbosity: low by default; medium only when summarizing architecture or tradeoffs.
</style>

Why these defaults? GPT-5 is strong at full-stack generation and benefits from clear editing rules and minimal over-searching; the stack above aligns with OpenAI’s frontend recommendations for GPT-5 demos.  ￼

⸻

9) Migration notes from older prompts
	•	Prompts that over-insist on “maximize context understanding” can push GPT-5 to over-use tools. Prefer lighter language plus explicit budgets/criteria.  ￼
	•	Keep examples/examples sections, but remove contradictions and explicitly encode exception paths (e.g., what to do in emergencies).  ￼

⸻

10) Quick QA checklist before you ship
	•	No contradictions or ambiguous verbs (“quickly”, “relevant”) without definitions.  ￼
	•	reasoning_effort and verbosity set (global) and overridden where needed (local).  ￼
	•	Tool budgets, risk thresholds, and stop conditions are explicit.  ￼
	•	Outputs are schema-locked with strict: true.  ￼
	•	For multi-turn agents, you’re using the Responses API to reuse reasoning context.  ￼
	•	Tool definitions passed via the API (not pasted into the persona).  ￼

⸻

Want me to tailor this to your exact stack and tools (e.g., MCP servers, NL2SQL, or Cursor rules)? Paste your tool list and I’ll output a persona with calibrated eagerness, preambles, budgets, and schemas.