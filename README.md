# Super Prompt

[![npm version](https://img.shields.io/npm/v/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt) [![npm downloads](https://img.shields.io/npm/dt/@cdw0424/super-prompt.svg)](https://www.npmjs.com/package/@cdw0424/super-prompt) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Super Prompt is a powerful MCP-First SDD Development Platform designed for Cursor IDE integration, providing comprehensive AI-assisted development workflows with evidence-based analysis and quality gates.

## Features

- **MCP-First Architecture**: Built on Model Context Protocol for seamless AI integration
- **SDD Workflow**: Spec-Driven Development with automated documentation and phase tracking
- **29+ Specialized Personas**: Tailored AI tools for different development roles
- **Cursor Integration**: Optimized for Cursor IDE with MCP server integration
- **Quality Assurance**: Built-in validation, todo tracking, and regression testing
- **Enterprise-Grade**: Production-ready with audit trails and team collaboration features
- **Codex Compatible**: Works alongside existing Codex CLI installations without conflicts

## Installation

Install globally via npm:

```bash
sudo npm install -g @cdw0424/super-prompt
```

Initialize in your project:

```bash
super-prompt super:init --force
```

## Quick Start

### Installation
```bash
npm install -g @cdw0424/super-prompt
```

### Initialize Project
```bash
super-prompt super:init --force
```

### Switch Language Modes
- **GPT Mode**: `super-prompt gpt-mode-on` (default)
- **Grok Mode**: `super-prompt grok-mode-on`
- **Claude Mode**: `super-prompt claude-mode-on`
- **High Mode**: `super-prompt high-mode-on` (for complex reasoning)

### Use Personas
- `/architect` - System architecture design
- `/frontend` - Frontend development
- `/backend` - Backend implementation
- `/doc-master` - Documentation generation
- `/security` - Security analysis
- `/performance` - Performance optimization

### SDD Workflow
- `/specify` - Requirements specification
- `/plan` - Implementation planning
- `/tasks` - Task breakdown
- `/implement` - Implementation execution

### Example Usage
```bash
# Initialize your project
super-prompt super:init --force

# Switch to Grok mode for fast development
super-prompt grok-mode-on

# Use architect persona to design system
/architect "Design a user authentication system"

# Follow SDD workflow
/specify "Build a task management app"
/plan "Implement user stories"
/tasks "Break down into development tasks"
```

## Development

### Prerequisites
- Node.js 18+
- Python 3.10+

### Setup
```bash
git clone https://github.com/your-repo/super-prompt.git
cd super-prompt
npm install
```

### Building
```bash
npm run build
```

### Testing
```bash
npm test
```

## Contributing

Contributions are welcome! Please see our [contributing guide](docs/contributing.md) and follow the SDD workflow for new features.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/super-prompt/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/super-prompt/discussions)
