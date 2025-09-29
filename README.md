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

### Global Installation (Recommended)
```bash
# Install globally (requires sudo on macOS/Linux)
sudo npm install -g @cdw0424/super-prompt@latest

# Or install specific version
sudo npm install -g @cdw0424/super-prompt@6.1.1
```

### Project Initialization
```bash
# Initialize Super Prompt in your project
super-prompt super:init --force
```

## Quick Start

### Basic Setup
```bash
# 1. Install globally
sudo npm install -g @cdw0424/super-prompt@latest

# 2. Initialize your project
super-prompt super:init --force

# 3. Start MCP server for Cursor IDE
super-prompt-mcp
```

### Language Modes
- **GPT Mode**: `super-prompt gpt-mode-on` (default)
- **Grok Mode**: `super-prompt grok-mode-on`
- **Claude Mode**: `super-prompt claude-mode-on`
- **High Mode**: `super-prompt high-mode-on` (for complex reasoning)

### Personas (29+ Available)
- `/architect` - System architecture design
- `/frontend` - Frontend development
- `/backend` - Backend implementation
- `/doc-master` - Documentation generation
- `/security` - Security analysis
- `/performance` - Performance optimization
- `/qa` - Quality assurance
- `/devops` - DevOps and deployment
- And 20+ more specialized roles

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
/implement "Execute the implementation"
```

### MCP Server
```bash
# Start MCP server for Cursor IDE integration
super-prompt-mcp

# Or use Python module directly
python -m super_prompt.mcp_stdio
```

## Troubleshooting

### Common Issues and Solutions

#### npm Installation Conflicts (EEXIST Error)
**Problem**: `npm error EEXIST: file already exists` during installation

**Solution**: This issue has been resolved in v6.1.1+. The binary name has been changed from `sp-mcp` to `super-prompt-mcp` to prevent conflicts with other packages.

```bash
# Clean installation (if you encounter conflicts)
sudo npm uninstall -g @cdw0424/super-prompt
sudo npm install -g @cdw0424/super-prompt@latest
```

#### macOS Permission Issues
**Problem**: Permission denied during global installation

**Solution**: Use `sudo` for global npm installations:
```bash
sudo npm install -g @cdw0424/super-prompt@latest
```

#### Cursor IDE Integration Issues
**Problem**: Super Prompt commands not appearing in Cursor

**Solution**: Ensure MCP server is running and Cursor is configured:
```bash
# Start MCP server
super-prompt-mcp

# Then restart Cursor IDE
```

#### Python Module Not Found
**Problem**: Import errors when running Super Prompt

**Solution**: Ensure Python dependencies are installed:
```bash
python -m pip install --break-system-packages typer pyyaml pathspec mcp fastmcp
```

## Development

### Prerequisites
- Node.js 18+
- Python 3.10+
- Git

### Setup
```bash
git clone https://github.com/cdw0424/super-prompt.git
cd super-prompt
npm install
```

### Building and Testing
```bash
# Build the project
npm run build

# Run tests
npm test

# Verify SSOT compliance
npm run sp:verify:all
```

### Development Scripts
```bash
# Development mode
npm run dev

# Initialize for development
npm run dev:init

# Start MCP server in development
npm run sp:mcp

# List available MCP tools
npm run sp:mcp:list-tools

# Doctor check
npm run sp:doctor
```

### Publishing
```bash
# Prepare and publish
npm run prepack
npm publish --access public
```

## Contributing

Contributions are welcome! Please see our [contributing guide](docs/contributing.md) and follow the SDD workflow for new features.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/super-prompt/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/super-prompt/discussions)
