# Changelog

## v5.2.32 — 2025-09-21

- **Enhanced CLI Mode**: All CLI commands now work without requiring SUPER_PROMPT_ALLOW_DIRECT=true
- **Improved CLI User Experience**: CLI mode automatically disables MCP-only enforcement for better usability
- **Simplified CLI Usage**: No need to set environment variables for basic CLI operations
- **Maintained MCP Security**: MCP-only enforcement still active for non-CLI operations
- **Fixed MCP Server Python Path Issue**: MCP server now correctly uses .super-prompt/lib/ Python packages
- **User-Centric Python Path Resolution**: All commands prioritize user's project .super-prompt/lib/ over system packages
- **Enhanced Package Discovery**: Improved PYTHONPATH resolution for both MCP server and CLI tools
- **Fixed "no tools" Error**: MCP server can now properly find and load all Super Prompt tools after initialization
- **Enhanced CLI User Experience**: Improved readability by hiding debug logs in CLI mode
- **Cleaner Initialization Output**: User input prompts are now clearly visible without debug message interference
- **Better Visual Separation**: Debug logs are hidden in CLI mode for better user experience
- **Fixed MCP Server Interference**: Removed MCP module imports from mode change functions to prevent server state disruption
- **Improved Mode Switching**: Mode changes (grok/gpt) no longer affect MCP tool availability
- **Enhanced Stability**: MCP server remains stable during mode transitions
- **Interactive Initialization**: Added dialog-based input for project root, MCP server path, and Python package path
- **Enhanced MCP Path Configuration**: Users can now specify custom paths for MCP server and Python packages during initialization
- **Improved User Experience**: Initialization process now asks for user input when needed instead of using defaults
- **Flexible Path Management**: Support for custom installation paths while maintaining backward compatibility

## v5.2.22 — 2025-09-21

- **Pure npm Self-Contained Package**: All Python files now copied from npm package to .super-prompt/lib/ - no pip install needed
- **Simplified Dependency Management**: No more pip install complications - everything comes from npm package
- **Complete Project Isolation**: Every Super Prompt component contained within .super-prompt/ folder for maximum portability
- **Enhanced .super-prompt Structure**: Added lib/ folder containing all Python packages that users can directly inspect
- **PYTHONPATH Configuration**: MCP server configured to use .super-prompt/lib/ in PYTHONPATH for seamless operation
- **Complete Project Isolation**: All Super Prompt files and dependencies contained within .super-prompt/ folder
- **Silent MCP Server**: Completely disabled all logging and progress output in MCP server to prevent protocol interference
- **Clean MCP Protocol**: MCP server now runs in complete silence, preventing "no tools" detection issues
- **Silent Progress Class**: Added SilentProgress class to replace progress.show_* methods with no-op implementations
- **Complete Initialization Process**: Added comprehensive setup including Python package installation and all configuration files
- **Super Prompt Internal Files**: Now creates .super-prompt/config.json, mode.json, cache/context_cache.json
- **Python Package Installation**: Automatically installs super-prompt-core package during initialization
- **Absolute Path MCP Configuration**: Changed MCP command to use absolute path based on user-specified project root

## v5.2.6 — 2025-09-21

- **CursorAdapter Template Source Fix**: Fixed generate_commands and generate_rules to copy from commands/rules directories instead of non-existent templates directory
- **Asset Path Correction**: Corrected source paths to use actual cursor-assets structure (commands/ and rules/ subdirectories)
- **Template-to-Source Mapping**: Updated file copying logic to match actual package structure in both development and published environments
- **Asset Discovery Enhancement**: Improved path resolution for command and rule file sources across different installation contexts

## v5.2.5 — 2025-09-21

- **Asset Template Path Resolution**: Fixed CursorAdapter to properly locate templates in both development and published package environments
- **Multi-Path Template Discovery**: Implemented fallback path resolution for command and rule templates across different package structures
- **Published Package Compatibility**: Ensured generate_commands and generate_rules work correctly in npm-published packages
- **Template File Copy Fix**: Resolved issue where command and rule templates were not being copied to project .cursor directories

## v5.2.4 — 2025-09-21

- **Asset Path Resolution**: Fixed assets_root() function to correctly locate cursor-assets in both development and published package environments
- **Cross-Platform Compatibility**: Ensured proper path resolution for nested package structures in npm-published versions
- **Project .cursor Directory**: Final fix for proper creation of project-local .cursor directories with all command and rule assets
- **Published Package Structure**: Corrected asset discovery logic for npm registry package layout

## v5.2.3 — 2025-09-21

- **Project-Local .cursor Directory**: Fixed initialization to properly create project-local .cursor directories with command and rule assets
- **Local Asset Generation**: Re-enabled local generation of Cursor commands and rules in project .cursor folder
- **Per-Project Initialization**: Ensured each project gets its own .cursor directory with complete asset set
- **Asset Verification**: Updated verification logic to check project-local directories instead of global-only
- **Multi-Project Support**: Projects can now have independent .cursor configurations while maintaining global MCP settings

## v5.2.2 — 2025-09-21

- **Critical .cursor Directory Fix**: Fixed initialization to properly create project-local .cursor directories with command and rule assets
- **Asset Copy Path Resolution**: Resolved path calculation issues for cursor-assets in published npm packages
- **Project-Specific Initialization**: Ensured super-prompt init creates .cursor folder in current working directory
- **Debug Logging Enhancement**: Added detailed logging for troubleshooting initialization issues
- **Multi-Environment Compatibility**: Verified initialization works across different package installation contexts

## v5.2.1 — 2025-09-21

- **Critical Path Resolution**: Fixed asset copying paths to work in both development and published package environments
- **Multi-Path Asset Discovery**: Implemented fallback path resolution for cursor-assets in nested package structures
- **Project-Specific Initialization**: Resolved issue where global installation failed to create project-local .cursor directories
- **Asset Synchronization Fix**: Ensured all 24 command files and 7 rule files are properly copied to project .cursor folder
- **Cross-Environment Compatibility**: Made initialization work consistently across development and npm-published versions

## v5.2.0 — 2025-09-21

- **Critical Initialization Fix**: Fixed super-init command to properly copy all command and rule assets during project setup
- **MCP Tools Availability**: Resolved "no tools" issue by ensuring all 24 MCP tools are properly loaded and accessible
- **Package Distribution**: Updated packaging to include latest command definitions and rule configurations
- **Asset Synchronization**: Enhanced initialization process to automatically sync cursor-assets with project .cursor directory
- **Version Alignment**: Synchronized all package versions (npm, Python, documentation) for consistency

## v5.1.9 — 2025-09-21

- **Documentation Structure**: Reorganized README with Installation section at the top for immediate access
- **Enhanced Quick Start Guide**: Comprehensive 5-step setup guide with detailed explanations and troubleshooting
- **Documentation Localization**: All documentation maintained in English only for consistency
- **Package Optimization**: Streamlined package structure with improved asset organization
- **User Experience Improvements**: Clearer installation instructions and better navigation flow

## v5.1.8 — 2025-09-21

- **Architect Mermaid Integration**: Architect command now always includes Mermaid diagrams for visual architecture representation, with comprehensive diagram types and Cursor documentation references.
- **Explicit MCP Usage**: All command instructions now explicitly require MCP usage with "Use MCP Only:" and "Run Double-Check: Use MCP with" directives across all 24 command files.
- **Enhanced Command Documentation**: Standardized all command documentation with clear MCP-first instructions and explicit execution requirements.
- **Packaging Improvements**: Updated initialization process to ensure all command assets and rules are properly synced during project setup.
- **MCP Architecture Clarity**: Made MCP usage mandatory and explicit throughout all command interfaces and execution checklists.

## v5.1.7 — 2025-09-21

- **Command Standardization**: All Super Prompt commands now feature standardized bodies with clear directives, actionable checklists, and mandatory double-check steps using sp_high (confession review mode).
- **MCP Tool Mapping Clarity**: Execution lines now explicitly show the mapped MCP tool (e.g., "sp_analyzer MCP") for transparent debugging and usage.
- **Installation Consistency**: Ensured super:init applies .cursor/ folder contents identically across fresh installations, with comprehensive asset syncing.
- **MCP Server Conflict Resolution**: Added logic to prevent global/local MCP server conflicts, ensuring only one runtime instance executes per project.
- **Command Frontmatter Automation**: New scripts for bulk updating command metadata, persona args, and frontmatter delimiters across all assets.
- **Documentation Architecture**: Enhanced command documentation with guided execution checklists and MCP tool integration guidance.
- **SDD Workflow Integration**: Strengthened Spec-Driven Development integration with plan delegation for specialized commands (wave, ultracompressed).

## v5.1.6 — 2025-09-21

- Streamlined documentation: Simplified README structure with clearer navigation and focused content.
- Enhanced documentation links: Added direct links to technical documentation in docs/ directory.
- Version synchronization fix: All version displays now correctly show v5.1.6 across CLI, runtime banners, and documentation.
- Enhanced MCP server architecture with improved modularity and stateless stdio entry points.
- Updated persona pipeline system with prompt-based workflows replacing legacy pipeline helpers.
- Refactored MCP server into modular components for better maintainability.
- Added new SDD architecture module with comprehensive Spec Kit lifecycle guidance.
- Improved asset validation and project bootstrap processes.
- Restored full MCP coverage for all Spec Kit personas with shared workflow executor.
- Enhanced troubleshooting persona with updated prompts and command metadata.

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
