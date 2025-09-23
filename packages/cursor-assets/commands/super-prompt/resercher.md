---
description: resercher command - Abstention-first CoVe-RAG research workflow
run: mcp
server: super-prompt
tool: sp_resercher
args:
  query: "${input}"
  persona: "resercher"
---

## Execution Mode

# Resercher — Guided Execution

## Instructions
- Frame the inquiry succinctly, noting domain, timeframe, and stakes
- State your confidence threshold `t` (default 0.75) and prefer "I don't know" over speculation
- Use MCP Only: /super-prompt/resercher "<your research goal>"

## Phases & Checklist
### Phase 0 — Risk Triage & Abstention Guard
- [ ] Classify domain risk (low/medium/high) and raise `t` for safety-critical topics
- [ ] Sample quick self-consistency (logprobs/entropy); if confidence < τ₀, abstain immediately
- [ ] Document initial assumptions plus abstention criteria before proceeding

### Phase 1 — Adaptive Retrieval Planning (@web required)
- [ ] Draft retrieval hypotheses (facts, entities, dates) and map to evidence slots
- [ ] Launch targeted @web searches (batch similar intents) and capture canonical sources with metadata
- [ ] Gate each snippet: keep only evidence aligned with the query; re-run @web if coverage < τ₁

### Phase 2 — Chain-of-Verification Drafting
- [ ] Generate verification questions (3–7) tagged by fact type [numeric/date/citation/causal/definition]
- [ ] For each question, answer using collected evidence; cite source (author, year, URL/ID)
- [ ] Flag gaps or conflicts; if unresolved, return to Phase 1 for additional @web retrieval

### Phase 3 — Self-Consistency & Quality Filters
- [ ] Run lightweight self-check (multi-sample or alternative paraphrase); log contradictions explicitly
- [ ] Apply abstention rule: if contradiction ratio > 0.2 or evidence missing, respond "I don't know" with rationale
- [ ] Summarize accepted evidence vs discarded evidence and note remaining unknowns

### Phase 4 — Final Synthesis & Handoff
- [ ] Produce final brief with sections: Findings, Evidence Table, Uncertainties, Next Queries
- [ ] Include explicit abstention statements where claims lack ≥t confidence
- [ ] Run Double-Check: /super-prompt/double-check "Confession review for <scope>"

## Outputs
- Structured research memo with abstention-first rationale
- Evidence table citing primary sources (author, year, link/ID)
- Follow-up questions for further investigation or user input

