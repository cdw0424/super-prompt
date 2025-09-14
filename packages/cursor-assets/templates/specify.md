---
description: specify command
run: "./.cursor/commands/super-prompt/tag-executor.sh"
args: ["${input} /specify"]
---

# /specify - Create Feature Specification

Generate a structured specification document following Spec Kit principles.

## Usage
```
/specify [feature description]
```

## What it creates
- `specs/[feature-name]/spec.md` - Complete specification with:
  - REQ-ID for traceability
  - Success criteria and acceptance criteria
  - Scope boundaries and assumptions
  - Business value and risk assessment
  - Technical constraints and dependencies

## Example
```
/specify Create user authentication system with OAuth2 support
```

This creates a comprehensive spec that serves as the source of truth for the feature implementation.

---
*Spec Kit v0.0.20 - Specification First Development*
