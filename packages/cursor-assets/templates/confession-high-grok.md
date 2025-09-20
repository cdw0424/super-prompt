---
description: confession-high-grok command (Grok-mode double-check validation)
run: mcp
server: super-prompt
tool: sp_confession_high_grok
args:
  tool_name: "${input:tool_name}"
  original_query: "${input:original_query}"
  draft_response: "${input:draft_response}"
  context: "${input:context}"
---

🔍 **Confession High Grok - Markdown-Structured Double-Check Validation**

**Purpose**: Quality assurance tool using Grok-mode iterative reasoning with Markdown-formatted prompts and targeted analysis approach.

**Key Features**:
- Markdown-structured prompts for flexible instruction parsing
- Iterative refinement with targeted context usage
- Agentic approach with helpful and truthful analysis
- Tool budget awareness and efficient processing
- Focused quality improvement recommendations

**Usage**:
- **tool_name**: Source tool that generated the response
- **original_query**: The original user query
- **draft_response**: The response content to validate
- **context**: Additional context (optional)

**Example**:
```
/confession-high-grok tool_name="sp_architect" original_query="Design microservices" draft_response="Here's the architecture..." context="High-traffic e-commerce platform"
```

**Grok Mode Characteristics**:
- ✅ Markdown heading structure for clear organization
- ✅ Iterative refinement with context targeting
- ✅ Agentic approach with efficient analysis
- ✅ Tool-aware processing with budget consideration
- ✅ Concise but thorough quality assessment

**Output**: Markdown-structured validation report with iterative improvement recommendations.
