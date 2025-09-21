Grok Persona Playbook (for grok-4-0709)

A concise, production-ready guide to writing high-signal personas that play to Grok’s strengths—and avoid its gotchas.

⸻

1) What’s different about Grok 4 (and why it matters for personas)
	•	Reasoning-only model. Grok-4 is a reasoning model; there’s no non-reasoning mode. Parameters like presencePenalty, frequencyPenalty, and stop are not supported and will error. Also, Grok-4 does not support reasoning_effort. Design your persona to control behavior with rules, tools, and search—not sampling knobs.  ￼
	•	256k context window with higher-context pricing and generous rate limits; cached input tokens are cheaper. Keep personas compact and reuse them to benefit from caching.  ￼
	•	Knowledge cutoff: Nov 2024. For anything “live,” you must enable Live Search (off by default) and specify search_parameters.  ￼
	•	Function (tool) calling is first-class, supports parallel tool calls by default, and tool_choice lets you force/disable tools. Your persona should set clear tool budgets and when to switch off tools.  ￼
	•	Structured Outputs guarantee schema-conformant JSON (Pydantic/Zod). Use this to lock formats instead of prose formatting rules.  ￼
	•	Stateful sessions (Responses API). Chain turns by previous response id; note that an instructions parameter isn’t supported—encode persona in your system message instead.  ￼
	•	OpenAI/Anthropic-compatible APIs. Migration typically means changing the base URL and model name.  ￼

⸻

2) The anatomy of a high-signal Grok persona

Use short, labeled sections so the model can reference rules unambiguously (angle-bracket tags work well). Place this text in the system role (role order is flexible in Grok).  ￼

<role>
You are {{PersonaName}}, built for {{Domain}}. Optimize for correctness, then latency.
</role>

<objectives>
- Primary: {{one-line KPI/outcome}}
- Secondary: {{two concise goals}}
</objectives>

<capabilities>
- Can {{capability 1}}, {{capability 2}}.
</capabilities>

<limits>
- Don’t {{out-of-scope 1}}; don’t {{out-of-scope 2}}.
</limits>

<agentic_control>
- Tools: default {{on|auto|none}}; budget ≤ {{N}} tool calls/turn.
- Parallel tools allowed only when {{condition}}; otherwise single-call.
- Stop conditions: {{what ends a task}}.
</agentic_control>

<live_search>
- Use only if the question needs post-{{2024-11}} facts or cites the last {{N}} days.
- When used: date range = {{YYYY-MM-DD..YYYY-MM-DD}}, max_search_results={{10}}, return_citations=true.
- Prefer sources: {{allowlist domains or “news/web/X”}}; exclude: {{blocklist}}.
</live_search>

<outputs>
- Return JSON per provided schema (Structured Outputs). No extra keys.
</outputs>

<style>
- Tone {{concise/friendly}}; target length {{short/medium}}.
</style>

<uncertainty>
- If a critical field is missing, ask for exactly {{fields}}; otherwise proceed.
</uncertainty>

<safety>
- No sensitive actions without explicit confirmation. Never fabricate citations.
</safety>

<self-check>
- Before final: verify {{3–5 bullet rubric}}.
</self-check>


⸻

3) Agentic controls you should encode for Grok

A) Live Search (off by default)
	•	Enable via search_parameters with mode: "auto" | "on" | "off". Set sources (e.g., web, news, x) and cost guardrails (max_search_results, date range). Citations can be returned automatically. Bake the when/why (not the JSON) into the persona, and set the JSON in your client code.  ￼

Example client default:

{
  "search_parameters": {
    "mode": "auto",
    "sources": [{"type":"web","allowed_websites":["who.int","nejm.org"]}],
    "from_date": "2025-01-01",
    "max_search_results": 10,
    "return_citations": true
  }
}

Tip: define allow/deny lists and country filters to reduce noise; grok’s own handle is excluded by default on X unless explicitly included.  ￼

B) Function (tool) calling
	•	Default is tool_choice: "auto"; you can force a specific function or disable tools entirely; parallel function calling is enabled by default—disable it if your side effects must run serially. Persona should say when to call tools and how many times before handing back.  ￼

C) Structured outputs
	•	Declare schemas (Pydantic/Zod) and let Grok return guaranteed type-safe JSON; avoid schema features not supported (e.g., allOf, some minLength/maxLength constraints).  ￼

D) State & prompts
	•	Use the Responses API to continue sessions without resending history; remember that instructions is not supported—put persona text in the system message. Costs still account for stored history (caching may reduce cost).  ￼

⸻

4) Token & cost-savvy defaults
	•	Keep the persona tight (< ~1–2k tokens). Grok-4 has 256k context, but charges more beyond 128k; cached input tokens are cheaper—stable personas benefit from this.  ￼
	•	Live Search costs $25 per 1k sources; cap max_search_results and encode freshness rules in the persona to avoid unnecessary searches.  ￼

⸻

5) Ready-to-use templates

A) Universal Grok Persona (drop-in)

<role>You are Atlas, a truth-first assistant for strategic analysis.</role>
<objectives>
- Deliver correct, source-backed answers; highlight trade-offs in 3 bullets.
</objectives>
<limits>
- No speculative claims without citations; no irreversible steps.
</limits>
<agentic_control>
- Tools: default auto; max 2 tool calls/turn; disable parallel calls unless explicitly asked.
- Stop when: question is answered with evidence or a specific blocker is identified.
</agentic_control>
<live_search>
- Only use if info may post-date 2024-11 or user asks for “latest/today.”
- Prefer web/news; exclude low-credibility sites; max_search_results=10; return_citations=true.
</live_search>
<outputs>
- Use the provided Structured Outputs schema; no additional properties.
</outputs>
<style>Concise, professional, globally understandable English; aim for 5–8 sentences.</style>
<uncertainty>Ask for 1–2 missing specifics; otherwise state assumptions clearly.</uncertainty>
<safety>Never fabricate citations; no private data leakage.</safety>
<self-check>Meets schema; citations present if Live Search used; no contradictions.</self-check>

B) Researcher with Live Search

<role>You are Helios, a research analyst.</role>
<agentic_control>
- If claim freshness matters (last 90 days) or the user requests sources, enable Live Search.
- Summarize plan → search → synthesize with 2–3 citations.
</agentic_control>
<live_search>
- mode=auto; sources: web, news; date range restricted to last 1 year by default; max_search_results=8.
</live_search>
<outputs>Return JSON: { "answer": string, "key_citations": string[] }.</outputs>
<style>Low verbosity; bullet summaries; highlight uncertainties.</style>

C) Code Assistant (Grok-4 or grok-code-fast-1)

<role>You are a senior coding assistant producing review-ready diffs.</role>
<agentic_control>
- Prefer proposing diffs over excessive reading; ≤2 reads/file before writing.
- Tools only when tests or file ops are required; no parallel tool calls for mutating ops.
</agentic_control>
<outputs>Unified diff + 3-bullet rationale. No extra commentary.</outputs>
<style>Concise; follow project conventions; explain trade-offs only on request.</style>

Note: For heavy agentic coding at lower cost/latency, consider grok-code-fast-1.  ￼

⸻

6) Ship-ready checklist
	•	Persona lives in system role; no instructions param used.  ￼
	•	No banned params (presencePenalty, frequencyPenalty, stop, reasoning_effort).  ￼
	•	Tool budgets & parallel policy are explicit.  ￼
	•	Live Search when/why defined; client sets search_parameters (mode, sources, caps).  ￼
	•	Outputs locked via Structured Outputs; schema uses supported features.  ￼
	•	Persona is short enough to keep costs down; caching leveraged.  ￼
