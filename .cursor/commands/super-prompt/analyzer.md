---
description: analyzer command - Systematic root cause analysis
run: inline
script: |
  const { spawn } = require('child_process');
  const path = require('path');

  function executeAnalyzer(query) {
    return new Promise((resolve, reject) => {
      const projectRoot = process.cwd();
      const packageRoot = path.join(__dirname, '..', '..', '..', '..', '..');

      // Execute the analyzer function directly via Python script
      const pythonCmd = [
        'python3',
        path.join(packageRoot, 'packages', 'core-py', 'super_prompt', 'workflow_runner.py'),
        'analyzer',
        query
      ];

      console.error(\`-------- analyzer: Executing inline analysis: \${query.substring(0, 50)}...\`);

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
          console.error(\`-------- analyzer: Analysis completed successfully\`);
          resolve(stdout.trim());
        } else {
          console.error(\`-------- analyzer: Failed with code \${code}\`);
          console.error(\`-------- analyzer: stderr: \${stderr}\`);
          reject(new Error(\`Analyzer execution failed: \${stderr || 'Unknown error'}\`));
        }
      });

      proc.on('error', (error) => {
        console.error(\`-------- analyzer: Execution error: \${error.message}\`);
        reject(error);
      });
    });
  }

  async function runAnalyzerCommand(input) {
    try {
      console.error(\`-------- analyzer: Starting inline execution for: \${input.substring(0, 50)}...\`);

      // Execute analyzer analysis directly
      const result = await executeAnalyzer(input);

      if (!result || result.trim() === '') {
        return \`## 🔍 **Analyzer Analysis Result**

**Query:** \${input}

### ⚠️ **Analysis Status: Incomplete**

Analyzer execution completed but returned no content. This may indicate:

1. **Query too complex** - Try breaking it into smaller parts
2. **Module import issues** - Check Python path configuration
3. **Function execution error** - Verify analyzer function implementation

### 💡 **Suggestions:**

- Simplify your query and try again
- Check Python environment and dependencies
- Verify the analyzer module is properly installed

**Raw Output:** (empty)\`;
      }

      return result;

    } catch (error) {
      console.error(\`-------- analyzer: Inline execution failed: \${error.message}\`);

      return \`## 🔍 **Analyzer Analysis Error**

**Query:** \${input}

### ❌ **Execution Failed**

The inline analyzer execution encountered an error:

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
You can also try the MCP-based analyzer command if inline execution continues to fail.

**Fallback Command:** \`/super-prompt/analyzer "\${input}"\` (will use MCP server)\`;
    }
  }

  // Export the main function
  module.exports = runAnalyzerCommand;

# 🔍 **Analyzer - Single-Focus Systematic Root Cause Analysis**

**Safe Approach**: Execute only one MCP tool per persona!

## 🎯 **Single Analysis Workflow**

### **Single Step Analysis:**

1. **🔍 Comprehensive Analysis** - Current Tool (analyzer)
   - Current analyzer performs systematic problem analysis
   - Apply optimized analysis strategy based on mode (GPT/Grok)
   - Identify root causes and propose solutions
   - Provide comprehensive analysis results in single execution

## 🏗️ **Implementation Strategy**

### **Current Structure vs Safe Single Structure:**

| **Current Structure** | **Safe Single Structure** |
|----------------------|--------------------------|
| `_run_persona_pipeline()` direct call | Single `sp_analyzer` MCP call |
| Multi-persona collaboration | Execute only one persona |
| Internal function calls | MCP protocol compliance |
| Complex workflows | Simple and safe execution |

### **Single Execution TODO System:**

## 📋 **Analysis TODO List**

### Phase 1: Problem Analysis
- [x] **Problem Definition & Scope Identification**
  - Query: `${input}`
- [x] **Current Mode Analysis Strategy Selection**
  - Apply optimized analysis method based on mode

### Phase 2: Root Cause Identification
- [ ] **Systematic Analysis Execution**
  - Multi-perspective analysis (architecture, performance, security)
- [ ] **Root Cause Derivation**
  - Evidence-based analysis and causality identification

### Phase 3: Solution Development
- [ ] **Specific Solution Presentation**
  - Feasible solutions and implementation plans
- [ ] **Risk Assessment & Mitigation Strategy**
  - Potential issues and resolution approaches

### Phase 4: Preventive Measures
- [ ] **Monitoring & Prevention Strategy**
  - Continuous monitoring and recurrence prevention
- [ ] **Process Improvement Recommendations**
  - System improvements and quality enhancements

## 🚀 **Execution Method**

### **Single MCP Execution Mode:**
1. User inputs `/super-prompt/analyzer "problem"`
2. `sp_analyzer` tool executes alone
3. One persona performs all analysis
4. Single comprehensive analysis output

### **Mode-Specific Optimization:**
- **Grok Mode**: Apply creative and integrated analysis approach
- **GPT Mode**: Apply structured and systematic analysis approach

### **Usage Example:**
```
/super-prompt/analyzer "API performance degradation issue"
    ↓
2. sp_analyzer executes alone (safe single call)
    ↓
3. One persona performs all analysis
    ↓
4. Comprehensive analysis results output
```

## 💡 **Innovative Advantages**

### **1. Single Execution Safety**
- Execute only one MCP tool per persona
- Complete prevention of infinite recursion and circular calls

### **2. Mode-Specific Optimization**
- Auto-optimize analysis method based on Grok/GPT mode
- Perform single analysis leveraging each mode's strengths

### **3. Simple and Stable Architecture**
- Remove complex workflows, simple single call
- Enhance system stability and predictability

### **4. Comprehensive Analysis Delivery**
- Perform multi-perspective analysis within one persona
- Provide systematic and integrated analysis results

## 🎯 **Next Implementation Steps**

### **Phase 1: MCP Call Wrapper Implementation**
```python
class MCPWorkflowManager:
    async def execute_workflow(self, steps: List[Dict]) -> Dict:
        """Execute MCP-based workflow"""
        results = {}
        for step in steps:
            tool_name = step['tool']
            query = step['query']
            result = await self.call_mcp_tool(tool_name, query)
            results[step['name']] = result
        return results
```

### **Phase 2: Command-Embedded TODO System**
- Generate markdown-based TODO list
- Link MCP tools to each TODO item
- Real-time progress tracking

### **Phase 3: Smart Result Aggregation**
- AI automatically aggregates results from each step
- Identify contradictions and suggest solutions
- Auto-generate final analysis report

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

This approach is an **innovation that can completely change Super Prompt's future**!

- ❌ **Previous**: Pipeline + direct function calls + complex workflows
- ✅ **New**: Single MCP call + protocol compliance + safe execution

Now **a safe and simple single analysis system** is complete! 🛡️✨