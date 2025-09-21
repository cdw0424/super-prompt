---
description: dev command - Feature development with quality and delivery focus
run: mcp
server: super-prompt
tool: sp_dev
args:
---
  query: "${input}"
## Execution Mode

➡️ Execution: This command executes via MCP (server: super-prompt; tool as defined above).

**Query:** \${input}

### ⚠️ **Analysis Status: Incomplete**

Dev execution completed but returned no content. This may indicate:

1. **Query too complex** - Try breaking it into smaller parts
2. **Module import issues** - Check Python path configuration
3. **Function execution error** - Verify dev function implementation

### 💡 **Suggestions:**

- Simplify your query and try again
- Check Python environment and dependencies
- Verify the dev module is properly installed

**Raw Output:** (empty)\`;
      }

      return result;

    } catch (error) {
      console.error(\`-------- dev: Inline execution failed: \${error.message}\`);

      return \`## 🚀 **Dev Analysis Error**

**Query:** \${input}

### ❌ **Execution Failed**

The inline dev execution encountered an error:

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
   python3 -c "from super_prompt.mcp_server import run_prompt_based_workflow; print('Import successful')"
   \`\`\`

4. **Check Environment:**
   \`\`\`bash
   echo \$PYTHONPATH
   \`\`\`

### 💡 **Alternative:**
You can also try the MCP-based dev command if inline execution continues to fail.

**Fallback Command:** \`/super-prompt/dev "\${input}"\` (will use MCP server)\`;
    }
  }

  // Export the main function
  module.exports = runDevCommand;

# 🚀 **Dev - Feature Development & Implementation Specialist**

**Expert Focus**: Feature development, code implementation, and delivery excellence

## 🎯 **Development Workflow**

### **Single Step Analysis:**

1. **🚀 Development Analysis** - Current Tool (dev)
   - Analyze development requirements and implementation strategies
   - Identify optimal development approaches and best practices
   - Provide comprehensive implementation guidance and code recommendations

## 🏗️ **Implementation Strategy**

### **Current Structure vs Optimized Structure:**

| **Current Structure** | **Optimized Structure** |
|----------------------|-------------------------|
| Direct function calls | Single `sp_dev` MCP call |
| Complex integrations | Clean MCP protocol compliance |
| Manual planning | Automated development assessment |

### **Development TODO System:**

## 📋 **Development TODO List**

### Phase 1: Requirements Analysis
- [x] **Development Overview**
  - Query: `${input}`
- [x] **Requirements Analysis**
  - Identify development requirements and constraints

### Phase 2: Implementation Planning
- [ ] **Architecture Design**
  - Design optimal system architecture for requirements
- [ ] **Technology Stack Selection**
  - Select appropriate technologies and frameworks

### Phase 3: Development Strategy
- [ ] **Implementation Plan**
  - Develop detailed implementation roadmap and milestones
- [ ] **Code Quality Standards**
  - Establish coding standards and best practices

### Phase 4: Delivery Planning
- [ ] **Deployment Strategy**
  - Plan deployment and release strategies
- [ ] **Monitoring & Maintenance**
  - Establish monitoring and maintenance procedures

## 🚀 **Execution Method**

### **Single MCP Execution Mode:**
1. User inputs `/super-prompt/dev "development query"`
2. `sp_dev` tool executes alone
3. One persona performs complete development analysis
4. Single comprehensive development guidance output

### **Mode-Specific Optimization:**
- **Grok Mode**: Creative development solutions and innovative approaches
- **GPT Mode**: Structured development methodologies and proven practices

### **Usage Example:**
```
1. /super-prompt/dev "Plan feature development for user authentication"
    ↓
2. sp_dev executes alone (safe single call)
    ↓
3. One persona performs complete development analysis
    ↓
4. Comprehensive development guidance output
```

## 💡 **Development Advantages**

### **1. Single Execution Safety**
- Execute only one MCP tool per development analysis
- Complete prevention of infinite recursion and circular calls

### **2. Comprehensive Planning**
- End-to-end development planning and strategy
- Technology selection and architecture design
- Implementation roadmap and milestone planning

### **3. Best Practices Integration**
- Industry-standard development methodologies
- Agile, Scrum, and other development frameworks
- Code quality and testing best practices

### **4. Implementation Guidance**
- Concrete development implementation plans
- Code structure and architecture recommendations
- Deployment and maintenance strategy guidance

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

## 🔥 **Conclusion**

Dev provides **comprehensive development planning and implementation guidance**!

- ✅ **Single safe execution** of development analysis
- ✅ **Complete implementation planning** in one call
- ✅ **Industry best practices** for software development
- ✅ **Implementation guidance** for feature development

Now **professional development planning** is available through single MCP execution! 🚀✨
