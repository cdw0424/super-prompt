"""
Super Prompt MCP Server - Modularized Version

This is the new modularized version of the MCP server.
The original mcp_server.py has been broken down into logical modules for better maintainability.
"""

import os
import sys
import builtins
from pathlib import Path
from typing import Optional

# MCP SDK initialization
from .mcp.version_detection import import_mcp_components, create_fallback_mcp

# Suppress MCP library warnings and all logs
import logging
import sys

# Disable all logging for MCP server
logging.getLogger('mcp').setLevel(logging.CRITICAL)
logging.getLogger('mcp.server').setLevel(logging.CRITICAL)
logging.getLogger('mcp.server.fastmcp').setLevel(logging.CRITICAL)

# Suppress all warnings
logging.getLogger().setLevel(logging.CRITICAL)

# CLI 환경에서는 SilentProgress 완전 비활성화
import sys
import os

# 환경 확인 - CLI 모드인지 확인
is_cli_mode = os.environ.get("SUPER_PROMPT_CLI_MODE") == "1"
debug_mode = os.environ.get("SUPER_PROMPT_DEBUG") == "1"

# CLI 모드에서는 SilentProgress를 완전히 제거
if is_cli_mode:
    # CLI 모드: SilentProgress가 로드되지 않도록 처리
    try:
        from .core.memory_manager import progress
        # SilentProgress가 이미 적용되어 있다면 제거
        if hasattr(progress, '_mcp_silent'):
            from .core.memory_manager import ProgressIndicator
            # 원래 메서드로 복원
            progress.show_progress = ProgressIndicator.show_progress.__get__(progress, ProgressIndicator)
            progress.show_success = ProgressIndicator.show_success.__get__(progress, ProgressIndicator)
            progress.show_error = ProgressIndicator.show_error.__get__(progress, ProgressIndicator)
            delattr(progress, '_mcp_silent')

        # 디버깅 모드 확인
        if debug_mode:
            # 디버깅 모드: 모든 로그를 stderr로 출력
            def debug_show_progress(message, **kwargs):
                print(f"DEBUG: {message}", file=sys.stderr, flush=True)
            def debug_show_success(message):
                print(f"SUCCESS: {message}", file=sys.stderr, flush=True)
            def debug_show_error(message):
                print(f"ERROR: {message}", file=sys.stderr, flush=True)

            progress.show_progress = debug_show_progress
            progress.show_success = debug_show_success
            progress.show_error = debug_show_error

    except Exception as e:
        # CLI 모드에서 import 실패 시 조용히 처리
        pass
else:
    # MCP 서버 모드: SilentProgress 적용 (기존 로직)
    # MCP 서버에서만 SilentProgress를 사용하도록 별도 처리
    pass

# SilentProgress 클래스 완전 제거 - 모든 로그 허용
# 모든 환경에서 SilentProgress를 사용하지 않음

# SilentProgress 클래스를 완전히 제거
# 모든 환경에서 SilentProgress를 사용하지 않음

# SilentProgress 클래스 제거
# 모든 환경에서 SilentProgress를 사용하지 않음

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

# Ensure mcp is always defined for import
if 'mcp' not in globals() or mcp is None:
    mcp, _ = create_fallback_mcp()

# Import and register tools
from .personas.tools.system_tools import (
    init, refresh, sp_version, sp_list_commands, list_personas,
    mode_get, mode_set, grok_mode_on, gpt_mode_on, grok_mode_off, gpt_mode_off
)

# Import persona tools for MCP registration
from .personas import tools as persona_tools

from .tools.registry import REGISTERED_TOOL_ANNOTATIONS
from .sdd.architecture import render_sdd_brief, list_sdd_sections

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

# Track registered tools to prevent duplicates
_REGISTERED_TOOLS: set = set()
# Store tool functions for stdio server access
_TOOL_REGISTRY: dict = {}


def _register_tool_once(tool_name: str):
    """Helper to register MCP tool only once to prevent duplicates"""
    def decorator(func):
        if tool_name not in _REGISTERED_TOOLS:
            _REGISTERED_TOOLS.add(tool_name)
            # Store function in registry for stdio server access
            _TOOL_REGISTRY[tool_name] = func
            try:
                return mcp.tool()(func)
            except Exception as e:
                # If tool already exists, just return original function
                if "already exists" in str(e).lower():
                    return func
                else:
                    raise
        else:
            # Return original function without MCP decoration
            return func
    return decorator


def _resolve_persona_label(persona_key: str) -> str:
    """Resolve a human-friendly label for logging."""
    try:
        from .personas.pipeline_manager import PIPELINE_CONFIGS
        config = PIPELINE_CONFIGS.get(persona_key)
        if config and getattr(config, "label", None):
            return config.label
    except Exception:
        pass
    text = persona_key.replace('-', ' ').replace('_', ' ').strip()
    return text.title() if text else "Persona"


def _register_persona_tool(tool_name: str, persona_key: str):
    """Factory to register MCP persona tools with consistent behavior."""

    label = _resolve_persona_label(persona_key)

    @_register_tool_once(tool_name)
    def _persona_tool(query: str, persona: str = persona_key):
        try:
            span_name = f"persona_{persona_key}_{hash(query) % 10000}"
            with memory_span(span_name) as span_id:
                progress.show_progress(f"Running {label} analysis for: {query[:50]}...")

                collector = ContextCollector()
                context_result = collector.collect_context(query, max_tokens=8000)

                span_manager.write_event(span_id, {
                    "type": "persona_analysis_started",
                    "persona": persona_key,
                    "query": query,
                    "context_files": len(context_result.get("files", []))
                })

                from .personas.pipeline_manager import PersonaPipeline
                pipeline = PersonaPipeline()
                result = pipeline.run_persona(persona_key, query)

                span_manager.write_event(span_id, {
                    "type": "persona_analysis_completed",
                    "persona": persona_key,
                    "success": True
                })

                response = result.text if hasattr(result, 'text') else str(result)
                progress.show_success(f"{label} analysis completed")
                return response

        except Exception as exc:
            progress.show_error(f"{label} analysis failed: {str(exc)}")
            return f"{label} analysis error: {str(exc)}"

    _persona_tool.__name__ = tool_name.replace('.', '_')
    _persona_tool.__doc__ = f"{label} persona: {tool_name} analysis"
    return _persona_tool


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

_TOOL_REGISTRY["sp_context_collect"] = sp_context_collect

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

_TOOL_REGISTRY["sp_context_clear_cache"] = sp_context_clear_cache

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

_TOOL_REGISTRY["sp_memory_stats"] = sp_memory_stats

# Minimal built-in tools
@mcp.tool()
def sp_health() -> str:
    """Check if Super Prompt MCP server is healthy"""
    return "Super Prompt MCP server is running"

# Register in tool registry for stdio access
_TOOL_REGISTRY["sp_health"] = sp_health


# Register MCP tools with decorators
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
    return result.text if hasattr(result, 'text') else str(result)

_TOOL_REGISTRY["sp_list_personas"] = sp_list_personas_mcp


# Import TextContent for MCP responses
from .mcp.version_detection import import_mcp_components

try:
    _, TextContent, _ = import_mcp_components()
except ImportError:
    from .mcp.version_detection import create_fallback_mcp
    _, TextContent = create_fallback_mcp()


@mcp.tool(name="sp_init")
def sp_init_mcp(force: bool = False):
    """Initialize Super Prompt for current project"""
    result = init(force=force)
    return result.text if hasattr(result, 'text') else str(result)

_TOOL_REGISTRY["sp_init"] = sp_init_mcp


@mcp.tool(name="sp_refresh")
def sp_refresh_mcp():
    """Refresh Super Prompt assets in current project"""
    result = refresh()
    return result.text if hasattr(result, 'text') else str(result)

_TOOL_REGISTRY["sp_refresh"] = sp_refresh_mcp


@mcp.tool(name="sp_mode_get")
def sp_mode_get_mcp():
    """Get current LLM mode (gpt|grok)"""
    result = mode_get()
    return result.text if hasattr(result, 'text') else str(result)

_TOOL_REGISTRY["sp_mode_get"] = sp_mode_get_mcp


@mcp.tool(name="sp_mode_set")
def sp_mode_set_mcp(mode: str):
    """Set LLM mode to 'gpt' or 'grok'"""
    result = mode_set(mode)
    return result.text if hasattr(result, 'text') else str(result)

_TOOL_REGISTRY["sp_mode_set"] = sp_mode_set_mcp


@mcp.tool(name="sp_grok_mode_on")
def sp_grok_mode_on_mcp():
    """Switch LLM mode to grok"""
    result = grok_mode_on()
    return result.text if hasattr(result, 'text') else str(result)

_TOOL_REGISTRY["sp_grok_mode_on"] = sp_grok_mode_on_mcp


@mcp.tool(name="sp_gpt_mode_on")
def sp_gpt_mode_on_mcp():
    """Switch LLM mode to gpt"""
    result = gpt_mode_on()
    return result.text if hasattr(result, 'text') else str(result)

_TOOL_REGISTRY["sp_gpt_mode_on"] = sp_gpt_mode_on_mcp


@mcp.tool(name="sp_grok_mode_off")
def sp_grok_mode_off_mcp():
    """Turn off Grok mode"""
    result = grok_mode_off()
    return result.text if hasattr(result, 'text') else str(result)

_TOOL_REGISTRY["sp_grok_mode_off"] = sp_grok_mode_off_mcp


@mcp.tool(name="sp_gpt_mode_off")
def sp_gpt_mode_off_mcp():
    """Turn off GPT mode"""
    result = gpt_mode_off()
    return result.text if hasattr(result, 'text') else str(result)

_TOOL_REGISTRY["sp_gpt_mode_off"] = sp_gpt_mode_off_mcp


# Persona-based analysis tools with Context Management Protocol
@_register_tool_once("sp_high")
def sp_high(query: str, persona: str = "high"):
    """High persona: sp_high analysis (defaults to prompt workflow unless USE_PIPELINE=true)."""
    try:
        use_pipeline = os.getenv("USE_PIPELINE", "false").lower() == "true"
        if not use_pipeline:
            # Prompt-only fast path (no cross-persona behavior)
            try:
                from .prompts.workflow_executor import run_prompt_based_workflow
                return run_prompt_based_workflow("high", query)
            except Exception as exc:
                # Fallback to pipeline if prompt path fails unexpectedly
                use_pipeline = True

        with memory_span(f"persona_high_{hash(query) % 10000}") as span_id:
            progress.show_progress(f"Running high analysis for: {query[:50]}...")

            collector = ContextCollector()
            context_result = collector.collect_context(query, max_tokens=8000)

            span_manager.write_event(span_id, {
                "type": "persona_analysis_started",
                "persona": "high",
                "query": query,
                "context_files": len(context_result.get("files", []))
            })

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

_TOOL_REGISTRY["sp_grok"] = sp_grok

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

_TOOL_REGISTRY["sp_gpt"] = sp_gpt

# Additional persona tools registered via helper
sp_analyzer = _register_persona_tool("sp_analyzer", "analyzer")
sp_architect = _register_persona_tool("sp_architect", "architect")
sp_frontend = _register_persona_tool("sp_frontend", "frontend")
sp_backend = _register_persona_tool("sp_backend", "backend")
sp_dev = _register_persona_tool("sp_dev", "dev")
sp_devops = _register_persona_tool("sp_devops", "devops")
sp_performance = _register_persona_tool("sp_performance", "performance")
sp_qa = _register_persona_tool("sp_qa", "qa")
sp_security = _register_persona_tool("sp_security", "security")
sp_refactorer = _register_persona_tool("sp_refactorer", "refactorer")
sp_optimize = _register_persona_tool("sp_optimize", "optimize")
sp_doc_master = _register_persona_tool("sp_doc_master", "doc_master")
sp_docs_refector = _register_persona_tool("sp_docs_refector", "docs_refector")
sp_db_expert = _register_persona_tool("sp_db_expert", "db_expert")
sp_review = _register_persona_tool("sp_review", "review")
sp_mentor = _register_persona_tool("sp_mentor", "mentor")
sp_scribe = _register_persona_tool("sp_scribe", "scribe")
sp_debate = _register_persona_tool("sp_debate", "debate")
sp_service_planner = _register_persona_tool("sp_service_planner", "service_planner")
sp_ultracompressed = _register_persona_tool("sp_ultracompressed", "ultracompressed")
sp_seq = _register_persona_tool("sp_seq", "seq")
sp_seq_ultra = _register_persona_tool("sp_seq_ultra", "seq_ultra")
sp_implement = _register_persona_tool("sp_implement", "implement")

# SDD (Spec-Driven Development) Workflow Tools
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


# Export the mcp instance and tool registry for use by mcp_stdio.py
__all__ = ['mcp', '_TOOL_REGISTRY']
