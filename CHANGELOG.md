# Changelog

## v5.0.5 — 2025-09-21

- Detect FastMCP automatically and fall back to a lightweight stdio loop when the runtime is unavailable, ensuring MCP tools always register.
- Provide explicit names for every `@mcp.tool` decorator so Cursor receives the canonical SSOT tool identifiers.
- Align Node and Python package versions (5.0.5) and surface the same number through runtime banners.
- Add `mcp>=0.4.0` to the Python core dependencies to ship FastMCP with the npm package.
- Refresh README documentation in English with updated quick start, troubleshooting, and release workflow guidance.
- Introduce the `sp.sdd_architecture` MCP tool plus persona overlays so every persona response references the Spec Kit SDD lifecycle.
- Added an SDD architecture knowledge base that maps Spec Kit stages, components, and runner contracts into reusable guidance.
- Restored MCP coverage for all Spec Kit personas (`sp_dev`, `sp_doc_master`, `sp_service_planner`, etc.) using a shared workflow executor and SDD-aligned guidance.
- Renamed the `tr` persona to full Troubleshooting mode with updated prompts, overlays, and command metadata.

## v5.0.0 — 2025-09-20

- Migrated all personas to prompt-based workflows and retired pipeline helper logic.
- Introduced mode-specialized prompt templates for GPT and Grok personas.
- Refactored the MCP server into modular components with a stateless stdio entry point.
- Hardened `super:init`, MCP diagnostics, and asset validation for project bootstrap scenarios.
- Expanded the CLI with interactive MCP modes and watch-based development tools.
