#!/usr/bin/env python3
"""SDD Scaffolding CLI - Initialize Spec Kit Projects (Spec Kit v0.0.20)
Creates the complete folder structure and initial files for SDD-enabled projects.
"""
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import json

class SDDScaffolder:
    """Scaffolds new SDD projects with complete Spec Kit structure"""

    def __init__(self):
        self.base_dirs = {
            'specs': 'specs',
            'memory': 'memory',
            'templates': 'specs/templates',
            'scripts': 'scripts/sdd',
            'prompts': '.prompts'
        }

        self.templates = {
            'constitution': 'memory/constitution/constitution.md',
            'spec_template': 'specs/templates/spec/spec-template.md',
            'plan_template': 'specs/templates/plan/plan-template.md',
            'tasks_template': 'specs/templates/tasks/tasks-template.md',
            'example_spec': 'specs/example-feature/spec.md'
        }

    def scaffold_project(self, project_name: str = "sdd-project", force: bool = False) -> Dict[str, any]:
        """Create complete SDD project structure"""
        result = {
            'success': True,
            'created_files': [],
            'skipped_files': [],
            'errors': []
        }

        try:
            # Create base directories
            for dir_name, dir_path in self.base_dirs.items():
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    result['created_files'].append(f"Directory: {dir_path}")
                except Exception as e:
                    result['errors'].append(f"Failed to create directory {dir_path}: {e}")

            # Create memory structure
            self._create_memory_structure(result, force)

            # Create template structure
            self._create_template_structure(result, force)

            # Create example feature
            self._create_example_feature(result, force)

            # Create scripts
            self._create_scripts(result, force)

            # Create initial configuration
            self._create_config_files(result, project_name, force)

            # Create documentation
            self._create_documentation(result, project_name, force)

        except Exception as e:
            result['success'] = False
            result['errors'].append(f"Scaffolding failed: {e}")

        return result

    def _create_memory_structure(self, result: Dict[str, any], force: bool) -> None:
        """Create memory bank structure"""
        memory_dirs = [
            'memory/constitution',
            'memory/rules',
            'memory/sessions'
        ]

        for dir_path in memory_dirs:
            try:
                os.makedirs(dir_path, exist_ok=True)
                if not os.path.exists(f"{dir_path}/.gitkeep"):
                    Path(f"{dir_path}/.gitkeep").touch()
                    result['created_files'].append(f"File: {dir_path}/.gitkeep")
            except Exception as e:
                result['errors'].append(f"Failed to create memory directory {dir_path}: {e}")

        # Create constitution
        constitution_path = self.templates['constitution']
        if force or not os.path.exists(constitution_path):
            constitution_content = self._get_constitution_template()
            try:
                os.makedirs(os.path.dirname(constitution_path), exist_ok=True)
                with open(constitution_path, 'w', encoding='utf-8') as f:
                    f.write(constitution_content)
                result['created_files'].append(f"File: {constitution_path}")
            except Exception as e:
                result['errors'].append(f"Failed to create constitution: {e}")
        else:
            result['skipped_files'].append(f"File: {constitution_path} (already exists)")

    def _create_template_structure(self, result: Dict[str, any], force: bool) -> None:
        """Create template structure"""
        template_dirs = [
            'specs/templates/spec',
            'specs/templates/plan',
            'specs/templates/tasks'
        ]

        for dir_path in template_dirs:
            try:
                os.makedirs(dir_path, exist_ok=True)
                result['created_files'].append(f"Directory: {dir_path}")
            except Exception as e:
                result['errors'].append(f"Failed to create template directory {dir_path}: {e}")

        # Create spec template
        spec_template_path = self.templates['spec_template']
        if force or not os.path.exists(spec_template_path):
            spec_template_content = self._get_spec_template()
            try:
                os.makedirs(os.path.dirname(spec_template_path), exist_ok=True)
                with open(spec_template_path, 'w', encoding='utf-8') as f:
                    f.write(spec_template_content)
                result['created_files'].append(f"File: {spec_template_path}")
            except Exception as e:
                result['errors'].append(f"Failed to create spec template: {e}")
        else:
            result['skipped_files'].append(f"File: {spec_template_path} (already exists)")

        # Create plan template
        plan_template_path = self.templates['plan_template']
        if force or not os.path.exists(plan_template_path):
            plan_template_content = self._get_plan_template()
            try:
                os.makedirs(os.path.dirname(plan_template_path), exist_ok=True)
                with open(plan_template_path, 'w', encoding='utf-8') as f:
                    f.write(plan_template_content)
                result['created_files'].append(f"File: {plan_template_path}")
            except Exception as e:
                result['errors'].append(f"Failed to create plan template: {e}")
        else:
            result['skipped_files'].append(f"File: {plan_template_path} (already exists)")

        # Create tasks template
        tasks_template_path = self.templates['tasks_template']
        if force or not os.path.exists(tasks_template_path):
            tasks_template_content = self._get_tasks_template()
            try:
                os.makedirs(os.path.dirname(tasks_template_path), exist_ok=True)
                with open(tasks_template_path, 'w', encoding='utf-8') as f:
                    f.write(tasks_template_content)
                result['created_files'].append(f"File: {tasks_template_path}")
            except Exception as e:
                result['errors'].append(f"Failed to create tasks template: {e}")
        else:
            result['skipped_files'].append(f"File: {tasks_template_path} (already exists)")

    def _create_example_feature(self, result: Dict[str, any], force: bool) -> None:
        """Create example feature structure"""
        example_dirs = [
            'specs/example-feature',
            'specs/example-feature/contracts',
            'specs/example-feature/research'
        ]

        for dir_path in example_dirs:
            try:
                os.makedirs(dir_path, exist_ok=True)
                result['created_files'].append(f"Directory: {dir_path}")
            except Exception as e:
                result['errors'].append(f"Failed to create example directory {dir_path}: {e}")

        # Create example spec
        example_spec_path = self.templates['example_spec']
        if force or not os.path.exists(example_spec_path):
            example_spec_content = self._get_example_spec()
            try:
                os.makedirs(os.path.dirname(example_spec_path), exist_ok=True)
                with open(example_spec_path, 'w', encoding='utf-8') as f:
                    f.write(example_spec_content)
                result['created_files'].append(f"File: {example_spec_path}")
            except Exception as e:
                result['errors'].append(f"Failed to create example spec: {e}")
        else:
            result['skipped_files'].append(f"File: {example_spec_path} (already exists)")

    def _create_scripts(self, result: Dict[str, any], force: bool) -> None:
        """Create SDD scripts"""
        script_files = [
            'scripts/sdd/acceptance_self_check.py'
        ]

        for script_path in script_files:
            if force or not os.path.exists(script_path):
                # Scripts are created separately - just ensure directories exist
                try:
                    os.makedirs(os.path.dirname(script_path), exist_ok=True)
                    result['created_files'].append(f"Directory: {os.path.dirname(script_path)}")
                except Exception as e:
                    result['errors'].append(f"Failed to create script directory {os.path.dirname(script_path)}: {e}")
            else:
                result['skipped_files'].append(f"Script: {script_path} (already exists)")

    def _create_config_files(self, result: Dict[str, any], project_name: str, force: bool) -> None:
        """Create configuration files"""
        config_files = {
            '.cursorrules': self._get_cursor_rules(project_name),
            'pyproject.toml': self._get_pyproject_config(project_name),
            '.gitignore': self._get_gitignore()
        }

        for config_file, content in config_files.items():
            if force or not os.path.exists(config_file):
                try:
                    with open(config_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    result['created_files'].append(f"File: {config_file}")
                except Exception as e:
                    result['errors'].append(f"Failed to create config file {config_file}: {e}")
            else:
                result['skipped_files'].append(f"File: {config_file} (already exists)")

    def _create_documentation(self, result: Dict[str, any], project_name: str, force: bool) -> None:
        """Create documentation files"""
        docs = {
            'README_SDD.md': self._get_readme_sdd(project_name),
            'SDD_WORKFLOW.md': self._get_workflow_docs()
        }

        for doc_file, content in docs.items():
            if force or not os.path.exists(doc_file):
                try:
                    with open(doc_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    result['created_files'].append(f"File: {doc_file}")
                except Exception as e:
                    result['errors'].append(f"Failed to create documentation {doc_file}: {e}")
            else:
                result['skipped_files'].append(f"File: {doc_file} (already exists)")

    def _get_constitution_template(self) -> str:
        """Get constitution template"""
        return """# Project Constitution

## Core Principles
- **Spec-First Development**: All features start with specification
- **Context Preservation**: Maintain design intent across all stages
- **Quality Gates**: Each stage validates against previous stages
- **Incremental Refinement**: Build complexity progressively

## Development Rules
- SPEC → PLAN → TASKS → IMPLEMENT workflow mandatory
- No implementation without approved plan
- All decisions documented with rationale
- Context artifacts version controlled

## Quality Standards
- Code quality: maintainable, testable, documented
- Security: secure by default, defense in depth
- Performance: optimize for user experience
- Accessibility: WCAG 2.1 AA compliance minimum

---
*Generated by Spec Kit v0.0.20*
"""

    def _get_spec_template(self) -> str:
        """Get spec template"""
        return """# Feature Specification

## REQ-ID: [Unique identifier, e.g., REQ-001]

## Overview
[Brief description of what this feature does and why it matters]

## User Journey
[Describe the user journey - what they want to achieve]

### Success Criteria
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]
- [ ] [Measurable outcome 3]

### Acceptance Criteria
- [ ] [Specific, testable condition 1]
- [ ] [Specific, testable condition 2]
- [ ] [Specific, testable condition 3]

## Scope & Boundaries
### In Scope
- [List what's included]

### Out of Scope
- [List what's explicitly excluded]

### Assumptions
- [List assumptions that must hold true]

### Dependencies
- [List external dependencies or prerequisites]

## Business Value
[Why this feature matters to users/business]

## Risk Assessment
### Technical Risks
- [List potential technical challenges]

### Business Risks
- [List potential business impact risks]

## Data Requirements
[If applicable, describe data structures or requirements]

## Security Considerations
[Security requirements or considerations]

## Performance Requirements
[Performance expectations or constraints]

## Accessibility Requirements
[Accessibility standards to meet]

## Internationalization
[i18n requirements if applicable]

## Future Considerations
[How this might evolve or connect to future features]

---
*Generated by Spec Kit v0.0.20 - [Current Date]*"""

    def _get_plan_template(self) -> str:
        """Get plan template"""
        return """# Implementation Plan

## REQ-ID: [Same as spec, e.g., REQ-001]

## Architecture Overview
[High-level technical approach and architecture decisions]

## Technical Stack
### Core Technologies
- Language: [e.g., Python 3.9+, TypeScript 5.0+]
- Framework: [e.g., FastAPI, React, Django]
- Database: [e.g., PostgreSQL, MongoDB]
- Infrastructure: [e.g., AWS, Docker, Kubernetes]

### Supporting Technologies
- Testing: [e.g., pytest, Jest, Cypress]
- CI/CD: [e.g., GitHub Actions, Jenkins]
- Monitoring: [e.g., Prometheus, DataDog]
- Security: [e.g., OAuth2, JWT, SSL/TLS]

## Component Design
[Describe key components and their relationships]

### Component 1: [Name]
- Purpose: [What it does]
- Interface: [APIs, contracts]
- Dependencies: [What it needs]

### Component 2: [Name]
- Purpose: [What it does]
- Interface: [APIs, contracts]
- Dependencies: [What it needs]

## Data Architecture
### Schema Design
[Database tables, collections, or data structures]

### Data Flow
[How data moves through the system]

### Migration Strategy
[How to handle data transitions]

## API Design
### Endpoints
```
GET    /api/v1/[resource]
POST   /api/v1/[resource]
PUT    /api/v1/[resource]/{id}
DELETE /api/v1/[resource]/{id}
```

### Request/Response Formats
[JSON schemas or examples]

## Security Architecture
### Authentication & Authorization
[Authentication & Authorization]

### Data Protection
- Encryption: [At rest, in transit]
- Privacy: [PII handling, GDPR compliance]

## Performance Strategy
### Scalability
[Scalability]

### Optimization Targets
[Optimization Targets]

## Testing Strategy
### Unit Tests
[Unit Tests]

### Integration Tests
[Integration Tests]

### End-to-End Tests
[End-to-End Tests]

## Deployment Strategy
### Environment Strategy
[Environment Strategy]

### Rollback Plan
[How to safely rollback if issues arise]

### Monitoring & Observability
- Metrics: [What to measure]
- Logging: [Log levels, aggregation]
- Alerting: [When to alert]

## Risk Mitigation
### Technical Risks
- Risk: [Description]
  - Mitigation: [Strategy]
  - Contingency: [Plan B]

### Operational Risks
- Risk: [Description]
  - Mitigation: [Strategy]
  - Contingency: [Plan B]

## Success Metrics
### Technical Metrics
- [ ] Code coverage: [X]%
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] Accessibility compliance verified

### Business Metrics
- [ ] Feature adoption rate: [X]%
- [ ] User satisfaction score: [X]/5
- [ ] Error rate: < [X]%

## Timeline & Milestones
### Phase 1: Foundation [X weeks]
- [ ] Component 1 implementation
- [ ] Basic testing framework
- [ ] CI/CD pipeline setup

### Phase 2: Core Features [X weeks]
- [ ] Component 2 implementation
- [ ] Integration testing
- [ ] Performance optimization

### Phase 3: Polish & Launch [X weeks]
- [ ] End-to-end testing
- [ ] Documentation completion
- [ ] Production deployment

## Team Requirements
### Skills Needed
- [Role]: [X] developers with [specific skills]
- [Role]: [X] specialists in [area]

### Training Required
- [List any training or knowledge transfer needed]

## Cost Estimation
### Development Cost
- Labor: [X] developer-weeks
- Infrastructure: [X] months of cloud costs
- Tools/Licenses: [X] one-time costs

### Operational Cost
- Hosting: [X]/month
- Monitoring: [X]/month
- Support: [X]/month

---
*Generated by Spec Kit v0.0.20 - [Current Date]*"""

    def _get_tasks_template(self) -> str:
        """Get tasks template"""
        return """# Implementation Tasks

## REQ-ID: [Same as spec/plan, e.g., REQ-001]

## Task Breakdown Strategy
[How tasks are organized - by component, by user story, by technical layer, etc.]

## Task Categories

### 🔧 Infrastructure & Setup
- [ ] **TASK-INF-001**: Set up development environment
  - **Description**: Configure local development environment with all required dependencies
  - **Acceptance Criteria**:
    - [ ] All required dependencies installed and configured
    - [ ] Development scripts working (build, test, lint)
    - [ ] Team members can run application locally
    - [ ] Environment variables and configuration documented
  - **Estimated Effort**: [X] hours
  - **Dependencies**: None
  - **Risk Level**: Low

### 🏗️ Core Components
[List TASK-CORE-XXX items here]

### 🔗 Integration & APIs
[List TASK-INT-XXX items here]

### 🧪 Testing & Quality Assurance
[List TASK-QA-XXX items here]

### 🚀 Deployment & Operations
[List TASK-OPS-XXX items here]

## Task Dependencies Graph
[Show dependency graph here]

## Effort Estimation Summary
[Calculate total effort here]

## Risk Assessment by Task
[Assess risks by task here]

## Acceptance Self-Check Template
[Generate self-check template here]

---
*Generated by Spec Kit v0.0.20 - [Current Date]*"""

    def _get_example_spec(self) -> str:
        """Get example spec"""
        return """# SDD Enhancement Feature Specification

## REQ-ID: REQ-SDD-001

## Overview
Enhance the Super Prompt project with complete Spec-Driven Development (SDD) support following Spec Kit principles. Implement /specify → /plan → /tasks workflow with constitution compliance and acceptance self-checks.

## User Journey
As a developer using Super Prompt, I want to use structured development workflows so that I can ensure quality and consistency in my development process. I want to start with clear specifications, create implementation plans, break down work into testable tasks, and have automatic quality checks.

### Success Criteria
- [ ] All developers can create and validate specifications
- [ ] Implementation plans are comprehensive and approved
- [ ] Tasks are properly broken down and tracked
- [ ] Constitution compliance is automatic
- [ ] Acceptance checks prevent premature implementation

### Acceptance Criteria
- [ ] /specify command creates valid spec templates
- [ ] /plan command generates implementation plans with constitution compliance
- [ ] /tasks command creates testable task breakdowns
- [ ] SDD gates prevent advancement without proper validation
- [ ] AMR handoff brief summarizes spec+plan+constitution correctly

## Scope & Boundaries
### In Scope
- Spec Kit folder structure and templates
- /specify, /plan, /tasks slash commands
- Enhanced SDD gates with constitution validation
- AMR handoff brief generation via MCP tools
- Acceptance self-check automation

### Out of Scope
- Changing existing persona functionality
- Modifying core CLI architecture
- Integration with external project management tools

### Assumptions
- Users have basic understanding of structured development
- Constitution file exists and is maintained
- Memory bank system is functional

### Dependencies
- Existing Super Prompt CLI framework
- Memory bank system
- Constitution compliance checking

## Business Value
Improves development quality and consistency by enforcing structured workflows. Reduces bugs and rework by ensuring proper planning and validation before implementation.

## Risk Assessment
### Technical Risks
- Integration complexity with existing persona system
- Template maintenance overhead

### Business Risks
- Developer resistance to structured workflows
- Learning curve for new commands

## Data Requirements
- Spec templates and validation rules
- Plan templates with constitution integration
- Task breakdown structures
- Acceptance criteria checklists

## Security Considerations
- No sensitive data handling required
- Template files should be validated for security

## Performance Requirements
- Command execution should be fast (< 2 seconds)
- File operations should not impact existing performance

## Accessibility Requirements
- CLI output should be readable and structured
- Error messages should be clear and actionable

## Internationalization
- All templates and messages in English only

## Future Considerations
- Integration with project management tools
- Automated testing integration
- Metrics and analytics for workflow effectiveness

---
*Generated by Spec Kit v0.0.20 - 2025-09-13*"""

    def _get_cursor_rules(self, project_name: str) -> str:
        """Get .cursorrules content"""
        return f"""# {project_name} - Cursor Rules

## SDD Workflow (MANDATORY)
- Always follow: /specify → /plan → /tasks → implementation
- Never implement without approved spec and plan
- Use acceptance self-check before marking tasks complete

## Quality Gates
- Run SDD gates before each phase transition
- Constitution compliance is required
- All acceptance criteria must be validated

## Documentation
- Keep all documentation in English
- Use REQ-ID for traceability
- Update memory bank for significant changes

## Code Quality
- Follow established patterns and conventions
- Write comprehensive tests
- Include security considerations
- Document all public APIs

---
*Generated by Spec Kit v0.0.20*"""

    def _get_pyproject_config(self, project_name: str) -> str:
        """Get pyproject.toml content"""
        return f"""[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
description = "SDD-enabled project using Spec Kit v0.0.20"
readme = "README.md"
requires-python = ">=3.9"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "isort>=5.0.0",
    "flake8>=4.0.0",
    "mypy>=1.0.0"
]

[tool.setuptools]
packages = ["src"]

[tool.black]
line-length = 88

[tool.isort]
profile = "black"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"

---
*Generated by Spec Kit v0.0.20*"""

    def _get_gitignore(self) -> str:
        """Get .gitignore content"""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# SDD Artifacts (uncomment to ignore generated files)
# .prompts/
# specs/*/plan.md
# specs/*/tasks.md

# Logs
*.log
logs/

---
*Generated by Spec Kit v0.0.20*"""

    def _get_readme_sdd(self, project_name: str) -> str:
        """Get SDD README content"""
        return f"""# {project_name}

SDD-enabled project using Spec Kit v0.0.20 - Complete Spec-Driven Development workflow.

## Quick Start

### 1. Initialize SDD Structure
```bash
# Project structure is already initialized
# Use existing scaffolding
```

### 2. Create Your First Feature
```bash
# Specify the feature
/specify Create user authentication system

# Plan the implementation
/plan Focus on security and scalability

# Break down into tasks
/tasks

# Generate AMR handoff brief (MCP)
# 1) Start MCP: npx super-prompt mcp:serve
# 2) Call tool: amr_handoff_brief(project_root, query)
```

### 3. Development Workflow
```bash
# Check gates before each phase
python3 -c "from packages.core_py.super_prompt.sdd.gates import check_spec_plan; print(check_spec_plan())"

# Run acceptance self-check
python3 scripts/sdd/acceptance_self_check.py
```

## SDD Workflow

### Phase 1: Specification (`/specify`)
- Create comprehensive feature specifications
- Define success and acceptance criteria
- Identify scope, assumptions, and dependencies

### Phase 2: Planning (`/plan`)
- Design technical architecture
- Select technology stack
- Define testing and deployment strategies

### Phase 3: Task Breakdown (`/tasks`)
- Break down work into testable units
- Define acceptance criteria per task
- Establish dependencies and effort estimates

### Phase 4: Implementation
- Implement according to plan
- Run acceptance self-checks
- Validate against original requirements

## Quality Gates

- **Spec Gate**: Validates specification completeness
- **Plan Gate**: Checks technical feasibility and constitution compliance
- **Tasks Gate**: Ensures proper breakdown and traceability
- **Implementation Gate**: Final validation before completion

## Constitution Compliance

This project follows strict constitution requirements:
- Spec-first development mandatory
- Context preservation across phases
- Quality gates enforced
- Incremental refinement approach

## Directory Structure

```
{project_name}/
├── specs/                    # Feature specifications
│   ├── templates/           # Reusable templates
│   └── example-feature/     # Example implementation
├── memory/                  # Constitution and rules
│   └── constitution/        # Project constitution
├── scripts/
│   └── sdd/                # SDD automation scripts
├── packages/
│   └── core-py/
│       └── super_prompt/
│           └── sdd/        # SDD core modules
└── .prompts/               # Generated prompts (created)
```

## Commands

- `/specify [description]` - Create feature specification
- `/plan [context]` - Generate implementation plan
- `/tasks [focus]` - Break down into actionable tasks
- Use MCP tools to assist AMR handoff: `amr_repo_overview`, `amr_handoff_brief`

## Scripts

- `scripts/sdd/acceptance_self_check.py` - Automated quality validation
- `packages/core-py/super_prompt/sdd/scaffolding.py` - Project initialization

---
*Generated by Spec Kit v0.0.20*"""

    def _get_workflow_docs(self) -> str:
        """Get workflow documentation"""
        return """# SDD Workflow Guide

## Overview

Spec-Driven Development (SDD) ensures quality and consistency through structured workflows. This guide explains the mandatory process for all feature development.

## Core Principles

1. **Spec First**: All development starts with comprehensive specifications
2. **Quality Gates**: Each phase validates against previous phases
3. **Constitution Compliance**: All work follows established project rules
4. **Traceability**: Every decision and implementation links back to requirements

## Phase Workflow

### 1. Specification Phase
**Command**: `/specify [feature description]`
**Output**: `specs/[feature]/spec.md`

**Activities**:
- Define user journey and success criteria
- Establish acceptance criteria
- Identify scope boundaries and assumptions
- Assess risks and dependencies

**Validation**: Spec quality score > 70

### 2. Planning Phase
**Command**: `/plan [additional context]`
**Output**: `specs/[feature]/plan.md`

**Activities**:
- Design technical architecture
- Select technology stack
- Define testing and deployment strategies
- Create risk mitigation plans

**Validation**: Constitution compliance + plan completeness

### 3. Task Breakdown Phase
**Command**: `/tasks [focus area]`
**Output**: `specs/[feature]/tasks.md`

**Activities**:
- Break work into testable units (TASK-XXX)
- Define acceptance criteria per task
- Establish dependencies and effort estimates
- Create risk assessments

**Validation**: All tasks have clear acceptance criteria

### 4. Implementation Phase
**Command**: Standard development workflow
**Output**: Code, tests, documentation

**Activities**:
- Implement according to approved plan
- Run acceptance self-checks regularly
- Maintain task status updates
- Follow constitution requirements

**Validation**: All acceptance criteria met + quality gates pass

## Quality Gates

### Spec Gate
```python
from packages.core_py.super_prompt.sdd.gates import check_spec_plan
result = check_spec_plan()
assert result.ok, f"Spec issues: {result.missing}"
```

### Plan Gate
```python
result = check_spec_plan()  # Validates both spec and plan
assert result.ok, f"Plan issues: {result.missing}"
```

### Tasks Gate
```python
from packages.core_py.super_prompt.sdd.gates import check_tasks
result = check_tasks()
assert result.ok, f"Tasks issues: {result.missing}"
```

### Implementation Gate
```python
from packages.core_py.super_prompt.sdd.gates import check_implementation_ready
result = check_implementation_ready()
assert result.ok, f"Implementation issues: {result.missing}"
```

## Constitution Requirements

### Core Principles
- Spec-first development mandatory
- Context preservation across phases
- Quality gates enforced
- Incremental refinement approach

### Development Rules
- No implementation without approved plan
- All decisions documented with rationale
- Context artifacts version controlled
- Acceptance criteria must be testable

### Quality Standards
- Code: maintainable, testable, documented
- Security: secure by default, defense in depth
- Performance: optimize for user experience
- Accessibility: WCAG 2.1 AA minimum

## Tooling

### Cursor Commands
- `/specify` - Create specifications
- `/plan` - Generate implementation plans
- `/tasks` - Break down work items

### Python Scripts
- `acceptance_self_check.py` - Automated validation
- `gates.py` - Quality gate checking

### Validation Scripts
```bash
# Full validation
python3 scripts/sdd/acceptance_self_check.py

# Handoff brief (MCP)
# Start MCP then call amr_handoff_brief(project_root, query)

# Gate checking
python3 -c "from packages.core_py.super_prompt.sdd.gates import *; print(check_implementation_ready())"
```

## Common Patterns

### Feature Development
1. `/specify "Add user profile management"`
2. `/plan "Focus on GDPR compliance"`
3. `/tasks "Backend first"`
4. Implement with regular self-checks
5. Validate all gates pass

### Bug Fixes
1. `/specify "Fix login timeout issue"`
2. `/plan "Root cause analysis required"`
3. `/tasks "Investigation and fix"`
4. Implement fix with tests
5. Validate acceptance criteria

### Refactoring
1. `/specify "Refactor authentication module"`
2. `/plan "Maintain API compatibility"`
3. `/tasks "Component by component"`
4. Implement with regression testing
5. Validate performance maintained

## Troubleshooting

### Spec Gate Fails
- Check all required sections are present
- Ensure REQ-ID format is correct
- Add measurable success criteria
- Define clear acceptance criteria

### Plan Gate Fails
- Verify constitution compliance
- Add technical stack specification
- Include security architecture
- Define testing strategy

### Tasks Gate Fails
- Use proper TASK-ID format
- Add acceptance criteria for each task
- Define task dependencies
- Include effort estimates

### Implementation Issues
- Run acceptance self-check regularly
- Validate against original spec
- Update task status as work progresses
- Document any requirement changes

---
*Generated by Spec Kit v0.0.20*"""

def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='SDD Scaffolding CLI - Spec Kit v0.0.20')
    parser.add_argument('project_name', nargs='?', default='sdd-project',
                       help='Name of the project to scaffold')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Overwrite existing files')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Only show final status')

    args = parser.parse_args()

    try:
        scaffold = SDDScaffolder()
        result = scaffold.scaffold_project(args.project_name, args.force)

        if args.quiet:
            # Quiet mode output disabled
            sys.exit(0 if result['success'] else 1)

        # Detailed output disabled - no print statements allowed
            sys.exit(1)

    except Exception as e:
        # Scaffolding failed with error
        sys.exit(1)

if __name__ == "__main__":
    main()
