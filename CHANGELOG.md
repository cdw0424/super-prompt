# Changelog

## v5.6.0 — 2025-09-26

- **Cross-Platform Init Flow**: `super:init` now prompts for macOS vs Windows (default macOS), stores the selection, and exports `SUPER_PROMPT_TARGET_OS` so follow-up tooling mirrors the choice.
- **Windows-Friendly Paths**: Project-local MCP configs emit the correct executable (`sp-mcp.cmd`) and path separators on Windows, ensuring Cursor launches the server without manual edits.
- **Persistent Config Sync**: The chosen OS is written to `~/.super-prompt/config.json`, reused on subsequent runs, and forwarded into MCP env vars for consistency.
- **Docs Refresh**: README quick start now highlights the new environment prompt and reiterates that it defaults to macOS while guiding Windows users to switch modes.

## v5.5.0 — 2025-09-25

- **Claude Mode & Persona Guidance**: Added `/sp_claude_mode_on|off`, Claude operations/persona guides, manifest overrides, and rule install so Claude can run alongside GPT/Grok.
- **High Reasoning Toggle**: Added `/sp_high_mode_on|off` tools so teams can opt into Codex-backed planning while `/high` and `/sp_high` still force Codex when invoked directly.
- **Language Alignment Rule**: Introduced an always-on rule that mirrors the user’s latest language for every reply while keeping system guidance in English.
- **Command Execution Guarantee**: Rewrote Principle #1 to mandate executing every requested command immediately, eliminating skipped-command regressions.
- **Docs Refresh**: Quick Start now highlights the Claude/high toggles and clarifies language mirroring; version strings bumped to 5.5.0 across npm/Python packages.

## v5.4.1 — 2025-09-24

- **Project Dossier Generation**: `/sp_init` now analyzes the repository and writes `.super-prompt/context/project-dossier.md` so every persona starts with a shared, high-signal brief.
- **Command Awareness**: All command instructions reference the dossier and point users to `/super-prompt/init` when the document is missing.
- **Simplified Permissions**: Init/refresh run by default (set `SUPER_PROMPT_ALLOW_INIT=false` only if you need to block them) and command assets now live solely in the npm package.
- **Analyzer Upgrade**: GPT/Grok analyzer prompts enforce @web reconnaissance with citations, multi-hypothesis scoring, and prevention steps. Dev personas now highlight SSOT alignment and SOLID principles.

## v5.3.0 — 2025-09-24

- **Abstention-First Research Stack**: Added `/sp_resercher` persona, Markdown command guide, GPT/Grok prompt templates, and MCP wiring for evidence-enforced CoVe-RAG workflows.
- **Universal Double-Check**: Introduced `/sp_double_check` command with confession ritual and ensured every persona checklist routes through the audit before handoff.
- **Delivery Playbook Refresh**: Rebuilt `/sp_dev` guidance into phased scope→design→plan→build→handoff execution pipeline.
- **Cursor-Ready Documentation**: Rewrote README to position Super Prompt as Cursor's research & delivery copilot, including SEO/GEO guidance and architecture overview.

## v5.2.65 — 2025-09-23

- **README Touch-ups**: Minor text/anchor updates for clarity and SEO.

## v5.2.60 — 2025-09-22

- **Fixed Assets Path Resolution**: Corrected `assets_root()` in `paths.py` to properly find template files in published npm packages
- **Fixed Command Template Loading**: Removed incorrect `packages/core-py/packages` path that was preventing template files from being found
- **Ensured Full Command Content**: All persona commands now copy complete template content instead of generating minimal stubs

## v5.2.59 — 2025-09-22

- **Fixed Personas Manifest Loading**: Added proper None handling for `yaml.safe_load()` results
- **Enhanced Error Handling**: Fixed `TypeError` when personas manifest is None or empty
- **Improved Manifest Validation**: Added safety checks for manifest structure and personas dictionary
- **Fixed MCP Server Python Path**: Updated `bin/sp-mcp` to use correct Python package
  path (`python-packages/super-prompt-core` instead of `packages/core-py`)
- **Enhanced PYTHONPATH Configuration**: MCP server now properly includes project-local
  Python packages in path resolution
- **Project-local MCP Configuration**: Added automatic creation of `.cursor/mcp.json`
  in project root during initialization for project-specific MCP server isolation
- **Enhanced Project Isolation**: Each project now has its own MCP configuration
  with project-specific paths and environments
- **Improved Cursor IDE Integration**: Cursor can now use project-specific MCP
  configurations instead of relying only on global settings
- **Perfect stdout/stderr Separation**: Complete MCP protocol compliance with zero stdout pollution
- **Fixed Package Root Resolution**: Corrected SUPER_PROMPT_PACKAGE_ROOT environment variable handling in init process
- **Simplified Initialization**: Reduced user inputs from 3 to 1 - now only prompts for project root path, automatically derives MCP server and Python package paths
- **Fixed Command Template Generation**: Fixed CursorAdapter to use correct template paths (`commands/super-prompt/` instead of `templates/`)
- **Fixed NPM Package Files**: Added `packages/` directory to npm package files so that `cursor-assets` are included in published packages

## v5.2.49 — 2025-09-22

- **MCP stdout/stderr Cleanup**: Removed all print statements that could pollute
  MCP protocol communication
- **Enhanced MCP Stability**: Debug prints now conditionally output to stderr
  only when SUPER_PROMPT_DEBUG=1
- **CLI Output Control**: CLI functions now respect MCP_SERVER_MODE environment
  variable to prevent stdout pollution
- **Improved Error Handling**: Better error handling without stdout
  contamination in MCP environments

## v5.2.48 — 2025-09-22

- **Complete MCP Server Integration**: Fully integrated MCP server with 29+ AI
  tools
- **Slash Commands Support**: All tools accessible via Cursor's slash commands
  (/)
- **Enhanced Persona Tools**: Added 6 specialized persona tools for different
  development tasks
- **Context Management Protocol**: Implemented context collection and caching
  system
- **SDD Workflow Tools**: Added Spec-Driven Development workflow tools
- **Zero-Config Setup**: Automatic MCP server registration and configuration
- **Improved Documentation**: Comprehensive English documentation for all
  features

## v5.2.47 — 2025-09-22

- **Robust Python Installation**: Implemented multiple fallback methods for
  Python dependency installation
- **Enhanced Auto-Installation**: More reliable Python package installation
  during npm install
- **Better User Experience**: Improved installation process for new users with
  comprehensive error handling

## v5.2.46 — 2025-09-22

- **Improved Python Dependencies Installation**: Enhanced npm install:python
  script for reliable dependency installation
- **Better postinstall Hook**: Streamlined postinstall process for better
  reliability
- **Enhanced Error Handling**: Improved fallback mechanisms for Python package
  installation

## v5.2.45 — 2025-09-22

- **Auto Python Dependencies**: npm install now automatically installs required
  Python dependencies (typer, pyyaml, pathspec, mcp)
- **Enhanced Installation Experience**: Users no longer need to manually install
  Python packages after npm installation
- **Fixed ModuleNotFoundError**: CLI now works seamlessly without missing
  dependencies

## v5.2.44 — 2025-09-22

- **Version Update**: Latest version with all improvements and bug fixes
- **Enhanced MCP Protocol Compliance**: All MCP functions now properly provide
  JSON-RPC results via stdout
- **Improved stdout/stderr Separation**: MCP server outputs only JSON-RPC
  messages to stdout, all logs to stderr
- **Updated Documentation**: All documentation updated to reflect latest
  features and improvements

## v5.2.43 — 2025-09-22

- **Fixed CLI Module Path**: Corrected Python module paths in CLI script from
  packages/core-py to python-packages/super-prompt-core
- **Enhanced super:init**: Fixed ModuleNotFoundError by using correct Python
  package paths
- **Improved Installation Experience**: Users can now run super:init without
  path issues after npm installation

## v5.2.42 — 2025-09-22

- **MCP stdout Pollution Fix**: Removed all print() statements from MCP server
  modules to prevent JSON-RPC protocol corruption
- **Global MCP Registration**: Enhanced MCP server global registration for
  seamless user experience
- **Enhanced MCP Tool Registry**: All 47+ persona tools properly registered in
  MCP server
- **Improved MCP Protocol Compliance**: MCP server now outputs only JSON-RPC
  messages to stdout, all logs to stderr
- **Updated Documentation**: README and documentation updated to reflect latest
  features and improvements

## v5.2.41 — 2025-09-21

- **Version Update**: Latest version with all improvements and bug fixes

## v5.2.40 — 2025-09-21

- **Python Package Auto-Installation**: npm install 후 super:init 실행 시 Python
  패키지가 자동으로 `.super-prompt/lib/`에 복사됨
- **Enhanced Package Path Resolution**: `SUPER_PROMPT_PACKAGE_ROOT` 환경변수로
  Python 패키지 위치 자동 감지
- **Updated PYTHONPATH**: `python-packages/super-prompt-core` 경로로 Python
  패키지 참조
- **Improved Init Process**: npm 설치만으로 모든 Python 파일이 프로젝트에 자동
  세팅됨
- **Global MCP Only**: MCP 설정을 전역 `~/.cursor/mcp.json`에서만 관리 (프로젝트
  로컬 MCP 설정 제거)

## v5.2.39 — 2025-09-21

- **Python Package Auto-Installation**: npm install 후 super:init 실행 시 Python
  패키지가 자동으로 `.super-prompt/lib/`에 복사됨
- **Enhanced Package Path Resolution**: `SUPER_PROMPT_PACKAGE_ROOT` 환경변수로
  Python 패키지 위치 자동 감지
- **Updated PYTHONPATH**: `python-packages/super-prompt-core` 경로로 Python
  패키지 참조
- **Improved Init Process**: npm 설치만으로 모든 Python 파일이 프로젝트에 자동
  세팅됨
- **Global MCP Only**: MCP 설정을 전역 `~/.cursor/mcp.json`에서만 관리 (프로젝트
  로컬 MCP 설정 제거)

## v5.2.38 — 2025-09-21

- **Bundled Python Copy Fix**: During init, Python package is now copied from
  the bundled install location reliably into `.super-prompt/lib/super_prompt/`
- **Auto CLI Detection**: CLI invocations (init/refresh/version) automatically
  enable CLI mode even if env vars are absent
- **Zero-Config Guarantee**: No env vars or PATH editing required; old wrappers
  are auto-bypassed and CLI mode is enforced
- **Auto-switch Wrapper**: If a Homebrew/old wrapper is first in PATH, auto
  re-exec to npm global binary (~/.local/bin/super-prompt)
- **Fixed Version Display Issue**: Version information now correctly shows the
  actual package version instead of "unknown"
- **Removed Venv References**: Completely removed all virtual environment
  references and messages
- **Cleaned Up Dependencies Message**: Changed "venv functionality removed" to
  clean "Using system Python"
- **Enhanced CLI Prompt Readability**: Added visual separators and clear
  formatting for user input prompts
- **Improved Interactive Initialization**: User inputs now have clear visual
  boundaries with decorative separators
- **Better Input Prompts**: Added emojis and clear formatting for project root,
  MCP server, and Python package paths
- **Enhanced CLI Mode**: All CLI commands now work without requiring
  SUPER_PROMPT_ALLOW_DIRECT=true
- **Improved CLI User Experience**: CLI mode automatically disables MCP-only
  enforcement for better usability
- **Simplified CLI Usage**: No need to set environment variables for basic CLI
  operations
- **Maintained MCP Security**: MCP-only enforcement still active for non-CLI
  operations
- **Fixed MCP Server Python Path Issue**: MCP server now correctly uses
  .super-prompt/lib/ Python packages
- **User-Centric Python Path Resolution**: All commands prioritize user's
  project .super-prompt/lib/ over system packages
- **Enhanced Package Discovery**: Improved PYTHONPATH resolution for both MCP
  server and CLI tools
- **Fixed "no tools" Error**: MCP server can now properly find and load all
  Super Prompt tools after initialization
- **Enhanced CLI User Experience**: Improved readability by hiding debug logs in
  CLI mode
- **Cleaner Initialization Output**: User input prompts are now clearly visible
  without debug message interference
- **Better Visual Separation**: Debug logs are hidden in CLI mode for better
  user experience
- **Fixed MCP Server Interference**: Removed MCP module imports from mode change
  functions to prevent server state disruption
- **Improved Mode Switching**: Mode changes (grok/gpt) no longer affect MCP tool
  availability
- **Enhanced Stability**: MCP server remains stable during mode transitions
- **Interactive Initialization**: Added dialog-based input for project root, MCP
  server path, and Python package path
- **Enhanced MCP Path Configuration**: Users can now specify custom paths for
  MCP server and Python packages during initialization
- **Improved User Experience**: Initialization process now asks for user input
  when needed instead of using defaults
- **Flexible Path Management**: Support for custom installation paths while
  maintaining backward compatibility

## v5.2.22 — 2025-09-21

- **Pure npm Self-Contained Package**: All Python files now copied from npm
  package to .super-prompt/lib/ - no pip install needed
- **Simplified Dependency Management**: No more pip install complications -
  everything comes from npm package
- **Complete Project Isolation**: Every Super Prompt component contained within
  .super-prompt/ folder for maximum portability
- **Enhanced .super-prompt Structure**: Added lib/ folder containing all Python
  packages that users can directly inspect
- **PYTHONPATH Configuration**: MCP server configured to use .super-prompt/lib/
  in PYTHONPATH for seamless operation
- **Complete Project Isolation**: All Super Prompt files and dependencies
  contained within .super-prompt/ folder
- **Silent MCP Server**: Completely disabled all logging and progress output in
  MCP server to prevent protocol interference
- **Clean MCP Protocol**: MCP server now runs in complete silence, preventing
  "no tools" detection issues
- **Silent Progress Class**: Added SilentProgress class to replace
  progress.show_* methods with no-op implementations
- **Complete Initialization Process**: Added comprehensive setup including
  Python package installation and all configuration files
- **Super Prompt Internal Files**: Now creates .super-prompt/config.json,
  mode.json, cache/context_cache.json
- **Python Package Installation**: Automatically installs super-prompt-core
  package during initialization
- **Absolute Path MCP Configuration**: Changed MCP command to use absolute path
  based on user-specified project root

## v5.2.6 — 2025-09-21

- **CursorAdapter Template Source Fix**: Fixed generate_commands and
  generate_rules to copy from commands/rules directories instead of non-existent
  templates directory
- **Asset Path Correction**: Corrected source paths to use actual cursor-assets
  structure (commands/ and rules/ subdirectories)
- **Template-to-Source Mapping**: Updated file copying logic to match actual
  package structure in both development and published environments
- **Asset Discovery Enhancement**: Improved path resolution for command and rule
  file sources across different installation contexts

## v5.2.5 — 2025-09-21

- **Asset Template Path Resolution**: Fixed CursorAdapter to properly locate
  templates in both development and published package environments
- **Multi-Path Template Discovery**: Implemented fallback path resolution for
  command and rule templates across different package structures
- **Published Package Compatibility**: Ensured generate_commands and
  generate_rules work correctly in npm-published packages
- **Template File Copy Fix**: Resolved issue where command and rule templates
  were not being copied to project .cursor directories

## v5.2.4 — 2025-09-21

- **Asset Path Resolution**: Fixed assets_root() function to correctly locate
  cursor-assets in both development and published package environments
- **Cross-Platform Compatibility**: Ensured proper path resolution for nested
  package structures in npm-published versions
- **Project .cursor Directory**: Final fix for proper creation of project-local
  .cursor directories with all command and rule assets
- **Published Package Structure**: Corrected asset discovery logic for npm
  registry package layout

## v5.2.3 — 2025-09-21

- **Project-Local .cursor Directory**: Fixed initialization to properly create
  project-local .cursor directories with command and rule assets
- **Local Asset Generation**: Re-enabled local generation of Cursor commands and
  rules in project .cursor folder
- **Per-Project Initialization**: Ensured each project gets its own .cursor
  directory with complete asset set
- **Asset Verification**: Updated verification logic to check project-local
  directories instead of global-only
- **Multi-Project Support**: Projects can now have independent .cursor
  configurations while maintaining global MCP settings

## v5.2.2 — 2025-09-21

- **Critical .cursor Directory Fix**: Fixed initialization to properly create
  project-local .cursor directories with command and rule assets
- **Asset Copy Path Resolution**: Resolved path calculation issues for
  cursor-assets in published npm packages
- **Project-Specific Initialization**: Ensured super-prompt init creates .cursor
  folder in current working directory
- **Debug Logging Enhancement**: Added detailed logging for troubleshooting
  initialization issues
- **Multi-Environment Compatibility**: Verified initialization works across
  different package installation contexts

## v5.2.1 — 2025-09-21

- **Critical Path Resolution**: Fixed asset copying paths to work in both
  development and published package environments
- **Multi-Path Asset Discovery**: Implemented fallback path resolution for
  cursor-assets in nested package structures
- **Project-Specific Initialization**: Resolved issue where global installation
  failed to create project-local .cursor directories
- **Asset Synchronization Fix**: Ensured all 24 command files and 7 rule files
  are properly copied to project .cursor folder
- **Cross-Environment Compatibility**: Made initialization work consistently
  across development and npm-published versions

## v5.2.0 — 2025-09-21

- **Critical Initialization Fix**: Fixed super-init command to properly copy all
  command and rule assets during project setup
- **MCP Tools Availability**: Resolved "no tools" issue by ensuring all 24 MCP
  tools are properly loaded and accessible
- **Package Distribution**: Updated packaging to include latest command
  definitions and rule configurations
- **Asset Synchronization**: Enhanced initialization process to automatically
  sync cursor-assets with project .cursor directory
- **Version Alignment**: Synchronized all package versions (npm, Python,
  documentation) for consistency

## v5.1.9 — 2025-09-21

- **Documentation Structure**: Reorganized README with Installation section at
  the top for immediate access
- **Enhanced Quick Start Guide**: Comprehensive 5-step setup guide with detailed
  explanations and troubleshooting
- **Documentation Localization**: All documentation maintained in English only
  for consistency
- **Package Optimization**: Streamlined package structure with improved asset
  organization
- **User Experience Improvements**: Clearer installation instructions and better
  navigation flow

## v5.1.8 — 2025-09-21

- **Architect Mermaid Integration**: Architect command now always includes
  Mermaid diagrams for visual architecture representation, with comprehensive
  diagram types and Cursor documentation references.
- **Explicit MCP Usage**: All command instructions now explicitly require MCP
  usage with "Use MCP Only:" and "Run Double-Check: Use MCP with" directives
  across all 24 command files.
- **Enhanced Command Documentation**: Standardized all command documentation
  with clear MCP-first instructions and explicit execution requirements.
- **Packaging Improvements**: Updated initialization process to ensure all
  command assets and rules are properly synced during project setup.
- **MCP Architecture Clarity**: Made MCP usage mandatory and explicit throughout
  all command interfaces and execution checklists.

## v5.1.7 — 2025-09-21

- **Command Standardization**: All Super Prompt commands now feature
  standardized bodies with clear directives, actionable checklists, and
  mandatory double-check steps using sp_high (confession review mode).
- **MCP Tool Mapping Clarity**: Execution lines now explicitly show the mapped
  MCP tool (e.g., "sp_analyzer MCP") for transparent debugging and usage.
- **Installation Consistency**: Ensured super:init applies .cursor/ folder
  contents identically across fresh installations, with comprehensive asset
  syncing.
- **MCP Server Conflict Resolution**: Added logic to prevent global/local MCP
  server conflicts, ensuring only one runtime instance executes per project.
- **Command Frontmatter Automation**: New scripts for bulk updating command
  metadata, persona args, and frontmatter delimiters across all assets.
- **Documentation Architecture**: Enhanced command documentation with guided
  execution checklists and MCP tool integration guidance.
- **SDD Workflow Integration**: Strengthened Spec-Driven Development integration
  with plan delegation for specialized commands (wave, ultracompressed).

## v5.1.6 — 2025-09-21

- Streamlined documentation: Simplified README structure with clearer navigation
  and focused content.
- Enhanced documentation links: Added direct links to technical documentation in
  docs/ directory.
- Version synchronization fix: All version displays now correctly show v5.1.6
  across CLI, runtime banners, and documentation.
- Enhanced MCP server architecture with improved modularity and stateless stdio
  entry points.
- Updated persona pipeline system with prompt-based workflows replacing legacy
  pipeline helpers.
- Refactored MCP server into modular components for better maintainability.
- Added new SDD architecture module with comprehensive Spec Kit lifecycle
  guidance.
- Improved asset validation and project bootstrap processes.
- Restored full MCP coverage for all Spec Kit personas with shared workflow
  executor.
- Enhanced troubleshooting persona with updated prompts and command metadata.

## v5.1.5 — 2025-09-21

- Simplified Quick Start: Streamlined installation with project-local setup as
  the primary method.
- Version synchronization fix: All version displays now correctly show v5.1.5
  across CLI, runtime banners, and documentation.
- Enhanced MCP server architecture with improved modularity and stateless stdio
  entry points.
- Updated persona pipeline system with prompt-based workflows replacing legacy
  pipeline helpers.
- Refactored MCP server into modular components for better maintainability.
- Added new SDD architecture module with comprehensive Spec Kit lifecycle
  guidance.
- Improved asset validation and project bootstrap processes.
- Restored full MCP coverage for all Spec Kit personas with shared workflow
  executor.
- Enhanced troubleshooting persona with updated prompts and command metadata.

## v5.1.4 — 2025-09-21

- Enhanced troubleshooting guide: Comprehensive installation troubleshooting for
  legacy version issues.
- Version synchronization fix: All version displays now correctly show v5.1.4
  across CLI, runtime banners, and documentation.
- Enhanced MCP server architecture with improved modularity and stateless stdio
  entry points.
- Updated persona pipeline system with prompt-based workflows replacing legacy
  pipeline helpers.
- Refactored MCP server into modular components for better maintainability.
- Added new SDD architecture module with comprehensive Spec Kit lifecycle
  guidance.
- Improved asset validation and project bootstrap processes.
- Restored full MCP coverage for all Spec Kit personas with shared workflow
  executor.
- Enhanced troubleshooting persona with updated prompts and command metadata.

## v5.1.3 — 2025-09-21

- Enhanced installation guidance: Clear instructions to always install the
  latest version for optimal experience.
- Version synchronization fix: All version displays now correctly show v5.1.3
  across CLI, runtime banners, and documentation.
- Enhanced MCP server architecture with improved modularity and stateless stdio
  entry points.
- Updated persona pipeline system with prompt-based workflows replacing legacy
  pipeline helpers.
- Refactored MCP server into modular components for better maintainability.
- Added new SDD architecture module with comprehensive Spec Kit lifecycle
  guidance.
- Improved asset validation and project bootstrap processes.
- Restored full MCP coverage for all Spec Kit personas with shared workflow
  executor.
- Enhanced troubleshooting persona with updated prompts and command metadata.

## v5.1.1 — 2025-09-21

- Version synchronization fix: All version displays now correctly show v5.1.1
  across CLI, runtime banners, and documentation.
- Enhanced MCP server architecture with improved modularity and stateless stdio
  entry points.
- Updated persona pipeline system with prompt-based workflows replacing legacy
  pipeline helpers.
- Refactored MCP server into modular components for better maintainability.
- Added new SDD architecture module with comprehensive Spec Kit lifecycle
  guidance.
- Improved asset validation and project bootstrap processes.
- Restored full MCP coverage for all Spec Kit personas with shared workflow
  executor.
- Enhanced troubleshooting persona with updated prompts and command metadata.

## v5.1.0 — 2025-09-21

- Enhanced MCP server architecture with improved modularity and stateless stdio
  entry points
- Updated persona pipeline system with prompt-based workflows replacing legacy
  pipeline helpers
- Refactored MCP server into modular components for better maintainability
- Added new SDD architecture module with comprehensive Spec Kit lifecycle
  guidance
- Improved asset validation and project bootstrap processes
- Restored full MCP coverage for all Spec Kit personas with shared workflow
  executor
- Enhanced troubleshooting persona with updated prompts and command metadata
- Synchronized versioning across Node package, Python core, and runtime banners
- Updated documentation and README with current setup guidance in English
- Cleaned up deprecated GitHub workflow files and redundant manifest
  configurations

## v5.0.5 — 2025-09-21

- Detect FastMCP automatically and fall back to a lightweight stdio loop when
  the runtime is unavailable, ensuring MCP tools always register.
- Provide explicit names for every `@mcp.tool` decorator so Cursor receives the
  canonical SSOT tool identifiers.
- Align Node and Python package versions (5.0.5) and surface the same number
  through runtime banners.
- Add `mcp>=0.4.0` to the Python core dependencies to ship FastMCP with the npm
  package.
- Refresh README documentation in English with updated quick start,
  troubleshooting, and release workflow guidance.
- Introduce the `sp.sdd_architecture` MCP tool plus persona overlays so every
  persona response references the Spec Kit SDD lifecycle.
- Added an SDD architecture knowledge base that maps Spec Kit stages,
  components, and runner contracts into reusable guidance.
- Restored MCP coverage for all Spec Kit personas (`sp_dev`, `sp_doc_master`,
  `sp_service_planner`, etc.) using a shared workflow executor and SDD-aligned
  guidance.
- Renamed the `tr` persona to full Troubleshooting mode with updated prompts,
  overlays, and command metadata.

## v5.0.0 — 2025-09-20

- Migrated all personas to prompt-based workflows and retired pipeline helper
  logic.
- Introduced mode-specialized prompt templates for GPT and Grok personas.
- Refactored the MCP server into modular components with a stateless stdio entry
  point.
- Hardened `super:init`, MCP diagnostics, and asset validation for project
  bootstrap scenarios.
- Expanded the CLI with interactive MCP modes and watch-based development tools.
