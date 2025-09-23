"""
Super Prompt MCP Server - Simple Version

This is a simple version of the MCP server that manually registers all tools using @mcp.tool() decorator.
"""

import json
import os
import sys
from typing import Optional

# Initialize MCP components
try:
    from .mcp.version_detection import import_mcp_components, create_fallback_mcp

    FastMCP, TextContent, _MCP_VERSION = import_mcp_components()
    _HAS_MCP = True
except Exception:
    _HAS_MCP = False
    mcp_stub, TextContent = create_fallback_mcp()
    FastMCP = None

# Initialize MCP server
if _HAS_MCP and FastMCP:
    try:
        server_name = "super-prompt"
        mcp = FastMCP(name=server_name)
    except Exception:
        mcp, _ = create_fallback_mcp()
else:
    mcp, _ = create_fallback_mcp()

# Import required modules
from .personas.tools.system_tools import (
    sp_version,
    sp_list_commands,
    list_personas,
    mode_get,
    mode_set,
    grok_mode_on,
    gpt_mode_on,
    grok_mode_off,
    gpt_mode_off,
)
from .sdd.architecture import render_sdd_brief, list_sdd_sections
from .mode_store import get_mode, set_mode
from .context.collector import ContextCollector
from .core.memory_manager import span_manager, progress, memory_span
from .personas.pipeline_manager import PersonaPipeline
from .codex.client import run_codex_high_with_fallback
from .prompts.workflow_executor import run_prompt_based_workflow
from .high_mode import is_high_mode_enabled, set_high_mode

# Tool registry for stdio access
_TOOL_REGISTRY = {}


def _format_codex_context(context_result, max_files: int = 6, snippet_chars: int = 600, max_chars: int = 8000) -> str:
    """Convert collected context into a compact digest for Codex prompts."""

    if not context_result:
        return ""

    files = list(context_result.get("files") or [])
    if not files:
        return ""

    selected = files[:max_files]
    header_paths = ", ".join(part.get("path", "") for part in selected if part.get("path"))
    sections = []
    if header_paths:
        sections.append(f"Focus files: {header_paths}")

    for idx, part in enumerate(selected, start=1):
        path = part.get("path", "unknown") or "unknown"
        snippet = (part.get("content") or "").strip()
        if not snippet:
            continue
        snippet = snippet.replace("```", "``")
        if len(snippet) > snippet_chars:
            snippet = snippet[:snippet_chars] + "..."
        sections.append(f"[{idx}] {path}\n{snippet}")

    digest = "\n\n".join(sections).strip()
    if not digest:
        return ""
    if len(digest) > max_chars:
        digest = digest[:max_chars] + "\n\n[context truncated]"
    return digest


# Register basic tools
@mcp.tool()
def sp_health() -> str:
    """Check if Super Prompt MCP server is healthy"""
    return "Super Prompt MCP server is running"


_TOOL_REGISTRY["sp_health"] = sp_health


@mcp.tool(name="sp.version")
def sp_version_mcp() -> str:
    """Get the current version of Super Prompt"""
    return sp_version()


_TOOL_REGISTRY["sp.version"] = sp_version_mcp


@mcp.tool(name="sp_list_commands")
def sp_list_commands_mcp() -> str:
    """List all available Super Prompt commands"""
    return sp_list_commands()


_TOOL_REGISTRY["sp_list_commands"] = sp_list_commands_mcp


@mcp.tool(name="sp_list_personas")
def sp_list_personas_mcp() -> str:
    """List available Super Prompt personas"""
    result = list_personas()
    return result.text if hasattr(result, "text") else str(result)


_TOOL_REGISTRY["sp_list_personas"] = sp_list_personas_mcp


@mcp.tool(name="sp_init")
def sp_init_mcp(force: bool = False):
    """Initialize Super Prompt for current project"""
    result = init(force=force)
    return result.text if hasattr(result, "text") else str(result)


_TOOL_REGISTRY["sp_init"] = sp_init_mcp


@mcp.tool(name="sp_refresh")
def sp_refresh_mcp():
    """Refresh Super Prompt assets in current project"""
    result = refresh()
    return result.text if hasattr(result, "text") else str(result)


_TOOL_REGISTRY["sp_refresh"] = sp_refresh_mcp


@mcp.tool(name="sp_mode_get")
def sp_mode_get_mcp():
    """Get current LLM mode (gpt|grok)"""
    result = mode_get()
    return result.text if hasattr(result, "text") else str(result)


_TOOL_REGISTRY["sp_mode_get"] = sp_mode_get_mcp


@mcp.tool(name="sp_mode_set")
def sp_mode_set_mcp(mode: str):
    """Set LLM mode to 'gpt' or 'grok'"""
    result = mode_set(mode)
    return result.text if hasattr(result, "text") else str(result)


_TOOL_REGISTRY["sp_mode_set"] = sp_mode_set_mcp


@mcp.tool(name="sp_grok_mode_on")
def sp_grok_mode_on_mcp():
    """Switch LLM mode to grok"""
    try:
        grok_mode_on()
        return "-------- Grok mode: ENABLED (.cursor/.grok-mode)"
    except Exception as e:
        return f"❌ Error enabling Grok mode: {str(e)}"


_TOOL_REGISTRY["sp_grok_mode_on"] = sp_grok_mode_on_mcp


@mcp.tool(name="sp_gpt_mode_on")
def sp_gpt_mode_on_mcp():
    """Switch LLM mode to gpt"""
    try:
        gpt_mode_on()
        return "-------- GPT mode: ENABLED (.cursor/.gpt-mode)"
    except Exception as e:
        return f"❌ Error enabling GPT mode: {str(e)}"


_TOOL_REGISTRY["sp_gpt_mode_on"] = sp_gpt_mode_on_mcp


@mcp.tool(name="sp_grok_mode_off")
def sp_grok_mode_off_mcp():
    """Turn off Grok mode"""
    try:
        grok_mode_off()
        return "-------- Grok mode: DISABLED"
    except Exception as e:
        return f"❌ Error disabling Grok mode: {str(e)}"


_TOOL_REGISTRY["sp_grok_mode_off"] = sp_grok_mode_off_mcp


@mcp.tool(name="sp_gpt_mode_off")
def sp_gpt_mode_off_mcp():
    """Turn off GPT mode"""
    try:
        gpt_mode_off()
        return "-------- GPT mode: DISABLED"
    except Exception as e:
        return f"❌ Error disabling GPT mode: {str(e)}"


_TOOL_REGISTRY["sp_gpt_mode_off"] = sp_gpt_mode_off_mcp


@mcp.tool(name="sp_high_mode_on")
def sp_high_mode_on_mcp():
    """Enable Codex-backed high reasoning."""
    try:
        set_high_mode(True)
        return "-------- High mode: ENABLED"
    except Exception as e:
        return f"❌ Error enabling high mode: {str(e)}"


_TOOL_REGISTRY["sp_high_mode_on"] = sp_high_mode_on_mcp


@mcp.tool(name="sp_high_mode_off")
def sp_high_mode_off_mcp():
    """Disable Codex-backed high reasoning."""
    try:
        set_high_mode(False)
        return "-------- High mode: DISABLED"
    except Exception as e:
        return f"❌ Error disabling high mode: {str(e)}"


_TOOL_REGISTRY["sp_high_mode_off"] = sp_high_mode_off_mcp


# Context Management Protocol Tools
@mcp.tool()
def sp_context_collect(query: str, max_tokens: int = 16000) -> str:
    """Collect relevant context for a given query using Context Management Protocol"""
    try:
        with memory_span(f"context_collect_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Collecting context for: {query[:50]}...")

            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=max_tokens)

            span_manager.write_event(
                span_id,
                {
                    "type": "context_collected",
                    "query": query,
                    "files_count": len(context_result.get("files", [])),
                    "total_tokens": context_result.get("metadata", {}).get("context_tokens", 0),
                },
            )

            files_info = []
            for file_info in context_result.get("files", []):
                files_info.append(f"📁 {file_info['path']}: {file_info.get('tokens', 0)} tokens")

            result = f"""Context collected successfully:

📊 Collection Stats:
• Query: {query}
• Files processed: {context_result.get('metadata', {}).get('total_files_scanned', 0)}
• Total tokens: {context_result.get('metadata', {}).get('context_tokens', 0)}
• Collection time: {context_result.get('metadata', {}).get('collection_time', 0):.2f}s

📁 Relevant Files:
{chr(10).join(files_info[:10])}  # Show first 10 files

✅ Context collection completed"""

            progress.show_success("Context collection completed")
            return result

    except Exception as e:
        progress.show_error(f"Context collection failed: {str(e)}")
        return f"Context collection error: {str(e)}"


_TOOL_REGISTRY["sp_context_collect"] = sp_context_collect


@mcp.tool()
def sp_context_clear_cache() -> str:
    """Clear the context collection cache"""
    try:
        with memory_span("context_clear_cache") as span_id:
            collector = ContextCollector()
            collector.clear_cache()

            span_manager.write_event(
                span_id, {"type": "cache_cleared", "action": "context_cache_clear"}
            )

            progress.show_success("Context cache cleared")
            return "Context collection cache has been cleared successfully"

    except Exception as e:
        progress.show_error(f"Cache clear failed: {str(e)}")
        return f"Cache clear error: {str(e)}"


_TOOL_REGISTRY["sp_context_clear_cache"] = sp_context_clear_cache


@mcp.tool()
def sp_memory_stats() -> str:
    """Get memory and span management statistics"""
    try:
        with memory_span("memory_stats") as span_id:
            span_stats = {
                "active_spans": len(span_manager.spans),
                "total_spans": span_manager._span_counter,
            }

            collector = ContextCollector()
            context_stats = collector.get_stats()

            span_manager.write_event(
                span_id,
                {
                    "type": "stats_retrieved",
                    "span_stats": span_stats,
                    "context_stats": context_stats,
                },
            )

            result = f"""Memory Management Statistics:

📊 Span Statistics:
• Active spans: {span_stats['active_spans']}
• Total spans created: {span_stats['total_spans']}

📊 Context Collection Statistics:
• Cache size: {context_stats.get('cache_size', 0)} entries
• .gitignore loaded: {context_stats.get('gitignore_loaded', False)}

✅ Statistics retrieved successfully"""

            return result

    except Exception as e:
        return f"Memory stats error: {str(e)}"


_TOOL_REGISTRY["sp_memory_stats"] = sp_memory_stats


# Persona-based analysis tools
def _normalize_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "on"}


@mcp.tool()
def sp_high(query: str, persona: str = "high", force_codex: Optional[bool] = False):
    """High persona planning via Codex high-effort reasoning."""

    try:
        force = _normalize_bool(force_codex)

        if not force and not is_high_mode_enabled():
            use_pipeline = os.getenv("USE_PIPELINE", "false").lower() == "true"
            if not use_pipeline:
                try:
                    return run_prompt_based_workflow("high", query)
                except Exception:
                    use_pipeline = True

            if use_pipeline:
                pipeline = PersonaPipeline()
                result = pipeline.run_persona("high", query)
                return result.text if hasattr(result, "text") else str(result)

        with memory_span(f"persona_high_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Collecting context for high reasoning: {query[:64]}...")

            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)
            context_digest = _format_codex_context(context_result)

            span_manager.write_event(
                span_id,
                {
                    "type": "codex_context_prepared",
                    "persona": persona or "high",
                    "query_preview": query[:120],
                    "context_files": [
                        part.get("path")
                        for part in (context_result.get("files") or [])[:6]
                    ],
                },
            )

            progress.show_progress("Running Codex high reasoning plan...")
            plan_output = run_codex_high_with_fallback(query=query, context=context_digest, persona=persona)

            success = not isinstance(plan_output, dict) and not str(plan_output).startswith("❌")
            span_manager.write_event(
                span_id,
                {
                    "type": "codex_high_completed",
                    "persona": persona or "high",
                    "success": success,
                    "preview": str(plan_output)[:400],
                },
            )

            if success:
                progress.show_success("High reasoning plan ready")
            else:
                progress.show_error("Codex high reasoning reported an issue")

            if isinstance(plan_output, dict):
                return json.dumps(plan_output, ensure_ascii=False)
            return plan_output

    except Exception as error:
        progress.show_error(f"High analysis failed: {error}")
        return f"High analysis error: {error}"


_TOOL_REGISTRY["sp_high"] = sp_high


@mcp.tool()
def sp_grok(query: str, persona: str = "grok"):
    """Grok persona: sp_grok analysis"""
    try:
        with memory_span(f"persona_grok_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Running grok analysis for: {query[:50]}...")

            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)

            span_manager.write_event(
                span_id,
                {
                    "type": "persona_analysis_started",
                    "persona": "grok",
                    "query": query,
                    "context_files": len(context_result.get("files", [])),
                },
            )

            pipeline = PersonaPipeline()
            result = pipeline.run_persona("grok", query)

            span_manager.write_event(
                span_id, {"type": "persona_analysis_completed", "persona": "grok", "success": True}
            )

            response = result.text if hasattr(result, "text") else str(result)
            progress.show_success("Grok analysis completed")
            return response

    except Exception as e:
        progress.show_error(f"Grok analysis failed: {str(e)}")
        return f"Grok analysis error: {str(e)}"


_TOOL_REGISTRY["sp_grok"] = sp_grok


@mcp.tool()
def sp_gpt(query: str, persona: str = "gpt"):
    """Gpt persona: sp_gpt analysis"""
    try:
        # Use prompt-based workflow for GPT persona (no pipeline config for 'gpt')
        from .prompts.workflow_executor import run_prompt_based_workflow
        return run_prompt_based_workflow("gpt", query)

    except Exception as e:
        return f"Gpt analysis error: {str(e)}"


_TOOL_REGISTRY["sp_gpt"] = sp_gpt


# SDD Workflow Tools
@mcp.tool()
def sp_specify(query: str, persona: str = "specify"):
    """SDD Phase 1: Requirements specification and gathering"""
    try:
        from .prompts.workflow_executor import run_prompt_based_workflow

        return run_prompt_based_workflow("specify", query)
    except Exception as e:
        return f"SDD Specify error: {str(e)}"


_TOOL_REGISTRY["sp_specify"] = sp_specify


@mcp.tool()
def sp_plan(query: str, persona: str = "plan"):
    """SDD Phase 2: Implementation planning and technical roadmap"""
    try:
        from .prompts.workflow_executor import run_prompt_based_workflow

        return run_prompt_based_workflow("plan", query)
    except Exception as e:
        return f"SDD Plan error: {str(e)}"


_TOOL_REGISTRY["sp_plan"] = sp_plan


@mcp.tool()
def sp_tasks(query: str, persona: str = "tasks"):
    """SDD Phase 3: Task breakdown and project execution planning"""
    try:
        from .prompts.workflow_executor import run_prompt_based_workflow

        return run_prompt_based_workflow("tasks", query)
    except Exception as e:
        return f"SDD Tasks error: {str(e)}"


_TOOL_REGISTRY["sp_tasks"] = sp_tasks


@mcp.tool(name="sp.sdd_architecture")
def sp_sdd_architecture(section: str = "", persona: Optional[str] = None):
    """Surface the Spec-Driven Development architecture playbook."""
    try:
        target_section = section.strip() or None
        brief = render_sdd_brief(target_section, persona)
        if target_section:
            return brief
        available = ", ".join(list_sdd_sections())
        return f"{brief}\n\nSections available: {available}"
    except ValueError as exc:
        available = ", ".join(list_sdd_sections())
        return f"SDD architecture error: {exc}. Known sections: {available}"


_TOOL_REGISTRY["sp.sdd_architecture"] = sp_sdd_architecture


@mcp.tool()
def sp_troubleshooting(query: str, persona: str = "troubleshooting"):
    """Troubleshooting: Systematic problem diagnosis, root cause analysis, and resolution strategies"""
    try:
        from .prompts.workflow_executor import run_prompt_based_workflow

        return run_prompt_based_workflow("troubleshooting", query)
    except Exception as e:
        return f"Troubleshooting error: {str(e)}"


_TOOL_REGISTRY["sp_troubleshooting"] = sp_troubleshooting


# Persona tools with manual registration
@mcp.tool()
def sp_analyzer(query: str) -> str:
    """Analyzer persona: sp_analyzer analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("analyzer", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Analyzer analysis error: {str(e)}"


_TOOL_REGISTRY["sp_analyzer"] = sp_analyzer


@mcp.tool()
def sp_architect(query: str) -> str:
    """Architect persona: sp_architect analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("architect", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Architect analysis error: {str(e)}"


_TOOL_REGISTRY["sp_architect"] = sp_architect


@mcp.tool()
def sp_doc_master(query: str) -> str:
    """Doc Master persona: sp_doc_master analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("doc-master", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Doc Master analysis error: {str(e)}"


_TOOL_REGISTRY["sp_doc_master"] = sp_doc_master


@mcp.tool()
def sp_refactorer(query: str) -> str:
    """Refactorer persona: sp_refactorer analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("refactorer", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Refactorer analysis error: {str(e)}"


_TOOL_REGISTRY["sp_refactorer"] = sp_refactorer


@mcp.tool()
def sp_frontend(query: str) -> str:
    """Frontend persona: sp_frontend analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("frontend", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Frontend analysis error: {str(e)}"


_TOOL_REGISTRY["sp_frontend"] = sp_frontend


@mcp.tool()
def sp_backend(query: str) -> str:
    """Backend persona: sp_backend analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("backend", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Backend analysis error: {str(e)}"


_TOOL_REGISTRY["sp_backend"] = sp_backend


@mcp.tool()
def sp_dev(query: str) -> str:
    """Dev persona: sp_dev analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("dev", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Dev analysis error: {str(e)}"


_TOOL_REGISTRY["sp_dev"] = sp_dev


@mcp.tool()
def sp_security(query: str) -> str:
    """Security persona: sp_security analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("security", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Security analysis error: {str(e)}"


_TOOL_REGISTRY["sp_security"] = sp_security


@mcp.tool()
def sp_performance(query: str) -> str:
    """Performance persona: sp_performance analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("performance", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Performance analysis error: {str(e)}"


_TOOL_REGISTRY["sp_performance"] = sp_performance


@mcp.tool()
def sp_qa(query: str) -> str:
    """QA persona: sp_qa analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("qa", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"QA analysis error: {str(e)}"


_TOOL_REGISTRY["sp_qa"] = sp_qa


@mcp.tool()
def sp_devops(query: str) -> str:
    """DevOps persona: sp_devops analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("devops", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"DevOps analysis error: {str(e)}"


_TOOL_REGISTRY["sp_devops"] = sp_devops


@mcp.tool()
def sp_db_expert(query: str) -> str:
    """DB Expert persona: sp_db_expert analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("db-expert", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"DB Expert analysis error: {str(e)}"


_TOOL_REGISTRY["sp_db_expert"] = sp_db_expert


@mcp.tool()
def sp_review(query: str) -> str:
    """Review persona: sp_review analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("review", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Review analysis error: {str(e)}"


_TOOL_REGISTRY["sp_review"] = sp_review


@mcp.tool()
def sp_optimize(query: str) -> str:
    """Optimize persona: sp_optimize analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("optimize", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Optimize analysis error: {str(e)}"


_TOOL_REGISTRY["sp_optimize"] = sp_optimize


@mcp.tool()
def sp_service_planner(query: str) -> str:
    """Service Planner persona: sp_service_planner analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("service-planner", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Service Planner analysis error: {str(e)}"


_TOOL_REGISTRY["sp_service_planner"] = sp_service_planner


@mcp.tool()
def sp_docs_refector(query: str) -> str:
    """Docs Refector persona: sp_docs_refector analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("docs-refector", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Docs Refector analysis error: {str(e)}"


_TOOL_REGISTRY["sp_docs_refector"] = sp_docs_refector


@mcp.tool()
def sp_resercher(query: str, persona: str = "resercher") -> str:
    """Resercher persona: sp_resercher analysis"""
    try:
        from .prompts.workflow_executor import run_prompt_based_workflow

        return run_prompt_based_workflow("resercher", query)
    except Exception as e:
        return f"Resercher analysis error: {str(e)}"


_TOOL_REGISTRY["sp_resercher"] = sp_resercher


@mcp.tool()
def sp_double_check(query: str, persona: str = "double_check") -> str:
    """Double Check persona: sp_double_check analysis"""
    try:
        from .prompts.workflow_executor import run_prompt_based_workflow

        return run_prompt_based_workflow("double_check", query)
    except Exception as e:
        return f"Double Check analysis error: {str(e)}"


_TOOL_REGISTRY["sp_double_check"] = sp_double_check


@mcp.tool()
def sp_seq(query: str) -> str:
    """Sequential persona: sp_seq analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("seq", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Sequential analysis error: {str(e)}"


_TOOL_REGISTRY["sp_seq"] = sp_seq


@mcp.tool()
def sp_seq_ultra(query: str) -> str:
    """Sequential Ultra persona: sp_seq_ultra analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("seq-ultra", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Sequential Ultra analysis error: {str(e)}"


_TOOL_REGISTRY["sp_seq_ultra"] = sp_seq_ultra


@mcp.tool()
def sp_ultracompressed(query: str) -> str:
    """Ultra Compressed persona: sp_ultracompressed analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("ultracompressed", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Ultra Compressed analysis error: {str(e)}"


_TOOL_REGISTRY["sp_ultracompressed"] = sp_ultracompressed


@mcp.tool()
def sp_wave(query: str) -> str:
    """Wave persona: sp_wave analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("wave", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Wave analysis error: {str(e)}"


_TOOL_REGISTRY["sp_wave"] = sp_wave


@mcp.tool()
def sp_debate(query: str) -> str:
    """Debate persona: sp_debate analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("debate", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Debate analysis error: {str(e)}"


_TOOL_REGISTRY["sp_debate"] = sp_debate


@mcp.tool()
def sp_mentor(query: str) -> str:
    """Mentor persona: sp_mentor analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("mentor", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Mentor analysis error: {str(e)}"


_TOOL_REGISTRY["sp_mentor"] = sp_mentor


@mcp.tool()
def sp_scribe(query: str) -> str:
    """Scribe persona: sp_scribe analysis"""
    try:
        pipeline = PersonaPipeline()
        result = pipeline.run_persona("scribe", query)
        return result.text if hasattr(result, "text") else str(result)
    except Exception as e:
        return f"Scribe analysis error: {str(e)}"


_TOOL_REGISTRY["sp_scribe"] = sp_scribe

# Export the mcp instance and tool registry for use by mcp_stdio.py
__all__ = ["mcp", "_TOOL_REGISTRY"]
