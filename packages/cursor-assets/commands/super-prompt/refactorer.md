---
description: refactorer command - Code quality and technical debt management
run: mcp
server: super-prompt
tool: sp_refactorer
args:
---
  query: "${input}"
## Execution Mode

➡️ Execution: This command executes via MCP (server: super-prompt; tool as defined above).

**Query:** \${input}

### ⚠️ **Analysis Status: Incomplete**

Refactorer execution completed but returned no content. This may indicate:

1. **Query too complex** - Try breaking it into smaller parts
2. **Module import issues** - Check Python path configuration
3. **Function execution error** - Verify refactorer function implementation

### 💡 **Suggestions:**

- Simplify your query and try again
- Check Python environment and dependencies
- Verify the refactorer module is properly installed

**Raw Output:** (empty)\`;
      }

      return result;

    } catch (error) {
      console.error(\`-------- refactorer: Inline execution failed: \${error.message}\`);

      return \`## 🔧 **Refactorer Analysis Error**

**Query:** \${input}

### ❌ **Execution Failed**

The inline refactorer execution encountered an error:

**Error:** \${error.message}

### 🔧 **Troubleshooting Steps:**

1. **Check Python Installation:**
   \`\`\`bash
   python3 --version
   pip list | grep super-prompt
   \`\`\`

2. **Verify Module Path:**
   \`\`\`bash
   ls -la \${path.join(__dirname, '..', '..', '..', '..', '..', 'packages', 'core-py')}
   \`\`\`

3. **Test Basic Import:**
   \`\`\`bash
   python3 -c "from super_prompt.mcp_server import refactorer; print('Import successful')"
   \`\`\`

4. **Check Environment:**
   \`\`\`bash
   echo \$PYTHONPATH
   \`\`\`

### 💡 **Alternative:**
You can also try the MCP-based refactorer command if inline execution continues to fail.

**Fallback Command:** \`/super-prompt/refactorer "\${input}"\` (will use MCP server)\`;
    }
  }

  // Export the main function
  module.exports = runRefactorerCommand;

🔧 Refactorer Code quality and technical debt management

## 🧠 **Strategic Planning Support**

**For complex reasoning and strategic planning tasks**, consider using the high command to get comprehensive analysis and plan development:

```bash
/super-prompt/high "Your strategic planning query here"
```

The high command provides:
- Deep reasoning and problem analysis
- Comprehensive strategic planning
- Implementation roadmap development
- Risk assessment and mitigation strategies

**When to use high command:**
- Complex system design decisions
- Strategic planning and roadmap development
- Architecture analysis and optimization
- Risk assessment and mitigation planning
- Multi-phase implementation strategies
