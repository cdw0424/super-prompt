# Super Prompt v3 - Modular Architecture

## Overview
Super Prompt v3 implements a modular architecture for prompt engineering and development workflow management.

## Key Improvements
- Modular Python core library with clear separation of concerns
- Data-driven persona and asset management
- Advanced context collection with ripgrep and caching
- Comprehensive test coverage and type safety
- Dual IDE support (Cursor + Codex)

## Architecture
- `packages/core-py/`: Python core library (engine, context, sdd, personas, adapters, validation)
- `packages/cli-node/`: Node.js CLI wrapper
- `packages/cursor-assets/`: Cursor IDE assets (data-driven)
- `packages/codex-assets/`: Codex CLI assets (data-driven)

## Installation
```bash
npm install -g @cdw0424/super-prompt
super-prompt init
```

## Usage
- Cursor: `/architect "design system"`
- Codex: `super-prompt --sp-architect "design system"`
- SDD: `super-prompt sdd spec "feature name"`

