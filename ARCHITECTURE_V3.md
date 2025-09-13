# Super Prompt v3 Architecture Plan

## 🎯 Design Goals

- **Single Source of Truth**: Python core engine contains all logic
- **Clean Separation**: Core ← Adapters ← Assets (data-driven)
- **Testability**: Each module can be unit tested in isolation
- **Performance**: Context caching, incremental loading, token optimization
- **Maintainability**: YAML manifests for personas/rules, no hardcoded templates

## 📁 New Package Structure

```
super-prompt/
├── packages/
│   ├── core-py/                    # 🧠 Python Engine (single source of truth)
│   │   ├── super_prompt/
│   │   │   ├── __init__.py
│   │   │   ├── engine/             # State machine, AMR, execution pipeline
│   │   │   │   ├── __init__.py
│   │   │   │   ├── state_machine.py    # INTENT→CLASSIFY→PLAN→EXECUTE→VERIFY→REPORT
│   │   │   │   ├── amr_router.py       # Auto Model Router (L0/L1/H classification)
│   │   │   │   └── pipeline.py         # Command execution pipeline
│   │   │   ├── context/            # .gitignore-aware file collection + caching
│   │   │   │   ├── __init__.py
│   │   │   │   ├── collector.py        # File discovery with .gitignore respect
│   │   │   │   ├── cache.py            # File hash indexing + session cache
│   │   │   │   └── tokenizer.py        # Token counting + budget allocation
│   │   │   ├── sdd/                # SPEC/PLAN/TASKS generation & validation
│   │   │   │   ├── __init__.py
│   │   │   │   ├── spec.py             # Specification generation
│   │   │   │   ├── plan.py             # Planning with gates
│   │   │   │   ├── tasks.py            # Task breakdown
│   │   │   │   └── gates.py            # Validation gates
│   │   │   ├── personas/           # YAML manifest loader + templating
│   │   │   │   ├── __init__.py
│   │   │   │   ├── loader.py           # YAML persona loading
│   │   │   │   ├── template.py         # Template engine
│   │   │   │   └── registry.py         # Persona registry
│   │   │   ├── adapters/           # Output generators for different targets
│   │   │   │   ├── __init__.py
│   │   │   │   ├── cursor.py           # .cursor/rules & commands generation
│   │   │   │   ├── codex.py            # .codex/agents & bootstrap generation
│   │   │   │   └── base.py             # Base adapter interface
│   │   │   ├── validation/         # TODO validation, build/test checks
│   │   │   │   ├── __init__.py
│   │   │   │   ├── todo_checker.py     # Git status, build, test validation
│   │   │   │   └── quality_gates.py    # Quality validation
│   │   │   └── cli.py              # Thin CLI interface
│   │   ├── pyproject.toml          # Python packaging (hatch/pdm)
│   │   ├── requirements.txt        # Dependencies
│   │   └── tests/                  # Comprehensive test suite
│   │       ├── test_engine/
│   │       ├── test_context/
│   │       ├── test_sdd/
│   │       ├── test_personas/
│   │       └── test_integration/
│   ├── cli-node/                   # 📦 NPM Distribution Layer
│   │   ├── bin/
│   │   │   └── super-prompt        # Node → Python delegation only
│   │   ├── src/
│   │   │   ├── index.js            # Minimal bootstrap
│   │   │   └── python-bridge.js    # Python execution wrapper
│   │   ├── package.json            # NPM packaging
│   │   └── README.md
│   ├── cursor-assets/              # 🎯 Cursor IDE Integration (data-driven)
│   │   ├── manifests/
│   │   │   ├── personas.yaml       # Persona definitions
│   │   │   ├── commands.yaml       # Command definitions
│   │   │   └── rules.yaml          # Rule definitions
│   │   └── templates/
│   │       ├── rules/              # .cursor/rules templates
│   │       └── commands/           # .cursor/commands templates
│   └── codex-assets/               # ⚡ Codex CLI Integration (data-driven)
│       ├── manifests/
│       │   ├── agents.yaml         # Agent definitions
│       │   └── bootstrap.yaml      # Bootstrap configurations
│       └── templates/
│           ├── agents/             # .codex/agents templates
│           └── bootstrap/          # Bootstrap prompt templates
├── tools/
│   ├── migration/                  # v2→v3 migration utilities
│   │   ├── migrate.py              # Main migration script
│   │   ├── backup.py               # Backup existing structure
│   │   └── validate.py             # Post-migration validation
│   └── scripts/                    # Shared utilities
│       ├── health-check.py         # System health validation
│       └── performance-test.py     # Performance benchmarking
├── docs/
│   ├── MIGRATION.md                # v2→v3 migration guide
│   ├── DEVELOPMENT.md              # Development setup
│   └── ARCHITECTURE.md             # This document
├── .github/workflows/              # Multi-OS CI/CD
│   ├── test.yml                    # Python + Node testing
│   ├── build.yml                   # Package building
│   └── release.yml                 # Automated releases
└── README.md                       # Updated documentation
```

## 🔄 Execution Flow (v3)

### Current (v2.9.x)
```
bash wrapper → python monolith (67KB) → hardcoded templates → output
```

### New (v3)
```
node cli → python core → YAML manifests → template engine → output
```

## 🧩 Module Responsibilities

### Core Engine (`packages/core-py/`)
- **Single source of truth** for all logic
- State machine execution (INTENT→CLASSIFY→PLAN→EXECUTE→VERIFY→REPORT)
- AMR routing decisions
- Context collection with .gitignore awareness
- SDD workflow orchestration
- Template rendering from YAML manifests

### CLI Node (`packages/cli-node/`)
- **Thin wrapper only** - delegates to Python core
- NPM distribution and global installation
- Python environment validation
- Cross-platform compatibility

### Assets (`cursor-assets/`, `codex-assets/`)
- **Data-driven configuration** - no hardcoded templates
- YAML manifests for personas, commands, rules
- Jinja2 templates for output generation
- Easy extensibility without code changes

## 🚀 Performance Improvements

### Context Collection Pipeline
```python
# New caching strategy
1. Git changes (git diff --name-only) → Priority files
2. Dependency graph → Related files
3. .gitignore respect → Excluded files
4. Token budget allocation → Smart truncation
5. Session cache → 0-1ms repeated queries
```

### Token Optimization
- **File hash indexing**: Cache tokenization results
- **Smart truncation**: Preserve critical sections
- **Incremental loading**: Load context progressively
- **Budget allocation**: Distribute tokens by priority

## 🧪 Testing Strategy

### Unit Tests
- Each module tested in isolation
- Mock external dependencies
- High coverage (>90%) for core logic

### Integration Tests
- End-to-end command execution
- Multiple OS validation (macOS, Ubuntu, Windows/WSL)
- Performance benchmarking

### Regression Tests
- Sample project validation
- v2→v3 migration verification
- Output consistency checks

## 📦 Packaging & Distribution

### Python Core
```toml
# pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "super-prompt-core"
dependencies = [
    "pathspec>=0.11.0",   # .gitignore parsing
    "jinja2>=3.1.0",      # Template engine
    "pyyaml>=6.0",        # YAML parsing
    "tiktoken>=0.5.0",    # Token counting
]
```

### Node CLI
```json
{
  "name": "@cdw0424/super-prompt",
  "version": "3.0.0",
  "bin": {
    "super-prompt": "./bin/super-prompt"
  },
  "dependencies": {
    "execa": "^8.0.0"
  }
}
```

## 🔧 Migration Strategy

### Phase 1: Structure Setup
1. Create new package structure
2. Move Python core to modular design
3. Convert hardcoded templates to YAML manifests

### Phase 2: Feature Parity
1. Implement all v2 features in new architecture
2. Add comprehensive test coverage
3. Performance optimization

### Phase 3: Enhancement
1. Advanced caching
2. Windows support (WSL)
3. Optional server mode (FastAPI)

### Migration Tool
```bash
# Automated migration
super-prompt migrate:v3
# - Backs up existing structure
# - Migrates configuration
# - Validates new setup
# - Provides rollback option
```

## 🎯 Benefits

### For Developers
- **Easier maintenance**: Clear module boundaries
- **Better testing**: Each component testable in isolation
- **Faster development**: No need to touch core for persona changes
- **Better debugging**: Clear error boundaries

### For Users
- **Better performance**: 60-80% faster context loading
- **More reliable**: Comprehensive test coverage
- **Easier customization**: YAML-based configuration
- **Cross-platform**: Windows support via WSL

### For Architecture
- **Single responsibility**: Each module has one job
- **Loose coupling**: Clear interfaces between components
- **High cohesion**: Related functionality grouped together
- **Extensible**: Add new personas/commands without code changes

## 🔮 Future Roadmap

### v3.1 - Enhanced Performance
- Parallel context collection
- Advanced caching strategies
- Token optimization algorithms

### v3.2 - Extended Platform Support
- Native Windows support
- Container/Docker integration
- Cloud deployment options

### v3.3 - Advanced Features
- Web UI (FastAPI + Next.js)
- Team collaboration features
- Advanced analytics & insights

---

This architecture provides a solid foundation for scaling Super Prompt while maintaining simplicity and performance.