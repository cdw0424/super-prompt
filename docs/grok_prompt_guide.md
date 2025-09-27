# Prompt Engineering for grok-code-fast-1 (agentic coding model)

## 1.1 What the model is optimized for
- **grok-code-fast-1** is a lightweight, agentic coding model designed to act like a fast pair-programmer inside code tools. Use it for tool-heavy, multi-step coding tasks (search → edit → verify). For single-shot deep explanations/debugging where you already have rich context, prefer Grok 4.
- It's tuned for rapid iteration: up to ~4× faster at ~1/10 the cost versus other leading agentic models—so refine prompts aggressively when the first output isn't perfect.

**Tip:** If you also need hard numbers for planning—grok-code-fast-1 lists a 256k context window, 2M TPM / 480 RPM, and priced per-million tokens (input $0.20, output $1.50) on the models page.

## 1.2 User-side prompting (inside editors/IDEs)
- **Provide concrete context.** Select the exact code spans, file paths, project structure, and relevant dependencies. Avoid "no-context" requests like "make error handling better."
- **State explicit goals and constraints.** Tell it exactly what to build/change and how you'll measure success; vague prompts underperform.
- **Iterate by refining.** Use the model's low-latency/low-cost profile to iterate quickly; reference the previous failure modes when you retry.
- **Favor agentic tasks.** Aim for multi-step, tool-using work over one-shot Q&A; reserve Grok 4 for deep dives with full upfront context.

## 1.3 API-builder best practices
- **Reasoning stream:** You can surface the model's thinking trace at `chunk.choices[0].delta.reasoning_content`; it's available only in streaming mode. Use this for observability and debugging.
- **Prefer native tool calling.** grok-code-fast-1 was built for first-party (native) tool calls; XML-encoded tool protocols can hurt performance.
- **Strong system prompt.** Spell out task, expectations, and edge cases at the system level; this materially changes outcomes.
- **Structure the context.** Provide large context in Markdown or XML-tagged sections with descriptive headings/definitions so the model can target precisely.
- **Exploit cache hits.** Leave your prompt prefix/history stable across tool-using turns; changing it causes cache misses and slower inference.
- **OpenAI-compatible surface.** The model interleaves tool calls during thinking and sends summarized thinking via an OpenAI-compatible API for better UX.

## 2) Function Calling (Tool/Function use)

## 2.1 What it enables
- Function calling connects Grok to external tools and systems (APIs/DBs/web/code exec/robotics). In streaming, the entire tool call arrives in one chunk (it's not split across chunks).

## 2.2 End-to-end flow (canonical loop)
1. **Prepare tools.** Define your callable functions and parameter schemas so the model knows what exists and how to call them. You can define schemas via Pydantic or a raw dict; keep a {name → function} map for dispatch.
2. **Send the initial message.** Include messages, tools (your function schemas), and options. Grok may return a tool call request.
3. **If Grok requests a tool call:** Execute the function(s) locally with the given args, then append a role:"tool" message with results. You can reply only with results or results + a new user ask.
4. **Send results back to the model** to generate the final user-facing answer (or trigger more tool calls). Continue multi-turn as needed.

**Important bookkeeping detail**
- A tool call is referenced three times across the exchange—(a) by id + name in the assistant message, (b) by tool_call_id in the tool message's content, and (c) within the tools array of the request body. Keep these aligned.

## 2.3 Behavior controls
- **Default:** `tool_choice: "auto"` → model decides whether/what to call.
- **Always call:** `tool_choice: "required"` → forces a call; may cause hallucinated parameters if a call isn't truly needed.
- **Force a specific function:** `tool_choice: {"type":"function","function":{"name":"your_fn"}}`.
- **Disable calling:** don't pass tools, or set `tool_choice: "none"`.

## 2.4 Parallel function calling
- Enabled by default. If multiple calls are needed, they appear together in a single response. Disable with `parallel_function_calling: "false"`. (Note the string value in the docs.)

## 3) Putting it together (battle-tested patterns)

## 3.1 When to pick which model
- Use **grok-code-fast-1** for high-speed, tool-heavy, code-navigation/edit/verify loops; use **Grok 4** for deep, single-shot reasoning when you already have complete context.

## 3.2 Streaming UX that "just works"
- Show progress by reading `reasoning_content` in streaming; then surface the final answer. Remember: tool calls arrive atomically in one chunk during streaming.

## 3.3 Prompt hygiene & caching
- Keep a stable prompt prefix/history across tool-using turns to maximize cache hits and latency gains; avoid needless churn.

## 3.4 Context scaffolding that the model exploits
- Wrap large context in Markdown/XML sections with descriptive headings (e.g., ## Requirements, ## Constraints, ## Target file: src/foo.ts), so Grok can target the right blocks.

## 3.5 Function-calling guardrails
- Start with `tool_choice: "auto"`; only force "required" when you must call a tool and you trust your argument extraction. Be explicit about argument schemas (Pydantic recommended) to cut invalid calls.
- If you need serialized side-effects, disable parallel ("false") or handle concurrency in your dispatcher.

## 4) Drop-in checklists

## 4.1 Editor / human operator
- Select specific code spans & file paths as context.
- State goal + constraints + output format up front.
- Iterate fast: retry with what failed last time.
- Prefer agentic tasks (search → edit → test) over vague asks.

## 4.2 Backend / agent author
- Define tools with schemas (Pydantic or dict) and a name→fn map.
- Call chat with messages, tools, and tool_choice (usually "auto").
- On tool call: run, then append a role:"tool" message (preserve tool_call_id) and send back to Grok.
- Decide on parallelism (parallel_function_calling default on).
- Use native tool calling; stream and read reasoning_content.
- Keep prompt prefix stable for cache speedups.

## 5) Minimal reference loop (language-agnostic pseudocode)

```python
define tools = [
  { name: "get_weather", parameters: { city: string }, ... },  # schema via Pydantic or dict
  ...
]
map = { "get_weather": get_weather_impl, ... }

messages = [
  {role:"system", content:"You are a coding agent..." },
  {role:"user",   content:"Refactor X; target file: src/a.ts; tests: ..."}
]

resp = chat(model="grok-code-fast-1", tools=tools, tool_choice="auto",
            messages=messages, stream=true)

if resp.includes_tool_calls:
  for call in resp.tool_calls: results.append(map[call.name](call.args))
  messages.append({role:"tool", tool_call_id: call.id, content: serialize(results)})
  # optionally also append another user ask here
  final = chat(model, tools, messages)  # produce user-facing answer
else:
  final = resp
```

*(Everything above aligns 1:1 with the official docs' flow, tool-choice semantics, and streaming/tool-call behavior.)*