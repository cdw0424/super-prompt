---
description: confession-high-gpt command (GPT-mode double-check validation)
run: mcp
server: super-prompt
tool: sp_confession_high_gpt
args:
  tool_name: "${input:tool_name}"
  original_query: "${input:original_query}"
  draft_response: "${input:draft_response}"
  context: "${input:context}"
---

🔍 **Confession High GPT - XML-Structured Double-Check Validation**

**Purpose**: Quality assurance tool using GPT-mode structured reasoning with XML-formatted prompts and systematic analysis approach.

**Key Features**:
- XML-structured prompts for precise instruction parsing
- Systematic reasoning with detailed checklists
- Structured output format with clear sections
- Self-reflection stage for quality validation
- Comprehensive technical accuracy assessment

**Usage**:
- **tool_name**: Source tool that generated the response
- **original_query**: The original user query
- **draft_response**: The response content to validate
- **context**: Additional context (optional)

**Example**:
```
/confession-high-gpt tool_name="sp_refactorer" original_query="Optimize this code" draft_response="Here's the optimized version..." context="Performance-critical application"
```

**GPT Mode Characteristics**:
- ✅ XML block structure for clear instruction parsing
- ✅ Detailed reasoning effort allocation
- ✅ Systematic checklist-based validation
- ✅ Structured self-reflection process
- ✅ Comprehensive technical assessment

**Output**: XML-influenced structured validation report with detailed analysis sections.
