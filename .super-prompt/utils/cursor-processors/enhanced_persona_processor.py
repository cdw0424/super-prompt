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
        self.current_persona = None

    def load_personas(self) -> Dict[str, PersonaConfig]:
        """Load personas from YAML manifest"""
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

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

    def generate_system_prompt(self, persona_key: str, user_input: str) -> str:
        """Generate comprehensive system prompt for the persona"""
        if persona_key not in self.personas:
            return f"You are a helpful coding assistant. Please help with: {user_input}"

        persona = self.personas[persona_key]

        # Build comprehensive system prompt based on research findings
        system_prompt = f"""# PERSONA ACTIVATION: {persona.name} {persona.icon}

{persona.persona_definition}

## ROLE CONFIGURATION
- **Role Type**: {persona.role_type}
- **Expertise Level**: {persona.expertise_level}
- **Goal Orientation**: {persona.goal_orientation}
- **Interaction Style**: {persona.interaction_style}
- **Communication Tone**: {persona.tone}

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

## COLLABORATION CONTEXT
{self._get_collaboration_context(persona)}

## USER REQUEST
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

    def _get_collaboration_context(self, persona: PersonaConfig) -> str:
        """Get collaboration context for multi-persona workflows"""
        if not persona.collaboration_with:
            return "Work independently with focus on your specialized expertise."

        context = "Collaborate effectively with other personas:\n"
        for other_persona, collaboration_type in persona.collaboration_with.items():
            context += f"- {other_persona}: {collaboration_type}\n"

        return context

    def execute_persona(self, persona_key: str, user_input: str) -> None:
        """Execute the persona with enhanced prompting"""
        if persona_key not in self.personas:
            print(f"-------- Unknown persona: {persona_key}")
            return

        persona = self.personas[persona_key]
        self.current_persona = persona_key

        # Generate comprehensive system prompt
        system_prompt = self.generate_system_prompt(persona_key, user_input)

        # Prepare super-prompt command with persona-specific flags
        cmd_args = ["super-prompt"] + persona.flags + [system_prompt]

        # Execute with enhanced error handling
        try:
            print(f"-------- Activating {persona.name} {persona.icon}")
            print(f"-------- Role: {persona.role_type} | Style: {persona.interaction_style}")

            result = subprocess.run(cmd_args, check=False)

            if result.returncode != 0:
                print(f"-------- Warning: Persona execution completed with return code {result.returncode}")

        except Exception as e:
            print(f"-------- Error executing persona: {e}")

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
            "Specialized Roles": ["devops", "scribe"]
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

    # Execute the persona
    processor.execute_persona(persona_key, args.user_input)


if __name__ == "__main__":
    main()