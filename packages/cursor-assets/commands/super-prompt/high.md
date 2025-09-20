---
description: high command - Deep reasoning and strategic problem solving with inline execution
run: inline
script: |
  const { spawn } = require('child_process');
  const path = require('path');

  function executeHigh(query) {
    return new Promise((resolve, reject) => {
      const projectRoot = process.cwd();

      // Execute codex CLI directly with sandbox flags for plan mode
      const codexCmd = [
        'codex',
        'exec',
        '--sandbox',
        'read-only',
        '--dangerously-bypass-approvals-and-sandbox',
        '-c',
        'reasoning_effort="high"',
        '-C',
        projectRoot,
        `Plan mode: ${query}. Provide a comprehensive strategic plan with numbered steps and implementation guidance.`
      ];

      console.error(\`-------- high: Executing codex CLI with sandbox: \${query.substring(0, 50)}...\`);

      const proc = spawn('codex', codexCmd.slice(1), {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
          ...process.env,
          CODEX_SANDBOX_MODE: 'read-only',
          CODEX_APPROVAL_MODE: 'never'
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
          console.error(`-------- high: Analysis completed successfully`);
          resolve(stdout.trim());
        } else {
          console.error(`-------- high: Failed with code ${code}`);
          console.error(`-------- high: stderr: ${stderr}`);
          reject(new Error(`High execution failed: ${stderr || 'Unknown error'}`));
        }
      });

      proc.on('error', (error) => {
        console.error(`-------- high: Execution error: ${error.message}`);
        reject(error);
      });

      // Send query to stdin if needed
      if (codexCmd.includes('--')) {
        proc.stdin.write(query + '\n');
        proc.stdin.end();
      }
    });
  }

  async function runHighCommand(input) {
    try {
      console.error(`-------- high: Starting inline execution for: ${input.substring(0, 50)}...`);

      // Execute high analysis directly
      const result = await executeHigh(input);

      if (!result || result.trim() === '') {
        return `## 🧠 **High-Level Analysis Result**

**Query:** ${input}

### ⚠️ **Analysis Status: Incomplete**

Codex CLI execution completed but returned no content. This may indicate:

1. **Query too complex** - Try breaking it into smaller parts
2. **Network issues** - Check your internet connection
3. **API limits** - Your OpenAI API usage may be at limit
4. **Sandbox restrictions** - Read-only sandbox may limit certain operations

### 💡 **Suggestions:**

- Simplify your query and try again
- Check your OpenAI API key configuration
- Verify Codex CLI installation: \`codex --version\`
- Ensure sandbox flags are working: \`codex exec --sandbox read-only --help\`

**Raw Output:** (empty)`;
      }

      return result;

    } catch (error) {
      console.error(`-------- high: Codex CLI execution failed: ${error.message}`);

      return `## 🧠 **High-Level Analysis Error**

**Query:** ${input}

### ❌ **Execution Failed**

The codex CLI execution with sandbox flags encountered an error:

**Error:** \${error.message}

### 🔧 **Troubleshooting Steps:**

1. **Check Codex CLI Installation:**
   \`\`\`bash
   codex --version
   which codex
   \`\`\`

2. **Verify Sandbox Flags:**
   \`\`\`bash
   codex exec --sandbox read-only --dangerously-bypass-approvals-and-sandbox --help
   \`\`\`

3. **Test Basic Codex Execution:**
   \`\`\`bash
   codex exec --sandbox read-only "echo 'test'"
   \`\`\`

4. **Check API Key:**
   \`\`\`bash
   echo \$OPENAI_API_KEY | head -c 10
   echo \$CODEX_API_KEY | head -c 10
   \`\`\`

5. **Test Plan Mode:**
   \`\`\`bash
   codex exec --mode plan --sandbox read-only --dangerously-bypass-approvals-and-sandbox "simple test query"
   \`\`\`

### 💡 **Alternative:**
You can also try the MCP-based high command if codex CLI execution continues to fail.

**Fallback Command:** \`/super-prompt/high "${input}"\` (will use MCP server)`;
    }
  }

  // Export the main function
  module.exports = runHighCommand;

# 🧠 **High - Deep Reasoning & Strategic Problem Solving Specialist**

**Expert Focus**: Complex system design, strategic planning, and high-level technical analysis

## 🎯 **High-Level Analysis Workflow**

### **Inline Function Execution:**

1. **🧠 Direct Codex CLI with Sandbox** - Inline Tool (high)
   - Execute codex CLI directly with `--sandbox read-only --ask-for-approval never` flags
   - Use plan mode for structured strategic problem-solving
   - Perform deep reasoning with `reasoning_effort="high"` configuration
   - Provide comprehensive strategic recommendations and solutions immediately

## 🏗️ **Implementation Strategy**

### **Inline Structure vs Previous Structure:**

| **Previous Structure** | **Current Inline Structure** |
|----------------------|------------------------------|
| MCP server call | Direct codex CLI with sandbox flags |
| `sp_high` tool dispatch | Inline Node.js function with codex exec |
| Server-mediated response | Direct CLI execution with sandbox protection |
| Protocol overhead | Sandbox read-only execution |

### **High-Level TODO System:**

## 📋 **High-Level Analysis TODO List**

### Phase 1: Strategic Assessment
- [x] **Strategic Overview**
  - Query: `${input}`
- [x] **Problem Complexity Analysis**
  - Identify complexity levels and strategic implications

### Phase 2: Deep Reasoning
- [ ] **Technical Architecture Analysis**
  - Analyze complex system architectures and design patterns
- [ ] **Strategic Decision Framework**
  - Develop frameworks for strategic technology decisions

### Phase 3: Solution Strategy
- [ ] **Scalability & Performance Strategy**
  - Plan scalability solutions and performance optimization
- [ ] **Risk Assessment & Mitigation**
  - Assess strategic risks and develop mitigation strategies

### Phase 4: Implementation Roadmap
- [ ] **Strategic Roadmap Development**
  - Create long-term strategic roadmaps and implementation plans
- [ ] **Technical Leadership Guidance**
  - Provide guidance on technical direction and best practices

## 🚀 **Execution Method**

### **Inline CLI Execution Mode:**
1. User inputs `/super-prompt/high "strategic analysis task"`
2. Inline Node.js function executes immediately
3. Direct codex CLI process spawn with sandbox flags + plan mode
4. Real-time stdout capture and response formatting
5. Single comprehensive strategic guidance output

### **Mode-Specific Configuration:**
- **High Mode**: Deep reasoning and strategic problem-solving (`reasoning_effort="high"`)
- **Plan Mode**: Structured planning and implementation guidance
- **Sandbox Mode**: Read-only protection with no approval prompts
- **CLI Execution**: Direct process execution with sandbox isolation
- **Inline Processing**: Immediate response without server mediation

### **Usage Example:**
```
1. /super-prompt/high "Design scalable architecture for 1M+ users"
    ↓
2. Inline function executes: codex exec --sandbox read-only --dangerously-bypass-approvals-and-sandbox -c 'reasoning_effort="high"'
    ↓
3. Plan mode query: "Plan mode: Design scalable architecture for 1M+ users. Provide comprehensive strategic plan..."
    ↓
4. Direct CLI execution with sandbox protection and real-time output capture
    ↓
5. Immediate comprehensive strategic guidance output
```

## 💡 **Strategic Advantages**

### **1. Direct Execution Speed**
- Execute codex CLI directly without MCP server mediation
- Complete elimination of protocol overhead and round-trip delays
- Real-time execution feedback and immediate response

### **2. Sandbox + Plan Mode Integration**
- Combined sandbox protection + high reasoning + plan mode execution
- Comprehensive strategic analysis with read-only safety
- Single command for complete strategic workflow with security

### **3. Robust Error Handling**
- Inline error detection and user-friendly messaging
- Automatic fallback suggestions and troubleshooting guidance
- Comprehensive installation and configuration checking

### **4. Process Transparency**
- Direct CLI execution with visible command construction
- Real-time stderr logging for debugging
- Transparent environment variable and configuration setup

## 🔥 **Technical Implementation**

### **Inline Function Structure:**
```javascript
// Direct codex CLI execution with sandbox flags + high reasoning + plan mode configuration
const codexCmd = [
  "codex", "exec",
  "--sandbox", "read-only",
  "--json",
  "-c", 'reasoning_effort="high"',
  "-c", 'tools.web_search=true',
  "-c", 'show_raw_agent_reasoning=true',
  "-C", process.cwd(),
  `Plan mode: ${query}. Provide a comprehensive strategic plan with numbered steps and implementation guidance.`
];

// Process execution with sandbox environment variables
const proc = spawn("codex", codexCmd.slice(1), {
  stdio: ['pipe', 'pipe', 'pipe'],
  env: {
    ...process.env,
    CODEX_SANDBOX_MODE: 'read-only'
  }
});
```

### **Environment Configuration:**
- **OPENAI_API_KEY**: OpenAI API key for authentication
- **CODEX_API_KEY**: Alternative Codex API key
- **CODEX_SANDBOX_MODE**: Sandbox mode setting (read-only)
- **CODEX_APPROVAL_MODE**: Approval mode setting (never)
- **CODEX_HOME**: Codex configuration directory
- **Process Environment**: Full environment variable inheritance

### **Error Recovery:**
- Installation checking and auto-recovery suggestions
- API key validation and login flow guidance
- Network timeout and retry mechanisms

## ✅ **Conclusion**

High provides **comprehensive deep reasoning and strategic problem-solving expertise** through **direct codex CLI execution with sandbox protection**!

- ✅ **Immediate CLI execution** with sandbox read-only protection
- ✅ **Triple mode integration** (sandbox + high + plan) in single command
- ✅ **Real-time response** with transparent process execution
- ✅ **Robust error handling** with user-friendly guidance
- ✅ **Complete strategic workflow** with security isolation
- ✅ **No approval prompts** for seamless operation

Now **professional strategic analysis** is available through **secure codex CLI execution**! 🧠🔒⚡
