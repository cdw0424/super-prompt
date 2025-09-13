#!/usr/bin/env python3
"""
Universal Codex CLI Integration Processor
Common workflow for all super-prompt commands requiring deep reasoning
"""

import os
import sys
import re
import json
import shlex
import shutil
import subprocess
import datetime
from typing import Dict, List, Optional, Tuple, Any

# Ensure PATH includes common CLI locations
_DEFAULT_PATHS = [
    "/opt/homebrew/bin",
    "/usr/local/bin", 
    "/usr/bin",
    "/bin",
]
os.environ["PATH"] = ":".join(_DEFAULT_PATHS + [os.environ.get("PATH", "")])

def log(msg: str):
    print(f"-------- {msg}")

def run_command(cmd: List[str], timeout: int = 120) -> Tuple[bool, str]:
    """Execute command and return success status and output"""
    try:
        if os.environ.get('SP_DEBUG'):
            print(f"DEBUG exec: {' '.join(shlex.quote(c) for c in cmd)}")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        
        if os.environ.get('SP_DEBUG'):
            print(f"DEBUG returncode: {result.returncode}")
            print(f"DEBUG stdout: {result.stdout[:200]}...")
        
        return result.returncode == 0, (result.stdout or "").strip()
    
    except subprocess.TimeoutExpired:
        log("Command timed out")
        return False, "Command execution timed out"
    except Exception as e:
        log(f"Command execution failed: {e}")
        return False, f"Error: {e}"

def get_project_context() -> Dict:
    """Gather comprehensive project context"""
    context = {
        "cwd": os.getcwd(),
        "frameworks": [],
        "key_files": [],
        "architecture_signals": [],
        "project_type": "general",
        "complexity_indicators": []
    }
    
    # Detect frameworks and project type
    if os.path.exists("package.json"):
        try:
            with open("package.json", "r") as f:
                pkg = json.load(f)
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                
                if "next" in deps: 
                    context["frameworks"].append("Next.js")
                    context["project_type"] = "frontend"
                if "react" in deps: 
                    context["frameworks"].append("React")
                    context["project_type"] = "frontend"
                if "vue" in deps: 
                    context["frameworks"].append("Vue")
                    context["project_type"] = "frontend"
                if "@angular/core" in deps: 
                    context["frameworks"].append("Angular")
                    context["project_type"] = "frontend"
                if "express" in deps: 
                    context["frameworks"].append("Express")
                    context["project_type"] = "backend"
                if "fastify" in deps:
                    context["frameworks"].append("Fastify")
                    context["project_type"] = "backend"
        except:
            pass
    
    # Check Python project
    if os.path.exists("requirements.txt") or os.path.exists("pyproject.toml"):
        context["project_type"] = "python"
        if os.path.exists("requirements.txt"):
            try:
                with open("requirements.txt", "r") as f:
                    content = f.read()
                    if "django" in content: context["frameworks"].append("Django")
                    if "fastapi" in content: context["frameworks"].append("FastAPI")
                    if "flask" in content: context["frameworks"].append("Flask")
            except:
                pass
    
    # Check for architecture files and complexity indicators
    arch_files = [
        "README.md", "ARCHITECTURE.md", "docker-compose.yml", "Dockerfile",
        ".github/workflows/*.yml", "terraform/*.tf", "k8s/*.yaml"
    ]
    
    for pattern in arch_files:
        if "*" in pattern:
            import glob
            matches = glob.glob(pattern)
            context["key_files"].extend(matches)
            if matches:
                context["complexity_indicators"].append(pattern.split('*')[0])
        elif os.path.exists(pattern):
            context["key_files"].append(pattern)
    
    # Detect project complexity
    if len(context["frameworks"]) > 1:
        context["complexity_indicators"].append("multi-framework")
    if "docker" in " ".join(context["key_files"]).lower():
        context["complexity_indicators"].append("containerized")
    if any("workflow" in f for f in context["key_files"]):
        context["complexity_indicators"].append("ci-cd")
    
    return context

class PersonaConfig:
    """Configuration for different persona types"""
    
    PERSONA_CONFIGS = {
        "architect": {
            "role": "Senior Software Architect and System Designer",
            "specialization": "system architecture, design patterns, technical strategy",
            "reasoning_effort": "high",
            "output_structure": [
                "ARCHITECTURE ASSESSMENT",
                "DESIGN RECOMMENDATIONS", 
                "IMPLEMENTATION STRATEGY",
                "RISK ANALYSIS",
                "TECHNICAL ROADMAP"
            ],
            "focus_areas": ["scalability", "maintainability", "system design", "technical debt"],
            "complexity_threshold": 0.3
        },
        
        "analyzer": {
            "role": "Senior Systems Analyst and Troubleshooting Expert",
            "specialization": "root cause analysis, performance investigation, system diagnostics",
            "reasoning_effort": "high",
            "output_structure": [
                "PROBLEM ANALYSIS",
                "ROOT CAUSE INVESTIGATION",
                "EVIDENCE REVIEW",
                "SOLUTION OPTIONS",
                "IMPLEMENTATION PLAN"
            ],
            "focus_areas": ["debugging", "performance", "system analysis", "troubleshooting"],
            "complexity_threshold": 0.4
        },
        
        "frontend": {
            "role": "Senior Frontend Engineer and UX Specialist",
            "specialization": "user experience, frontend architecture, modern web technologies",
            "reasoning_effort": "medium",
            "output_structure": [
                "UX ASSESSMENT",
                "TECHNICAL APPROACH",
                "IMPLEMENTATION GUIDE",
                "ACCESSIBILITY CONSIDERATIONS",
                "PERFORMANCE OPTIMIZATION"
            ],
            "focus_areas": ["user experience", "frontend performance", "accessibility", "responsive design"],
            "complexity_threshold": 0.3
        },
        
        "backend": {
            "role": "Senior Backend Engineer and Infrastructure Specialist",
            "specialization": "server architecture, API design, data systems, scalability",
            "reasoning_effort": "medium",
            "output_structure": [
                "SYSTEM ANALYSIS",
                "ARCHITECTURE RECOMMENDATIONS",
                "API DESIGN",
                "DATA STRATEGY",
                "SCALABILITY PLAN"
            ],
            "focus_areas": ["scalability", "performance", "security", "data architecture"],
            "complexity_threshold": 0.3
        },
        
        "seq": {
            "role": "Strategic Problem Solver with Sequential Reasoning",
            "specialization": "structured thinking, step-by-step analysis, logical problem solving",
            "reasoning_effort": "high",
            "output_structure": [
                "PROBLEM DECOMPOSITION",
                "SEQUENTIAL ANALYSIS (5 STEPS)",
                "LOGICAL REASONING CHAIN", 
                "SOLUTION SYNTHESIS",
                "VALIDATION PLAN"
            ],
            "focus_areas": ["logical reasoning", "problem solving", "systematic approach"],
            "complexity_threshold": 0.2
        },
        
        "seq-ultra": {
            "role": "Advanced Strategic Analyst with Deep Sequential Reasoning",
            "specialization": "comprehensive analysis, multi-dimensional thinking, complex system reasoning",
            "reasoning_effort": "high",
            "output_structure": [
                "COMPREHENSIVE SCOPE ANALYSIS",
                "DEEP SEQUENTIAL REASONING (10 STEPS)",
                "MULTI-PERSPECTIVE EVALUATION",
                "STRATEGIC SYNTHESIS",
                "IMPLEMENTATION ROADMAP"
            ],
            "focus_areas": ["complex analysis", "strategic thinking", "comprehensive reasoning"],
            "complexity_threshold": 0.1
        }
    }
    
    @classmethod
    def get_config(cls, persona: str) -> Dict:
        return cls.PERSONA_CONFIGS.get(persona, cls.PERSONA_CONFIGS["seq"])

def analyze_complexity(user_input: str, persona: str) -> Dict:
    """Analyze input complexity and determine if Codex consultation is needed"""
    
    # Keywords indicating complexity
    complexity_keywords = [
        "architecture", "design", "strategy", "complex", "system", "large-scale",
        "enterprise", "scalability", "performance", "optimization", "refactor",
        "migration", "integration", "microservice", "distributed", "async"
    ]
    
    reasoning_keywords = [
        "how", "why", "what", "which", "compare", "evaluate", "analyze", "decide",
        "choose", "recommend", "best", "approach", "strategy", "solution"
    ]
    
    technical_keywords = [
        "algorithm", "pattern", "framework", "library", "database", "api", 
        "security", "testing", "deployment", "monitoring", "infrastructure"
    ]
    
    text_lower = user_input.lower()
    
    complexity_score = sum(1 for kw in complexity_keywords if kw in text_lower) * 0.3
    reasoning_score = sum(1 for kw in reasoning_keywords if kw in text_lower) * 0.2  
    technical_score = sum(1 for kw in technical_keywords if kw in text_lower) * 0.1
    
    # Length and structure complexity
    length_score = min(len(user_input.split()) / 20, 1.0) * 0.2
    question_marks = text_lower.count('?') * 0.1
    
    total_score = complexity_score + reasoning_score + technical_score + length_score + question_marks
    
    persona_config = PersonaConfig.get_config(persona)
    threshold = persona_config["complexity_threshold"]
    
    analysis = {
        "complexity_score": total_score,
        "needs_codex": total_score >= threshold,
        "reasoning_type": "analytical" if reasoning_score > 0.5 else "technical",
        "focus_areas": [],
        "confidence": min(total_score * 2, 1.0)
    }
    
    # Identify focus areas
    if any(word in text_lower for word in ["performance", "speed", "optimize", "slow"]):
        analysis["focus_areas"].append("performance")
    if any(word in text_lower for word in ["security", "auth", "permission", "vulnerability"]):
        analysis["focus_areas"].append("security")
    if any(word in text_lower for word in ["architecture", "design", "structure", "pattern"]):
        analysis["focus_areas"].append("architecture")
    if any(word in text_lower for word in ["user", "ux", "ui", "experience", "interface"]):
        analysis["focus_areas"].append("user_experience")
    
    return analysis

def build_codex_prompt(user_input: str, persona: str, context: Dict, analysis: Dict) -> str:
    """Build persona-specific prompt for Codex CLI"""
    
    config = PersonaConfig.get_config(persona)
    
    prompt_parts = []
    
    # Role and expertise
    prompt_parts.append(f"**ROLE**: {config['role']}")
    prompt_parts.append(f"**EXPERTISE**: {config['specialization']}")
    
    # Project context
    prompt_parts.append("**PROJECT CONTEXT**:")
    prompt_parts.append(f"- Type: {context['project_type']}")
    if context["frameworks"]:
        prompt_parts.append(f"- Frameworks: {', '.join(context['frameworks'])}")
    if context["complexity_indicators"]:
        prompt_parts.append(f"- Complexity: {', '.join(context['complexity_indicators'])}")
    prompt_parts.append(f"- Working Directory: {os.path.basename(context['cwd'])}")
    
    # Analysis context
    if analysis["focus_areas"]:
        prompt_parts.append(f"**FOCUS AREAS**: {', '.join(analysis['focus_areas']).replace('_', ' ').title()}")
    
    # Output structure
    prompt_parts.append("**REQUIRED OUTPUT STRUCTURE**:")
    for i, section in enumerate(config["output_structure"], 1):
        prompt_parts.append(f"{i}. **{section}**")
    
    # Persona-specific instructions
    if persona == "architect":
        prompt_parts.append("""
**ARCHITECTURAL PRINCIPLES**:
- Consider long-term maintainability and scalability
- Evaluate trade-offs between different architectural approaches
- Provide concrete implementation guidance
- Address technical debt and migration strategies""")
    
    elif persona == "analyzer":
        prompt_parts.append("""
**ANALYSIS METHODOLOGY**:
- Use systematic investigation approach
- Provide evidence-based conclusions
- Consider multiple hypotheses
- Include debugging and monitoring strategies""")
    
    elif persona in ["frontend", "backend"]:
        prompt_parts.append("""
**TECHNICAL FOCUS**:
- Provide specific implementation guidance
- Consider performance and security implications
- Include testing and validation strategies
- Address best practices and modern approaches""")
    
    elif persona in ["seq", "seq-ultra"]:
        iterations = 5 if persona == "seq" else 10
        prompt_parts.append(f"""
**SEQUENTIAL REASONING REQUIREMENTS**:
- Break down the problem into exactly {iterations} logical steps
- Show clear reasoning chain between steps
- Validate each step before proceeding
- Synthesize findings into actionable recommendations""")
    
    # User request
    prompt_parts.append(f"\n**USER REQUEST**:\n{user_input}")
    
    # Quality requirements
    prompt_parts.append("""
**QUALITY REQUIREMENTS**:
- Provide specific, actionable recommendations
- Include concrete examples and code snippets where relevant
- Consider edge cases and potential issues
- Prioritize practical implementation over theoretical perfection
- Structure response clearly with proper headings and organization""")
    
    return "\n\n".join(prompt_parts)

def call_codex(prompt: str, reasoning_effort: str = "medium") -> Tuple[bool, str]:
    """Call Codex CLI with appropriate configuration"""
    
    if not shutil.which("codex"):
        return False, "❌ Codex CLI not found. Please install: npm install -g @openai/codex@latest"
    
    log(f"Consulting Codex CLI with {reasoning_effort} reasoning effort...")
    
    cmd = ["codex", "exec", "-c", f"model_reasoning_effort={reasoning_effort}", prompt]
    
    if os.environ.get('SP_VERBOSE'):
        print("-------- CODEX PROMPT BEGIN")
        print(prompt)
        print("-------- CODEX PROMPT END")
    
    timeout = 180 if reasoning_effort == "high" else 120
    success, output = run_command(cmd, timeout)
    
    if not success:
        return False, f"Codex execution failed: {output}"
    
    if not output.strip():
        return False, "Codex returned empty response"
    
    return True, output

def format_response(codex_response: str, persona: str, analysis: Dict, context: Dict, user_input: str) -> str:
    """Format Codex response for optimal Cursor integration"""
    
    config = PersonaConfig.get_config(persona)
    
    formatted_parts = []
    
    # Header with persona and context
    persona_icons = {
        "architect": "🏗️", "analyzer": "🔍", "frontend": "🎨", 
        "backend": "⚙️", "seq": "🔄", "seq-ultra": "🧠"
    }
    
    icon = persona_icons.get(persona, "🤖")
    formatted_parts.append(f"# {icon} {config['role']}")
    formatted_parts.append(f"**Specialization**: {config['specialization']}")
    
    if analysis["focus_areas"]:
        formatted_parts.append(f"**Focus Areas**: {', '.join(analysis['focus_areas']).replace('_', ' ').title()}")
    
    formatted_parts.append(f"**Complexity Score**: {analysis['complexity_score']:.2f}")
    formatted_parts.append("")
    
    # Main Codex response
    formatted_parts.append("## Strategic Analysis")
    formatted_parts.append(codex_response)
    formatted_parts.append("")
    
    # Project integration guidance
    formatted_parts.append("## Project Integration")
    
    if context["frameworks"]:
        formatted_parts.append(f"- **Technology Stack**: {', '.join(context['frameworks'])}")
    
    formatted_parts.append("- **Implementation Approach**: Follow existing project patterns and conventions")
    formatted_parts.append("- **Change Management**: Implement changes incrementally with proper testing")
    
    if analysis["complexity_score"] > 0.5:
        formatted_parts.append("- **Risk Mitigation**: Create proof-of-concept before full implementation")
        formatted_parts.append("- **Monitoring**: Establish success metrics and rollback procedures")
    
    formatted_parts.append("")
    
    # Next steps with persona-specific guidance
    formatted_parts.append("## Recommended Next Steps")
    
    if persona == "architect":
        formatted_parts.append("1. Review architectural recommendations above")
        formatted_parts.append("2. Create detailed technical design document")
        formatted_parts.append("3. Plan migration strategy with rollback points")
        formatted_parts.append("4. Set up monitoring and success metrics")
    
    elif persona == "analyzer":
        formatted_parts.append("1. Validate the analysis findings above")
        formatted_parts.append("2. Implement recommended debugging steps")
        formatted_parts.append("3. Set up monitoring for identified issues")
        formatted_parts.append("4. Create preventive measures")
    
    elif persona in ["frontend", "backend"]:
        formatted_parts.append("1. Review technical recommendations above")
        formatted_parts.append("2. Create implementation tickets with acceptance criteria")
        formatted_parts.append("3. Set up testing strategy")
        formatted_parts.append("4. Plan deployment and rollback procedures")
    
    elif persona in ["seq", "seq-ultra"]:
        formatted_parts.append("1. Review the sequential analysis above")
        formatted_parts.append("2. Validate each step of the reasoning chain")
        formatted_parts.append("3. Implement recommendations in logical order")
        formatted_parts.append("4. Monitor results at each step")
    
    # Cursor workflow integration
    formatted_parts.append("")
    formatted_parts.append("## Cursor Workflow Integration")
    formatted_parts.append("- **Detailed Implementation**: Copy specific recommendations into focused prompts")
    formatted_parts.append("- **Code Generation**: Use `/implement` for specific feature development")
    formatted_parts.append("- **Testing**: Use `/analyzer` for debugging and validation")
    formatted_parts.append("- **Documentation**: Use `/spec` and `/plan` for formal documentation")
    
    return "\n".join(formatted_parts)

def save_session_log(persona: str, user_input: str, analysis: Dict, codex_response: str, context: Dict) -> None:
    """Save session log for future reference"""
    
    if os.environ.get('SP_NO_LOGS') == '1':
        return
    
    try:
        logs_dir = os.path.join('.cursor', 'logs', 'persona-sessions')
        os.makedirs(logs_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        log_file = os.path.join(logs_dir, f"{persona}-{timestamp}.md")
        
        log_content = f"""# {persona.title()} Session Log

**Timestamp**: {datetime.datetime.now().isoformat()}
**Persona**: {persona}
**Complexity Score**: {analysis['complexity_score']:.2f}
**Codex Consultation**: {'Yes' if analysis['needs_codex'] else 'No'}
**Focus Areas**: {', '.join(analysis['focus_areas'])}
**Project Type**: {context['project_type']}
**Frameworks**: {', '.join(context['frameworks'])}

## User Input
{user_input}

## Analysis Results
{codex_response}

---
Generated by codex-processor.py
"""
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(log_content)
        
        log(f"Session saved to {log_file}")
        
    except Exception as e:
        log(f"Failed to save session log: {e}")

def process_persona_request(persona: str, user_input: str) -> int:
    """Main processing function for persona requests"""
    
    if not user_input.strip():
        print(f"❌ Usage: {persona}-processor.py \"your question or request\"")
        return 1
    
    config = PersonaConfig.get_config(persona)
    persona_name = config["role"]
    
    print(f"{persona_icons.get(persona, '🤖')} {persona_name}")
    print("=" * 60)
    
    # Step 1: Analyze complexity
    log("Analyzing request complexity...")
    analysis = analyze_complexity(user_input, persona)
    
    if os.environ.get('SP_DEBUG'):
        print(f"DEBUG analysis: {json.dumps(analysis, indent=2)}")
    
    # Step 2: Gather project context
    log("Gathering project context...")
    context = get_project_context()
    
    # Step 3: Decide processing approach
    if analysis["needs_codex"]:
        log(f"Complex request detected (score: {analysis['complexity_score']:.2f}) - consulting Codex CLI...")
        
        # Build optimized prompt
        codex_prompt = build_codex_prompt(user_input, persona, context, analysis)
        
        # Call Codex
        success, codex_response = call_codex(codex_prompt, config["reasoning_effort"])
        
        if not success:
            print(f"\n❌ {codex_response}")
            print("\n🔄 Fallback: Try breaking down your request into smaller parts")
            return 1
        
        # Format and present results
        log("Processing strategic insights...")
        formatted_response = format_response(codex_response, persona, analysis, context, user_input)
        
        print("\n" + formatted_response)
        
        # Save session log
        save_session_log(persona, user_input, analysis, codex_response, context)
        
        print(f"\n✅ {persona_name} analysis completed")
        print("💡 Use the insights above to create focused implementation plans")
        
    else:
        log(f"Simple request detected (score: {analysis['complexity_score']:.2f}) - providing direct guidance...")
        
        # Provide simple, direct response without Codex
        print(f"\n## {config['role']} - Quick Guidance")
        print(f"**Request**: {user_input}")
        print(f"**Project Context**: {context['project_type']} project with {', '.join(context['frameworks']) or 'general'} framework(s)")
        print("\n**Recommendation**: This appears to be a straightforward request that can be handled directly in Cursor.")
        print("- Use specific prompts for implementation details")
        print("- Consider breaking down complex tasks into smaller steps")
        print("- Apply existing project patterns and conventions")
        
        if analysis["focus_areas"]:
            print(f"- Focus on: {', '.join(analysis['focus_areas']).replace('_', ' ')}")
        
        print(f"\n💡 For more complex analysis, try rephrasing with more strategic context")
    
    return 0

# Icon mapping for consistent display
persona_icons = {
    "architect": "🏗️", "analyzer": "🔍", "frontend": "🎨", 
    "backend": "⚙️", "seq": "🔄", "seq-ultra": "🧠"
}

def main(args: List[str]) -> int:
    """Main entry point - can be called by individual persona processors"""
    
    if len(args) < 3:
        print("❌ Usage: codex-processor.py <persona> \"your request\"")
        print("\n🎯 Supported personas: architect, analyzer, frontend, backend, seq, seq-ultra")
        return 1
    
    persona = args[1].lower()
    user_input = " ".join(args[2:]).strip()
    
    if persona not in PersonaConfig.PERSONA_CONFIGS:
        print(f"❌ Unsupported persona: {persona}")
        print(f"🎯 Supported personas: {', '.join(PersonaConfig.PERSONA_CONFIGS.keys())}")
        return 1
    
    return process_persona_request(persona, user_input)

if __name__ == "__main__":
    sys.exit(main(sys.argv))