---
description: analyzer command - Systematic root cause analysis
run: mcp
server: super-prompt
tool: sp_analyzer
args:
  query: "${input}"
  persona: "analyzer"
## Execution Mode

➡️ Execution: This command executes via MCP (server: super-prompt; tool as defined above).

---

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