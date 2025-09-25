---
description: frontend command - UI/UX design and frontend development
run: mcp
server: super-prompt
tool: sp_frontend
args:
  query: "${input}"
  persona: "frontend"
---

## Execution Mode

# Frontend — Guided Execution

## Instructions
- Review `.super-prompt/context/project-dossier.md`, the design tokens library, and any product guidelines; regenerate with `/super-prompt/init` if missing or stale.
- Collect the user story, target devices, accessibility thresholds (WCAG 2.2 AA minimum), and brand guardrails before proposing solutions.
- Apply modern UI/UX practice: design thinking discovery → atomic design component stacking → design system alignment (tokens, grids, states) → validation.
- Treat Apple’s Human Interface Guidelines as the aesthetic baseline—emphasize clarity, depth, and deference while keeping interactions intuitive and delightful.
- Use MCP Only (MCP server call): /super-prompt/frontend "<your feature or screen brief>"

## Phases & Checklist
### Phase 0 — Discovery & Intent
- [ ] Confirm user goal, end-user persona, accessibility needs, and success metrics
- [ ] Inventory existing assets: design tokens, component library entries, motion patterns, copy tone
- [ ] Note platform nuances (iOS/macOS vs web) and performance constraints

### Phase 1 — Experience Architecture
- [ ] Outline end-to-end user flow with states, empty/error/loading scenarios
- [ ] Define information hierarchy using modern heuristics (Nielsen, Fitts, Hick) and Apple HIG patterns
- [ ] Capture content model, interactions, and feedback requirements for each state

### Phase 2 — Visual System & Layout
- [ ] Establish grid, spacing, typography, and color decisions mapped to tokens (e.g., `spacing-16`, `radius-lg`, `elevation-2`)
- [ ] Specify component anatomy (atoms → molecules → organisms) and responsive behavior at key breakpoints
- [ ] Detail motion/micro-interaction guidelines (durations, easing) plus inclusive affordances (focus, reduced motion)

### Phase 3 — Implementation Blueprint
- [ ] Provide diff-style snippets or component updates (React/Vue/etc.) with BEM/utility class guidance as appropriate
- [ ] Call out CSS/Design Token updates, padding/margin values, and semantic HTML requirements
- [ ] List test coverage (visual regression, accessibility, interaction) and tooling commands (`npm test`, `npm run lint`, `axe`, etc.) with expected outcomes

### Phase 4 — Validation & Handoff
- [ ] Summarize QA across devices, screen readers, and dark/light themes; flag known debt
- [ ] Package handoff artifacts: updated Figma/JPG refs, storybook links, changelog entries, rollout plan
- [ ] Run Double-Check MCP: /super-prompt/double-check "Confession review for frontend delivery"

## Outputs
- Experience architecture brief (user flow, heuristics, state coverage)
- Visual system spec with spacing/motion tokens and intuitive Apple-inspired styling guidance
- Implementation package: code snippets, token adjustments, validation commands, and Double-Check MCP confirmation
