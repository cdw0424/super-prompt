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
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Import local quality enhancer
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from quality_enhancer import QualityEnhancer

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
    # Safe fallback: no-op memory controller for packaged installs
    class MemoryController:  # type: ignore
        def __init__(self, *_args, **_kwargs):
            pass
        def build_context_block(self, *args, **kwargs) -> str:
            return "{}"
        def append_interaction(self, *args, **kwargs):
            return None
        def update_from_extraction(self, *args, **kwargs):
            return None

from reasoning_delegate import ReasoningDelegate


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
        self.reasoning_delegate = ReasoningDelegate()  # Deep reasoning planner

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

    def generate_system_prompt(self, persona_key: str, user_input: str, external_plan: Optional[dict] = None) -> str:
        """Generate comprehensive system prompt for the persona"""
        if persona_key not in self.personas:
            return f"You are a helpful coding assistant. Please help with: {user_input}"

        persona = self.personas[persona_key]
        # Build memory context block
        memory_context_json = self.memory.build_context_block()

        # Build comprehensive system prompt based on research findings
        system_prompt = f"""# PERSONA ACTIVATION: {persona.name} {persona.icon}

{persona.persona_definition}

## ROLE CONFIGURATION
- **Role Type**: {persona.role_type}
- **Expertise Level**: {persona.expertise_level}
- **Goal Orientation**: {persona.goal_orientation}
- **Interaction Style**: {persona.interaction_style}
- **Communication Tone**: {persona.tone}
- **Language**: English (concise, professional)

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
{self._get_global_prompt_engineering_rules()}

## PROJECT-WIDE CONSISTENCY & QUALITY
{self._format_global_standards()}

## COLLABORATION CONTEXT
{self._get_collaboration_context(persona)}

## MEMORY CONTEXT (MCI Preview)
{memory_context_json}

## EXTERNAL PLAN (if present)
{json.dumps(external_plan, indent=2) if external_plan else 'None'}

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

    def execute_persona(self, persona_key: str, user_input: str) -> None:
        """Execute the persona with enhanced prompting"""
        if persona_key not in self.personas:
            print(f"-------- Unknown persona: {persona_key}")
            return

        persona = self.personas[persona_key]
        self.current_persona = persona_key

        # Optionally delegate deep reasoning to Codex (GPT-5) for a plan
        external_plan = None
        if getattr(self, "_force_delegate", False) or self._needs_deep_reasoning(persona_key, user_input):
            try:
                print("-------- Delegating deep reasoning to codex exec (high)")
                del_prompt = self.reasoning_delegate.build_plan_prompt(self.personas[persona_key].name, user_input, self._get_global_prompt_engineering_rules())
                result = self.reasoning_delegate.request_plan(del_prompt)
                if result.get("ok"):
                    external_plan = result.get("plan")
                    print("-------- Received external plan")
                else:
                    print(f"-------- Delegation failed: {result.get('error')}")
            except Exception as e:
                print(f"-------- Delegation error: {e}")

        # Generate comprehensive system prompt (include external plan if any)
        system_prompt = self.generate_system_prompt(persona_key, user_input, external_plan=external_plan)

        # Prepare super-prompt command with persona-specific flags
        cmd_args = ["super-prompt"] + persona.flags + [system_prompt]

        # Execute with enhanced error handling
        try:
            print(f"-------- Activating {persona.name} {persona.icon}")
            print(f"-------- Role: {persona.role_type} | Style: {persona.interaction_style}")

            # Stream output while capturing for memory update
            assistant_output_chunks: List[str] = []
            with subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
                assert proc.stdout is not None
                for line in proc.stdout:
                    assistant_output_chunks.append(line)
                    print(line, end="")
                returncode = proc.wait()

            if returncode != 0:
                print(f"-------- Warning: Persona execution completed with return code {returncode}")
            else:
                # Apply quality enhancement after successful execution
                print("\n" + "="*60)
                print("🎯 QUALITY ENHANCEMENT - 고해성사 & 더블체크")
                print("="*60)

                # Generate quality enhancement prompt
                quality_prompt = self._generate_quality_enhancement_prompt(persona_key, user_input)
                quality_cmd = ["super-prompt", "--high"] + [quality_prompt]

                print("-------- Applying quality enhancement...")
                quality_result = subprocess.run(quality_cmd, check=False)

                if quality_result.returncode == 0:
                    print("-------- Quality enhancement completed successfully")
                else:
                    print(f"-------- Quality enhancement warning: return code {quality_result.returncode}")

        except Exception as e:
            print(f"-------- Error executing persona: {e}")
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
                        res = self.reasoning_delegate.request_plan(extraction_prompt, timeout=120)
                        if res.get('ok') and res.get('plan'):
                            self.memory.update_from_extraction(res['plan'])
                            print("-------- Memory enriched from extraction plan")
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
        s = (user_input or "").lower()
        keywords = [
            "plan", "architecture", "design", "strategy", "spec", "threat model",
            "root cause", "investigate", "optimize", "performance", "modernize",
            "migration", "refactor", "debug", "bottleneck", "adr", "rfc"
        ]
        if any(k in s for k in keywords):
            return True
        return persona_key in {"architect", "security", "performance", "analyzer", "qa", "doc-master"}


def main():
    """Main entry point for enhanced persona processor"""
    parser = argparse.ArgumentParser(
        description="Enhanced Persona Processor for Super Prompt"
    )
    parser.add_argument("--persona", "-p", help="Persona to activate")
    parser.add_argument("--user-input", "-i", help="User input to process")
    parser.add_argument("--list", "-l", action="store_true", help="List available personas")
    parser.add_argument("--auto-detect", "-a", action="store_true",
                       help="Auto-detect persona from user input")
    parser.add_argument("--manifest", "-m", help="Path to persona manifest file")
    parser.add_argument("--delegate-reasoning", action="store_true", help="Force delegate deep reasoning to Codex (GPT-5)")

    args = parser.parse_args()

    # Initialize processor
    processor = EnhancedPersonaProcessor(args.manifest)

    if args.list:
        processor.list_personas()
        return

    if not args.user_input:
        print("-------- Error: User input is required")
        parser.print_help()
        return

    # Determine persona to use
    persona_key = args.persona

    if args.auto_detect or not persona_key:
        detected_persona = processor.detect_persona_from_input(args.user_input)
        if detected_persona:
            persona_key = detected_persona
            print(f"-------- Auto-detected persona: {processor.personas[persona_key].name}")
        elif not persona_key:
            print("-------- No persona specified and auto-detection failed")
            print("-------- Falling back to general assistant")
            # Execute without specific persona
            subprocess.run(["super-prompt", args.user_input], check=False)
            return

    # Set delegation flag
    if args.delegate_reasoning:
        processor._force_delegate = True

    # Execute the persona
    processor.execute_persona(persona_key, args.user_input)


if __name__ == "__main__":
    main()
