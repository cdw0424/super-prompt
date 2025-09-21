# Super Prompt v5.1.1

[![npm version](https://img.shields.io/npm/v/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.17-brightgreen)](https://nodejs.org/)

Super Prompt enables Cursor to apply language-specific optimized personas and guidelines, maximizing development performance. It provides a pure Python MCP server with specialized personas, model routing rules, and command-line tooling in a single npm package, allowing you to install, initialize, and register the MCP server in one step.

## Quick Start

### Installation

```bash
# Install globally (recommended for system-wide usage)
npm install -g @cdw0424/super-prompt@latest
```

### Project Setup

```bash
# Initialize Super Prompt assets in your workspace
super-prompt super:init --force
```

### Cursor Configuration

1. Open **Cursor → Settings → MCP**
2. Add the following configuration:

```json
{
  "mcpServers": {
    "super-prompt": {
      "type": "stdio",
      "command": "./bin/sp-mcp",
      "args": [],
      "env": {
        "SUPER_PROMPT_ALLOW_INIT": "true",
        "SUPER_PROMPT_REQUIRE_MCP": "1",
        "SUPER_PROMPT_PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONUNBUFFERED": "1",
        "PYTHONUTF8": "1"
      }
    }
  }
}
```

3. Restart Cursor and start using personas!

### First Usage

```bash
# Get architecture help
/super-prompt/architect "Design a user authentication system"

/super-prompt/backend "Implement REST API endpoints"
/super-prompt/frontend "Build React login component"
```

## Model Mode Configuration

Super Prompt supports different AI models with specialized capabilities:

### GPT Mode (Default)
- **Best for**: Structured reasoning, code generation, and technical documentation
- **When to use**: General development tasks, API design, code reviews
- **Commands**:
  ```bash
  /super-prompt/gpt-mode-on   # Enable GPT mode
  /super-prompt/gpt-mode-off  # Disable GPT mode
  ```

### Grok Mode
- **Best for**: Creative problem-solving, innovative approaches, and complex reasoning
- **When to use**: Architecture decisions, debugging complex issues, innovative solutions
- **Commands**:
  ```bash
  /super-prompt/grok-mode-on   # Enable Grok mode
  /super-prompt/grok-mode-off  # Disable Grok mode
  ```

### Mode-Specific Personas

| Persona | GPT Mode Focus | Grok Mode Focus |
|---------|---------------|-----------------|
| **Architect** | Structured design patterns | Creative architectural solutions |
| **Backend** | Standard frameworks & patterns | Innovative backend approaches |
| **Frontend** | UI/UX best practices | Creative user experiences |
| **Analyzer** | Systematic code analysis | Deep insight generation |
| **Doc Master** | Technical documentation | Creative content structure |

### Recommended Model Configuration

For optimal performance in Cursor, we recommend using **max mode** with these AI models:

#### **Primary Recommendation: Grok Code Fast**
```bash
# In Cursor Settings → AI → Model Configuration
Model: Grok Code Fast
Mode: Max
```

**Why Grok Code Fast?**
- **Superior reasoning**: Advanced logical reasoning capabilities
- **Creative solutions**: Generates innovative approaches to complex problems
- **Context awareness**: Better understanding of project context and dependencies
- **Performance optimized**: Fast response times with high-quality output

#### **Alternative: GPT-5 Low Fast**
```bash
# In Cursor Settings → AI → Model Configuration
Model: GPT-5 Low Fast
Mode: Max
```

**When to use GPT-5 Low Fast:**
- **Structured tasks**: API design, documentation, code reviews
- **Consistency needed**: Following established patterns and best practices
- **Large codebases**: Better handling of extensive context windows
- **Enterprise environments**: Familiar interface for team collaboration

### Automatic Mode Detection

Super Prompt automatically detects your project's context and applies the most appropriate mode:

- **New Projects**: Starts in GPT mode for structured planning
- **Complex Debugging**: Switches to Grok mode for creative problem-solving
- **Documentation**: Uses GPT mode for clear, structured writing
- **Innovation Tasks**: Applies Grok mode for breakthrough thinking

### Mode Selection Guidelines

| **Task Type** | **Recommended Model** | **Mode** |
|---------------|----------------------|----------|
| **Architecture Design** | Grok Code Fast | Max |
| **Code Generation** | Grok Code Fast | Max |
| **Debugging** | Grok Code Fast | Max |
| **Code Review** | GPT-5 Low Fast | Max |
| **Documentation** | GPT-5 Low Fast | Max |
| **API Design** | GPT-5 Low Fast | Max |
| **Refactoring** | Grok Code Fast | Max |

## What’s new in 5.1.1

- **Version synchronization fix** – All version displays now correctly show v5.1.1 across CLI, runtime banners, and documentation.
- **Enhanced MCP server architecture** – Improved modularity with stateless stdio entry points and better component separation.
- **Persona pipeline modernization** – Replaced legacy pipeline helpers with modern prompt-based workflows for all personas.
- **SDD architecture integration** – Added comprehensive Spec Kit lifecycle guidance with new architecture knowledge base.
- **Full Spec Kit persona coverage** – Restored MCP coverage for all Spec Kit personas using shared workflow executor.
- **Troubleshooting persona enhancement** – Updated prompts, overlays, and command metadata for better debugging capabilities.
- **Asset validation improvements** – Enhanced project bootstrap processes and configuration validation.
- **Documentation standardization** – Complete README and CHANGELOG refresh in English with current guidance.

## Overview

Super Prompt provides two core entry points designed to maximize development performance in Cursor:

- `super-prompt` – project initialization, MCP diagnostics, and persona utilities
- `sp-mcp` – stdio MCP server for Cursor usage

Internally, it follows these principles:

- **Single Source of Truth** – personas manifest → `.cursor/rules` → Cursor workspace configuration
- **Language-Specific Optimization Routing** – automatically applies optimal personas and guidelines for each programming language
- **Performance-Centric Logging** – all logs start with `--------` and sensitive information is masked (`sk-***`)

## Project Philosophy

### **Performance-First Development**

Super Prompt is built on the belief that **development productivity is maximized when AI assistance is tailored to specific programming languages and development contexts**. We reject the one-size-fits-all approach and instead provide specialized personas that understand the nuances of different programming paradigms.

### **Language-Specific Intelligence**

Each programming language has its own idioms, best practices, and common patterns. Super Prompt automatically detects your project's language context and applies the most appropriate AI persona:

- **Python**: Focuses on readability, testing, and framework-specific patterns
- **JavaScript/TypeScript**: Emphasizes async patterns, modern ES features, and web development best practices
- **Java**: Prioritizes object-oriented design, performance optimization, and enterprise patterns
- **Go**: Centers on simplicity, concurrency patterns, and cloud-native development
- **Rust**: Focuses on memory safety, performance optimization, and systems programming

### **Contextual Intelligence**

Beyond language-specific optimization, Super Prompt understands your development context:

- **Framework Detection**: Automatically recognizes React, Vue, Django, FastAPI, Spring Boot, and other frameworks
- **Project Structure Analysis**: Analyzes your codebase to provide contextually relevant suggestions
- **Development Phase Awareness**: Adapts guidance based on whether you're prototyping, refactoring, or optimizing

### **Seamless Integration**

We believe AI assistance should **enhance, not replace, developer workflow**. Super Prompt integrates deeply with Cursor while maintaining:

- **Zero Configuration**: Works out of the box with sensible defaults
- **Transparent Operation**: Clear logging and predictable behavior
- **Fallback Resilience**: Graceful degradation when dependencies are unavailable
- **Performance Optimization**: Minimal latency impact on development workflow

### **Continuous Evolution**

Super Prompt evolves with the development ecosystem. We regularly update personas to reflect:

- **Emerging Language Features**: Support for new language versions and features
- **Framework Updates**: Compatibility with latest framework versions
- **Best Practice Changes**: Updated guidance as industry standards evolve
- **Performance Improvements**: Optimized execution and reduced latency

## Core Development Workflows

Super Prompt provides structured workflows that ensure high-quality development outcomes. Our core methodologies include **Spec-Driven Development (SDD)**, **Confession Mode**, and **Double-Check** validation.

### **Spec-Driven Development (SDD)**

SDD ensures every feature starts with clear specifications and follows a structured development process:

> Tip: you can surface the Spec Kit playbook on demand with
> `./bin/super-prompt mcp call sp.sdd_architecture --args-json '{"persona": "architect"}'`
> to get persona-aligned guardrails before you run the slash commands.

#### **SDD Workflow Phases:**

1. **📋 SPEC Phase** (Requirements & Planning)
   ```bash
   # Create comprehensive specifications
   /super-prompt/specify "Design a user authentication system with OAuth2"
   ```

2. **🎯 PLAN Phase** (Architecture & Roadmap)
   ```bash
   # Develop technical implementation plan
   /super-prompt/plan "Create implementation roadmap for OAuth2 auth system"
   ```

3. **⚡ TASKS Phase** (Execution Planning)
   ```bash
   # Break down into actionable development tasks
   /super-prompt/tasks "Break down OAuth2 implementation into specific tasks"
   ```

#### **SDD Benefits:**
- **Structured Approach**: Eliminates guesswork and ensures comprehensive planning
- **Quality Assurance**: Built-in validation at each phase
- **Scalable Development**: Works for both small features and large projects
- **Documentation First**: Specifications serve as living documentation

### **Confession Mode**

A unique debugging methodology where you "confess" all known issues and context to get comprehensive solutions:

#### **When to Use Confession Mode:**
- Complex debugging scenarios
- Multi-component system issues
- Performance bottlenecks
- Integration problems
- Legacy code refactoring

#### **Confession Mode Workflow:**
```bash
# Comprehensive issue analysis with full context
/super-prompt/troubleshooting "My React app has performance issues, memory leaks, and slow rendering - full confession needed"

/super-prompt/security "Security audit needed for authentication system with known vulnerabilities"
```

#### **Confession Mode Benefits:**
- **Full Context Analysis**: No issue is too complex or multi-faceted
- **Comprehensive Solutions**: Addresses root causes, not just symptoms
- **Prevention Focus**: Identifies potential future issues
- **Knowledge Transfer**: Documents solutions for team learning

### **Double-Check Validation**

Every critical decision and implementation goes through rigorous validation:

#### **Double-Check Workflow:**
```bash
# Initial implementation
/super-prompt/architect "Design scalable microservices architecture"

# Validation and verification
/super-prompt/review "Review the proposed microservices design for scalability"

# Quality assurance
/super-prompt/qa "Perform quality assurance on the architecture design"
```

#### **Double-Check Benefits:**
- **Quality Assurance**: Multiple validation layers prevent issues
- **Consistency**: Ensures alignment with best practices and standards
- **Risk Mitigation**: Early identification of potential problems
- **Continuous Improvement**: Feedback loops drive better outcomes

### **Integrated Workflow Example**

For a new feature development:

```bash
# 1. SDD Phase - Specification
/super-prompt/specify "Build a real-time chat feature with WebSocket"

# 2. SDD Phase - Planning
/super-prompt/plan "Technical roadmap for WebSocket chat implementation"

# 3. SDD Phase - Task Breakdown
/super-prompt/tasks "Detailed tasks for chat feature development"

# 4. Implementation with Double-Check
/super-prompt/backend "Implement WebSocket server for real-time chat"
/super-prompt/frontend "Build React chat component"
/super-prompt/review "Review complete chat implementation"

# 5. Confession Mode for Issues
/super-prompt/troubleshooting "Chat feature has connection issues and performance problems"

# 6. Final Quality Assurance
/super-prompt/qa "End-to-end testing and quality validation"
```

### **Workflow Selection Guide**

| **Scenario** | **Recommended Workflow** | **Primary Tool** |
|-------------|-------------------------|------------------|
| New feature planning | SDD (SPEC → PLAN → TASKS) | `/super-prompt/specify` |
| Complex debugging | Confession Mode | `/super-prompt/troubleshooting` |
| Architecture decisions | Double-Check | `/super-prompt/architect` + `/super-prompt/review` |
| Code quality issues | Double-Check | `/super-prompt/qa` + `/super-prompt/review` |
| Security concerns | Confession Mode | `/super-prompt/security` |
| Performance problems | Confession Mode | `/super-prompt/performance` |

These workflows ensure **consistent quality**, **comprehensive problem-solving**, and **scalable development practices** across all your projects.

## Troubleshooting

| Symptom | Resolution |
| --- | --- |
| Cursor reports "no tools available" | Check `~/.cursor/mcp.log` for `-------- MCP:` entries. If FastMCP is missing, install the runtime manually: `pip install mcp`. The fallback server will operate automatically once the CLI reconnects. |
| `sp_high` missing or duplicated | The 5.0.5 release registers a single `sp_high` backed by the persona pipeline. Restart `sp-mcp` to reload the registry. |
| Stdout parse errors | Ensure you never print to stdout in custom scripts. Super Prompt reserves stdout for JSON-RPC; use `--------`-prefixed logs on stderr. |

## Release workflow

1. `npm install` – refreshes `package-lock.json`.
2. `npm run prepack` – builds the Python wheel into `dist/` (optional for local testing).
3. `npm publish` – publishes `@cdw0424/super-prompt@5.1.1` with synchronized Python assets.

Super Prompt is MIT licensed. Contributions and issues are welcome at [https://github.com/cdw0424/super-prompt](https://github.com/cdw0424/super-prompt).
