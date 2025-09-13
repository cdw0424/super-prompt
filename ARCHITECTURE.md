# Super Prompt v3 Architecture

**Production-ready prompt engineering toolkit** with modular architecture, dual IDE support, and intelligent reasoning optimization.

## 🏗️ System Overview

Super Prompt v3 is built on a **modular architecture** that separates concerns into distinct layers:

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                    │
├─────────────────────┬───────────────────────────────────────┤
│   Cursor IDE        │         Codex CLI                     │
│   Slash Commands    │         Flag-based Commands           │
│   /architect        │         --sp-architect                │
│   /frontend         │         --sp-frontend                 │
│   /init-sp          │         super-prompt init             │
└─────────────────────┴───────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Command Router                           │
│   • CLI Wrapper (bin/super-prompt)                         │
│   • Command Detection & Mapping                            │
│   • Legacy Compatibility (super:init → init)              │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                  Core Engine Layer                         │
│   • Python Core (packages/core-py/)                        │
│   • Execution Pipeline                                     │
│   • AMR (Auto Model Router)                                │
│   • State Machine                                          │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                            │
├───────────────┬─────────────────┬───────────────────────────┤
│   Personas    │    Context      │         SDD               │
│   • Architect │    • Collector  │    • Spec-Driven Dev     │
│   • Frontend  │    • Cache      │    • Quality Gates       │
│   • Security  │    • Tokenizer  │    • Pipeline             │
│   • Backend   │                 │                           │
└───────────────┴─────────────────┴───────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Adapter Layer                           │
├─────────────────────┬───────────────────────────────────────┤
│   Cursor Adapter    │         Codex Adapter                │
│   • Command Gen     │         • Asset Generation           │
│   • Rules Gen       │         • Bootstrap Scripts          │
│   • Integration     │         • AMR Configuration          │
└─────────────────────┴───────────────────────────────────────┘
```

## 🧠 Core Components

### 1. Command Router (`bin/super-prompt`)

**Intelligent routing system** that handles command detection and mapping:

```bash
# Legacy compatibility mapping
super:init → init

# Persona detection
--sp-architect → Enhanced Persona Processor

# Direct CLI delegation
super-prompt init → Python Core CLI
```

**Key Features:**
- **Legacy Support**: Maps `super:init` to modern `init` command
- **Persona Routing**: Direct routing for `--sp-*` flags
- **CLI Resolution**: Project-local vs. packaged CLI selection
- **Error Handling**: Graceful fallbacks and clear error messages

### 2. Python Core Engine (`packages/core-py/`)

**Modular Python architecture** with clean separation of concerns:

```
packages/core-py/super_prompt/
├── cli.py                 # Main CLI interface
├── engine/
│   ├── execution_pipeline.py  # Task execution
│   ├── amr_router.py          # Auto Model Router
│   └── state_machine.py       # Workflow state
├── context/
│   ├── collector.py           # Context gathering
│   ├── cache.py               # Caching system
│   └── tokenizer.py           # Token management
├── personas/
│   ├── loader.py              # Persona loading
│   └── config.py              # Configuration
├── sdd/
│   ├── gates.py               # Quality gates
│   ├── spec_processor.py      # Spec handling
│   └── tasks_processor.py     # Task management
├── adapters/
│   ├── cursor_adapter.py      # Cursor integration
│   └── codex_adapter.py       # Codex integration
└── validation/
    ├── quality_checker.py     # Quality assurance
    └── todo_validator.py      # Task validation
```

### 3. AMR (Auto Model Router)

**Intelligent reasoning optimization** with automatic model switching:

```python
# State Machine: INTENT → CLASSIFY → PLAN → EXECUTE → VERIFY → REPORT
class AMRRouter:
    def route_request(self, complexity: float, context: dict):
        if complexity > 0.7:
            return "gpt-5-high"  # Deep reasoning
        else:
            return "gpt-5-medium"  # Standard execution
```

**Features:**
- **Automatic Switching**: Based on task complexity analysis
- **Context Awareness**: Considers current project state
- **Performance Optimization**: 30-50% token reduction
- **Quality Gates**: Validation at each stage

### 4. Persona System

**29 Specialized AI personalities** for domain-specific tasks:

#### Technical Specialists
- **`architect`**: Systems design, long-term architecture
- **`frontend`**: UI/UX, accessibility, performance
- **`backend`**: Server-side, APIs, reliability
- **`security`**: Threat modeling, vulnerability assessment
- **`performance`**: Optimization, bottleneck elimination

#### Process Experts
- **`analyzer`**: Root cause analysis, investigation
- **`qa`**: Quality assurance, testing strategies
- **`refactorer`**: Code quality, technical debt
- **`devops`**: Infrastructure, deployment automation

#### Communication Specialists
- **`mentor`**: Educational guidance, knowledge transfer
- **`scribe`**: Documentation, professional writing

**Persona Configuration:**
```yaml
personas:
  architect:
    name: "Systems Architect"
    role_type: "Technical Leadership"
    expertise_level: "Senior"
    specializations: ["system-design", "scalability", "architecture"]
    interaction_style: "Strategic and long-term focused"
```

### 5. SDD (Spec-Driven Development)

**Complete development workflow** with quality gates:

```
SPEC → PLAN → TASKS → IMPLEMENT
  ↓      ↓       ↓        ↓
Gate1  Gate2   Gate3   Gate4
```

**Quality Gates:**
1. **Specification Gate**: Requirements clarity, completeness
2. **Planning Gate**: Technical feasibility, resource estimation
3. **Task Gate**: Implementation readiness, dependency resolution
4. **Implementation Gate**: Code quality, testing, documentation

## 🔄 Execution Flow

### 1. Command Processing
```bash
user: /super-prompt/analyzer super-prompt super:init
  ↓
bin/super-prompt detects super:init → maps to init
  ↓
Enhanced Persona Processor (analyzer persona)
  ↓
Python Core CLI (init command)
  ↓
Execution Pipeline + Quality Gates
  ↓
Result with validation and documentation
```

### 2. Persona Activation
```bash
user: --sp-architect "design authentication system"
  ↓
Persona detection (--sp-architect)
  ↓
Enhanced Persona Processor loads architect config
  ↓
System prompt + persona context + user input
  ↓
AI execution with architect specializations
  ↓
Structured output with architectural recommendations
```

### 3. SDD Workflow
```bash
user: super-prompt --sp-sdd-spec "user authentication"
  ↓
SDD Spec Processor
  ↓
Quality Gate 1 (Specification validation)
  ↓
Spec generation with requirements analysis
  ↓
Context preservation for next stage (PLAN)
```

## 🛡️ Security & Quality

### Security Features
- **Path Validation**: Prevents access to sensitive directories (`.git`, `.cursor`, `.npm`)
- **Input Sanitization**: Comprehensive validation of user inputs
- **Context Isolation**: Secure JSON-based context passing
- **Permission Control**: Controlled file system access

### Quality Assurance
- **8-Step Validation Cycle**: Comprehensive quality gates
- **Automated Testing**: Unit, integration, and E2E tests
- **TODO Validation**: Automatic task completion verification
- **Performance Monitoring**: Token usage and execution time tracking

### Global Write Protection
```python
# Only safe outputs allowed
SAFE_WRITE_PATTERNS = [
    ".codex/reports/",
    "specs/",
    "memory/constitution/",
    "memory/rules/"
]
```

## 📊 Performance Optimization

### Token Management
- **Context Engineering**: 30-50% token reduction
- **Intelligent Caching**: Context reuse across sessions
- **Selective Injection**: Only relevant context included
- **Compression Techniques**: Structured output formatting

### Execution Optimization
- **Parallel Processing**: Concurrent task execution where possible
- **Cache Strategy**: Intelligent caching of expensive operations
- **Resource Management**: Memory and CPU optimization
- **Error Recovery**: Graceful handling of failures

## 🔧 Configuration & Customization

### Project Configuration
```json
{
  "super_prompt": {
    "personas": {
      "default": "architect",
      "custom_personas": "./personas/"
    },
    "sdd": {
      "quality_gates": true,
      "auto_validation": true
    },
    "amr": {
      "complexity_threshold": 0.7,
      "auto_routing": true
    }
  }
}
```

### Environment Variables
```bash
# Optional configuration
SP_SKIP_CODEX_UPGRADE=1    # Skip automatic Codex updates
SP_SELF_UPDATE=1           # Enable self-updates
SUPER_PROMPT_DEBUG=1       # Enable debug mode
```

## 🚀 Extension Points

### Custom Personas
```python
# Add custom personas
class CustomPersona(BasePersona):
    name = "data-scientist"
    specializations = ["ml", "data-analysis", "statistics"]

    def process_request(self, context: dict) -> dict:
        # Custom processing logic
        pass
```

### Custom Adapters
```python
# Integrate with new IDEs
class VSCodeAdapter(BaseAdapter):
    def generate_commands(self, personas: List[Persona]):
        # Generate VSCode-specific commands
        pass
```

### Custom SDD Stages
```python
# Add custom SDD stages
class CustomGate(QualityGate):
    def validate(self, context: dict) -> GateResult:
        # Custom validation logic
        pass
```

## 📈 Monitoring & Analytics

### Execution Metrics
- **Command Usage**: Track most used commands and personas
- **Performance**: Execution time, token usage, success rates
- **Quality**: Gate pass rates, validation success
- **User Patterns**: Usage analytics and optimization opportunities

### Health Monitoring
- **System Health**: Check dependencies, versions, configurations
- **Performance Monitoring**: Track resource usage and bottlenecks
- **Error Tracking**: Log and analyze failure patterns
- **User Experience**: Monitor and improve user workflows

---

## 🔗 Integration Architecture

### Cursor IDE Integration
```
.cursor/
├── commands/super-prompt/     # Generated commands
│   ├── architect.md
│   ├── frontend.md
│   └── ...
└── rules/                     # Generated rules
    ├── 00-organization.mdc
    ├── 10-sdd-core.mdc
    └── ...
```

### Codex CLI Integration
```bash
# Automatic Codex updates
npm install -g @openai/codex@latest

# High reasoning mode
codex-amr high "strategic analysis"

# AMR bootstrap
codex-amr print-bootstrap > prompt.txt
```

This architecture provides a **robust, scalable, and maintainable** foundation for prompt engineering workflows across multiple development environments.