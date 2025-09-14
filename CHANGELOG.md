# Changelog

## v4.0.0 - 2025-09-14

### 🚀 **v4.0.0: The MCP Revolution**

This is a monumental upgrade that refactors the entire `super-prompt` architecture to be MCP-first, providing a robust, programmatic interface for IDEs and other clients. Legacy CLI execution has been deprecated in favor of a powerful and extensible MCP server.

### ✨ Major Features & Architectural Changes

- **👑 MCP-First Architecture**: The core logic is now exposed via a **FastMCP server** (`packages/core-py/super_prompt/mcp_srv/server.py`). All personas and utilities are available as discrete MCP tools, enabling seamless IDE integration.
- **🧠 Fused Intelligent Memory System**:
    - **EvolKV LLM Optimization**: A new SQLite-backed memory system (`evol_kv_memory.db`) based on the "Evol-Instruct" concept to persist and evolve task-aware KV-cache profiles, optimizing LLM inference performance over time.
    - **Context-Aware Memory**: A simple, persistent SQLite-backed key-value store (`context_memory.db`) to maintain task context (e.g., `current_task_tag`) across sessions, ensuring continuity.
- **🕵️‍♂️ Confession Mode (더블 체크)**: A unique self-auditing decorator (`@confession_decorator`) has been applied to **all MCP tools**. After every operation, the tool provides an honest assessment of what it knows, what it *doesn't* know (potential side-effects, edge cases), and suggests countermeasures, enhancing reliability and transparency.
- **🐍 Encapsulated Python Environment**: The entire Python backend, including the MCP server and all utilities, is now managed as a proper Python package (`packages/core-py`) and runs within a dedicated, self-contained virtual environment (`venv`) created automatically during installation. This eliminates system dependency conflicts.
- **🧹 Comprehensive Legacy Cleanup**: Removed dozens of legacy files, including old CLI wrappers (`bin/sp`, `bin/codex-*`), redundant Python scripts, and obsolete scaffolding and template assets. The `package.json` has been streamlined to match the new architecture.

### 🔄 Migration for Existing Users

Migrating from v3.x is seamless. No manual steps are required.

```bash
# Simply run the install/update command
npm install -g @cdw0424/super-prompt@latest
```

The new installation script (`install.js`) handles everything:
1.  It sets up the new encapsulated Python `venv`.
2.  It installs the `super_prompt` Python package and all its dependencies.
3.  The main `super-prompt` command is automatically linked to the new MCP-aware entry point.

**Note**: Old files from previous versions in your project's `.super-prompt` directory are no longer used and can be safely deleted. The new version will create its databases (`evol_kv_memory.db`, `context_memory.db`) inside your project's `.super-prompt` folder upon first use.

## v3.1.73 - 2025-09-14

### 🔄 Enhanced Exclusive Mode Switching
- feat(mode): Support both short and long mode command variants (`/grok-on` + `/grok-mode-on`, `/codex-on` + `/codex-mode-on`)
- feat(mode): Support both short and long mode off commands (`/grok-off` + `/grok-mode-off`, `/codex-off` + `/codex-mode-off`)
- fix(mode): Ensure all grok/codex mode commands trigger exclusive switching
- docs: Updated to reflect comprehensive mode command support

## v3.1.72 - 2025-09-14

### 🔄 Exclusive Mode Switching
- feat(mode): Implement exclusive grok/codex mode switching - enabling one automatically disables the other
- feat(tag-executor): Enhanced tag-executor.sh with mode management for automatic file-based state switching
- fix(mode): grok-mode-on now removes .codex-mode and creates .grok-mode
- fix(mode): codex-mode-on now removes .grok-mode and creates .codex-mode
- docs: Updated mode commands to reflect exclusive behavior

## v3.1.71 - 2025-09-14

### 🔧 Codex AMR Mode Toggle System
- feat(mode): Add codex mode toggle commands (`codex-mode-on`, `codex-mode-off`, `codex`)
- feat(mode): Create `.codex-mode` flag file for mode state tracking
- feat(mode): Implement codex-amr mode system similar to grok mode
- docs: Update command descriptions for codex AMR auto model routing

## v3.1.65 - 2025-09-14

### 🏷️ Flag-only mode (no prefix required)
- feat(cli): New `sp` ultra-minimal wrapper to run `--sp-*` flags directly.
- feat(cli): New `sp-setup-shell` to enable shell-level handler so that commands starting with `--sp-*` are automatically routed to `sp`. Example: `--sp-analyzer "..."`.

## v3.1.64 - 2025-09-14

### 🧰 No-global fallback (works without super-prompt)
- feat(tag-executor): Prefer project-local Python CLI `.super-prompt/cli.py` (venv if present) so commands work without a global `super-prompt` binary or network access. Fallbacks remain: global binary → npx.

## v3.1.63 - 2025-09-14

### 🧪 Persona flag reliability (--sp-*)
- fix(bin): When using `--sp-<persona>` (e.g., `--sp-analyzer`), the wrapper now ensures PyYAML is available before executing the enhanced persona processor. Resolves failures on systems without preinstalled PyYAML.

## v3.1.62 - 2025-09-14

### 🧵 Exact tag-executor byte match
- fix(init): Write tag-executor.sh via line-joined string (no trailing newline) so it exactly matches the template copied by installer.

## v3.1.61 - 2025-09-14

### 📦 Rules from templates + package fix
- fix(rules): `super:init` copies all `.mdc` rules from packaged templates (`packages/cursor-assets/templates`) to ensure identical content across environments.
- fix(amr): `amr:rules` also copies `05-amr.mdc` from templates (fallback writes a minimal placeholder only if templates missing).
- chore(pkg): Ran `npm pkg fix` to normalize `bin` paths and tidy package metadata.

## v3.1.60 - 2025-09-14

### 🧩 Canonical tag-executor everywhere
- fix(init): super:init writer now emits the exact same canonical tag-executor.sh as the installer/templates (comments + trailing newline), eliminating byte-level drift.
- chore(docs): README updated to reflect v3.1.60 verification.

## v3.1.59 - 2025-09-14

### 🛠️ Canonical tag executor & drift fix
- fix(templates): Replace tag-executor.sh with canonical minimal wrapper that delegates to `super-prompt optimize` (or `npx` fallback).
- fix(install): Ensure install.js copies the same canonical tag-executor to `.cursor/commands/super-prompt/` with clear logging.
- fix(cursor-adapter): Generation path now pulls the same template, guaranteeing identical assets across install and `super:init`.
- docs: Update README to reflect v3.1.59 and drift fix.

## v3.1.56 - 2025-09-14

### 🚀 **COMPLETE .super-prompt DIRECTORY SYNCHRONIZATION**

- **🎯 EXTENDED TEMPLATE SYSTEM**: Solved the broader problem of .super-prompt directory inconsistency between development environment and user installations
- **📁 FORCE COPY ADVANCED .super-prompt UTILITIES**: All .super-prompt files now use templates as the single source of truth, eliminating version drift
- **🔧 ENHANCED install.js**: Updated installation script to force-copy entire .super-prompt directory from templates instead of using potentially outdated local files
- **📦 COMPREHENSIVE ASSET MIGRATION**: Migrated ALL .super-prompt files including:
  - **CLI utilities**: cli.py, enhanced_persona_processor.py, context_injector.py, etc.
  - **Configuration files**: config.json, personas.yaml, execution_context.json
  - **Processor scripts**: All cursor-processor files with enhanced functionality
  - **Utility modules**: quality_enhancer.py, fallback_memory.py, sdd modules
  - **Template assets**: prisma templates, simple_cli.py, etc.
- **✅ PERFECT CONSISTENCY**: Every file in .super-prompt directory now matches exactly between development environment and all user projects
- **📦 PACKAGES SYNCHRONIZATION ADDED**: Extended template system to include complete packages/ directory
  - **core-py**: Complete Python core library with all modules and dependencies
  - **cli-node**: Node.js CLI wrapper with executable scripts and configurations
  - **cursor-assets**: All Cursor IDE assets, manifests, and enhanced templates
- **🔧 ENHANCED INSTALLATION**: Updated install.js to force-copy entire packages suite alongside .super-prompt
- **📦 PACKAGES DIRECTORY FULLY SYNCHRONIZED**: Added complete packages/ directory synchronization including:
  - **core-py**: Full Python core library with all modules and dependencies
  - **cli-node**: Complete Node.js CLI wrapper with all scripts and configurations
  - **cursor-assets**: All Cursor IDE assets, manifests, and enhanced templates
- **🔄 FUTURE-PROOF**: Template system now prevents any future version drift issues across ALL project files
- **📊 DYNAMIC VERSION DISPLAY**: Added automatic version detection from package.json for accurate version display in CLI
- **🔍 ENHANCED ANALYZER COMMAND**: Improved analyzer command description with more detailed capabilities and expertise areas

## v3.1.58 - 2025-09-14
- **🐛 FIXED**: `super-prompt init` now correctly displays the latest dynamic version instead of the outdated `v2.9.1`.
- **🛠️ REFACTORED**: Unified all CLI command executions to a single, consistent entry point (`.super-prompt/cli.py`), eliminating architectural debt from legacy files.
- **🧹 CLEANED**: Removed obsolete legacy `cli.py` and redundant `cursor_adapter.py` copy logic from the installation process for a cleaner and more reliable package.

## v3.1.48 - 2025-09-14

### 🚀 **FORCED ADVANCED TAG-EXECUTOR.SH IMPLEMENTATION**

- **🎯 ROOT CAUSE RESOLVED**: Critical issue where `super-prompt super:init` was generating 7-line basic version instead of 599-line advanced tag-executor.sh
- **💪 FORCE IMPLEMENTATION**: 
  - **install.js**: Added forced copy of advanced tag-executor.sh during installation
  - **project_scaffold.py**: Enhanced to always prioritize advanced version from multiple possible locations
  - **Multi-path Search**: Implemented fallback system searching multiple locations for advanced version
- **🔧 TECHNICAL FIXES**:
  - Modified installation script to guarantee advanced version deployment
  - Enhanced project scaffold to detect and use advanced tag-executor.sh
  - Added comprehensive error handling and logging for debugging
- **✅ RESULT**: All new installations now get the full-featured 599-line advanced tag-executor.sh
- **🎉 IMPACT**: Users get consistent advanced functionality across all environments

## v3.1.46 - 2025-09-14

### 🔧 **COMPREHENSIVE CONSISTENCY FIX**: Development vs Generated File Synchronization

- **🎯 ROOT CAUSE IDENTIFIED**: Critical inconsistency discovered between development environment files and files generated during `super-prompt super:init` initialization. This affected all command templates, icons, descriptions, and supporting files.

- **📦 SOLUTION IMPLEMENTED**: Complete template system overhaul:
  - **Template Migration**: Moved all current project `.md` command files, `README.md`, `health-report.json`, and other assets to `packages/cursor-assets/templates/`
  - **Adapter Refactoring**: Updated `cursor_adapter.py` to use templates as the primary source instead of generating from scratch
  - **Consistency Guarantee**: All files now match exactly between development environment and user installations
  - **Fallback System**: Maintained robust fallback generation for edge cases

- **🔄 FILES SYNCHRONIZED**:
  - All 35+ `.md` command files with correct icons and descriptions
  - `tag-executor.sh` (advanced 599-line version)
  - `README.md` and `health-report.json`
  - SDD workflow command files

- **✅ IMPACT**: Users installing v3.1.46+ will get identical experience to the development environment, eliminating confusion and ensuring feature parity.

## v3.1.39 - 2025-09-14

### 🐛 **CRITICAL FIX**: Complete Command Installation

- **Problem**: A critical packaging bug was discovered where `npm install -g @cdw0424/super-prompt` only installed a small subset of the available commands (approx. 8 instead of 35+). The issue was caused by an incomplete `"files"` array in `package.json` that excluded the `.cursor` directory, which contains all command definitions and supporting scripts.
- **Solution**:
  - **`package.json`**: Modified the `"files"` array to explicitly include the `.cursor` directory, ensuring all necessary files are bundled in the published npm package.
  - **`bin/super-prompt`**: Reworked the initialization logic to bypass the older, limited Python CLI and directly execute the full-featured initialization script located at `.cursor/commands/super-prompt/.super-prompt/utils/cli.py`. This ensures the installer has access to and correctly creates all 35+ commands.
- **Impact**: All users installing v3.1.39 and later will now have the complete suite of `super-prompt` commands installed correctly. This resolves the core issue of missing commands in new environments.

## v3.1.38 - 2025-09-14

### 🐛 Critical Display Bug Fix - Command Visibility

- **🔧 Fixed Command Display**: Resolved critical user experience issue where `super-prompt super:init` only displayed 8 commands in the "Available:" message instead of all 35+ commands
- **📋 Complete Command Listing**: Updated initialization output to show all available commands:
  - **Core Personas (8)**: `/high`, `/frontend-ultra`, `/frontend`, `/backend`, `/analyzer`, `/architect`, `/seq`, `/seq-ultra`
  - **Additional Personas (17)**: `/debate`, `/performance`, `/security`, `/task`, `/wave`, `/ultracompressed`, `/docs-refector`, `/refactorer`, `/implement`, `/review`, `/dev`, `/devops`, `/doc-master`, `/mentor`, `/qa`, `/scribe`
  - **SDD Workflow (6)**: `/spec`, `/plan`, `/tasks`, `/specify`, `/optimize`, `/tr`
  - **Special Commands (2)**: `/init-sp`, `/re-init-sp`
  - **Grok Integration (3)**: `/grok`, `/grok-on`, `/grok-off`

### 📊 Impact Assessment

- **Before**: Users saw only 8/35+ commands (23% visibility)
- **After**: Users see all 35+ commands (100% visibility)
- **User Experience**: Complete transparency in available commands
- **Discovery**: Improved command discoverability and usage

## v3.1.37 - 2025-09-14

### 🧠 Memory System Enhancement - Real-time Context Loading

- **🔄 DB Context Integration**: Confirmed and documented real-time DB context loading from `memory/ltm.db` during command execution
- **💬 Conversation History Persistence**: Verified conversation history persistence with recent 8 messages retrieval per session
- **📊 Project State Tracking**: Enhanced project state tracking through SDD compliance checking (SPEC/PLAN files)
- **🔗 Context Continuity**: Improved context continuity across sessions using SQLite-backed memory controller
- **📈 Performance Optimization**: Optimized memory queries with LIMIT 8 for recent chat history

### 📝 Memory System Architecture

```sql
-- Real-time context loading query
SELECT author, body FROM memory
WHERE project_id=? AND kind='message'
ORDER BY id DESC LIMIT 8
```

### 🔍 Context Building Process

1. **Project Detection**: Auto-detect project from user input or use default
2. **DB Query**: Retrieve recent conversation history from SQLite database
3. **SDD Context**: Load SPEC/PLAN files and framework detection
4. **Context Injection**: Build comprehensive context block for AI processing
5. **Session Persistence**: Store new interactions back to database

## v3.1.36 - 2025-09-14

### 🐛 Critical Initialization Bug Fix

- **🔧 Fixed Command Installation**: Resolved critical bug where `super-prompt super:init` only installed 8 commands instead of all 35+ available commands
- **📋 Complete Persona Support**: Updated `install_cursor_commands_in_project()` function to properly generate all Cursor command files:
  - Core Personas (8): high, frontend-ultra, frontend, backend, analyzer, architect, seq, seq-ultra
  - Additional Personas (17): debate, performance, security, task, wave, ultracompressed, docs-refector, refactorer, implement, review, dev, devops, doc-master, mentor, qa, scribe
  - SDD Workflow (6): spec, plan, tasks, specify, optimize, tr
  - Special Commands (2): init-sp, re-init-sp
  - Grok Integration (3): grok, grok-on, grok-off

- **🎯 Path Corrections**: Fixed tag-executor.sh path references to use correct absolute paths
- **⚙️ Special Command Handling**: Properly configured init-sp and re-init-sp to run Python scripts directly with correct --mode parameters

### 📊 Impact Assessment

- **Before**: Only 8/35+ commands installed (23% coverage)
- **After**: All 35+ commands installed (100% coverage)
- **User Experience**: Complete command set now available after `super-prompt super:init`

## v3.1.32 - 2025-09-14

### 🎨 Visual Enhancement

- **🎯 Added ASCII Art Banner**: Restored beautiful ASCII art logo to `super-prompt super:init` command
- **🇰🇷 Korean Pride**: Added "Made by Daniel Choi from Korea" signature to init display
- **🌈 Colorful Display**: Enhanced visual presentation with cyan/magenta color scheme matching install script

```
   ███████╗██╗   ██╗██████╗ ███████╗██████╗
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗
   ███████╗██║   ██║██████╔╝█████╗  ██████╔╝
   ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗
   ███████║╚██████╔╝██║     ███████╗██║  ██║
   ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝

   ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ████████╗
   ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝
   ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝   ██║
   ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝    ██║
   ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║        ██║
   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝
              Dual IDE Prompt Engineering Toolkit
                 Made by Daniel Choi from Korea
```

## v3.1.31 - 2025-09-14

### 🐍 Python Virtual Environment Auto-Setup Enhancement

- **🔧 Fixed Virtual Environment Detection**: Resolved issue where `super-prompt super:init` failed to detect existing virtual environments
- **📁 Improved Path Resolution**: Fixed pyproject.toml path resolution from `parents[2]` to `parents[1]` for correct dependency detection
- **⚡ Smart Dependency Checking**: Added intelligent check for existing dependencies before attempting installation
- **🛡️ Homebrew Compatibility**: Enhanced compatibility with macOS Homebrew's externally-managed Python environments
- **🎯 Grok-Optimized**: Added documentation highlighting optimization for [grok-code-fast-1 MAX mode] in Cursor IDE

### 🔄 Installation Flow Improvements

```python
# Enhanced virtual environment detection logic:
if venv_python.exists():
    # Check if dependencies are already installed
    result = subprocess.run([
        str(venv_python), "-c",
        "import typer, yaml, pathspec; print('Dependencies available')"
    ], check=True, capture_output=True, text=True)
    if "Dependencies available" in result.stdout:
        typer.echo("   ✅ Virtual environment and dependencies already available")
        venv_ready = True
```

### 📚 Documentation Updates

- **🆘 Enhanced Troubleshooting**: Added comprehensive Python environment troubleshooting section
- **🤖 Grok Integration**: Documented Cursor IDE grok-code-fast-1 MAX mode optimization
- **🔧 macOS Homebrew Guide**: Added specific guidance for Homebrew Python environment issues

## v3.1.30 - 2025-09-13

### 🎯 Enhanced Persona System with Mandatory Core Development Principles

- **🛡️ Quality Assurance Framework**: Added mandatory core development principles to all personas
- **🏗️ SOLID Principles**: Enforced Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion across all development personas
- **🧪 TDD/BDD Integration**: Mandatory test-first development approach with comprehensive test coverage requirements
- **🏛️ Clean Architecture**: Enforced proper layering (Presentation → Domain → Infrastructure) with clear separation of concerns
- **⚠️ Over-engineering Prevention**: Added guidelines to prefer simple solutions and avoid premature optimization
- **🧐 Confession & Double-Check**: Implemented mandatory self-review methodology for validating assumptions and critical decisions
- **📋 Code Quality Standards**: Standardized patterns, maintainability requirements, and self-documenting code practices

### 🔧 Technical Implementation

```yaml
# Added to all development personas:
CORE DEVELOPMENT PRINCIPLES (MANDATORY):
- SOLID Principles: Always follow Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion
- TDD/BDD: Write tests first, ensure comprehensive test coverage, practice test-driven development
- Clean Architecture: Maintain clear separation of concerns with proper layering (Presentation → Domain → Infrastructure)
- No Over-engineering: Prefer simple solutions, avoid premature optimization, implement only what's needed
- Code Quality: Follow established patterns, ensure maintainability, write self-documenting code
- Confession & Double-Check: Always perform self-review through confession methodology, validate assumptions, and double-check critical decisions before implementation
```

### 📈 Quality & Consistency Improvements

- **10 Personas Enhanced**: architect, backend, frontend, dev, refactorer, analyzer, implement, troubleshooter, performance, high
- **Standardized Approach**: Consistent development methodology across all personas
- **Quality Gates**: Mandatory principles ensure consistent code quality and architectural decisions
- **Self-Review Process**: Built-in confession methodology for critical decision validation

## v3.1.25 - 2025-09-13

### 🎯 Installation Simplification & PATH Issue Resolution

- **🚫 Removed PATH Migration Logic**: Eliminated problematic npm prefix modification that forced `.npm-global` usage
- **🏠 Use System Defaults**: Installation now uses system npm defaults (Homebrew `/opt/homebrew/bin` on macOS)
- **✨ Zero Configuration**: No PATH configuration needed - works immediately after `npm install -g`
- **🧹 Simplified Troubleshooting**: Streamlined README with basic installation troubleshooting only

### 🔧 Technical Changes
```bash
# Before: Forced npm prefix change causing PATH issues
npm config set prefix ~/.npm-global  # ❌ Removed

# After: Use system defaults that are already in PATH
# /opt/homebrew/bin is already in macOS PATH ✅
```

### 📚 Documentation Cleanup
- **Removed**: Complex cross-platform PATH configuration guides
- **Simplified**: Basic troubleshooting with standard npm commands
- **Focus**: Install → Use, no configuration steps

### 🎉 User Experience
- **Install**: `npm install -g @cdw0424/super-prompt@latest`
- **Use**: `super-prompt super:init` (works immediately)
- **No**: PATH configuration, shell setup, or manual exports needed

## v3.1.24 - 2025-09-13

### 🪟 Cross-Platform Support & Windows Enhancement

- **🔧 Enhanced Platform Detection**: Robust platform detection in bash script supporting MINGW, MSYS, CYGWIN, Windows_NT environments
- **🪟 Windows PATH Configuration**: Native Windows PATH setup via PowerShell and registry modification
- **🐍 Windows Python venv**: Proper Windows virtual environment path handling (`Scripts/python.exe` vs `bin/python`)
- **📚 Platform-Specific Documentation**: Separate Mac/Linux and Windows troubleshooting sections

### 🛠️ Technical Improvements
```bash
# Enhanced platform detection
case "$platform" in
  Darwin|Linux|*BSD*)     # Unix-like systems
  MINGW*|MSYS*|CYGWIN*)   # Windows environments
  *)                      # Fallback with auto-detection
```

### 🎯 Windows-Specific Features
- **PowerShell Integration**: Automatic Windows user PATH configuration via registry
- **Multi-Shell Support**: Git Bash, PowerShell, WSL environment detection
- **Native Windows Commands**: `where` instead of `which`, `setx` for persistent PATH
- **Path Format Handling**: Both Windows (`%USERPROFILE%`) and Unix (`$HOME`) formats

### 📖 Documentation Updates
- **Windows Troubleshooting**: Complete Windows PATH configuration guide
- **Platform-Specific Commands**: Separate command sets for Windows vs Unix-like systems
- **Shell Environment Notes**: Git Bash, WSL, PowerShell specific instructions
- **Cross-Platform Examples**: Both Windows CMD and Unix shell examples

## v3.1.23 - 2025-09-13

### 🛤️ PATH Configuration & Troubleshooting

- **🔧 Enhanced PATH Setup**: Robust PATH configuration across multiple shell types (.zshrc, .bashrc, .profile)
- **⚡ Current Session Fix**: Attempts to update PATH in current installation session
- **🧪 Command Verification**: Post-install verification that super-prompt is accessible
- **📚 Comprehensive Troubleshooting**: Detailed README troubleshooting with step-by-step PATH fixes
- **🔄 Duplicate Prevention**: Smart detection to prevent duplicate PATH entries

### 🎯 User Experience Improvements
```bash
# Quick fix guidance in installation output
export PATH="$HOME/.npm-global/bin:$PATH"

# Enhanced troubleshooting documentation
# 1. Quick fix for current session
# 2. Installation status check
# 3. PATH verification
# 4. Persistent PATH configuration
# 5. Reinstallation guidance
```

### 🔧 Technical Enhancements
- **Multi-Shell Support**: Configures PATH in zsh, bash, and general shell profiles
- **Session Awareness**: Detects and attempts to fix PATH in current Node.js process
- **Installation Validation**: Real-time verification that commands work after installation
- **User Guidance**: Clear instructions for manual PATH fixes when automatic setup fails

## v3.1.22 - 2025-09-13

### ⚡ Performance Optimization & Dependencies

- **📦 Minimal Dependencies**: Removed unnecessary Python packages (pydantic, rich)
- **🎯 Essential Only**: Core dependencies reduced to typer, pyyaml, pathspec
- **🐍 Proper venv Activation**: Shell script now properly activates virtual environment
- **⚙️ Environment Variables**: Sets VIRTUAL_ENV, PATH, unsets PYTHONHOME for clean execution
- **📈 Performance**: Faster startup with fewer imports and proper environment setup

### 🔧 Technical Improvements
```bash
# Before: 5 dependencies (typer, pyyaml, rich, pathspec, pydantic)
# After: 3 essential dependencies (typer, pyyaml, pathspec)
# Result: ~40% fewer dependencies, faster imports, smaller footprint
```

### 🎯 Benefits
- **Faster Startup**: Reduced import time and memory usage
- **Cleaner Environment**: Proper virtual environment activation
- **Minimal Footprint**: Only essential dependencies installed
- **Better Isolation**: Proper Python path and environment setup

## v3.1.21 - 2025-09-13

### 🐍 Python Virtual Environment Integration

- **🏗️ Isolated Environment**: Creates Python venv in `.super-prompt/venv/` directory
- **📦 Self-Contained**: All Python dependencies installed in project-local venv
- **🗄️ Database Isolation**: SQLite and DB files stored in `venv/data/` directory
- **🚫 Build Exclusion**: venv directory excluded from git and npm packaging
- **⚡ Smart Detection**: CLI automatically detects and uses venv Python when available

### 🔄 Python Environment Management
```bash
# After npm install -g @cdw0424/super-prompt@latest
cd your-project
super-prompt super:init

# ✅ Creates:
# .super-prompt/venv/          - Python virtual environment
# .super-prompt/venv/data/     - SQLite databases and data files
# .super-prompt/venv/bin/      - venv Python interpreter
```

### 🎯 Benefits
- **No System Pollution**: Python packages contained in project venv
- **Build Safety**: venv excluded from git and npm builds
- **Performance**: Faster Python imports with isolated dependencies
- **Reliability**: Consistent Python environment across deployments

## v3.1.20 - 2025-09-13

### 📖 Documentation Improvements

- **🎯 Clear Instructions**: Emphasized that `super-prompt super:init` must be run in project directory
- **📦 @latest Flag**: Updated all installation commands to use `@latest` for automatic updates
- **⚠️ User Guidance**: Added warning about running commands in correct directory
- **🔄 Migration Info**: Added automatic migration feature documentation

### 🚀 User Experience
```bash
# Updated installation pattern (always use @latest)
npm install -g @cdw0424/super-prompt@latest

# Clear guidance: run in YOUR project directory
cd your-project
super-prompt super:init  # ✅ Creates .super-prompt in your project
```

## v3.1.19 - 2025-09-13

### 🚀 Automatic Legacy Migration

- **🔄 Smart Migration**: Automatically detects and migrates legacy installations
- **🧹 Symlink Cleanup**: Removes old Homebrew symlinks automatically
- **⚙️ Auto-Configuration**: Sets up user npm global directory without sudo
- **🛤️ PATH Setup**: Automatically configures shell PATH for seamless operation
- **✅ Zero-Config**: Users just run `npm install -g @cdw0424/super-prompt@latest`

### 🎯 User Experience Improvements
```bash
# For ALL users (new and existing)
npm install -g @cdw0424/super-prompt@latest
# ✅ Automatically migrates legacy installations
# ✅ Sets up user-owned npm global directory
# ✅ Configures PATH in shell
# ✅ super-prompt super:init works immediately
```

## v3.1.18 - 2025-09-13

### 🔧 Legacy Installation Compatibility Fix

- **🚀 Backward Compatibility**: Enhanced CLI routing to handle mixed installation environments
- **✅ Universal Fix**: `super:init` command now works consistently across all installation methods
- **🔄 Seamless Updates**: Existing users can update without manual cleanup
- **📦 Robust Fallback**: Better handling of legacy symlinks and installation paths

### 🧪 Installation Testing
```bash
# For existing users with issues
npm install -g @cdw0424/super-prompt@latest
super-prompt super:init  # ✅ Now works universally
```

## v3.1.17 - 2025-09-13

### 🔧 CLI Routing Fix

- **🚀 Critical Fix**: Updated bin/super-prompt wrapper to correctly map `super:init` → `init` command
- **❌ Removed Legacy Routing**: Eliminated incorrect routing to non-existent init script path
- **✅ Unified Command Logic**: Both project-local and system CLI now use consistent routing logic
- **🎯 Persona Integration**: Fixed `/super-prompt/analyzer super-prompt super:init` workflow compatibility

### 🧪 Verified Fix
```bash
./bin/super-prompt super:init --help    # ✅ Now works correctly
super-prompt super:init --help          # ✅ Will work after npm update
```

## v3.1.16 - 2025-09-13

### 🔧 CLI Fixes

- **✅ Command Routing Fixed**: Resolved `super:init` command argument parsing error that prevented proper command execution
- **🎯 Legacy Compatibility**: Enhanced CLI wrapper to properly map `super:init` → `init` for backward compatibility
- **🚀 Persona Integration**: Fixed cursor command integration allowing `/super-prompt/analyzer super-prompt super:init` workflow to work seamlessly
- **⚡ Dual Command Support**: Both `super-prompt init` and `super-prompt super:init` now work correctly
- **🛠️ Error Resolution**: Fixed "invalid choice: 'init'" error by updating command routing logic in bin/super-prompt wrapper

### 🧪 Verified Working Commands
```bash
super-prompt --help           # ✅ Shows all available commands
super-prompt init --help      # ✅ Modern syntax
super-prompt super:init --help # ✅ Legacy syntax support
```

## v3.1.15 - 2025-01-12

### ✨ Installation Enhancement
- **Installation Enhancement**: Updated all installation commands to include `sudo` for proper global package installation
- **🔧 Security**: Enhanced permission handling for npm global installations
- **📋 Documentation**: Improved installation instructions across README and CLI scripts
- **🐛 Bug Fix**: Fixed permission-related installation issues on macOS/Linux systems

## v3.1.13 - 2025-09-13

### 🐛 Fixes
- fix(bin): send CLI path detection logs to stderr to avoid capture.

## v3.1.14 - 2025-09-13

### 🐛 Fixes
- fix(py): add missing `super_prompt.personas.config` module and make personas __init__ robust to import variants.


# Changelog

## v3.1.12 - 2025-09-13

### 🐛 Fixes
- fix(cli): Add project-local Python launcher shim to resolve relative import errors in `super:init` and persona flags.
- chore(pkg): Include `packages/core-py/` in npm package files to support Python CLI.

### 🧰 Maintenance
- chore(release): Prepare packaging and ensure minimal Python deps auto-install.

# Changelog

## v3.1.10

### 🐛 **Bug Fixes**

- **Package Publishing**: Resolved npm publishing issues and updated version for deployment
- **Version Synchronization**: Synchronized version numbers across package.json and pyproject.toml

## v3.1.9

### 🚀 Major Features

- **High Command Enhancement**: Complete integration with Codex CLI for deep strategic analysis. Now provides automatic input generation when none provided, enabling instant codebase analysis without manual prompts.
- **Grok Mode Toggle System**: Fully implemented `/grok-on` and `/grok-off` commands with persistent state management. Enhanced command detection and AI reasoning capabilities.
- **Absolute Command Detection**: Implemented guaranteed command execution system with multi-level pattern matching, supporting explicit formats (`--sp-persona`, `/command`) and implicit detection.
- **Security Hardening**: Added comprehensive path validation and hidden folder protection. Prevents access to `.git`, `.cursor`, `.npm`, and other sensitive directories.
- **Automated Python Environment**: Enhanced `super:init` command with automatic Python virtual environment creation and dependency installation via `pip install -e .`.
- **Context-Based Execution**: Replaced OS environment variables with secure JSON file-based context passing, eliminating environment pollution and improving security.
- **Execution Plan Framework**: Added structured plan generation after each command execution, with quality enhancement and double-check capabilities.

### 🛠️ Technical Improvements

- **Enhanced Persona Processor**: Improved with execution context management, plan generation, and quality enhancement integration.
- **Tag Executor Security**: Implemented comprehensive security directives, path validation functions, and controlled access to system directories.
- **Command Parsing**: Added sophisticated command detection algorithms with guaranteed execution guarantees and fallback mechanisms.
- **Codex Integration**: Seamless integration with OpenAI Codex CLI for high-level reasoning and strategic analysis.
- **Performance Optimization**: Improved execution flow with better error handling and resource management.

### 🔧 Bug Fixes

- **High Command Input Error**: Fixed "User input is required" error by providing automatic strategic analysis prompts.
- **Syntax Errors**: Resolved bash syntax errors in tag-executor.sh for improved stability.
- **Environment Pollution**: Eliminated OS-level environment variable usage for cleaner execution contexts.

### 📚 Documentation

- **Usage Examples**: Added comprehensive examples for new command formats and features.
- **Security Guidelines**: Documented security measures and best practices.
- **Command Reference**: Updated with all new commands and their usage patterns.

## v3.1.8

### 🛠️ Maintenance

- **Code Refactoring**: Performed general code cleanup and refactoring for improved maintainability and readability.

## v3.1.7

### ✨ New Features

- **README Update**: Added guidance on optimal model selection for Cursor IDE, recommending Gemini Flash and Grok Code Fast with maximized context windows for enhanced performance.
## v3.1.66 - 2025-09-14

### 🛠️ Dev persona flag
- feat(cli): Add `--sp-dev` and `--dev` flags to `optimize` command.
- feat(optimizer): Add `dev` persona to PromptOptimizer so `/dev` and flags resolve without unknown-persona errors.
