# Super Prompt v5.0.0 — Architecture Plan (Prompt-Based Workflow)

## Goals
- **Prompt-Based Architecture**: All persona functions converted to prompt-based workflow
- **Stateless MCP Server**: Modular design with improved reliability and maintainability
- **Mode-Specific Optimization**: 40 specialized prompt templates (20 GPT + 20 Grok)
- **Performance Excellence**: Streamlined execution with template-based processing
- **Single Source of Truth**: SSOT maintained across personas, rules, and documentation

## Layout (v5.0.0 Architecture)
```
super-prompt/
├─ packages/
│  └─ core-py/
│     └─ super_prompt/
│        ├─ mcp/           # mcp_app.py (modular), mcp_stdio.py (minimal)
│        ├─ prompts/       # 40 specialized prompt templates (20 GPT + 20 Grok)
│        ├─ personas/      # loader.py (YAML), updated persona configs
│        ├─ engine/        # state_machine.py, execution_pipeline.py
│        ├─ context/       # collector.py (enhanced), tokenizer.py
│        ├─ sdd/           # gates.py, plan_processor.py, spec_processor.py
│        ├─ tools/         # system_tools.py, registry.py
│        ├─ utils/         # helpers.py, span_manager.py, progress.py
│        ├─ validation/    # todo_validator.py, quality_checker.py
│        └─ modes/         # mode_store.py, modes.py
├─ packages/cursor-assets/
│  ├─ commands/           # 35+ Cursor command definitions
│  ├─ rules/              # MDC rules for AMR, SDD, personas
│  └─ manifests/
│     └─ personas.yaml     # SSOT persona manifest
├─ packages/codex-assets/
│  └─ agents/             # Codex agent configurations
└─ personas/
   └─ manifest.yaml        # Project-specific persona overrides
```

## State Machine & AMR (Enhanced)
- **Steps**: INTENT→TASK_CLASSIFY→PLAN→EXECUTE→VERIFY→REPORT
- **AMR**: classify (L0/L1/H) → decide switch medium↔high
- **New**: Prompt-based execution with mode-specific template selection
- **Enhanced**: Memory span tracking across all operations

## Prompt-Based Workflow Architecture

### Core Components
- **`run_prompt_based_workflow`**: Main execution function replacing complex pipelines
- **40 Prompt Templates**: Specialized templates for each persona in GPT/Grok modes
- **Stateless MCP Server**: `mcp_app.py` + `mcp_stdio.py` for modular design
- **Enhanced Context Collection**: Improved performance with git-aware processing

### Persona Architecture
```python
# Before (v4.x): Complex pipeline
_run_persona_pipeline(persona, query, context, configs...)

# After (v5.0.0): Simple prompt execution
run_prompt_based_workflow(persona, query, mode="gpt")
# → Selects appropriate template → Executes with optimized prompts
```

### Mode-Specific Optimization
- **GPT Mode**: Structured analysis, practical solutions, systematic approaches
- **Grok Mode**: Truth-seeking analysis, realistic considerations, innovative thinking
- **Template Selection**: Automatic template selection based on persona + mode combination

## Migration Command (Updated)
- `super-prompt super:init --force` — Clean initialization with v5.0.0 architecture
- `super-prompt scaffold:v5` — Ensures all required directories and templates exist

## Key Improvements in v5.0.0

### Performance Enhancements
- **Template-Based Execution**: Eliminates complex pipeline overhead
- **Memory Optimization**: Reduced footprint with simplified architecture
- **Faster Response Times**: Direct prompt execution without routing complexity

### Reliability Improvements
- **Stateless MCP Server**: No PID management or daemon processes
- **Modular Design**: `mcp_app.py` for tools, `mcp_stdio.py` for minimal wrapper
- **Enhanced Error Handling**: Better fallback mechanisms and error recovery

### Maintainability
- **Cleaner Codebase**: Removed legacy pipeline code and complex routing
- **Better Separation**: Clear separation between prompt templates and execution logic
- **SSOT Compliance**: Single source of truth across all persona configurations

## Next Steps (v5.0.1+)
- Enhanced prompt template optimization based on user feedback
- Additional persona specializations for specific domains
- Performance monitoring and template effectiveness analysis
- CI/CD pipeline improvements with comprehensive testing

## Legacy Files (Safe to Remove)

### Obsolete Pipeline Infrastructure
```
packages/core-py/super_prompt/engine/pipeline/     # Old pipeline code
packages/core-py/super_prompt/core/pipeline.py     # Legacy pipeline configs
packages/core-py/super_prompt/mcp/mcp_server.py   # Old server with PID management
packages/core-py/super_prompt/mcp_server_new.py   # Deprecated server version
bin/sp-mcp-legacy                                 # Legacy MCP launcher
```

### Deprecated CLI Wrappers
```
bin/sp                                             # Old wrapper script
bin/codex-*                                        # Legacy codex commands
```

### Files to Preserve
```
packages/core-py/super_prompt/mcp_app.py           # New modular MCP app
packages/core-py/super_prompt/mcp_stdio.py         # Minimal wrapper
packages/core-py/super_prompt/prompts/             # All 40 prompt templates
packages/core-py/super_prompt/personas/            # Updated persona configs
.cursor/commands/                                  # Cursor command definitions
.cursor/rules/                                     # Rules and templates
personas/manifest.yaml                             # SSOT persona manifest
```
