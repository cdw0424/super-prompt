#!/usr/bin/env python3
"""Prompt Optimizer - Generate Structured Prompts (Spec Kit v0.0.20)
Combines spec, plan, and constitution into optimized prompts for LLM consumption.
"""
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

class PromptOptimizer:
    """Optimizer for generating structured prompts from SDD artifacts"""

    def __init__(self):
        self.specs_dir = "specs"
        self.memory_dir = "memory"
        self.prompts_dir = ".prompts"

    def find_latest_artifacts(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Find the most recent spec, plan, and constitution files"""
        spec_path = plan_path = constitution_path = None

        # Find latest spec and plan
        if os.path.exists(self.specs_dir):
            spec_files = []
            plan_files = []

            for root, dirs, files in os.walk(self.specs_dir):
                for file in files:
                    if file == 'spec.md':
                        path = os.path.join(root, file)
                        mtime = os.path.getmtime(path)
                        spec_files.append((path, mtime))
                    elif file == 'plan.md':
                        path = os.path.join(root, file)
                        mtime = os.path.getmtime(path)
                        plan_files.append((path, mtime))

            if spec_files:
                spec_path = max(spec_files, key=lambda x: x[1])[0]
            if plan_files:
                plan_path = max(plan_files, key=lambda x: x[1])[0]

        # Find constitution
        constitution_candidates = [
            os.path.join(self.memory_dir, 'constitution', 'constitution.md'),
            os.path.join(self.memory_dir, 'constitution.md'),
            'constitution.md'
        ]

        for candidate in constitution_candidates:
            if os.path.exists(candidate):
                constitution_path = candidate
                break

        return spec_path, plan_path, constitution_path

    def analyze_artifacts(self, spec_path: str = None, plan_path: str = None,
                         constitution_path: str = None) -> Dict[str, any]:
        """Analyze all artifacts for prompt generation"""
        analysis = {
            'spec': self._analyze_spec(spec_path) if spec_path else None,
            'plan': self._analyze_plan(plan_path) if plan_path else None,
            'constitution': self._analyze_constitution(constitution_path) if constitution_path else None,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'spec_tokens': 0,
                'plan_tokens': 0,
                'constitution_tokens': 0,
                'total_tokens': 0
            },
            'quality_score': self._calculate_quality_score(spec_path, plan_path, constitution_path)
        }

        # Estimate token counts (rough approximation)
        if spec_path:
            analysis['metadata']['spec_tokens'] = self._estimate_tokens(spec_path)
        if plan_path:
            analysis['metadata']['plan_tokens'] = self._estimate_tokens(plan_path)
        if constitution_path:
            analysis['metadata']['constitution_tokens'] = self._estimate_tokens(constitution_path)

        analysis['metadata']['total_tokens'] = (
            analysis['metadata']['spec_tokens'] +
            analysis['metadata']['plan_tokens'] +
            analysis['metadata']['constitution_tokens']
        )

        return analysis

    def _analyze_spec(self, spec_path: str) -> Dict[str, any]:
        """Analyze spec file content"""
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            'req_id': self._extract_req_id(content),
            'title': self._extract_title(content, 'Feature Specification'),
            'overview': self._extract_section(content, 'Overview'),
            'success_criteria': self._extract_checklist(content, 'Success Criteria'),
            'acceptance_criteria': self._extract_checklist(content, 'Acceptance Criteria'),
            'scope': self._extract_scope_info(content),
            'business_value': self._extract_section(content, 'Business Value'),
            'constraints': self._extract_constraints_from_spec(content),
            'risks': self._extract_risks_from_spec(content)
        }

    def _analyze_plan(self, plan_path: str) -> Dict[str, any]:
        """Analyze plan file content"""
        with open(plan_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            'req_id': self._extract_req_id(content),
            'architecture': self._extract_section(content, 'Architecture Overview'),
            'tech_stack': self._extract_tech_stack(content),
            'components': self._extract_components(content),
            'data_architecture': self._extract_section(content, 'Data Architecture'),
            'api_design': self._extract_section(content, 'API Design'),
            'security_architecture': self._extract_section(content, 'Security Architecture'),
            'testing_strategy': self._extract_section(content, 'Testing Strategy'),
            'deployment_strategy': self._extract_section(content, 'Deployment Strategy'),
            'timeline': self._extract_timeline(content),
            'team_requirements': self._extract_team_requirements(content),
            'cost_estimate': self._extract_section(content, 'Cost Estimation'),
            'risk_mitigation': self._extract_risk_mitigation(content),
            'success_metrics': self._extract_success_metrics(content)
        }

    def _analyze_constitution(self, constitution_path: str) -> Dict[str, any]:
        """Analyze constitution file content"""
        with open(constitution_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            'core_principles': self._extract_section(content, 'Core Principles'),
            'development_rules': self._extract_section(content, 'Development Rules'),
            'quality_standards': self._extract_section(content, 'Quality Standards'),
            'key_constraints': self._extract_constitution_constraints(content)
        }

    def _extract_req_id(self, content: str) -> str:
        """Extract REQ-ID"""
        match = re.search(r'## REQ-ID:\s*(REQ-[\w-]+)', content)
        return match.group(1) if match else 'REQ-UNKNOWN'

    def _extract_title(self, content: str, default: str) -> str:
        """Extract title from first heading"""
        lines = content.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if line.startswith('# '):
                return line[2:].strip()
        return default

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract content from a specific section"""
        pattern = rf'## {re.escape(section_name)}\s*\n(.*?)(?=\n## |\n---|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ''

    def _extract_checklist(self, content: str, section_name: str) -> List[str]:
        """Extract checklist items from a section"""
        section_content = self._extract_section(content, section_name)
        if not section_content:
            return []

        items = []
        for line in section_content.split('\n'):
            line = line.strip()
            if line.startswith('- [ ]') or line.startswith('- [x]'):
                items.append(line[5:].strip())

        return items

    def _extract_scope_info(self, content: str) -> Dict[str, List[str]]:
        """Extract scope information"""
        scope = {'in_scope': [], 'out_of_scope': []}

        # In Scope
        in_scope_content = self._extract_section(content, 'In Scope')
        if in_scope_content:
            scope['in_scope'] = [line.strip('- ').strip() for line in in_scope_content.split('\n') if line.strip().startswith('-')]

        # Out of Scope
        out_scope_content = self._extract_section(content, 'Out of Scope')
        if out_scope_content:
            scope['out_of_scope'] = [line.strip('- ').strip() for line in out_scope_content.split('\n') if line.strip().startswith('-')]

        return scope

    def _extract_constraints_from_spec(self, content: str) -> Dict[str, List[str]]:
        """Extract constraints from spec"""
        constraints = {
            'performance': self._extract_checklist(content, 'Performance Requirements'),
            'security': self._extract_checklist(content, 'Security Considerations'),
            'accessibility': self._extract_checklist(content, 'Accessibility Requirements')
        }
        return constraints

    def _extract_risks_from_spec(self, content: str) -> Dict[str, List[str]]:
        """Extract risks from spec"""
        risks = {'technical': [], 'business': []}

        # Technical risks
        tech_risks_content = self._extract_section(content, 'Technical Risks')
        if tech_risks_content:
            risks['technical'] = [line.strip('- ').strip() for line in tech_risks_content.split('\n') if line.strip().startswith('-')]

        # Business risks
        biz_risks_content = self._extract_section(content, 'Business Risks')
        if biz_risks_content:
            risks['business'] = [line.strip('- ').strip() for line in biz_risks_content.split('\n') if line.strip().startswith('-')]

        return risks

    def _extract_tech_stack(self, content: str) -> Dict[str, List[str]]:
        """Extract technology stack"""
        stack = {}

        # Extract from Technical Stack section
        stack_content = self._extract_section(content, 'Technical Stack')
        if stack_content:
            current_category = None
            for line in stack_content.split('\n'):
                line = line.strip()
                if line.startswith('### ') and ':' in line:
                    current_category = line[4:].split(':')[0].strip().lower()
                    stack[current_category] = []
                elif line.startswith('- ') and current_category:
                    stack[current_category].append(line[2:].strip())

        return stack

    def _extract_components(self, content: str) -> List[Dict[str, str]]:
        """Extract component information"""
        components = []

        # Find component sections
        component_pattern = r'### Component \d+: (.+)\n(.*?)(?=\n### |\Z)'
        matches = re.finditer(component_pattern, content, re.DOTALL)

        for match in matches:
            component_name = match.group(1)
            component_content = match.group(2)

            component = {'name': component_name}

            # Extract purpose, interface, dependencies
            for line in component_content.split('\n'):
                line = line.strip()
                if line.startswith('- Purpose:'):
                    component['purpose'] = line[10:].strip()
                elif line.startswith('- Interface:'):
                    component['interface'] = line[11:].strip()
                elif line.startswith('- Dependencies:'):
                    component['dependencies'] = line[15:].strip()

            components.append(component)

        return components

    def _extract_timeline(self, content: str) -> Dict[str, str]:
        """Extract timeline information"""
        timeline = {}

        # Extract phase information
        phase_pattern = r'### Phase (\d+): (.+) \[(.+)\]'
        matches = re.findall(phase_pattern, content)

        for match in matches:
            phase_num, name, duration = match
            timeline[f'phase_{phase_num}'] = f"{name} ({duration})"

        return timeline

    def _extract_team_requirements(self, content: str) -> Dict[str, List[str]]:
        """Extract team requirements"""
        team = {'skills': [], 'training': []}

        # Skills needed
        skills_content = self._extract_section(content, 'Skills Needed')
        if skills_content:
            team['skills'] = [line.strip('- ').strip() for line in skills_content.split('\n') if line.strip().startswith('-')]

        # Training required
        training_content = self._extract_section(content, 'Training Required')
        if training_content:
            team['training'] = [line.strip('- ').strip() for line in training_content.split('\n') if line.strip().startswith('-')]

        return team

    def _extract_risk_mitigation(self, content: str) -> List[str]:
        """Extract risk mitigation strategies"""
        mitigation_content = self._extract_section(content, 'Risk Mitigation')
        if not mitigation_content:
            return []

        mitigations = []
        for line in mitigation_content.split('\n'):
            line = line.strip()
            if line.startswith('- Risk:') or line.startswith('- Mitigation:'):
                mitigations.append(line[2:].strip())

        return mitigations

    def _extract_success_metrics(self, content: str) -> Dict[str, List[str]]:
        """Extract success metrics"""
        metrics = {'technical': [], 'business': []}

        # Technical metrics
        tech_content = self._extract_section(content, 'Technical Metrics')
        if tech_content:
            metrics['technical'] = self._extract_checklist_from_text(tech_content)

        # Business metrics
        biz_content = self._extract_section(content, 'Business Metrics')
        if biz_content:
            metrics['business'] = self._extract_checklist_from_text(biz_content)

        return metrics

    def _extract_constitution_constraints(self, content: str) -> List[str]:
        """Extract key constraints from constitution"""
        constraints = []

        # Look for key rules and standards
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('- ') and any(keyword in line.lower() for keyword in
                ['must', 'required', 'mandatory', 'shall', 'should', 'quality', 'security', 'performance']):
                constraints.append(line[2:].strip())

        return constraints

    def _extract_checklist_from_text(self, text: str) -> List[str]:
        """Extract checklist items from text"""
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('- [ ]') or line.startswith('- [x]'):
                items.append(line[5:].strip())
        return items

    def _estimate_tokens(self, file_path: str) -> int:
        """Roughly estimate token count (1 token ≈ 4 characters)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Rough approximation: ~4 characters per token
            return len(content) // 4
        except:
            return 0

    def _calculate_quality_score(self, spec_path: str = None, plan_path: str = None,
                                constitution_path: str = None) -> Dict[str, any]:
        """Calculate overall quality score"""
        score = 100
        issues = []

        # Check for required files
        if not spec_path:
            score -= 30
            issues.append("Missing spec.md file")
        if not plan_path:
            score -= 30
            issues.append("Missing plan.md file")
        if not constitution_path:
            score -= 10
            issues.append("Missing constitution.md file (recommended)")

        # Check file sizes (very basic quality indicator)
        if spec_path and os.path.getsize(spec_path) < 1000:
            score -= 10
            issues.append("Spec file seems too short")
        if plan_path and os.path.getsize(plan_path) < 2000:
            score -= 10
            issues.append("Plan file seems too short")

        return {
            'score': max(0, score),
            'issues': issues,
            'grade': 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'F'
        }

    def generate_structured_prompts(self, analysis: Dict[str, any]) -> Dict[str, str]:
        """Generate structured prompts for different LLM consumption patterns"""
        prompts = {}

        # System Prompt - Core instructions and context
        prompts['system'] = self._generate_system_prompt(analysis)

        # Developer Prompt - Constitution and development guidelines
        prompts['developer'] = self._generate_developer_prompt(analysis)

        # User Prompt - Specific task requirements
        prompts['user'] = self._generate_user_prompt(analysis)

        # Combined Prompt - All information in single context
        prompts['combined'] = self._generate_combined_prompt(analysis)

        return prompts

    def _generate_system_prompt(self, analysis: Dict[str, any]) -> str:
        """Generate system-level prompt with core context"""
        lines = [
            "# System Context - Spec Kit v0.0.20",
            "",
            "## Project Overview",
            f"You are implementing: {analysis['spec']['title'] if analysis['spec'] else 'Unknown Feature'}",
            f"REQ-ID: {analysis['spec']['req_id'] if analysis['spec'] else 'REQ-UNKNOWN'}",
            "",
            "## Core Requirements",
        ]

        if analysis['spec']:
            if analysis['spec']['success_criteria']:
                lines.append("**Success Criteria:**")
                for criteria in analysis['spec']['success_criteria'][:3]:  # Top 3
                    lines.append(f"- {criteria}")
                lines.append("")

            if analysis['spec']['acceptance_criteria']:
                lines.append("**Acceptance Criteria:**")
                for criteria in analysis['spec']['acceptance_criteria'][:5]:  # Top 5
                    lines.append(f"- {criteria}")
                lines.append("")

        if analysis['plan']:
            lines.extend([
                "## Technical Context",
                f"**Architecture:** {analysis['plan']['architecture'][:200]}..." if len(analysis['plan']['architecture']) > 200 else f"**Architecture:** {analysis['plan']['architecture']}",
                "",
                "**Technology Stack:**"
            ])

            # Add key technologies
            if 'core' in analysis['plan']['tech_stack']:
                for tech in analysis['plan']['tech_stack']['core'][:5]:
                    lines.append(f"- {tech}")

            lines.extend([
                "",
                f"**Timeline:** {', '.join(analysis['plan']['timeline'].values()) if analysis['plan']['timeline'] else 'Not specified'}",
                "",
                "## Quality Standards"
            ])

        if analysis['constitution']:
            lines.append("**Constitution Requirements:**")
            for constraint in analysis['constitution']['key_constraints'][:5]:
                lines.append(f"- {constraint}")

        return "\n".join(lines)

    def _generate_developer_prompt(self, analysis: Dict[str, any]) -> str:
        """Generate developer-focused prompt with constitution and best practices"""
        lines = [
            "# Developer Guidelines - Spec Kit v0.0.20",
            "",
            "## Constitution & Standards"
        ]

        if analysis['constitution']:
            if analysis['constitution']['core_principles']:
                lines.extend([
                    "### Core Principles",
                    analysis['constitution']['core_principles'],
                    ""
                ])

            if analysis['constitution']['development_rules']:
                lines.extend([
                    "### Development Rules",
                    analysis['constitution']['development_rules'],
                    ""
                ])

            if analysis['constitution']['quality_standards']:
                lines.extend([
                    "### Quality Standards",
                    analysis['constitution']['quality_standards'],
                    ""
                ])

        lines.extend([
            "## Implementation Guidelines",
            "",
            "### Code Quality",
            "- Follow established patterns and conventions",
            "- Write self-documenting code with clear naming",
            "- Include comprehensive error handling",
            "- Add logging with consistent prefixes",
            "",
            "### Security",
            "- Never commit secrets or sensitive data",
            "- Validate all inputs and sanitize outputs",
            "- Follow principle of least privilege",
            "- Implement secure defaults",
            "",
            "### Testing",
            "- Write tests before implementation when possible",
            "- Cover happy path and error scenarios",
            "- Test integrations between components",
            "- Maintain >80% code coverage target"
        ])

        if analysis['plan']:
            if analysis['plan']['security_architecture']:
                lines.extend([
                    "",
                    "### Security Requirements",
                    analysis['plan']['security_architecture'][:500] + "..." if len(analysis['plan']['security_architecture']) > 500 else analysis['plan']['security_architecture']
                ])

        return "\n".join(lines)

    def _generate_user_prompt(self, analysis: Dict[str, any]) -> str:
        """Generate user-focused prompt with specific task requirements"""
        lines = [
            "# Implementation Task - Spec Kit v0.0.20",
            "",
            f"## Feature: {analysis['spec']['title'] if analysis['spec'] else 'Unknown Feature'}",
            f"**REQ-ID:** {analysis['spec']['req_id'] if analysis['spec'] else 'REQ-UNKNOWN'}",
            "",
            "## What to Implement"
        ]

        if analysis['spec'] and analysis['spec']['overview']:
            lines.extend([
                analysis['spec']['overview'],
                ""
            ])

        if analysis['plan']:
            lines.extend([
                "## Technical Approach",
                analysis['plan']['architecture'],
                "",
                "## Components to Build"
            ])

            for component in analysis['plan']['components'][:3]:  # Top 3 components
                lines.extend([
                    f"### {component['name']}",
                    f"**Purpose:** {component.get('purpose', 'Not specified')}",
                    f"**Interface:** {component.get('interface', 'Not specified')}",
                    ""
                ])

            if analysis['plan']['tech_stack']:
                lines.append("## Technology Stack")
                for category, technologies in analysis['plan']['tech_stack'].items():
                    if technologies:
                        lines.append(f"**{category.title()}:** {', '.join(technologies[:3])}")
                lines.append("")

        lines.extend([
            "## Acceptance Criteria",
            "Before completing this task, ensure:"
        ])

        if analysis['spec'] and analysis['spec']['acceptance_criteria']:
            for criteria in analysis['spec']['acceptance_criteria']:
                lines.append(f"- [ ] {criteria}")
        else:
            lines.extend([
                "- [ ] Code compiles without errors",
                "- [ ] Basic functionality works",
                "- [ ] No security vulnerabilities introduced"
            ])

        lines.extend([
            "",
            "## Next Steps",
            "1. Review the system and developer context above",
            "2. Implement the required functionality",
            "3. Test against acceptance criteria",
            "4. Run acceptance self-check script",
            "5. Submit for review only when all criteria pass"
        ])

        return "\n".join(lines)

    def _generate_combined_prompt(self, analysis: Dict[str, any]) -> str:
        """Generate combined prompt with all context"""
        sections = []

        # Header
        sections.extend([
            "# Complete Implementation Context - Spec Kit v0.0.20",
            "",
            f"**Feature:** {analysis['spec']['title'] if analysis['spec'] else 'Unknown Feature'}",
            f"**REQ-ID:** {analysis['spec']['req_id'] if analysis['spec'] else 'REQ-UNKNOWN'}",
            f"**Generated:** {analysis['metadata']['generated_at']}",
            f"**Quality Score:** {analysis['quality_score']['score']}/100 ({analysis['quality_score']['grade']})",
            "",
            "---",
            ""
        ])

        # System Context
        sections.extend([
            "# 🤖 System Context",
            "",
            self._generate_system_prompt(analysis),
            "",
            "---",
            ""
        ])

        # Developer Guidelines
        sections.extend([
            "# 👨‍💻 Developer Guidelines",
            "",
            self._generate_developer_prompt(analysis),
            "",
            "---",
            ""
        ])

        # Implementation Task
        sections.extend([
            "# 🎯 Implementation Task",
            "",
            self._generate_user_prompt(analysis),
            "",
            "---",
            ""
        ])

        # Full Spec (Reference)
        if analysis['spec']:
            sections.extend([
                "# 📋 Full Specification Reference",
                "",
                "## Overview",
                analysis['spec']['overview'] or "Not specified",
                "",
                "## Success Criteria"
            ])

            for criteria in analysis['spec']['success_criteria']:
                sections.append(f"- [ ] {criteria}")

            sections.extend([
                "",
                "## Acceptance Criteria"
            ])

            for criteria in analysis['spec']['acceptance_criteria']:
                sections.append(f"- [ ] {criteria}")

            sections.extend([
                "",
                "## Scope & Constraints"
            ])

            if analysis['spec']['scope']['in_scope']:
                sections.append("**In Scope:**")
                for item in analysis['spec']['scope']['in_scope']:
                    sections.append(f"- {item}")

            if analysis['spec']['scope']['out_of_scope']:
                sections.append("**Out of Scope:**")
                for item in analysis['spec']['scope']['out_of_scope']:
                    sections.append(f"- {item}")

            sections.extend([
                "",
                "---",
                ""
            ])

        # Full Plan (Reference)
        if analysis['plan']:
            sections.extend([
                "# 📊 Full Implementation Plan Reference",
                "",
                "## Architecture Overview",
                analysis['plan']['architecture'] or "Not specified",
                "",
                "## Technology Stack"
            ])

            for category, technologies in analysis['plan']['tech_stack'].items():
                if technologies:
                    sections.append(f"**{category.title()}:** {', '.join(technologies)}")

            sections.extend([
                "",
                "## Success Metrics"
            ])

            for category, metrics in analysis['plan']['success_metrics'].items():
                sections.append(f"**{category.title()}:**")
                for metric in metrics:
                    sections.append(f"- [ ] {metric}")

            sections.extend([
                "",
                "---",
                ""
            ])

        # Constitution (Reference)
        if analysis['constitution']:
            sections.extend([
                "# ⚖️ Constitution Reference",
                "",
                "## Core Principles",
                analysis['constitution']['core_principles'] or "Not specified",
                "",
                "## Development Rules",
                analysis['constitution']['development_rules'] or "Not specified",
                "",
                "---",
                ""
            ])

        return "\n".join(sections)

    def generate_metadata(self, analysis: Dict[str, any]) -> Dict[str, any]:
        """Generate metadata for the prompt package"""
        return {
            'generated_at': analysis['metadata']['generated_at'],
            'req_id': analysis['spec']['req_id'] if analysis['spec'] else 'REQ-UNKNOWN',
            'feature_title': analysis['spec']['title'] if analysis['spec'] else 'Unknown Feature',
            'quality_score': analysis['quality_score']['score'],
            'quality_grade': analysis['quality_score']['grade'],
            'quality_issues': analysis['quality_score']['issues'],
            'token_counts': {
                'spec': analysis['metadata']['spec_tokens'],
                'plan': analysis['metadata']['plan_tokens'],
                'constitution': analysis['metadata']['constitution_tokens'],
                'total': analysis['metadata']['total_tokens']
            },
            'artifacts_used': {
                'spec': analysis['spec'] is not None,
                'plan': analysis['plan'] is not None,
                'constitution': analysis['constitution'] is not None
            }
        }

    def optimize_and_save(self, output_dir: str = None) -> str:
        """Main optimization function - analyze and generate all prompts"""
        if not output_dir:
            output_dir = self.prompts_dir

        os.makedirs(output_dir, exist_ok=True)

        # Find and analyze artifacts
        spec_path, plan_path, constitution_path = self.find_latest_artifacts()

        if not spec_path:
            raise ValueError("No spec.md file found. Run /specify first.")

        analysis = self.analyze_artifacts(spec_path, plan_path, constitution_path)

        # Generate prompts
        prompts = self.generate_structured_prompts(analysis)

        # Save individual prompts
        for prompt_type, content in prompts.items():
            if prompt_type != 'combined':  # Save combined separately
                filename = f"{prompt_type}.txt"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

        # Save combined prompt
        combined_path = os.path.join(output_dir, 'combined.md')
        with open(combined_path, 'w', encoding='utf-8') as f:
            f.write(prompts['combined'])

        # Save metadata
        metadata = self.generate_metadata(analysis)
        metadata_path = os.path.join(output_dir, 'meta.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # Generate quality report
        quality_report = self._generate_quality_report(analysis)
        quality_path = os.path.join(output_dir, 'score.json')
        with open(quality_path, 'w', encoding='utf-8') as f:
            json.dump(quality_report, f, indent=2, ensure_ascii=False)

        print("----- Prompt optimization completed successfully!"        print(f"----- Output directory: {output_dir}")
        print(f"----- Quality score: {metadata['quality_score']}/100 ({metadata['quality_grade']})")
        print(f"----- Total tokens: ~{metadata['token_counts']['total']}")
        print("----- Files generated:"
        print(f"  - combined.md (main prompt)")
        print(f"  - system.txt, developer.txt, user.txt (separated)")
        print(f"  - meta.json (metadata)")
        print(f"  - score.json (quality report)")

        return output_dir

    def _generate_quality_report(self, analysis: Dict[str, any]) -> Dict[str, any]:
        """Generate detailed quality report"""
        return {
            'overall_score': analysis['quality_score']['score'],
            'grade': analysis['quality_score']['grade'],
            'issues': analysis['quality_score']['issues'],
            'breakdown': {
                'spec_completeness': self._score_spec_completeness(analysis),
                'plan_completeness': self._score_plan_completeness(analysis),
                'constitution_compliance': self._score_constitution_compliance(analysis),
                'artifact_quality': self._score_artifact_quality(analysis)
            },
            'recommendations': self._generate_recommendations(analysis)
        }

    def _score_spec_completeness(self, analysis: Dict[str, any]) -> int:
        """Score spec completeness"""
        if not analysis['spec']:
            return 0

        score = 100
        spec = analysis['spec']

        # Required sections
        if not spec['overview']:
            score -= 20
        if not spec['success_criteria']:
            score -= 15
        if not spec['acceptance_criteria']:
            score -= 15
        if not spec['scope']['in_scope']:
            score -= 10

        return max(0, score)

    def _score_plan_completeness(self, analysis: Dict[str, any]) -> int:
        """Score plan completeness"""
        if not analysis['plan']:
            return 0

        score = 100
        plan = analysis['plan']

        # Required sections
        if not plan['architecture']:
            score -= 20
        if not plan['tech_stack']:
            score -= 15
        if not plan['security_architecture']:
            score -= 10
        if not plan['testing_strategy']:
            score -= 10

        return max(0, score)

    def _score_constitution_compliance(self, analysis: Dict[str, any]) -> int:
        """Score constitution compliance"""
        if not analysis['constitution']:
            return 50  # Partial credit for having some standards

        # Basic check - if constitution exists and has content
        constitution = analysis['constitution']
        if constitution['core_principles'] and constitution['development_rules']:
            return 100
        elif constitution['core_principles'] or constitution['development_rules']:
            return 75
        else:
            return 25

    def _score_artifact_quality(self, analysis: Dict[str, any]) -> int:
        """Score overall artifact quality"""
        score = 100

        # Token-based quality indicator (rough)
        total_tokens = analysis['metadata']['total_tokens']
        if total_tokens < 1000:
            score -= 30  # Too short
        elif total_tokens > 20000:
            score -= 10  # Might be too verbose

        return max(0, score)

    def _generate_recommendations(self, analysis: Dict[str, any]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        if not analysis['spec']:
            recommendations.append("Create a spec.md file using /specify command")
        elif analysis['quality_score']['score'] < 70:
            recommendations.append("Improve spec completeness - add missing required sections")

        if not analysis['plan']:
            recommendations.append("Create a plan.md file using /plan command")
        elif analysis['quality_score']['score'] < 70:
            recommendations.append("Enhance plan with more detailed technical specifications")

        if not analysis['constitution']:
            recommendations.append("Add constitution.md file for development standards")

        if analysis['metadata']['total_tokens'] > 20000:
            recommendations.append("Consider breaking down large artifacts into smaller, focused documents")

        return recommendations

def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Prompt Optimizer - Spec Kit v0.0.20')
    parser.add_argument('-o', '--output', help='Output directory for prompts')
    parser.add_argument('--spec', help='Path to spec file')
    parser.add_argument('--plan', help='Path to plan file')
    parser.add_argument('--constitution', help='Path to constitution file')

    args = parser.parse_args()

    try:
        optimizer = PromptOptimizer()

        # Override paths if specified
        if args.spec or args.plan or args.constitution:
            analysis = optimizer.analyze_artifacts(args.spec, args.plan, args.constitution)
            prompts = optimizer.generate_structured_prompts(analysis)

            output_dir = args.output or optimizer.prompts_dir
            os.makedirs(output_dir, exist_ok=True)

            # Save prompts
            for prompt_type, content in prompts.items():
                if prompt_type == 'combined':
                    filepath = os.path.join(output_dir, 'combined.md')
                else:
                    filepath = os.path.join(output_dir, f'{prompt_type}.txt')

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

            print("----- Custom prompt generation completed!")
        else:
            # Full optimization
            output_dir = optimizer.optimize_and_save(args.output)

    except Exception as e:
        print(f"----- Error during prompt optimization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
