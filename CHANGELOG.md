# Changelog

## v3.1.11 - 2025-09-13

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
