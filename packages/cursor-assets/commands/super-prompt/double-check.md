---
description: double-check command - Confessional verification and integrity audit
run: mcp
server: super-prompt
tool: sp_double_check
args:
  query: "${input}"
  persona: "double_check"
---

## Execution Mode

# Double-Check — Guided Execution

## Instructions
- Review the project dossier at `.super-prompt/context/project-dossier.md`; if it is missing, run `/super-prompt/init` to regenerate it.
- Provide a concise summary of what you just completed and what you think is still pending
- Admit uncertainty openly; "I don't know" is preferred over guessing
- Use MCP Only (MCP server call): /super-prompt/double-check "<your confession & next steps>"

## Phases & Checklist
### Phase 1 — Confession Intake
- [ ] List the concrete actions taken (files touched, tests run, artifacts produced)
- [ ] Highlight any areas of doubt or missing evidence
- [ ] Tag each item as `done`, `in-progress`, or `blocked`

### Phase 2 — Integrity Audit
- [ ] Enumerate what has NOT been completed yet (tests, docs, reviews, deployments)
- [ ] Surface skipped steps, outstanding risks, or unverifiable assumptions
- [ ] Capture why each gap exists (time, missing data, access, uncertainty)

### Phase 3 — Gap Resolution Plan
- [ ] For every gap, outline the verification or follow-up work required
- [ ] Note owners or stakeholders who need to weigh in (if any)
- [ ] Provide a lightweight sequencing plan (what to tackle first, why)

### Phase 4 — Information Request
- [ ] Ask the user for the minimal additional inputs or artifacts required to close gaps
- [ ] Offer a confession summary so the user can validate completeness
- [ ] Confirm readiness to resume once the requested information arrives

## Outputs
- Structured confession covering completed work, gaps, and blockers
- Prioritized follow-up actions with rationale
- Targeted questions for the user to supply missing information

