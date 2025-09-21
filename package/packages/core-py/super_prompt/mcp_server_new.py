"""
Super Prompt MCP Server - Clean Version

Core MCP server providing all persona tools and mode management.
All persona functions are dynamically generated from personas/manifest.yaml.
"""

import os
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
        mcp = FastMCP(name="super-prompt")
    except Exception as e:
        mcp, _ = create_fallback_mcp()
else:
    mcp, _ = create_fallback_mcp()

# Mode and persona management
from .mode_store import get_mode, set_mode

# YAML manifest loader
import yaml
from pathlib import Path

def load_persona_manifest():
    """Load persona manifest from YAML file"""
    try:
        manifest_path = Path(__file__).parent.parent.parent.parent / "personas" / "manifest.yaml"

        if not manifest_path.exists():
            print(f"Warning: Could not find persona manifest at {manifest_path}")
            return {}

        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)

        return manifest.get('personas', {})

    except Exception as e:
        print(f"Error loading persona manifest: {e}")
        return {}

# Load persona manifest
PERSONA_MANIFEST = load_persona_manifest()

def get_persona_guidance(persona_name: str, mode: str) -> str:
    """Get persona guidance from manifest for specific mode"""
    try:
        if persona_name not in PERSONA_MANIFEST:
            return f"Standard {persona_name} guidance"

        persona_config = PERSONA_MANIFEST[persona_name]
        model_overrides = persona_config.get('model_overrides', {})

        # Try to get mode-specific guidance first
        if mode in model_overrides:
            mode_config = model_overrides[mode]
            if 'guidance' in mode_config:
                return mode_config['guidance']

        # Fallback to default guidance
        return f"Standard {persona_name} guidance for {mode} mode"

    except Exception as e:
        return f"Error loading guidance: {str(e)}"

def create_persona_mcp_function(persona_name: str):
    """Create a dynamic MCP function for a persona"""
    def persona_function(query: str, persona: str = persona_name) -> str:
        try:
            import os
            from pathlib import Path

            # Get current mode for persona selection
            project_root = os.environ.get('SUPER_PROMPT_PROJECT_ROOT', os.getcwd())
            mode_file = Path(project_root) / '.super-prompt' / 'mode.json'

            current_mode = 'gpt'  # default
            if mode_file.exists():
                try:
                    import json
                    with open(mode_file, 'r', encoding='utf-8') as f:
                        mode_data = json.load(f)
                        current_mode = mode_data.get('llm_mode', 'gpt')
                except:
                    pass

            # Get persona info from manifest
            persona_config = PERSONA_MANIFEST.get(persona_name, {})
            persona_icon = persona_config.get('icon', '🤖')
            persona_desc = persona_config.get('description', f'{persona_name} assistant')

            # Get optimized guidance from manifest
            optimized_guidance = get_persona_guidance(persona_name, current_mode)

            result = f"""{persona_icon} **{persona_name.title()}**

**Query:** {query}
**Mode:** {current_mode.upper()}
**Persona:** {persona_name}

{optimized_guidance}

## 📋 **{persona_name.title()} Workflow**
Following systematic methodology for {persona_name}.

**Status:** Ready for {persona_name} analysis"""

            return result

        except Exception as e:
            return f"❌ {persona_name.title()} failed: {str(e)}"

    # Set function name and docstring dynamically
    persona_function.__name__ = f"sp_{persona_name}"
    persona_function.__doc__ = f"{persona_name.title()} persona: {PERSONA_MANIFEST.get(persona_name, {}).get('description', f'{persona_name} assistant')}"

    return persona_function



# Core MCP System Tools

# System Management Tools
@mcp.tool()
def sp_health() -> str:
    """Check if Super Prompt MCP server is healthy"""
    return "Super Prompt MCP server is running"

@mcp.tool()
def sp_version_mcp() -> str:
    """Get the current version of Super Prompt"""
    try:
        import json
        package_path = Path(__file__).parent.parent.parent.parent / "package.json"
        if package_path.exists():
            with open(package_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                return f"Super Prompt v{package_data.get('version', 'unknown')}"
        return "Super Prompt v0.1.0"
    except Exception:
        return "Super Prompt v0.1.0"

@mcp.tool()
def sp_list_commands_mcp() -> str:
    """List all available Super Prompt commands"""
    try:
        commands = []
        for persona_name in PERSONA_MANIFEST.keys():
            commands.append(f"sp_{persona_name}")

        commands.extend([
            "sp_health", "sp_version_mcp", "sp_list_commands_mcp",
            "sp_list_personas_mcp", "sp_init_mcp", "sp_refresh_mcp",
            "sp_mode_get_mcp", "sp_mode_set_mcp", "sp_grok_mode_on_mcp",
            "sp_gpt_mode_on_mcp", "sp_grok_mode_off_mcp", "sp_gpt_mode_off_mcp"
        ])

        return "Available MCP tools:\n" + "\n".join(f"- {cmd}" for cmd in sorted(commands))
    except Exception as e:
        return f"Error listing commands: {str(e)}"

@mcp.tool()
def sp_list_personas_mcp() -> str:
    """List available Super Prompt personas"""
    try:
        personas = []
        for name, config in PERSONA_MANIFEST.items():
            icon = config.get('icon', '🤖')
            desc = config.get('description', f'{name} assistant')
            personas.append(f"{icon} {name}: {desc}")

        return "Available personas:\n" + "\n".join(personas)
    except Exception as e:
        return f"Error listing personas: {str(e)}"

@mcp.tool()
def sp_init_mcp(force: bool = False) -> str:
    """Initialize Super Prompt for current project"""
    try:
        set_mode("gpt")  # Default to GPT mode
        return f"✅ Super Prompt initialized (mode: gpt)"
    except Exception as e:
        return f"❌ Initialization failed: {str(e)}"

@mcp.tool()
def sp_refresh_mcp() -> str:
    """Refresh Super Prompt assets in current project"""
    try:
        # Reload manifest
        global PERSONA_MANIFEST
        PERSONA_MANIFEST = load_persona_manifest()

        # Re-register all persona functions
        register_persona_functions()

        return f"✅ Super Prompt refreshed ({len(PERSONA_MANIFEST)} personas loaded)"
    except Exception as e:
        return f"❌ Refresh failed: {str(e)}"

@mcp.tool()
def sp_mode_get_mcp() -> str:
    """Get current LLM mode (gpt|grok)"""
    try:
        current_mode = get_mode()
        return f"Current LLM mode: {current_mode}"
    except Exception as e:
        return f"Error getting mode: {str(e)}"

@mcp.tool()
def sp_mode_set_mcp(mode: str) -> str:
    """Set LLM mode to 'gpt' or 'grok'"""
    try:
        if mode not in ['gpt', 'grok']:
            return f"❌ Invalid mode: {mode}. Use 'gpt' or 'grok'"

        set_mode(mode)
        return f"✅ LLM mode set to: {mode}"
    except Exception as e:
        return f"❌ Error setting mode: {str(e)}"

@mcp.tool()
def sp_grok_mode_on_mcp() -> str:
    """Switch LLM mode to grok"""
    try:
        set_mode("grok")
        return "✅ Grok mode enabled"
    except Exception as e:
        return f"❌ Error enabling Grok mode: {str(e)}"

@mcp.tool()
def sp_gpt_mode_on_mcp() -> str:
    """Switch LLM mode to gpt"""
    try:
        set_mode("gpt")
        return "✅ GPT mode enabled"
    except Exception as e:
        return f"❌ Error enabling GPT mode: {str(e)}"

@mcp.tool()
def sp_grok_mode_off_mcp() -> str:
    """Turn off Grok mode"""
    try:
        set_mode("gpt")  # Default to GPT when turning off Grok
        return "✅ Grok mode disabled (switched to GPT)"
    except Exception as e:
        return f"❌ Error disabling Grok mode: {str(e)}"

@mcp.tool()
def sp_gpt_mode_off_mcp() -> str:
    """Turn off GPT mode"""
    try:
        set_mode("grok")  # Default to Grok when turning off GPT
        return "✅ GPT mode disabled (switched to Grok)"
    except Exception as e:
        return f"❌ Error disabling GPT mode: {str(e)}"


# Dynamic Persona Registration
def register_persona_functions():
    """Register persona MCP functions dynamically from manifest"""
    persona_names = list(PERSONA_MANIFEST.keys())

    registered_count = 0
    for persona_name in persona_names:
        try:
            # Create dynamic function
            persona_func = create_persona_mcp_function(persona_name)

            # Register as MCP tool
            decorated_func = mcp.tool()(persona_func)

            # Add to global namespace
            globals()[f"sp_{persona_name}"] = decorated_func

            registered_count += 1

        except Exception as e:
            print(f"⚠️  Failed to register {persona_name} persona: {e}")

    print(f"📊 Total personas registered: {registered_count}")

# Add missing MCP functions that commands expect
@mcp.tool()
def sp_seq_ultra(query: str) -> str:
    """Sequential Ultra - Ultra-deep sequential reasoning for complex problems"""
    try:
        current_mode = get_mode()
        persona_config = PERSONA_MANIFEST.get('seq-ultra', {})
        icon = persona_config.get('icon', '🧠')
        desc = persona_config.get('description', 'Ultra-deep sequential reasoning')

        guidance = get_persona_guidance('seq-ultra', current_mode)

        result = f"""{icon} **Sequential Ultra**

**Query:** {query}
**Mode:** {current_mode.upper()}

{guidance}

## 📋 **Sequential Ultra Workflow**
Ultra-deep sequential reasoning methodology.

**Status:** Ready for ultra-deep analysis"""
        return result
    except Exception as e:
        return f"❌ Sequential Ultra failed: {str(e)}"

@mcp.tool()
def sp_plan(query: str) -> str:
    """Plan - Create Implementation Plan"""
    try:
        current_mode = get_mode()
        persona_config = PERSONA_MANIFEST.get('plan', {})
        icon = persona_config.get('icon', '📋')
        desc = persona_config.get('description', 'Implementation planning')

        guidance = get_persona_guidance('plan', current_mode)

        result = f"""{icon} **Plan**

**Query:** {query}
**Mode:** {current_mode.upper()}

{guidance}

## 📋 **Plan Workflow**
Implementation planning methodology.

**Status:** Ready for planning"""
        return result
    except Exception as e:
        return f"❌ Plan failed: {str(e)}"

@mcp.tool()
def grok_mode_off() -> str:
    """Turn off Grok mode"""
    try:
        set_mode("gpt")
        return "✅ Grok mode disabled (switched to GPT)"
    except Exception as e:
        return f"❌ Error disabling Grok mode: {str(e)}"

@mcp.tool()
def gpt_mode_off() -> str:
    """Turn off GPT mode"""
    try:
        set_mode("grok")
        return "✅ GPT mode disabled (switched to Grok)"
    except Exception as e:
        return f"❌ Error disabling GPT mode: {str(e)}"

@mcp.tool()
def grok_mode_on() -> str:
    """Switch LLM mode to grok"""
    try:
        set_mode("grok")
        return "✅ Grok mode enabled"
    except Exception as e:
        return f"❌ Error enabling Grok mode: {str(e)}"

@mcp.tool()
def gpt_mode_on() -> str:
    """Switch LLM mode to gpt"""
    try:
        set_mode("gpt")
        return "✅ GPT mode enabled"
    except Exception as e:
        return f"❌ Error enabling GPT mode: {str(e)}"

@mcp.tool()
def sp_specify(query: str) -> str:
    """Specify - Create Feature Specification"""
    try:
        current_mode = get_mode()
        persona_config = PERSONA_MANIFEST.get('specify', {})
        icon = persona_config.get('icon', '📋')
        desc = persona_config.get('description', 'Feature specification')

        guidance = get_persona_guidance('specify', current_mode)

        result = f"""{icon} **Specify**

**Query:** {query}
**Mode:** {current_mode.upper()}

{guidance}

## 📋 **Specify Workflow**
Feature specification methodology.

**Status:** Ready for specification"""
        return result
    except Exception as e:
        return f"❌ Specify failed: {str(e)}"

@mcp.tool()
def sp_tasks(query: str) -> str:
    """Tasks - Create Task Breakdown"""
    try:
        current_mode = get_mode()
        persona_config = PERSONA_MANIFEST.get('tasks', {})
        icon = persona_config.get('icon', '📋')
        desc = persona_config.get('description', 'Task breakdown')

        guidance = get_persona_guidance('tasks', current_mode)

        result = f"""{icon} **Tasks**

**Query:** {query}
**Mode:** {current_mode.upper()}

{guidance}

## 📋 **Tasks Workflow**
Task breakdown methodology.

**Status:** Ready for task breakdown"""
        return result
    except Exception as e:
        return f"❌ Tasks failed: {str(e)}"

@mcp.tool()
def sp_implement(query: str) -> str:
    """Implement - Execute Implementation"""
    try:
        current_mode = get_mode()
        persona_config = PERSONA_MANIFEST.get('implement', {})
        icon = persona_config.get('icon', '📋')
        desc = persona_config.get('description', 'Implementation execution')

        guidance = get_persona_guidance('implement', current_mode)

        result = f"""{icon} **Implement**

**Query:** {query}
**Mode:** {current_mode.upper()}

{guidance}

## 📋 **Implement Workflow**
Implementation execution methodology.

**Status:** Ready for implementation"""
        return result
    except Exception as e:
        return f"❌ Implement failed: {str(e)}"

@mcp.tool()
def sp_doc_master(query: str) -> str:
    """Doc Master - Documentation Architecture & Writing Specialist"""
    try:
        current_mode = get_mode()
        persona_config = PERSONA_MANIFEST.get('doc-master', {})
        icon = persona_config.get('icon', '📚')
        desc = persona_config.get('description', 'Documentation architecture and writing')

        guidance = get_persona_guidance('doc-master', current_mode)

        result = f"""{icon} **Doc Master**

**Query:** {query}
**Mode:** {current_mode.upper()}

{guidance}

## 📋 **Doc Master Workflow**
Documentation architecture and writing methodology.

**Status:** Ready for documentation mastery"""
        return result
    except Exception as e:
        return f"❌ Doc Master failed: {str(e)}"

@mcp.tool()
def sp_service_planner(query: str) -> str:
    """Service Planner - Service planning expert"""
    try:
        current_mode = get_mode()
        persona_config = PERSONA_MANIFEST.get('service-planner', {})
        icon = persona_config.get('icon', '🧭')
        desc = persona_config.get('description', 'Service planning expert')

        guidance = get_persona_guidance('service-planner', current_mode)

        result = f"""{icon} **Service Planner**

**Query:** {query}
**Mode:** {current_mode.upper()}

{guidance}

## 📋 **Service Planner Workflow**
Service planning methodology.

**Status:** Ready for service planning"""
        return result
    except Exception as e:
        return f"❌ Service Planner failed: {str(e)}"

@mcp.tool()
def sp_docs_refector(query: str) -> str:
    """Docs Refector - Documentation Audit & Refactoring Specialist"""
    try:
        current_mode = get_mode()
        persona_config = PERSONA_MANIFEST.get('docs-refector', {})
        icon = persona_config.get('icon', '🧹')
        desc = persona_config.get('description', 'Documentation audit and refactoring')

        guidance = get_persona_guidance('docs-refector', current_mode)

        result = f"""{icon} **Docs Refector**

**Query:** {query}
**Mode:** {current_mode.upper()}

{guidance}

## 📋 **Docs Refector Workflow**
Documentation refactoring methodology.

**Status:** Ready for documentation refactoring"""
        return result
    except Exception as e:
        return f"❌ Docs Refector failed: {str(e)}"

@mcp.tool()
def sp_db_expert(query: str) -> str:
    """DB Expert - Database Design & Optimization Specialist"""
    try:
        current_mode = get_mode()
        persona_config = PERSONA_MANIFEST.get('db-expert', {})
        icon = persona_config.get('icon', '🗄️')
        desc = persona_config.get('description', 'Database design and optimization')

        guidance = get_persona_guidance('db-expert', current_mode)

        result = f"""{icon} **DB Expert**

**Query:** {query}
**Mode:** {current_mode.upper()}

{guidance}

## 📋 **DB Expert Workflow**
Database optimization methodology.

**Status:** Ready for database analysis"""
        return result
    except Exception as e:
        return f"❌ DB Expert failed: {str(e)}"

# Mode control functions for command compatibility
@mcp.tool()
def grok_mode_on() -> str:
    """Switch LLM mode to grok"""
    try:
        set_mode("grok")
        return "✅ Grok mode enabled"
    except Exception as e:
        return f"❌ Error enabling Grok mode: {str(e)}"

@mcp.tool()
def grok_mode_off() -> str:
    """Turn off Grok mode"""
    try:
        set_mode("gpt")
        return "✅ Grok mode disabled (switched to GPT)"
    except Exception as e:
        return f"❌ Error disabling Grok mode: {str(e)}"

@mcp.tool()
def gpt_mode_on() -> str:
    """Switch LLM mode to gpt"""
    try:
        set_mode("gpt")
        return "✅ GPT mode enabled"
    except Exception as e:
        return f"❌ Error enabling GPT mode: {str(e)}"

@mcp.tool()
def gpt_mode_off() -> str:
    """Turn off GPT mode"""
    try:
        set_mode("grok")
        return "✅ GPT mode disabled (switched to Grok)"
    except Exception as e:
        return f"❌ Error disabling GPT mode: {str(e)}"

# Register all persona functions from manifest
register_persona_functions()
