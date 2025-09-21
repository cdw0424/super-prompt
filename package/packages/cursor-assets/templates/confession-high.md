---
description: confession-high command (mode-aware standalone double-check validation)
run: mcp
server: super-prompt
tool: sp_confession_high
args:
  tool_name: "${input:tool_name}"
  original_query: "${input:original_query}"
  draft_response: "${input:draft_response}"
  context: "${input:context}"
---

🔍 **Confession High - Mode-Aware Standalone Double-Check Validation**

**Purpose**: Intelligent quality assurance and validation tool that automatically selects the optimal analysis mode (GPT or Grok) based on current system settings.

**Usage**:
- **tool_name**: Source tool that generated the response (e.g., "sp_architect", "sp_refactorer")
- **original_query**: The original user query that was processed
- **draft_response**: The response content to validate
- **context**: Additional context (optional)

**Mode Selection**:
- **GPT Mode**: Uses XML-structured prompts with systematic reasoning and detailed checklists
- **Grok Mode**: Uses Markdown-structured prompts with iterative refinement and targeted analysis
- **Auto Mode**: Automatically selects based on current system mode (`/mode get` to check)

**Example**:
```
/confession-high tool_name="sp_architect" original_query="Design a scalable API" draft_response="Here's my API design..." context="For a fintech application"
```

**Available Specialized Tools**:
- `sp_confession_high_gpt`: Force GPT mode analysis
- `sp_confession_high_grok`: Force Grok mode analysis
- `sp_confession_high`: Auto mode selection (recommended)

**Features**:
- ✅ Mode-aware analysis with optimal prompt structure
- ✅ Independent validation without recursion
- ✅ Codex high reasoning for quality analysis
- ✅ Structured QA framework with mode-specific formatting
- ✅ Technical accuracy validation
- ✅ Confidence scoring and recommendations
- ✅ Automatic error handling and fallback

**Output**: Comprehensive validation report with mode-appropriate formatting and actionable insights.
