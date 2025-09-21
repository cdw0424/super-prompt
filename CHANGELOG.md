# Changelog

## v5.1.5 — 2025-09-21

- Simplified Quick Start: Streamlined installation with project-local setup as the primary method.
- Version synchronization fix: All version displays now correctly show v5.1.5 across CLI, runtime banners, and documentation.
- Enhanced MCP server architecture with improved modularity and stateless stdio entry points.
- Updated persona pipeline system with prompt-based workflows replacing legacy pipeline helpers.
- Refactored MCP server into modular components for better maintainability.
- Added new SDD architecture module with comprehensive Spec Kit lifecycle guidance.
- Improved asset validation and project bootstrap processes.
- Restored full MCP coverage for all Spec Kit personas with shared workflow executor.
- Enhanced troubleshooting persona with updated prompts and command metadata.

## v5.1.4 — 2025-09-21

- Enhanced troubleshooting guide: Comprehensive installation troubleshooting for legacy version issues.
- Version synchronization fix: All version displays now correctly show v5.1.4 across CLI, runtime banners, and documentation.
- Enhanced MCP server architecture with improved modularity and stateless stdio entry points.
- Updated persona pipeline system with prompt-based workflows replacing legacy pipeline helpers.
- Refactored MCP server into modular components for better maintainability.
- Added new SDD architecture module with comprehensive Spec Kit lifecycle guidance.
- Improved asset validation and project bootstrap processes.
- Restored full MCP coverage for all Spec Kit personas with shared workflow executor.
- Enhanced troubleshooting persona with updated prompts and command metadata.

## v5.1.3 — 2025-09-21

- Enhanced installation guidance: Clear instructions to always install the latest version for optimal experience.
- Version synchronization fix: All version displays now correctly show v5.1.3 across CLI, runtime banners, and documentation.
- Enhanced MCP server architecture with improved modularity and stateless stdio entry points.
- Updated persona pipeline system with prompt-based workflows replacing legacy pipeline helpers.
- Refactored MCP server into modular components for better maintainability.
- Added new SDD architecture module with comprehensive Spec Kit lifecycle guidance.
- Improved asset validation and project bootstrap processes.
- Restored full MCP coverage for all Spec Kit personas with shared workflow executor.
- Enhanced troubleshooting persona with updated prompts and command metadata.

## v5.1.1 — 2025-09-21

- Version synchronization fix: All version displays now correctly show v5.1.1 across CLI, runtime banners, and documentation.
- Enhanced MCP server architecture with improved modularity and stateless stdio entry points.
- Updated persona pipeline system with prompt-based workflows replacing legacy pipeline helpers.
- Refactored MCP server into modular components for better maintainability.
- Added new SDD architecture module with comprehensive Spec Kit lifecycle guidance.
- Improved asset validation and project bootstrap processes.
- Restored full MCP coverage for all Spec Kit personas with shared workflow executor.
- Enhanced troubleshooting persona with updated prompts and command metadata.

## v5.1.0 — 2025-09-21

- Enhanced MCP server architecture with improved modularity and stateless stdio entry points
- Updated persona pipeline system with prompt-based workflows replacing legacy pipeline helpers
- Refactored MCP server into modular components for better maintainability
- Added new SDD architecture module with comprehensive Spec Kit lifecycle guidance
- Improved asset validation and project bootstrap processes
- Restored full MCP coverage for all Spec Kit personas with shared workflow executor
- Enhanced troubleshooting persona with updated prompts and command metadata
- Synchronized versioning across Node package, Python core, and runtime banners
- Updated documentation and README with current setup guidance in English
- Cleaned up deprecated GitHub workflow files and redundant manifest configurations

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
