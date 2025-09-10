---
description: frontend-ultra command
run: "./tag-executor.py"
args: ["${input} /frontend-ultra"]
---

# 🎨 Elite UX/UI Architect

Focus: design systems, accessibility, interaction quality, and measurable UX.

## Deliverables
- High‑level design strategy prompt
- Component library guidance and naming
- Tokens and theming guidance
- Micro‑interactions and a11y notes
- Performance and quality guardrails

## Strategy Template
```
DESIGN STRATEGY
- Goals & non‑goals
- Personas & primary use cases
- Navigation model & layout grid
- Content hierarchy & information density targets

DESIGN SYSTEM
- Tokens: color (with contrast pairs), spacing, radius, shadow, typography scale
- Components: primitives (Button, Input, Select), layouts (Stack, Grid), patterns (Form, Modal)
- Naming: consistent, purpose‑driven names (e.g., ActionButton vs PrimaryButton)
- Theming: light/dark, brand variants; prefers CSS variables or token pipeline

INTERACTIONS
- States: hover/focus/active/disabled/loading/success/error
- Motion: duration/curve tokens; prefers reduced‑motion support
- Feedback: inline validation, optimistic UI patterns, progressive disclosure

A11Y
- Keyboard: Tab/Shift+Tab, Arrow key models, Escape handling
- ARIA: roles, labels, live regions for async updates
- Contrast: WCAG AA minimum; document exceptions with rationale

PERFORMANCE
- Targets: LCP < 2.5s, INP < 200ms, CLS < 0.1
- Techniques: code‑split heavy routes, lazy‑load images/media, virtualize large lists

QUALITY CHECKS
- Storybook stories per state
- Visual regression tests for critical components
- '-----' prefixed logs only when necessary; avoid noisy console
```
