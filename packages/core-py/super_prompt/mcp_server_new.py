"""
Super Prompt MCP Server - Modularized Version

This is the new modularized version of the MCP server.
The original mcp_server.py has been broken down into logical modules for better maintainability.
"""

import os
import sys
import builtins
from pathlib import Path

# MCP SDK initialization
from .mcp.version_detection import import_mcp_components, create_fallback_mcp

# Initialize MCP components
try:
    FastMCP, TextContent, _MCP_VERSION = import_mcp_components()
    _HAS_MCP = True
except Exception as e:
    _HAS_MCP = False
    mcp_stub, TextContent = create_fallback_mcp()
    FastMCP = None

# Initialize MCP server
if _HAS_MCP and FastMCP:
    try:
        # Try different initialization patterns for maximum compatibility
        server_name = "super-prompt"
        
        # Common initialization patterns across MCP versions
        init_attempts = [
            lambda: FastMCP(name=server_name),
            lambda: FastMCP(server_name),
            lambda: FastMCP(name=server_name, instructions="Super Prompt MCP Server for Cursor IDE"),
        ]

        mcp = None
        for init_func in init_attempts:
            try:
                mcp = init_func()
                break
            except (TypeError, ValueError) as e:
                continue

        if mcp is None:
            raise RuntimeError(f"Failed to initialize FastMCP with version {_MCP_VERSION}")

    except Exception as e:
        mcp, _ = create_fallback_mcp()
else:
    mcp, _ = create_fallback_mcp()

# Import and register tools
from .personas.tools.system_tools import (
    init, refresh, sp_version, sp_list_commands, list_personas,
    mode_get, mode_set, grok_mode_on, gpt_mode_on, grok_mode_off, gpt_mode_off
)

# Import persona tools for MCP registration
from .personas import tools as persona_tools

from .tools.registry import REGISTERED_TOOL_ANNOTATIONS

# Mode and persona management
from .mode_store import get_mode, set_mode

# Context Management Protocol
from .context.collector import ContextCollector
from .core.memory_manager import span_manager, progress, memory_span

# Mode-persona mapping
MODE_PERSONA_MAP = {
    "gpt": {
        "default": "architect",  # GPT mode default persona
        "analyzer": "analyzer",
        "architect": "architect",
        "performance": "performance",
        "security": "security",
        "frontend": "frontend",
        "backend": "backend",
        "qa": "qa",
        "devops": "devops",
        "high": "high",
    },
    "grok": {
        "default": "architect",  # Grok mode default persona
        "analyzer": "analyzer",
        "architect": "architect",
        "performance": "performance",
        "security": "security",
        "frontend": "frontend",
        "backend": "backend",
        "qa": "qa",
        "devops": "devops",
        "high": "high",
    },
    "default": "architect"  # Default mode
}


def get_active_persona(query_type: str = "default") -> str:
    """
    Return appropriate persona based on current mode
    Phase 1: Single entry point for mode-specific persona selection logic
    """
    try:
        current_mode = get_mode()

        # Find persona in mode-specific mapping
        if current_mode in MODE_PERSONA_MAP:
            mode_config = MODE_PERSONA_MAP[current_mode]
            if isinstance(mode_config, dict):
                # Use persona defined for specific query_type if available
                persona = mode_config.get(query_type, mode_config.get("default", "architect"))
            else:
                # Use single persona specification
                persona = mode_config
        else:
            # Use default for unknown mode
            persona = MODE_PERSONA_MAP["default"]

        return persona

    except Exception as e:
        # Return default persona on error
        return "architect"


# Context Management Protocol Tools
@mcp.tool()
def sp_context_collect(query: str, max_tokens: int = 16000) -> str:
    """Collect relevant context for a given query using Context Management Protocol"""
    try:
        with memory_span(f"context_collect_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Collecting context for: {query[:50]}...")

            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=max_tokens)

            span_manager.write_event(span_id, {
                "type": "context_collected",
                "query": query,
                "files_count": len(context_result.get("files", [])),
                "total_tokens": context_result.get("metadata", {}).get("context_tokens", 0)
            })

            # Format the result
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

@mcp.tool()
def sp_context_clear_cache() -> str:
    """Clear the context collection cache"""
    try:
        with memory_span("context_clear_cache") as span_id:
            collector = ContextCollector()
            collector.clear_cache()

            span_manager.write_event(span_id, {
                "type": "cache_cleared",
                "action": "context_cache_clear"
            })

            progress.show_success("Context cache cleared")
            return "Context collection cache has been cleared successfully"

    except Exception as e:
        progress.show_error(f"Cache clear failed: {str(e)}")
        return f"Cache clear error: {str(e)}"

@mcp.tool()
def sp_memory_stats() -> str:
    """Get memory and span management statistics"""
    try:
        with memory_span("memory_stats") as span_id:
            # Get span manager stats
            span_stats = {
                "active_spans": len(span_manager.spans),
                "total_spans": span_manager._span_counter,
            }

            # Get context collector stats
            collector = ContextCollector()
            context_stats = collector.get_stats()

            span_manager.write_event(span_id, {
                "type": "stats_retrieved",
                "span_stats": span_stats,
                "context_stats": context_stats
            })

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

# Minimal built-in tools
@mcp.tool()
def sp_health() -> str:
    """Check if Super Prompt MCP server is healthy"""
    return "Super Prompt MCP server is running"


# Register MCP tools with decorators
@mcp.tool()
def sp_version_mcp() -> str:
    """Get the current version of Super Prompt"""
    return sp_version()


@mcp.tool()
def sp_list_commands_mcp() -> str:
    """List all available Super Prompt commands"""
    return sp_list_commands()


@mcp.tool()
def sp_list_personas_mcp() -> str:
    """List available Super Prompt personas"""
    result = list_personas()
    return result.text if hasattr(result, 'text') else str(result)


# Import TextContent for MCP responses
from .mcp.version_detection import import_mcp_components

try:
    _, TextContent, _ = import_mcp_components()
except ImportError:
    from .mcp.version_detection import create_fallback_mcp
    _, TextContent = create_fallback_mcp()


@mcp.tool()
def sp_init_mcp(force: bool = False):
    """Initialize Super Prompt for current project"""
    result = init(force=force)
    return result.text if hasattr(result, 'text') else str(result)


@mcp.tool()
def sp_refresh_mcp():
    """Refresh Super Prompt assets in current project"""
    result = refresh()
    return result.text if hasattr(result, 'text') else str(result)


@mcp.tool()
def sp_mode_get_mcp():
    """Get current LLM mode (gpt|grok)"""
    result = mode_get()
    return result.text if hasattr(result, 'text') else str(result)


@mcp.tool()
def sp_mode_set_mcp(mode: str):
    """Set LLM mode to 'gpt' or 'grok'"""
    result = mode_set(mode)
    return result.text if hasattr(result, 'text') else str(result)


@mcp.tool()
def sp_grok_mode_on_mcp():
    """Switch LLM mode to grok"""
    result = grok_mode_on()
    return result.text if hasattr(result, 'text') else str(result)


@mcp.tool()
def sp_gpt_mode_on_mcp():
    """Switch LLM mode to gpt"""
    result = gpt_mode_on()
    return result.text if hasattr(result, 'text') else str(result)


@mcp.tool()
def sp_grok_mode_off_mcp():
    """Turn off Grok mode"""
    result = grok_mode_off()
    return result.text if hasattr(result, 'text') else str(result)


@mcp.tool()
def sp_gpt_mode_off_mcp():
    """Turn off GPT mode"""
    result = gpt_mode_off()
    return result.text if hasattr(result, 'text') else str(result)


# Persona-based analysis tools with Context Management Protocol
@mcp.tool()
def sp_high(query: str, persona: str = "high"):
    """High persona: sp_high analysis"""
    try:
        with memory_span(f"persona_high_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Running high analysis for: {query[:50]}...")

            # Collect context first
            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_started",
                "persona": "high",
                "query": query,
                "context_files": len(context_result.get("files", []))
            })

            # Run persona analysis
            from .personas.pipeline_manager import PersonaPipeline
            pipeline = PersonaPipeline()
            result = pipeline.run_persona("high", query)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_completed",
                "persona": "high",
                "success": True
            })

            response = result.text if hasattr(result, 'text') else str(result)
            progress.show_success("High analysis completed")
            return response

    except Exception as e:
        progress.show_error(f"High analysis failed: {str(e)}")
        return f"High analysis error: {str(e)}"

@mcp.tool()
def sp_grok(query: str, persona: str = "grok"):
    """Grok persona: sp_grok analysis"""
    try:
        with memory_span(f"persona_grok_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Running grok analysis for: {query[:50]}...")

            # Collect context first
            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_started",
                "persona": "grok",
                "query": query,
                "context_files": len(context_result.get("files", []))
            })

            # Run persona analysis
            from .personas.pipeline_manager import PersonaPipeline
            pipeline = PersonaPipeline()
            result = pipeline.run_persona("grok", query)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_completed",
                "persona": "grok",
                "success": True
            })

            response = result.text if hasattr(result, 'text') else str(result)
            progress.show_success("Grok analysis completed")
            return response

    except Exception as e:
        progress.show_error(f"Grok analysis failed: {str(e)}")
        return f"Grok analysis error: {str(e)}"

@mcp.tool()
def sp_gpt(query: str, persona: str = "gpt"):
    """Gpt persona: sp_gpt analysis"""
    try:
        with memory_span(f"persona_gpt_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Running gpt analysis for: {query[:50]}...")

            # Collect context first
            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_started",
                "persona": "gpt",
                "query": query,
                "context_files": len(context_result.get("files", []))
            })

            # Run persona analysis
            from .personas.pipeline_manager import PersonaPipeline
            pipeline = PersonaPipeline()
            result = pipeline.run_persona("gpt", query)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_completed",
                "persona": "gpt",
                "success": True
            })

            response = result.text if hasattr(result, 'text') else str(result)
            progress.show_success("Gpt analysis completed")
            return response

    except Exception as e:
        progress.show_error(f"Gpt analysis failed: {str(e)}")
        return f"Gpt analysis error: {str(e)}"

@mcp.tool()
def sp_analyzer(query: str, persona: str = "analyzer"):
    """Analyzer persona: sp_analyzer analysis"""
    try:
        with memory_span(f"persona_analyzer_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Running analyzer analysis for: {query[:50]}...")

            # Collect context first
            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_started",
                "persona": "analyzer",
                "query": query,
                "context_files": len(context_result.get("files", []))
            })

            # Run persona analysis
            from .personas.pipeline_manager import PersonaPipeline
            pipeline = PersonaPipeline()
            result = pipeline.run_persona("analyzer", query)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_completed",
                "persona": "analyzer",
                "success": True
            })

            response = result.text if hasattr(result, 'text') else str(result)
            progress.show_success("Analyzer analysis completed")
            return response

    except Exception as e:
        progress.show_error(f"Analyzer analysis failed: {str(e)}")
        return f"Analyzer analysis error: {str(e)}"

@mcp.tool()
def sp_architect(query: str, persona: str = "architect"):
    """Architect persona: sp_architect analysis"""
    try:
        with memory_span(f"persona_architect_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Running architect analysis for: {query[:50]}...")

            # Collect context first
            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_started",
                "persona": "architect",
                "query": query,
                "context_files": len(context_result.get("files", []))
            })

            # Run persona analysis
            from .personas.pipeline_manager import PersonaPipeline
            pipeline = PersonaPipeline()
            result = pipeline.run_persona("architect", query)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_completed",
                "persona": "architect",
                "success": True
            })

            response = result.text if hasattr(result, 'text') else str(result)
            progress.show_success("Architect analysis completed")
            return response

    except Exception as e:
        progress.show_error(f"Architect analysis failed: {str(e)}")
        return f"Architect analysis error: {str(e)}"

@mcp.tool()
def sp_performance(query: str, persona: str = "performance"):
    """Performance persona: sp_performance analysis"""
    try:
        with memory_span(f"persona_performance_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Running performance analysis for: {query[:50]}...")

            # Collect context first
            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_started",
                "persona": "performance",
                "query": query,
                "context_files": len(context_result.get("files", []))
            })

            # Run persona analysis
            from .personas.pipeline_manager import PersonaPipeline
            pipeline = PersonaPipeline()
            result = pipeline.run_persona("performance", query)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_completed",
                "persona": "performance",
                "success": True
            })

            response = result.text if hasattr(result, 'text') else str(result)
            progress.show_success("Performance analysis completed")
            return response

    except Exception as e:
        progress.show_error(f"Performance analysis failed: {str(e)}")
        return f"Performance analysis error: {str(e)}"

@mcp.tool()
def sp_security(query: str, persona: str = "security"):
    """Security persona: sp_security analysis"""
    try:
        with memory_span(f"persona_security_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Running security analysis for: {query[:50]}...")

            # Collect context first
            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_started",
                "persona": "security",
                "query": query,
                "context_files": len(context_result.get("files", []))
            })

            # Run persona analysis
            from .personas.pipeline_manager import PersonaPipeline
            pipeline = PersonaPipeline()
            result = pipeline.run_persona("security", query)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_completed",
                "persona": "security",
                "success": True
            })

            response = result.text if hasattr(result, 'text') else str(result)
            progress.show_success("Security analysis completed")
            return response

    except Exception as e:
        progress.show_error(f"Security analysis failed: {str(e)}")
        return f"Security analysis error: {str(e)}"

@mcp.tool()
def sp_frontend(query: str, persona: str = "frontend"):
    """Frontend persona: sp_frontend analysis"""
    try:
        with memory_span(f"persona_frontend_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Running frontend analysis for: {query[:50]}...")

            # Collect context first
            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_started",
                "persona": "frontend",
                "query": query,
                "context_files": len(context_result.get("files", []))
            })

            # Run persona analysis
            from .personas.pipeline_manager import PersonaPipeline
            pipeline = PersonaPipeline()
            result = pipeline.run_persona("frontend", query)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_completed",
                "persona": "frontend",
                "success": True
            })

            response = result.text if hasattr(result, 'text') else str(result)
            progress.show_success("Frontend analysis completed")
            return response

    except Exception as e:
        progress.show_error(f"Frontend analysis failed: {str(e)}")
        return f"Frontend analysis error: {str(e)}"

@mcp.tool()
def sp_backend(query: str, persona: str = "backend"):
    """Backend persona: sp_backend analysis"""
    try:
        with memory_span(f"persona_backend_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Running backend analysis for: {query[:50]}...")

            # Collect context first
            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_started",
                "persona": "backend",
                "query": query,
                "context_files": len(context_result.get("files", []))
            })

            # Run persona analysis
            from .personas.pipeline_manager import PersonaPipeline
            pipeline = PersonaPipeline()
            result = pipeline.run_persona("backend", query)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_completed",
                "persona": "backend",
                "success": True
            })

            response = result.text if hasattr(result, 'text') else str(result)
            progress.show_success("Backend analysis completed")
            return response

    except Exception as e:
        progress.show_error(f"Backend analysis failed: {str(e)}")
        return f"Backend analysis error: {str(e)}"

@mcp.tool()
def sp_qa(query: str, persona: str = "qa"):
    """Qa persona: sp_qa analysis"""
    try:
        with memory_span(f"persona_qa_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Running qa analysis for: {query[:50]}...")

            # Collect context first
            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_started",
                "persona": "qa",
                "query": query,
                "context_files": len(context_result.get("files", []))
            })

            # Run persona analysis
            from .personas.pipeline_manager import PersonaPipeline
            pipeline = PersonaPipeline()
            result = pipeline.run_persona("qa", query)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_completed",
                "persona": "qa",
                "success": True
            })

            response = result.text if hasattr(result, 'text') else str(result)
            progress.show_success("Qa analysis completed")
            return response

    except Exception as e:
        progress.show_error(f"Qa analysis failed: {str(e)}")
        return f"Qa analysis error: {str(e)}"

@mcp.tool()
def sp_devops(query: str, persona: str = "devops"):
    """Devops persona: sp_devops analysis"""
    try:
        with memory_span(f"persona_devops_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Running devops analysis for: {query[:50]}...")

            # Collect context first
            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_started",
                "persona": "devops",
                "query": query,
                "context_files": len(context_result.get("files", []))
            })

            # Run persona analysis
            from .personas.pipeline_manager import PersonaPipeline
            pipeline = PersonaPipeline()
            result = pipeline.run_persona("devops", query)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_completed",
                "persona": "devops",
                "success": True
            })

            response = result.text if hasattr(result, 'text') else str(result)
            progress.show_success("Devops analysis completed")
            return response

    except Exception as e:
        progress.show_error(f"Devops analysis failed: {str(e)}")
        return f"Devops analysis error: {str(e)}"


# SDD (Spec-Driven Development) Workflow Tools
@mcp.tool()
def sp_specify(query: str, persona: str = "specify"):
    """SDD Phase 1: Requirements specification and gathering"""
    try:
        from .prompts.workflow_executor import run_prompt_based_workflow
        return run_prompt_based_workflow("specify", query)
    except Exception as e:
        return f"SDD Specify error: {str(e)}"


@mcp.tool()
def sp_plan(query: str, persona: str = "plan"):
    """SDD Phase 2: Implementation planning and technical roadmap"""
    try:
        from .prompts.workflow_executor import run_prompt_based_workflow
        return run_prompt_based_workflow("plan", query)
    except Exception as e:
        return f"SDD Plan error: {str(e)}"


@mcp.tool()
def sp_tasks(query: str, persona: str = "tasks"):
    """SDD Phase 3: Task breakdown and project execution planning"""
    try:
        from .prompts.workflow_executor import run_prompt_based_workflow
        return run_prompt_based_workflow("tasks", query)
    except Exception as e:
        return f"SDD Tasks error: {str(e)}"


@mcp.tool()
def sp_high(query: str, persona: str = "high") -> str:
    """Execute high-level reasoning and strategic problem solving using codex CLI"""
    try:
        import subprocess
        import os

        # Build codex CLI command for high reasoning
        plan_query = f"Plan mode: {query}. Provide a comprehensive strategic plan with numbered steps and implementation guidance."
        cmd = [
            "codex", "exec",
            "--sandbox", "read-only",
            "-c", 'reasoning_effort="high"',
            "-c", 'tools.web_search=true',
            "-c", 'show_raw_agent_reasoning=true',
            "-C", os.getcwd(),
            plan_query
        ]

        # Execute the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            env=os.environ.copy()
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                return output
            else:
                return "Codex CLI executed successfully but returned no output"
        else:
            error_output = result.stderr.strip()
            return f"Codex CLI execution failed (exit code {result.returncode}):\n{error_output}"

    except subprocess.TimeoutExpired:
        return "Codex CLI execution timed out after 5 minutes"
    except FileNotFoundError:
        return "Codex CLI not found. Please ensure codex is installed and in PATH"
    except Exception as e:
        return f"High analysis error: {str(e)}"


@mcp.tool()
def sp_troubleshooting(query: str, persona: str = "troubleshooting"):
    """Troubleshooting: Systematic problem diagnosis, root cause analysis, and resolution strategies"""
    try:
        from .prompts.workflow_executor import run_prompt_based_workflow
        return run_prompt_based_workflow("troubleshooting", query)
    except Exception as e:
        return f"Troubleshooting error: {str(e)}"
