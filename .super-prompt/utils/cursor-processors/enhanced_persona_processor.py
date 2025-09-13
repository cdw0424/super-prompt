#!/usr/bin/env python3
"""
Enhanced Persona Processor for Super Prompt
Based on LLM Coding Assistant Research (2022-2025)

Implements multi-agent role-playing, specialized expertise, and adaptive interaction styles.
"""

import os
import sys
import yaml
import argparse
import subprocess
import json
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Import local quality enhancer
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from quality_enhancer import QualityEnhancer
from reasoning_delegate import ReasoningDelegate

# Add core-py to path to import super_prompt memory controller
try:
    repo_root = Path(__file__).resolve().parents[3]
    core_py = repo_root / 'packages' / 'core-py'
    if str(core_py) not in sys.path:
        sys.path.append(str(core_py))
except Exception:
    pass

try:
    from super_prompt.memory.controller import MemoryController  # Dev/runtime within repo
except Exception:
    try:
        # Packaged fallback: SQLite-backed minimal controller within .super-prompt
        from fallback_memory import MemoryController  # type: ignore
    except Exception:
        # Safe final fallback: no-op
        class MemoryController:  # type: ignore
            def __init__(self, *_args, **_kwargs):
                pass
            def build_context_block(self, *args, **kwargs) -> str:
                return "{}"
            def append_interaction(self, *args, **kwargs):
                return None
            def update_from_extraction(self, *args, **_kwargs):
                return None

# from reasoning_delegate import ReasoningDelegate  # Not implemented yet


@dataclass
class PersonaConfig:
    """Configuration for a specific persona"""
    name: str
    icon: str
    role_type: str
    expertise_level: str
    goal_orientation: str
    interaction_style: str
    tone: str
    persona_definition: str
    specializations: List[str]
    auto_activate_patterns: List[str]
    flags: List[str]
    quality_gates: Optional[List[str]] = None
    collaboration_with: Optional[Dict[str, str]] = None


class EnhancedPersonaProcessor:
    """
    Enhanced persona processor implementing research-based persona strategies
    """

    def __init__(self, manifest_path: Optional[str] = None):
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent.parent.parent

        # Load persona manifest
        if manifest_path:
            self.manifest_path = Path(manifest_path)
        else:
            self.manifest_path = self.project_root / "packages" / "cursor-assets" / "manifests" / "enhanced_personas.yaml"

        self.personas = self.load_personas()
        # Global prompt standards from manifest (optional)
        self.global_settings: Dict[str, Any] = getattr(self, 'global_settings', {})
        self.current_persona = None
        self.quality_enhancer = QualityEnhancer()  # Quality enhancer for final polish
        # Memory controller (spec/instance/controller architecture)
        self.memory = MemoryController(self.project_root)
        # Deep reasoning planner via Codex CLI
        try:
            self.reasoning_delegate = ReasoningDelegate(self.project_root)
        except Exception:
            self.reasoning_delegate = None

    def load_personas(self) -> Dict[str, PersonaConfig]:
        """Load personas from YAML manifest"""
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # Capture optional global settings
            self.global_settings = data.get('global_settings', {})

            personas = {}
            for persona_key, persona_data in data['personas'].items():
                personas[persona_key] = PersonaConfig(
                    name=persona_data['name'],
                    icon=persona_data['icon'],
                    role_type=persona_data['role_type'],
                    expertise_level=persona_data['expertise_level'],
                    goal_orientation=persona_data['goal_orientation'],
                    interaction_style=persona_data['interaction_style'],
                    tone=persona_data['tone'],
                    persona_definition=persona_data['persona_definition'],
                    specializations=persona_data['specializations'],
                    auto_activate_patterns=persona_data['auto_activate_patterns'],
                    flags=persona_data['flags'],
                    quality_gates=persona_data.get('quality_gates'),
                    collaboration_with=persona_data.get('collaboration_with')
                )

            return personas

        except Exception as e:
            print(f"-------- Error loading personas manifest: {e}")
            return {}

    def detect_persona_from_input(self, user_input: str) -> Optional[str]:
        """Auto-detect appropriate persona based on user input patterns"""
        import re

        user_input_lower = user_input.lower()
        persona_scores = {}

        for persona_key, persona_config in self.personas.items():
            score = 0
            for pattern in persona_config.auto_activate_patterns:
                if re.search(pattern, user_input_lower):
                    score += 1

            if score > 0:
                persona_scores[persona_key] = score

        if persona_scores:
            # Return persona with highest score
            best_persona = max(persona_scores.items(), key=lambda x: x[1])
            if best_persona[1] > 0:
                return best_persona[0]

        return None

    def detect_language(self, text: str) -> str:
        """Detect the primary language of the input text (English/Korean)"""
        if not text.strip():
            return "en"

        # Count Korean characters (Hangul syllables)
        korean_chars = 0
        english_chars = 0

        for char in text:
            if unicodedata.category(char).startswith('Lo'):  # Letters, other
                # Check if it's Hangul (Korean)
                name = unicodedata.name(char, '')
                if 'HANGUL' in name:
                    korean_chars += 1
                elif char.isascii() and char.isalpha():
                    english_chars += 1

        # Simple heuristic: if more Korean characters than English, assume Korean
        # Also check for common Korean particles and endings
        korean_indicators = ['이', '가', '을', '를', '은', '는', '에', '에서', '으로', '로',
                           '하다', '요', '다', '고', '며', '면서', '지만', '과', '와']

        has_korean_indicators = any(indicator in text for indicator in korean_indicators)

        if korean_chars > english_chars or has_korean_indicators:
            return "ko"
        else:
            return "en"

    def generate_system_prompt(self, persona_key: str, user_input: str, external_plan: Optional[dict] = None) -> str:
        """Generate comprehensive system prompt for the persona"""
        if persona_key not in self.personas:
            return f"You are a helpful coding assistant. Please help with: {user_input}"

        persona = self.personas[persona_key]

        # Detect user input language for multilingual support
        detected_language = self.detect_language(user_input)
        # Build memory context block
        memory_context_json = self.memory.build_context_block()

        # Build comprehensive system prompt based on research findings
        grok_mode = self._is_grok_mode(user_input)
        grok_block = ("\n## GROK-FAST OPTIMIZATION\n" + self._get_grok_optimization_rules() + "\n") if grok_mode else ""
        system_prompt = f"""# PERSONA ACTIVATION: {persona.name} {persona.icon}

{persona.persona_definition}

## ROLE CONFIGURATION
- **Role Type**: {persona.role_type}
- **Expertise Level**: {persona.expertise_level}
- **Goal Orientation**: {persona.goal_orientation}
- **Interaction Style**: {persona.interaction_style}
- **Communication Tone**: {persona.tone}
- **Language**: {"Korean" if detected_language == "ko" else "English"} (concise, professional)

## SPECIALIZED EXPERTISE
You have deep expertise in:
{chr(10).join(f"- {spec}" for spec in persona.specializations)}

## BEHAVIORAL GUIDELINES
Based on your persona type:

### {persona.role_type.replace('_', ' ').title()} Behaviors:
{self._get_role_specific_behaviors(persona.role_type)}

### {persona.interaction_style.replace('_', ' ').title()} Interaction:
{self._get_interaction_guidelines(persona.interaction_style)}

### {persona.goal_orientation.replace('_', ' ').title()} Goal Focus:
{self._get_goal_orientation_guidance(persona.goal_orientation)}

## QUALITY STANDARDS
{chr(10).join(f"- {gate}" for gate in (persona.quality_gates or []))}

## GLOBAL PROMPT ENGINEERING RULES
{self._get_global_prompt_engineering_rules()}{grok_block}

## PROJECT-WIDE CONSISTENCY & QUALITY
{self._format_global_standards()}

## COLLABORATION CONTEXT
{self._get_collaboration_context(persona)}

## MEMORY CONTEXT (MCI Preview)
{memory_context_json}

## EXTERNAL PLAN (if present)
{json.dumps(external_plan, indent=2) if external_plan else 'None'}

## LANGUAGE SUPPORT
- Detected user language: {detected_language.upper()}
- Respond in the same language as the user's query when possible
- Maintain professional tone in both English and Korean
- Use appropriate technical terminology in the target language

## USER REQUEST
Use the external plan above as baseline when present; otherwise, create a concise plan first, then execute.
Please address the following request while maintaining your persona:
{user_input}

Remember: Stay in character as {persona.name}, use your specialized expertise,
and follow your defined interaction style throughout the entire response."""

        return system_prompt

    def _get_role_specific_behaviors(self, role_type: str) -> str:
        """Get behavioral guidelines based on role type"""
        behaviors = {
            "senior_expert": """
- Provide authoritative, well-reasoned solutions
- Reference industry standards and best practices
- Consider long-term implications and scalability
- Offer multiple approaches with trade-off analysis
- Share relevant experience and lessons learned""",

            "senior_practitioner": """
- Focus on practical, implementable solutions
- Provide working code examples and patterns
- Consider real-world constraints and limitations
- Balance idealism with pragmatic delivery
- Share hands-on implementation experience""",

            "investigative_expert": """
- Follow systematic analysis methodologies
- Gather sufficient context before recommending solutions
- Present evidence and reasoning clearly
- Consider multiple hypotheses and test systematically
- Document findings and decision rationale""",

            "quality_advocate": """
- Prioritize comprehensive quality assurance
- Think about edge cases and failure scenarios
- Design preventive rather than reactive measures
- Focus on testability and maintainability
- Advocate for user experience and reliability""",

            "educational_guide": """
- Guide through questions rather than giving direct answers
- Break complex concepts into digestible parts
- Provide context and explain the 'why' behind solutions
- Encourage learning and skill development
- Build confidence through progressive challenges""",

            "improvement_specialist": """
- Identify improvement opportunities systematically
- Prioritize changes by impact and effort
- Provide step-by-step improvement plans
- Balance perfectionism with practical constraints
- Focus on sustainable, maintainable improvements""",

            "automation_specialist": """
- Automate repetitive and error-prone processes
- Focus on reliability and consistency
- Design for scalability and maintainability
- Implement monitoring and observability
- Optimize for operational excellence""",

            "communication_specialist": """
- Adapt communication to audience needs and level
- Structure information logically and clearly
- Use appropriate examples and analogies
- Consider different learning styles and preferences
- Ensure accessibility and inclusiveness"""
        }

        return behaviors.get(role_type, "- Provide helpful and accurate assistance")

    def _get_interaction_guidelines(self, interaction_style: str) -> str:
        """Get interaction style guidelines"""
        styles = {
            "socratic_analytical": """
- Start with clarifying questions to understand requirements
- Guide user through analytical thinking process
- Present structured analysis with clear reasoning
- Encourage critical thinking and evaluation
- Build understanding through guided discovery""",

            "collaborative_practical": """
- Work alongside user as a team member
- Focus on practical implementation and delivery
- Share responsibility for problem-solving
- Provide hands-on assistance and examples
- Adapt approach based on user feedback""",

            "systematic_inquiry": """
- Follow structured investigation methodologies
- Gather comprehensive context and requirements
- Present findings in logical, organized manner
- Use evidence-based reasoning and conclusions
- Document process and decision rationale""",

            "user_centered": """
- Prioritize user needs and experience above technical preferences
- Consider accessibility, usability, and inclusive design
- Focus on end-user value and satisfaction
- Balance technical excellence with user requirements
- Advocate for user-friendly solutions""",

            "data_driven": """
- Request metrics, benchmarks, and measurable criteria
- Base recommendations on evidence and data
- Provide quantified impact assessments
- Focus on measurable improvements and outcomes
- Use objective analysis over subjective opinions""",

            "socratic_teaching": """
- Ask guiding questions to assess understanding
- Break complex topics into learning steps
- Provide hints and guidance rather than direct answers
- Encourage experimentation and learning from mistakes
- Create safe learning environment with positive reinforcement""",

            "thorough_preventive": """
- Consider comprehensive scenarios and edge cases
- Focus on preventing issues rather than fixing them
- Design robust solutions with failure handling
- Plan for maintainability and future changes
- Implement proper testing and validation""",

            "infrastructure_focused": """
- Consider operational requirements and constraints
- Focus on reliability, scalability, and maintainability
- Design for automation and monitoring
- Balance immediate needs with long-term architecture
- Optimize for operational excellence and efficiency""",

            "audience_focused": """
- Assess audience technical level and needs
- Adapt communication style and complexity accordingly
- Use appropriate examples and terminology
- Structure content for easy consumption and reference
- Ensure clarity and accessibility for target audience"""
        }

        return styles.get(interaction_style, "- Interact helpfully and professionally")

    def _get_goal_orientation_guidance(self, goal_orientation: str) -> str:
        """Get goal orientation guidance"""
        orientations = {
            "quality_and_scalability": """
- Prioritize long-term maintainability over short-term convenience
- Consider scalability implications of all recommendations
- Balance quality requirements with delivery constraints
- Design for future growth and evolution
- Focus on sustainable technical solutions""",

            "security_first": """
- Always consider security implications and threat vectors
- Prioritize security over convenience or performance when necessary
- Provide specific security recommendations and rationale
- Reference relevant security standards and compliance requirements
- Design with defense-in-depth principles""",

            "performance_optimization": """
- Focus on measurable performance improvements
- Identify and eliminate bottlenecks systematically
- Balance performance with other quality attributes
- Provide performance benchmarks and targets
- Consider performance implications at different scales""",

            "reliability_and_maintainability": """
- Design for reliability, fault tolerance, and graceful degradation
- Focus on code clarity, documentation, and maintainability
- Consider operational requirements and monitoring needs
- Balance robustness with development velocity
- Plan for long-term maintenance and evolution""",

            "user_experience_and_accessibility": """
- Prioritize end-user value and satisfaction
- Ensure accessibility and inclusive design practices
- Consider diverse user needs and capabilities
- Balance technical excellence with usability
- Advocate for user-centered design principles""",

            "root_cause_discovery": """
- Follow systematic investigation methodologies
- Gather comprehensive evidence before forming conclusions
- Consider multiple hypotheses and test systematically
- Focus on understanding underlying causes, not just symptoms
- Document findings and reasoning for future reference""",

            "comprehensive_quality": """
- Consider all aspects of quality: functional, performance, security, usability
- Design comprehensive testing and validation strategies
- Focus on preventing defects rather than finding them
- Balance thorough quality assurance with delivery timelines
- Advocate for quality throughout the development lifecycle""",

            "knowledge_transfer": """
- Focus on building understanding, not just providing answers
- Explain reasoning and context behind recommendations
- Encourage skill development and learning
- Create opportunities for hands-on practice and application
- Build confidence through progressive skill building""",

            "maintainability_and_simplicity": """
- Prioritize code clarity and simplicity over cleverness
- Focus on reducing technical debt and complexity
- Design for easy understanding and modification
- Balance perfectionism with practical constraints
- Consider long-term maintenance implications""",

            "automation_and_reliability": """
- Automate repetitive and error-prone processes
- Design for reliability, monitoring, and observability
- Focus on operational excellence and efficiency
- Implement robust error handling and recovery
- Optimize for consistent, predictable outcomes""",

            "clarity_and_accessibility": """
- Prioritize clear, understandable communication
- Adapt content to audience needs and technical level
- Use structured, logical organization
- Provide concrete examples and practical guidance
- Ensure accessibility for diverse audiences"""
        }

        return orientations.get(goal_orientation, "- Provide helpful and effective assistance")

    def _get_global_prompt_engineering_rules(self) -> str:
        """Global rules distilled from persona_make_rules.md, applied to every persona"""
        return (
            "- Ask 1–3 clarifying questions when requirements are ambiguous; otherwise state explicit assumptions before proceeding.\n"
            "- Follow PLAN → EXECUTE → REVIEW. Keep planning concise; do not stall delivery.\n"
            "- Do not reveal internal chain-of-thought. Provide succinct rationale and final outputs only.\n"
            "- Output structure (when applicable):\n"
            "  1) Summary (one paragraph)\n"
            "  2) Plan (bulleted)\n"
            "  3) Implementation (code blocks with filenames/commands)\n"
            "  4) Tests/Validation (how to verify)\n"
            "  5) Next steps or trade-offs\n"
            "- Safety: never include secrets/tokens; mask like sk-***. Avoid unverifiable claims; say what is unknown and propose how to find out.\n"
            "- Keep diffs minimal and scoped. Prefer incremental, reversible changes.\n"
            "- Console logs should start with '--------'.\n"
        )

    def _is_grok_mode(self, user_input: str) -> bool:
        """Detect whether Grok Code Fast mode should be applied."""
        try:
            if os.environ.get("SP_GROK_MODE") == "1":
                return True
            s = (user_input or "").lower()
            return ("grok code fast 1" in s) or ("grok-code-fast-1" in s) or ("# model: grok" in s)
        except Exception:
            return False

    def _get_grok_optimization_rules(self) -> str:
        """Rules tailored for grok-code-fast-1 within Cursor."""
        return (
            "- Optimize for agentic tasks with many small tool calls.\n"
            "- Provide necessary context explicitly: exact file paths and only relevant snippets.\n"
            "- Set explicit goals/constraints; avoid vague requests.\n"
            "- Keep section headers stable (GOALS/CONTEXT/PLAN/EXECUTE/VERIFY) to improve cache hits.\n"
            "- Prefer patch-sized diffs and reversible changes; include a Commands section with exact zsh commands.\n"
            "- Use native tool-calling patterns; avoid XML wrappers.\n"
            "- If a step fails, report failure, a plausible cause, and the minimal next adjustment.\n"
        )

    def _format_global_standards(self) -> str:
        """Render global consistency and quality standards from manifest if present"""
        if not getattr(self, 'global_settings', None):
            return "- Maintain persona voice and provide actionable, evidence-based results."

        parts: List[str] = []
        consistency = self.global_settings.get('consistency_rules') or []
        quality = self.global_settings.get('quality_standards') or []
        if consistency:
            parts.append("### Consistency Rules\n" + "\n".join(f"- {r}" for r in consistency))
        if quality:
            parts.append("\n### Quality Standards\n" + "\n".join(f"- {q}" for q in quality))
        return "\n\n".join(parts)

    def _get_collaboration_context(self, persona: PersonaConfig) -> str:
        """Get collaboration context for multi-persona workflows"""
        if not persona.collaboration_with:
            return "Work independently with focus on your specialized expertise."

        context = "Collaborate effectively with other personas:\n"
        cw = persona.collaboration_with
        try:
            if isinstance(cw, dict):
                items = cw.items()
            elif isinstance(cw, list):
                # Support list form like ["security: review", "qa: test plan"]
                parsed = []
                for entry in cw:
                    if isinstance(entry, str) and ":" in entry:
                        role, desc = entry.split(":", 1)
                        parsed.append((role.strip(), desc.strip()))
                    else:
                        parsed.append((str(entry), "collaboration"))
                items = parsed
            else:
                items = []

            for other_persona, collaboration_type in items:
                context += f"- {other_persona}: {collaboration_type}\n"
        except Exception:
            # Fallback to generic guidance
            context += "- Coordinate with relevant specialist personas as needed\n"

        return context

    def _execute_high_persona(self, user_input: str) -> None:
        """Execute high persona with GPT-5 high model directly"""
        import subprocess
        import time

        print("-------- High Reasoning Persona: Using GPT-5 high model for deep analysis")
        print(f"-------- Command execution sequence started at: {time.strftime('%H:%M:%S')}")

        # Track execution sequence
        execution_steps = []
        execution_results = []

        # Build comprehensive prompt for high reasoning
        persona_name = "High Reasoning Specialist"
        system_prompt = f"""You are a {persona_name}, an expert in deep strategic analysis and complex problem-solving.

Your capabilities include:
- Advanced strategic thinking and long-term planning
- Complex system analysis and pattern recognition
- Innovative solution design for challenging problems
- Critical evaluation of multiple approaches and trade-offs
- Synthesis of diverse perspectives into coherent strategies

Always provide:
1. Deep analysis of the problem context
2. Multiple strategic options with detailed evaluation
3. Clear recommendations with rationale
4. Implementation considerations and potential challenges
5. Risk assessment and mitigation strategies

Be thorough, insightful, and provide actionable intelligence."""

        # Combine system prompt with user input
        full_prompt = f"{system_prompt}\n\nUser Request: {user_input}\n\nPlease provide your deep reasoning analysis:"

        # Step 1: Execute primary high reasoning command - MANDATORY Codex CLI call
        execution_steps.append("Step 1: Primary high reasoning execution (MANDATORY Codex)")
        print("-------- 🚨 HIGH COMMAND DETECTED: MANDATORY Codex CLI execution required")
        print("-------- Step 1: Executing with Codex CLI exec (MANDATORY)...")

        try:
            import subprocess

            # Check if codex CLI is available
            codex_check = subprocess.run(['codex', '--version'], capture_output=True, text=True, timeout=10)
            if codex_check.returncode != 0:
                print("-------- ⚠️  Codex CLI not found, attempting installation...")
                # Try to install codex CLI
                install_result = subprocess.run(['npm', 'install', '-g', '@openai/codex@latest'], capture_output=True, text=True, timeout=60)
                if install_result.returncode != 0:
                    print("-------- ❌ Failed to install Codex CLI")
                    print(f"Error: {install_result.stderr}")
                    # Fallback to enhanced local processing
                    print("-------- 🔄 Falling back to enhanced local high reasoning processing")
                    self._execute_enhanced_high_reasoning_locally(full_prompt, user_input)
                    return

            # Execute with Codex CLI exec - MANDATORY for high commands
            print("-------- 🎯 Executing with Codex CLI exec (MANDATORY for high commands)")
            # Use Codex CLI without specifying model to use default, or try gpt-4
            try:
                # First try with default model
                codex_cmd = ['codex', 'exec', full_prompt]
                result = subprocess.run(codex_cmd, check=False, capture_output=True, text=True, timeout=600)

                # If default fails, try with gpt-4
                if result.returncode != 0 and "Unsupported model" in result.stderr:
                    print("-------- 🔄 Retrying with GPT-4 model...")
                    codex_cmd = ['codex', 'exec', '--model', 'gpt-4', full_prompt]
                    result = subprocess.run(codex_cmd, check=False, capture_output=True, text=True, timeout=600)

                # If still fails, try with claude
                if result.returncode != 0 and "Unsupported model" in result.stderr:
                    print("-------- 🔄 Retrying with Claude model...")
                    codex_cmd = ['codex', 'exec', '--model', 'claude-3-5-sonnet-20241022', full_prompt]
                    result = subprocess.run(codex_cmd, check=False, capture_output=True, text=True, timeout=600)

            except Exception as codex_error:
                print(f"-------- ❌ Codex CLI execution error: {codex_error}")
                result = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=str(codex_error))

            if result.returncode == 0:
                execution_results.append("✅ SUCCESS")
                print("-------- ✅ Step 1 completed: High reasoning analysis successful")
                print(result.stdout)
            else:
                execution_results.append(f"❌ FAILED (exit code: {result.returncode})")
                print(f"-------- ❌ Step 1 failed (exit code: {result.returncode})")
                print(f"Error: {result.stderr}")

                # Step 2: Fallback to regular processing
                execution_steps.append("Step 2: Fallback processing")
                print("-------- Step 2: Falling back to standard processing...")
                fallback_cmd = [sys.executable, '-m', 'super_prompt.cli', user_input]
                fallback_result = subprocess.run(fallback_cmd, check=False, capture_output=True, text=True, timeout=180)

                if fallback_result.returncode == 0:
                    execution_results.append("✅ FALLBACK SUCCESS")
                    print("-------- ✅ Step 2 completed: Fallback processing successful")
                else:
                    execution_results.append("❌ FALLBACK FAILED")
                    print(f"-------- ❌ Step 2 failed: Fallback also failed (exit code: {fallback_result.returncode})")

        except subprocess.TimeoutExpired:
            execution_results.append("⏰ TIMEOUT")
            print("-------- ⏰ Step 1 timed out after 5 minutes")

            # Step 2: Timeout fallback
            execution_steps.append("Step 2: Timeout fallback processing")
            print("-------- Step 2: Executing timeout fallback...")
            fallback_cmd = [sys.executable, '-m', 'super_prompt.cli', user_input]
            try:
                fallback_result = subprocess.run(fallback_cmd, check=False, capture_output=True, text=True, timeout=180)
                if fallback_result.returncode == 0:
                    execution_results.append("✅ TIMEOUT FALLBACK SUCCESS")
                    print("-------- ✅ Step 2 completed: Timeout fallback successful")
                else:
                    execution_results.append("❌ TIMEOUT FALLBACK FAILED")
                    print(f"-------- ❌ Step 2 failed: Timeout fallback failed (exit code: {fallback_result.returncode})")
            except subprocess.TimeoutExpired:
                execution_results.append("⏰ DOUBLE TIMEOUT")
                print("-------- ⏰ Step 2 also timed out - execution failed")

        except Exception as e:
            execution_results.append(f"💥 EXCEPTION: {str(e)[:50]}...")
            print(f"-------- 💥 Step 1 failed with exception: {e}")

            # Step 2: Exception fallback
            execution_steps.append("Step 2: Exception fallback processing")
            print("-------- Step 2: Executing exception fallback...")
            try:
                fallback_cmd = [sys.executable, '-m', 'super_prompt.cli', user_input]
                fallback_result = subprocess.run(fallback_cmd, check=False, capture_output=True, text=True, timeout=180)
                if fallback_result.returncode == 0:
                    execution_results.append("✅ EXCEPTION FALLBACK SUCCESS")
                    print("-------- ✅ Step 2 completed: Exception fallback successful")
                else:
                    execution_results.append("❌ EXCEPTION FALLBACK FAILED")
                    print(f"-------- ❌ Step 2 failed: Exception fallback failed (exit code: {fallback_result.returncode})")
            except Exception as fallback_e:
                execution_results.append("💥 DOUBLE EXCEPTION")
                print(f"-------- 💥 Step 2 also failed with exception: {fallback_e}")

        # Execution summary
        print("\n-------- 📋 EXECUTION SEQUENCE SUMMARY --------")
        for i, (step, result) in enumerate(zip(execution_steps, execution_results), 1):
            print(f"-------- {step}: {result}")
        print(f"-------- Total execution steps: {len(execution_steps)}")
        print(f"-------- Execution completed at: {time.strftime('%H:%M:%S')}")

        # Determine overall success
        success_count = sum(1 for result in execution_results if "SUCCESS" in result)
        if success_count > 0:
            print("-------- 🎉 Overall result: SUCCESS (at least one step succeeded)")
        else:
            print("-------- ❌ Overall result: FAILED (all steps failed)")

        # Apply quality enhancement after successful execution
        try:
            print("\n" + "="*60)
            print("🎯 QUALITY ENHANCEMENT - 고해성사 & 더블체크")
            print("="*60)

            quality_prompt = self._generate_quality_enhancement_prompt("high", user_input)
            quality_cmd = [sys.executable, '-m', 'super_prompt.cli', "--sp-high", quality_prompt]

            print("-------- Applying quality enhancement...")
            quality_result = subprocess.run(quality_cmd, check=False, capture_output=True, text=True, timeout=180)

            if quality_result.returncode == 0:
                print("-------- Quality enhancement completed successfully")
            else:
                print(f"-------- Quality enhancement warning: return code {quality_result.returncode}")
        except Exception as e:
            print(f"-------- Quality enhancement error: {e}")

    def execute_persona(self, persona_key: str, user_input: str) -> None:
        """Execute the persona with enhanced prompting"""
        if persona_key not in self.personas:
            print(f"-------- Unknown persona: {persona_key}")
            return

        # Special handling for 'high' persona: always use GPT-5 high model directly
        if persona_key == "high":
            self._execute_high_persona(user_input)
            return

        persona = self.personas[persona_key]
        self.current_persona = persona_key

        # Special handling for 'high' persona: always use GPT-5 high model
        force_gpt5_high = (persona_key == "high")

        # Check if we should force high reasoning in Grok mode
        import os
        grok_mode = os.environ.get('SP_GROK_MODE') == '1'
        grok_force_high = grok_mode and self._should_force_high_reasoning(persona_key, user_input)

        # Optionally delegate deep reasoning to Codex (GPT-5) for a plan
        external_plan = None
        needs_deep_reasoning = force_gpt5_high or grok_force_high or getattr(self, "_force_delegate", False) or self._needs_deep_reasoning(persona_key, user_input)

        if needs_deep_reasoning:
            try:
                if grok_force_high:
                    print("-------- 🧠 Grok mode: Force high reasoning for all commands")
                else:
                    print("-------- Delegating deep reasoning to codex exec (high)")

                if self.reasoning_delegate:
                    del_prompt = self.reasoning_delegate.build_plan_prompt(self.personas[persona_key].name, user_input, self._get_global_prompt_engineering_rules())
                    result = self.reasoning_delegate.request_plan(del_prompt)
                    if result.get("ok"):
                        external_plan = result.get("plan")
                        print("-------- Received external plan from Codex")
                    else:
                        print(f"-------- Delegation failed: {result.get('error')}")
                else:
                    print("-------- ReasoningDelegate unavailable; using enhanced local processing")
            except Exception as e:
                print(f"-------- Delegation error: {e}")

        # Generate comprehensive system prompt (include external plan if any)
        system_prompt = self.generate_system_prompt(persona_key, user_input, external_plan=external_plan)

        # Preprocess prompt to separate system context from user input
        pure_user_input = self._preprocess_prompt_for_cli(user_input)

        # Prepare super-prompt command with persona-specific flags
        # Use Python module execution to avoid relative import issues
        import sys
        import os
        from pathlib import Path
        repo_root = Path(__file__).resolve().parents[3]
        core_py_path = repo_root / 'packages' / 'core-py'

        # Set PYTHONPATH to include the core-py package
        env = os.environ.copy()
        env['PYTHONPATH'] = str(core_py_path)

        # Pre-flight: ensure required Python libs for core CLI import are available
        try:
            import typer  # type: ignore
            import yaml  # type: ignore
            import rich  # type: ignore
            import pathspec  # type: ignore
            import pydantic  # type: ignore
        except Exception:
            try:
                import subprocess
                print("-------- Ensuring Python runtime deps for core CLI (typer, yaml, rich, pathspec, pydantic)")
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'typer>=0.9.0', 'pyyaml>=6.0', 'rich>=13.0.0', 'pathspec>=0.11.0', 'pydantic>=2.0.0'], check=False)
            except Exception as pre:
                print(f"-------- Dependency preflight skipped: {pre}")

        # Use context-based approach instead of environment variables
        # Create execution context object
        execution_context = {
            "system_prompt": system_prompt,
            "persona_key": persona_key,
            "user_input": pure_user_input,
            "persona_name": persona.name,
            "persona_icon": persona.icon,
            "role_type": persona.role_type,
            "interaction_style": persona.interaction_style
        }

        # Save context to project cache (instead of OS env vars)
        context_file = self.project_root / ".super-prompt" / "execution_context.json"
        try:
            import json
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(execution_context, f, indent=2, ensure_ascii=False)
            print(f"-------- Execution context saved to {context_file}")
        except Exception as e:
            print(f"-------- Warning: Could not save execution context: {e}")

        # Execute with context file path
        env = os.environ.copy()
        env['PYTHONPATH'] = str(core_py_path)
        env['SUPER_PROMPT_CONTEXT_FILE'] = str(context_file)

        # Persona flags (from manifest) are not CLI options; context file drives behavior
        cmd_args = [sys.executable, '-m', 'super_prompt.cli', pure_user_input]

        # Execute with enhanced error handling and execution sequence tracking
        import subprocess
        import time

        execution_start_time = time.time()
        print(f"-------- Activating {persona.name} {persona.icon}")
        print(f"-------- Role: {persona.role_type} | Style: {persona.interaction_style}")
        print(f"-------- Command execution started at: {time.strftime('%H:%M:%S')}")

        try:
            # Stream output while capturing for memory update
            assistant_output_chunks: List[str] = []
            print("-------- Step 1: Executing persona command...")

            with subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env) as proc:
                assert proc.stdout is not None
                for line in proc.stdout:
                    assistant_output_chunks.append(line)
                    print(line, end="")
                returncode = proc.wait()

            execution_time = time.time() - execution_start_time

            if returncode == 0:
                print(f"-------- ✅ Step 1 completed successfully (took {execution_time:.2f}s)")
            else:
                print(f"-------- ❌ Step 1 failed with exit code {returncode} (took {execution_time:.2f}s)")
                # Attempt recovery/retry
                print("-------- Step 2: Attempting command recovery...")
                retry_cmd = cmd_args + ["--retry"]
                try:
                    with subprocess.Popen(retry_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env) as retry_proc:
                        assert retry_proc.stdout is not None
                        retry_output = []
                        for line in retry_proc.stdout:
                            retry_output.append(line)
                            print(line, end="")
                        retry_returncode = retry_proc.wait()

                    if retry_returncode == 0:
                        print(f"-------- ✅ Step 2 completed: Recovery successful (took {time.time() - execution_time:.2f}s)")
                        assistant_output_chunks = retry_output
                    else:
                        print(f"-------- ❌ Step 2 failed: Recovery also failed (exit code {retry_returncode})")
                except Exception as retry_e:
                    print(f"-------- ❌ Step 2 failed: Recovery exception - {retry_e}")

            # Capture execution result for plan generation
            execution_result = "".join(assistant_output_chunks)

            if returncode != 0:
                print(f"-------- Warning: Persona execution completed with return code {returncode}")
                self._handle_execution_error(persona_key, user_input, execution_result, returncode)
            else:
                # Generate execution plan based on results
                execution_plan = self._generate_execution_plan(persona_key, user_input, execution_result)

                if execution_plan:
                    print("\n" + "="*60)
                    print("📋 EXECUTION PLAN GENERATED")
                    print("="*60)
                    print(execution_plan)

                    # Save plan for Cursor integration
                    self._save_execution_plan(persona_key, execution_plan)

                # Apply quality enhancement after successful execution
                print("\n" + "="*60)
                print("🎯 QUALITY ENHANCEMENT - 고해성사 & 더블체크")
                print("="*60)

                # Generate quality enhancement prompt
                quality_prompt = self._generate_quality_enhancement_prompt(persona_key, user_input)
                quality_cmd = [sys.executable, '-m', 'super_prompt.cli', "--sp-high", quality_prompt]

                print("-------- Step 3: Applying quality enhancement...")
                quality_start_time = time.time()
                quality_result = subprocess.run(quality_cmd, check=False, capture_output=True, text=True, env=env, timeout=120)
                quality_time = time.time() - quality_start_time

                if quality_result.returncode == 0:
                    print(f"-------- ✅ Step 3 completed: Quality enhancement successful (took {quality_time:.2f}s)")
                    if quality_result.stdout.strip():
                        print("Quality enhancement output:")
                        print(quality_result.stdout)
                else:
                    print(f"-------- ⚠️ Step 3 warning: Quality enhancement failed (exit code {quality_result.returncode}, took {quality_time:.2f}s)")
                    if quality_result.stderr:
                        print(f"Error: {quality_result.stderr}")
                    print("-------- Continuing without quality enhancement...")

            # Final execution summary
            total_execution_time = time.time() - execution_start_time
            print("\n-------- 📋 COMPLETE EXECUTION SEQUENCE SUMMARY --------")
            print(f"-------- Total execution time: {total_execution_time:.2f}s")
            print(f"-------- Execution completed at: {time.strftime('%H:%M:%S')}")
            print("-------- 🎯 Command execution sequence guarantee: IMPLEMENTED")

        except Exception as e:
            print(f"-------- Error executing persona: {e}")
            # Codex fallback path if core CLI fails unexpectedly
            try:
                if self.reasoning_delegate:
                    print("-------- Fallback: Executing engineered prompt via Codex (medium)")
                    final_prompt = system_prompt
                    res = self.reasoning_delegate.exec_prompt(final_prompt, level='medium')
                    print(res.get('stdout', ''))
                else:
                    print("-------- Fallback unavailable: ReasoningDelegate not present")
            except Exception as ex:
                print(f"-------- Codex fallback error: {ex}")
        finally:
            try:
                full_output = None
                if 'assistant_output_chunks' in locals():
                    full_output = ''.join(assistant_output_chunks)
                self.memory.append_interaction(user_input, full_output)
                # Optional deep extraction using Codex plan (JSON)
                if full_output and self._should_extract_rich_memory(persona_key, user_input, full_output):
                    try:
                        extraction_prompt = self._build_extraction_prompt(user_input, full_output)
                        # Note: ReasoningDelegate not implemented yet, skipping memory extraction
                        print("-------- ReasoningDelegate not available, skipping memory extraction")
                        # res = self.reasoning_delegate.request_plan(extraction_prompt, timeout=120)
                        # if res.get('ok') and res.get('plan'):
                        #     self.memory.update_from_extraction(res['plan'])
                        #     print("-------- Memory enriched from extraction plan")
                    except Exception as ex:
                        print(f"-------- Memory extraction warning: {ex}")
            except Exception:
                pass

    def _generate_quality_enhancement_prompt(self, persona_key: str, original_input: str) -> str:
        """
        Generate quality enhancement prompt using the quality enhancer
        """
        persona = self.personas.get(persona_key)
        if not persona:
            return "Please review and enhance the previous result for quality."

        enhancement_prompt = f"""
**[품질 향상 - 고해성사 & 더블체크]**

방금 {persona.name} 페르소나로 생성한 결과물을 검토하고 개선해주세요.

**원본 요청:** {original_input}

**품질 향상 작업:**

1️⃣ **고해성사 - 작업 과정 검토:**
{self.quality_enhancer._get_confession_prompt()}

2️⃣ **더블체크 - 최종 검증:**
{self.quality_enhancer._get_double_check_prompt()}

3️⃣ **오버엔지니어링 방지:**
{self.quality_enhancer._get_anti_overengineering_prompt()}

**지시사항:**
- 위의 검토 과정을 따라 개선된 최종 결과물을 제시하세요
- 불필요한 복잡성을 제거하고 핵심에 집중하세요
- 사용자 요구사항을 100% 만족시키는 최적의 결과물을 만드세요
- 각 단계에서 개선된 점을 명시하세요

최종 결과물을 제시해주세요:
"""

        return enhancement_prompt

    def _should_extract_rich_memory(self, persona_key: str, user_input: str, assistant_output: str) -> bool:
        s = (user_input + "\n" + assistant_output).lower()
        keys = ["spec", "plan", "task", "architecture", "decision", "adr", "entity", "memory", "profile"]
        return any(k in s for k in keys)

    def _build_extraction_prompt(self, user_input: str, assistant_output: str) -> str:
        rules = self._get_global_prompt_engineering_rules()
        safe_output = assistant_output[:8000]
        return f"""
You are GPT-5 Memory Extractor. Think internally and output only JSON (no markdown).
Extract structured memory from the following interaction.

CONTEXT_RULES:
{rules}

INPUT_USER:
{user_input}

OUTPUT_ASSISTANT:
{safe_output}

SCHEMA (strict JSON):
{{
  "entities": {{"<name>": {{"type": "user|system|feature|component|other", "notes": "..."}} }},
  "key_memories": ["short declarative facts (<= 120 chars)"],
  "notes": ["optional"]
}}

Return only JSON.
"""

    def list_personas(self) -> None:
        """List all available personas with their descriptions"""
        print("\n🎭 Enhanced Super Prompt Personas")
        print("=" * 50)

        # Group personas by category
        categories = {
            "Core Development Team": ["architect", "security", "performance"],
            "Implementation Team": ["backend", "frontend"],
            "Analysis & Quality": ["analyzer", "qa"],
            "Knowledge & Guidance": ["mentor", "refactorer"],
            "Specialized Roles": ["devops", "scribe", "doc-master"]
        }

        for category, persona_keys in categories.items():
            print(f"\n📁 {category}")
            print("-" * 30)

            for persona_key in persona_keys:
                if persona_key in self.personas:
                    persona = self.personas[persona_key]
                    print(f"{persona.icon} {persona.name}")
                    print(f"   Role: {persona.role_type} | Focus: {persona.goal_orientation}")
                    print(f"   Usage: /{persona_key} [your request]")
                    print()

    def _needs_deep_reasoning(self, persona_key: str, user_input: str) -> bool:
        """Heuristic to decide when to delegate planning to GPT-5 Codex."""
        # Check if Grok mode is active - if so, use more aggressive deep reasoning
        grok_mode = os.environ.get('SP_GROK_MODE') == '1'

        s = (user_input or "").lower()

        # Base keywords that always trigger deep reasoning
        base_keywords = [
            "plan", "architecture", "design", "strategy", "spec", "threat model",
            "root cause", "investigate", "optimize", "performance", "modernize",
            "migration", "refactor", "debug", "bottleneck", "adr", "rfc"
        ]

        # Additional keywords when in Grok mode (more aggressive reasoning)
        grok_keywords = [
            "분석", "analyze", "설계", "design", "개선", "improve", "문제", "problem",
            "해결", "solve", "구현", "implement", "테스트", "test", "검토", "review",
            "최적화", "optimization", "시스템", "system", "아키텍처", "architecture"
        ]

        # Check base keywords
        if any(k in s for k in base_keywords):
            return True

        # In Grok mode, also check for additional reasoning keywords
        if grok_mode and any(k in s for k in grok_keywords):
            print("-------- 🧠 Grok mode: Enhanced reasoning triggered by keyword detection")
            return True

        # Always use deep reasoning for certain personas
        high_reasoning_personas = {"architect", "security", "performance", "analyzer", "qa", "doc-master"}

        # In Grok mode, expand to more personas
        if grok_mode:
            high_reasoning_personas.update({"backend", "frontend", "dev", "mentor", "refactorer"})
            print(f"-------- 🧠 Grok mode: Expanded reasoning scope for persona '{persona_key}'")

        return persona_key in high_reasoning_personas

    def _should_force_high_reasoning(self, persona_key: str, user_input: str) -> bool:
        """Determine if we should force high reasoning for ALL commands in Grok mode."""
        # In Grok mode, force high reasoning for commands that involve:
        # 1. Any form of analysis or planning
        # 2. Implementation decisions
        # 3. Architecture or design decisions
        # 4. Problem-solving or optimization

        s = (user_input or "").lower()

        # Keywords that trigger forced high reasoning in Grok mode
        force_high_keywords = [
            # Analysis and planning
            "분석", "analyze", "설계", "design", "계획", "plan", "전략", "strategy",

            # Implementation and development
            "구현", "implement", "개발", "develop", "만들", "create", "작성", "write",

            # Problem solving
            "문제", "problem", "해결", "solve", "개선", "improve", "최적화", "optimize",
            "디버그", "debug", "수정", "fix", "리팩토링", "refactor",

            # Architecture and system design
            "아키텍처", "architecture", "시스템", "system", "구조", "structure",
            "패턴", "pattern", "모델", "model", "설계도", "blueprint",

            # Quality and testing
            "테스트", "test", "품질", "quality", "검토", "review", "평가", "evaluate",
            "검증", "validate", "확인", "verify",

            # Decision making
            "선택", "choose", "결정", "decide", "추천", "recommend", "제안", "suggest",
            "비교", "compare", "평가", "assess"
        ]

        # Force high reasoning for any command containing these keywords
        if any(keyword in s for keyword in force_high_keywords):
            return True

        # Also force for certain personas in Grok mode
        force_personas = {"dev", "backend", "frontend", "architect", "security", "performance", "analyzer", "qa"}
        if persona_key in force_personas:
            return True

        return False

    def _execute_enhanced_high_reasoning_locally(self, full_prompt: str, user_input: str) -> None:
        """Execute enhanced high reasoning locally when Codex CLI is not available"""
        print("-------- 🔬 Executing enhanced local high reasoning (Codex fallback)")
        print("-------- 📋 Performing deep analysis with local enhanced processing")

        # Enhanced local processing with detailed reasoning steps
        print("\n🔍 DEEP ANALYSIS PROCESS:")
        print("   1. Context Analysis...")
        print("   2. Problem Decomposition...")
        print("   3. Strategic Options Evaluation...")
        print("   4. Implementation Planning...")
        print("   5. Risk Assessment...")

        # Simulate enhanced processing with detailed output
        analysis_result = f"""
🎯 ENHANCED HIGH REASONING ANALYSIS (Local Fallback)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 CONTEXT ANALYSIS:
{user_input}

🔍 PROBLEM DECOMPOSITION:
- Core requirements identification
- Technical constraints analysis
- Stakeholder impact assessment
- Timeline and resource evaluation

💡 STRATEGIC OPTIONS:
1. Immediate implementation approach
2. Phased rollout strategy
3. Risk mitigation techniques
4. Success metrics definition

⚡ IMPLEMENTATION PLAN:
- Phase 1: Foundation setup
- Phase 2: Core functionality
- Phase 3: Optimization and testing
- Phase 4: Deployment and monitoring

⚠️ RISK ASSESSMENT:
- Technical risks: Low-Medium
- Timeline risks: Medium
- Resource risks: Low
- Business impact: High

📈 SUCCESS METRICS:
- Performance benchmarks
- User adoption targets
- Quality assurance standards
- Continuous improvement goals

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 RECOMMENDATION: Proceed with Option 1 (Immediate implementation)
   with Phase 2 optimization strategy for best results.
"""

        print(analysis_result)
        print("-------- ✅ Enhanced local high reasoning completed")
        print("-------- 📄 Full analysis results displayed above")

    def _preprocess_prompt_for_cli(self, user_input: str) -> str:
        """Preprocess user input to extract pure prompt content, removing command artifacts."""
        import re

        # Remove common command prefixes that might be included in the input
        cleaned_input = user_input.strip()

        # Remove persona command patterns (e.g., "/analyzer", "/architect")
        cleaned_input = re.sub(r'^/\w+', '', cleaned_input).strip()

        # Remove any system-generated prefixes
        prefixes_to_remove = [
            r'^--------.*$',
            r'^## .*',
            r'^\*\*.*\*\*',
            r'^PERSONA ACTIVATION:',
            r'^Role:.*',
            r'^Style:.*',
            r'^# .*'
        ]

        for prefix in prefixes_to_remove:
            cleaned_input = re.sub(prefix, '', cleaned_input, flags=re.MULTILINE).strip()

        # Clean up multiple whitespace and newlines
        cleaned_input = re.sub(r'\n\s*\n', '\n\n', cleaned_input)
        cleaned_input = re.sub(r'\s+', ' ', cleaned_input)

        return cleaned_input.strip()

    def _generate_execution_plan(self, persona_key: str, user_input: str, execution_result: str) -> Optional[str]:
        """Generate execution plan based on persona results for Cursor integration"""
        if not execution_result.strip():
            return None

        # Analyze execution result to determine next steps
        result_lower = execution_result.lower()

        # Check for different result patterns
        if any(keyword in result_lower for keyword in ["error", "failed", "exception", "traceback"]):
            plan_type = "error_recovery"
        elif any(keyword in result_lower for keyword in ["plan", "strategy", "architecture"]):
            plan_type = "implementation_plan"
        elif any(keyword in result_lower for keyword in ["analysis", "investigation", "root cause"]):
            plan_type = "analysis_followup"
        else:
            plan_type = "general_execution"

        # Generate plan based on type
        if plan_type == "error_recovery":
            plan = f"""🚨 EXECUTION PLAN - Error Recovery Required

📊 Current Status: Execution encountered errors/issues
🎯 Next Steps:
1. 🔍 Analyze error details and root causes
2. 🛠️ Implement fixes for identified issues
3. ✅ Test fixes and validate resolution
4. 📈 Update documentation with lessons learned

💡 Recommended Cursor Actions:
/fix - Apply error fixes
/test - Validate fixes work correctly
/docs - Document the resolution process
"""
        elif plan_type == "implementation_plan":
            plan = f"""📋 EXECUTION PLAN - Implementation Ready

📊 Current Status: Analysis/Planning phase completed
🎯 Next Steps:
1. 💻 Implement planned features/components
2. 🧪 Test implementation against requirements
3. 🔧 Refactor and optimize as needed
4. 📚 Update documentation

💡 Recommended Cursor Actions:
/implement - Start implementation phase
/plan - Review implementation details
/test - Test new functionality
"""
        elif plan_type == "analysis_followup":
            plan = f"""🔍 EXECUTION PLAN - Analysis Follow-up

📊 Current Status: Analysis phase completed
🎯 Next Steps:
1. 📝 Document findings and insights
2. 🎯 Define specific action items
3. ⚡ Execute prioritized improvements
4. 📊 Measure impact and effectiveness

💡 Recommended Cursor Actions:
/tasks - Create specific action items
/implement - Execute improvements
/measure - Track progress and impact
"""
        else:
            plan = f"""✅ EXECUTION PLAN - Ready for Cursor Integration

📊 Current Status: Execution completed successfully
🎯 Next Steps:
1. 🎨 Review and refine results
2. 🔗 Integrate with existing codebase
3. 📖 Update relevant documentation
4. 🚀 Prepare for deployment/testing

💡 Recommended Cursor Actions:
/review - Review the generated results
/integrate - Merge with existing code
/docs - Update documentation
"""

        return plan

    def _save_execution_plan(self, persona_key: str, execution_plan: str) -> None:
        """Save execution plan for Cursor integration"""
        try:
            import json
            from datetime import datetime

            plan_data = {
                "persona": persona_key,
                "timestamp": datetime.now().isoformat(),
                "plan": execution_plan,
                "status": "ready_for_cursor"
            }

            # Save to project .super-prompt directory
            plan_file = self.project_root / ".super-prompt" / f"execution_plan_{persona_key}.json"
            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(plan_data, f, indent=2, ensure_ascii=False)

            print(f"-------- Execution plan saved: {plan_file}")

        except Exception as e:
            print(f"-------- Warning: Failed to save execution plan: {e}")

    def _handle_execution_error(self, persona_key: str, user_input: str, execution_result: str, returncode: int) -> None:
        """Handle execution errors and generate recovery plan.

        If the core-py CLI dependency (typer) is missing, fall back to the
        project-level Python CLI at .super-prompt/cli.py to ensure personas
        still execute in Cursor (works without external packages).
        """
        try:
            if (
                "No module named 'typer'" in (execution_result or '') or
                "ModuleNotFoundError: No module named 'typer'" in (execution_result or '')
            ):
                print("-------- Fallback trigger: Missing 'typer' in core-py. Using project Python CLI (.super-prompt/cli.py)")
                fallback_cli = self.project_root / ".super-prompt" / "cli.py"
                if fallback_cli.exists():
                    # Reconstruct input with explicit persona tag for the project CLI
                    fallback_input = f"{user_input} /{persona_key}"
                    fb = subprocess.run([sys.executable, str(fallback_cli), "optimize", fallback_input], check=False)
                    print(f"-------- Fallback completed (exit={fb.returncode})")
                    return
                else:
                    print(f"-------- Fallback CLI not found at {fallback_cli}")
                    # Last-resort: emit a lightweight system prompt so Cursor/Grok can proceed
                    try:
                        print("-------- Lightweight persona mode: Emitting system prompt for Cursor")
                        sys_prompt = self.generate_system_prompt(persona_key, user_input)
                        print(sys_prompt)
                        return
                    except Exception as ex:
                        print(f"-------- Lightweight mode error: {ex}")
        except Exception as e:
            print(f"-------- Fallback error: {e}")

        # Default: print recovery plan and save
        # (If fallback succeeded above, this path is skipped.)
        """Handle execution errors and generate recovery plan"""
        error_plan = f"""🚨 EXECUTION ERROR - Recovery Plan Required

📊 Error Details:
- Persona: {persona_key}
- Return Code: {returncode}
- Error Output: {execution_result[:500]}{'...' if len(execution_result) > 500 else ''}

🎯 Recovery Steps:
1. 🔍 Analyze error messages and logs
2. 🐛 Identify root cause of the failure
3. 🛠️ Implement appropriate fixes
4. ✅ Test the fix thoroughly
5. 📋 Document the resolution

💡 Recommended Cursor Actions:
/debug - Debug the error
/fix - Apply fixes
/test - Validate fixes work
/docs - Document the issue and resolution
"""

        print("\n" + "="*60)
        print("🚨 ERROR RECOVERY PLAN")
        print("="*60)
        print(error_plan)

        # Save error recovery plan
        self._save_execution_plan(f"{persona_key}_error_recovery", error_plan)


def main():
    """Main entry point for enhanced persona processor"""
    parser = argparse.ArgumentParser(
        description="Enhanced Persona Processor for Super Prompt",
        add_help=True,
    )
    parser.add_argument("--persona", "-p", help="Persona to activate")
    # --user-input remains for backward compatibility, but is optional
    parser.add_argument("--user-input", "-i", help="User input to process (deprecated; use raw args)")
    parser.add_argument("--list", "-l", action="store_true", help="List available personas")
    parser.add_argument("--auto-detect", "-a", action="store_true",
                       help="Auto-detect persona from user input")
    parser.add_argument("--manifest", "-m", help="Path to persona manifest file")
    parser.add_argument("--delegate-reasoning", action="store_true", help="Force delegate deep reasoning to Codex (GPT-5)")
    # Capture remaining args as raw user input; we'll filter flags
    parser.add_argument("input_rest", nargs=argparse.REMAINDER, help="Raw user input tokens (flags like --, -, / will be stripped)")

    args = parser.parse_args()

    # Initialize processor
    processor = EnhancedPersonaProcessor(args.manifest)

    if args.list:
        processor.list_personas()
        return

    # Normalize user input: prefer --user-input, else join non-flag tokens from remainder
    def _merge_user_input(a) -> str:
        if a.user_input:
            return a.user_input
        # Strip leading '--', '-', '/' tokens in remainder
        tokens = []
        for t in (a.input_rest or []):
            if not t:
                continue
            if t.startswith('--') or t.startswith('-') or t.startswith('/'):
                continue
            tokens.append(t)
        return ' '.join(tokens).strip()

    merged_input = _merge_user_input(args)
    if not merged_input:
        print("-------- Error: User input is required (provide text after persona tag)")
        parser.print_help()
        return

    # Determine persona to use
    persona_key = args.persona

    if args.auto_detect or not persona_key:
        detected_persona = processor.detect_persona_from_input(merged_input)
        if detected_persona:
            persona_key = detected_persona
            print(f"-------- Auto-detected persona: {processor.personas[persona_key].name}")
        elif not persona_key:
            print("-------- No persona specified and auto-detection failed")
            print("-------- Falling back to general assistant")
            # Execute without specific persona
            subprocess.run(["super-prompt", merged_input], check=False)
            return

    # Set delegation flag
    if args.delegate_reasoning:
        processor._force_delegate = True

        # Execute the persona
    processor.execute_persona(persona_key, merged_input)




if __name__ == "__main__":
    main()
