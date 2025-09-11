---
description: frontend command
run: "./frontend-processor.py"
args: ["${input}"]
---

# 🎨 Frontend Development Specialist

User-centered frontend development with Codex CLI integration for complex UX challenges.

## Usage
- Write your request and append `/frontend` (e.g., "Refactor header /frontend").

## Output
- Cursor‑ready prompt
- Context bullets
- Small‑step plan
- Accessibility and performance checklist

## Prompt Template
```
TASK
- What UI change is needed and why

CONTEXT
- Framework (React/Vue/Svelte), routing, state mgmt
- Design system/tokens (colors, spacing, typography)
- Constraints (bundle budget, SSR/SSG, hydration)

SPEC
- Component API (props, events)
- States: idle, loading, success, empty, error
- Responsive behavior (breakpoints)
- Interaction: hover/focus/active/disabled
- i18n/RTL considerations

PLAN (Small Steps)
1) Create/modify component
2) Wire state/data
3) Add a11y roles/labels/keyboard navigation
4) Optimize performance (memoization, virtualization if needed)
5) Tests and stories

CHECKLIST
- Accessibility: roles, labels, tab order, contrast, reduced motion
- Performance: LCP/INP/CLS budgets, lazy load heavy assets
- Quality: deterministic, resilient to missing data
- Observability: '-----' prefixed logs only when necessary
```
