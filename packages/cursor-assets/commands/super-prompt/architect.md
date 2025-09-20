---
description: architect command - System design and architecture analysis
run: inline
script: |
  const { spawn } = require('child_process');
  const path = require('path');

  function executeArchitect(query) {
    return new Promise((resolve, reject) => {
      const projectRoot = process.cwd();
      const packageRoot = path.join(__dirname, '..', '..', '..', '..', '..');

      // Execute the architect function directly via Python script
      const pythonCmd = [
        'python3',
        path.join(packageRoot, 'packages', 'core-py', 'super_prompt', 'workflow_runner.py'),
        'architect',
        query
      ];

      console.error(\`-------- architect: Executing inline analysis: \${query.substring(0, 50)}...\`);

      const proc = spawn('python3', pythonCmd.slice(1), {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
          ...process.env,
          PYTHONPATH: [
            path.join(packageRoot, 'packages', 'core-py'),
            process.env.PYTHONPATH || ''
          ].filter(Boolean).join(':'),
          PYTHONUNBUFFERED: '1'
        },
        cwd: projectRoot
      });

      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      proc.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      proc.on('close', (code) => {
        if (code === 0) {
          console.error(\`-------- architect: Analysis completed successfully\`);
          resolve(stdout.trim());
        } else {
          console.error(\`-------- architect: Failed with code \${code}\`);
          console.error(\`-------- architect: stderr: \${stderr}\`);
          reject(new Error(\`Architect execution failed: \${stderr || 'Unknown error'}\`));
        }
      });

      proc.on('error', (error) => {
        console.error(\`-------- architect: Execution error: \${error.message}\`);
        reject(error);
      });
    });
  }

  async function runArchitectCommand(input) {
    try {
      console.error(\`-------- architect: Starting inline execution for: \${input.substring(0, 50)}...\`);

      // Execute architect analysis directly
      const result = await executeArchitect(input);

      if (!result || result.trim() === '') {
        return \`## 🏗️ **Architect Analysis Result**

**Query:** \${input}

### ⚠️ **Analysis Status: Incomplete**

Architect execution completed but returned no content. This may indicate:

1. **Query too complex** - Try breaking it into smaller parts
2. **Module import issues** - Check Python path configuration
3. **Function execution error** - Verify architect function implementation

### 💡 **Suggestions:**

- Simplify your query and try again
- Check Python environment and dependencies
- Verify the architect module is properly installed

**Raw Output:** (empty)\`;
      }

      return result;

    } catch (error) {
      console.error(\`-------- architect: Inline execution failed: \${error.message}\`);

      return \`## 🏗️ **Architect Analysis Error**

**Query:** \${input}

### ❌ **Execution Failed**

The inline architect execution encountered an error:

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
You can also try the MCP-based architect command if inline execution continues to fail.

**Fallback Command:** \`/super-prompt/architect "\${input}"\` (will use MCP server)\`;
    }
  }

  // Export the main function
  module.exports = runArchitectCommand;

# 🏗️ **Architect - System Design & Architecture Specialist**

**Expert Focus**: System architecture analysis and design recommendations

## 🎯 **Architecture Analysis Workflow**

### **Single Step Analysis:**

1. **🏗️ Architecture Analysis** - Current Tool (architect)
   - Analyze system architecture and design patterns
   - Identify structural issues and improvement opportunities
   - Provide architectural recommendations and best practices

## 🏗️ **Implementation Strategy**

### **Current Structure vs Optimized Structure:**

| **Current Structure** | **Optimized Structure** |
|----------------------|-------------------------|
| Direct function calls | Single `sp_architect` MCP call |
| Complex integrations | Clean MCP protocol compliance |
| Manual analysis | Automated architectural assessment |

### **Architecture TODO System:**

## 📋 **Architecture Analysis TODO List**

### Phase 1: System Assessment
- [x] **Architecture Overview**
  - Query: `${input}`
- [x] **Current Architecture Analysis**
  - Identify existing architectural patterns

### Phase 2: Structural Analysis
- [ ] **Design Pattern Evaluation**
  - Assess architectural patterns and anti-patterns
- [ ] **Component Architecture Review**
  - Review component relationships and dependencies

### Phase 3: Optimization Recommendations
- [ ] **Scalability Assessment**
  - Evaluate system scalability and performance bottlenecks
- [ ] **Architecture Improvement Plan**
  - Provide specific architectural recommendations

### Phase 4: Implementation Guidance
- [ ] **Migration Strategy**
  - Plan architectural improvements and refactoring
- [ ] **Best Practices Application**
  - Apply architectural best practices and standards

## 🚀 **Execution Method**

### **Single MCP Execution Mode:**
1. User inputs `/super-prompt/architect "architecture query"`
2. `sp_architect` tool executes alone
3. One persona performs complete architectural analysis
4. Single comprehensive architecture assessment output

### **Mode-Specific Optimization:**
- **Grok Mode**: Creative architectural solutions and innovative designs
- **GPT Mode**: Structured architectural analysis and proven patterns

### **Usage Example:**
```
1. /super-prompt/architect "Review current system architecture"
    ↓
2. sp_architect executes alone (safe single call)
    ↓
3. One persona performs complete architecture analysis
    ↓
4. Comprehensive architecture assessment output
```

## 💡 **Architectural Advantages**

### **1. Single Execution Safety**
- Execute only one MCP tool per architectural analysis
- Complete prevention of infinite recursion and circular calls

### **2. Comprehensive Analysis**
- System-wide architectural assessment
- Design pattern evaluation and recommendations
- Scalability and performance architecture review

### **3. Best Practices Integration**
- Industry-standard architectural patterns
- Modern system design principles
- Scalable and maintainable architecture guidance

### **4. Implementation Guidance**
- Concrete architectural improvement plans
- Migration strategies and refactoring guidance
- Technology stack recommendations

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

Architect provides **comprehensive system architecture analysis and design recommendations**!

- ✅ **Single safe execution** of architectural analysis
- ✅ **Complete architectural assessment** in one call
- ✅ **Industry best practices** and modern design patterns
- ✅ **Implementation guidance** for architectural improvements

Now **professional architectural analysis** is available through single MCP execution! 🏗️✨
