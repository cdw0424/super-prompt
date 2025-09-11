# Super Prompt Project Brief

## Project Overview

Super Prompt is a CLI tool and framework for Cursor IDE that provides
specialized AI personas for different development tasks. It integrates with
OpenAI's Codex CLI to provide expert-level analysis and guidance across multiple
domains.

## Core Purpose

To enhance developer productivity by providing specialized AI assistance
through:

- Domain-specific analysis (architect, analyzer, frontend, backend)
- Sequential reasoning capabilities (seq, seq-ultra)
- Structured problem-solving approaches
- Integration with Cursor IDE workflows

## Key Components

- **CLI Framework**: Core command-line interface with persona routing
- **Processor Modules**: Individual persona processors for specialized analysis
- **Codex Integration**: OpenAI Codex CLI integration for advanced reasoning
- **Cursor Commands**: IDE integration through .cursor/commands structure

## Success Criteria

- [ ] All persona processors functional and tested
- [ ] Successful Codex CLI integration
- [ ] Clear documentation and usage examples
- [ ] Stable command routing and error handling
- [ ] Memory bank system for context management

## Current Status

- ✅ Basic CLI structure implemented
- ✅ Multiple persona processors created (analyzer, architect, frontend,
  backend, seq, seq-ultra)
- ✅ Codex processor framework functional
- 🔄 Import/module loading issues resolved
- ⏳ Testing and validation needed
- ⏳ Documentation completion pending

## Technical Scope

- Python-based CLI application
- Modular processor architecture
- OpenAI Codex CLI integration
- Cursor IDE command integration
- Memory bank system for context persistence

## Project Goals

1. Provide reliable, specialized AI assistance for developers
2. Enable complex analysis through Codex integration
3. Maintain clean, modular codebase
4. Support multiple development domains and workflows
5. Ensure robust error handling and user experience
