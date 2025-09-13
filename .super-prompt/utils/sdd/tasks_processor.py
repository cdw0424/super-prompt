#!/usr/bin/env python3
"""Tasks Processor - Generate Task Breakdowns (Spec Kit v0.0.20)
Creates detailed, testable tasks from specifications and implementation plans.
"""
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import quality enhancer
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from quality_enhancer import QualityEnhancer

class TasksProcessor:
    """Processor for generating task breakdowns"""

    def __init__(self):
        self.templates_dir = "specs/templates/tasks"
        self.specs_dir = "specs"
        self.quality_enhancer = QualityEnhancer()  # Quality enhancer for final polish

    def find_latest_spec_and_plan(self) -> Tuple[Optional[str], Optional[str]]:
        """Find the most recently modified spec and plan files"""
        if not os.path.exists(self.specs_dir):
            return None, None

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

        latest_spec = max(spec_files, key=lambda x: x[1])[0] if spec_files else None
        latest_plan = max(plan_files, key=lambda x: x[1])[0] if plan_files else None

        return latest_spec, latest_plan

    def analyze_requirements(self, spec_path: str, plan_path: str) -> Dict[str, any]:
        """Analyze spec and plan to extract task requirements"""
        # Read files
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec_content = f.read()
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan_content = f.read()

        analysis = {
            'req_id': self._extract_req_id(spec_content),
            'spec_sections': self._analyze_spec_sections(spec_content),
            'plan_components': self._analyze_plan_components(plan_content),
            'technologies': self._extract_technologies(plan_content),
            'complexity': self._estimate_overall_complexity(spec_content, plan_content),
            'timeline': self._extract_timeline(plan_content),
            'risks': self._extract_all_risks(spec_content, plan_content)
        }

        return analysis

    def _extract_req_id(self, content: str) -> str:
        """Extract REQ-ID"""
        match = re.search(r'## REQ-ID:\s*(REQ-[\w-]+)', content)
        return match.group(1) if match else 'REQ-UNKNOWN'

    def _analyze_spec_sections(self, spec_content: str) -> Dict[str, List[str]]:
        """Analyze spec sections for task generation"""
        sections = {}

        # Extract acceptance criteria
        acceptance_match = re.search(r'### Acceptance Criteria\s*\n((?:- \[.\] .*\n?)*)',
                                   spec_content, re.MULTILINE)
        if acceptance_match:
            criteria_text = acceptance_match.group(1)
            sections['acceptance_criteria'] = [
                line.strip('- [ ] ').strip()
                for line in criteria_text.split('\n')
                if line.strip().startswith('- [ ]')
            ]

        # Extract scope items
        in_scope_match = re.search(r'### In Scope\s*\n(.*?)(?=\n###|\Z)', spec_content, re.DOTALL)
        if in_scope_match:
            sections['in_scope'] = [
                line.strip('- ').strip()
                for line in in_scope_match.group(1).split('\n')
                if line.strip().startswith('-')
            ]

        return sections

    def _analyze_plan_components(self, plan_content: str) -> List[Dict[str, str]]:
        """Analyze plan components"""
        components = []

        # Extract component sections
        component_pattern = r'### Component \d+: (.+)\n(?:- Purpose: (.+)\n)?(?:- Interface: (.+)\n)?(?:- Dependencies: (.+)\n)?'
        matches = re.finditer(component_pattern, plan_content, re.MULTILINE)

        for match in matches:
            component = {
                'name': match.group(1),
                'purpose': match.group(2) or '',
                'interface': match.group(3) or '',
                'dependencies': match.group(4) or ''
            }
            components.append(component)

        return components

    def _extract_technologies(self, plan_content: str) -> List[str]:
        """Extract technology stack from plan"""
        technologies = []

        # Extract from Technical Stack section
        stack_match = re.search(r'## Technical Stack\s*\n(.*?)(?=\n## |\Z)', plan_content, re.DOTALL)
        if stack_match:
            stack_content = stack_match.group(1)
            tech_lines = [line.strip('- ').strip() for line in stack_content.split('\n') if line.strip().startswith('-')]
            technologies.extend(tech_lines)

        return technologies

    def _estimate_overall_complexity(self, spec_content: str, plan_content: str) -> str:
        """Estimate overall project complexity"""
        combined_content = (spec_content + plan_content).lower()

        high_indicators = ['distributed', 'microservices', 'enterprise', 'real-time', 'high-performance', 'scalability']
        medium_indicators = ['integration', 'workflow', 'dashboard', 'api', 'database', 'security']
        low_indicators = ['form', 'list', 'basic', 'simple', 'static']

        high_score = sum(1 for indicator in high_indicators if indicator in combined_content)
        medium_score = sum(1 for indicator in medium_indicators if indicator in combined_content)
        low_score = sum(1 for indicator in low_indicators if indicator in combined_content)

        if high_score >= 2:
            return 'high'
        elif medium_score >= 3:
            return 'medium'
        elif low_score >= 2:
            return 'low'
        else:
            return 'medium'

    def _extract_timeline(self, plan_content: str) -> Dict[str, str]:
        """Extract timeline information"""
        timeline = {}

        # Extract phase information
        phase_pattern = r'### Phase (\d+): (.+) \[(.+)\]'
        matches = re.findall(phase_pattern, plan_content)

        for match in matches:
            phase_num, name, duration = match
            timeline[f'phase_{phase_num}'] = {
                'name': name,
                'duration': duration
            }

        return timeline

    def _extract_all_risks(self, spec_content: str, plan_content: str) -> Dict[str, List[str]]:
        """Extract all risks from spec and plan"""
        risks = {'technical': [], 'business': []}

        combined_content = spec_content + plan_content

        # Technical risks
        tech_risks_match = re.search(r'### Technical Risks?\s*\n(.*?)(?=\n###|\n## |\Z)', combined_content, re.DOTALL)
        if tech_risks_match:
            risks['technical'] = [
                line.strip('- ').strip()
                for line in tech_risks_match.group(1).split('\n')
                if line.strip().startswith('-')
            ]

        # Business risks
        biz_risks_match = re.search(r'### Business Risks?\s*\n(.*?)(?=\n###|\n## |\Z)', combined_content, re.DOTALL)
        if biz_risks_match:
            risks['business'] = [
                line.strip('- ').strip()
                for line in biz_risks_match.group(1).split('\n')
                if line.strip().startswith('-')
            ]

        return risks

    def generate_tasks(self, analysis: Dict[str, any], focus_area: str = "") -> List[Dict[str, any]]:
        """Generate detailed tasks based on analysis"""
        tasks = []
        task_counter = 1

        # Infrastructure & Setup tasks
        tasks.extend(self._generate_infrastructure_tasks(analysis, task_counter))
        task_counter += len(tasks)

        # Component implementation tasks
        component_tasks = self._generate_component_tasks(analysis, task_counter)
        tasks.extend(component_tasks)
        task_counter += len(component_tasks)

        # Integration tasks
        integration_tasks = self._generate_integration_tasks(analysis, task_counter)
        tasks.extend(integration_tasks)
        task_counter += len(integration_tasks)

        # Quality assurance tasks
        qa_tasks = self._generate_qa_tasks(analysis, task_counter)
        tasks.extend(qa_tasks)
        task_counter += len(qa_tasks)

        # Deployment & operations tasks
        ops_tasks = self._generate_operations_tasks(analysis, task_counter)
        tasks.extend(ops_tasks)

        # Apply focus area filtering if specified
        if focus_area:
            tasks = [task for task in tasks if focus_area.lower() in str(task).lower()]

        return tasks

    def _generate_infrastructure_tasks(self, analysis: Dict[str, any], start_id: int) -> List[Dict[str, any]]:
        """Generate infrastructure and setup tasks"""
        tasks = []
        technologies = analysis['technologies']
        complexity = analysis['complexity']

        # Development environment setup
        task_id = "02d"
        tasks.append({
            'id': f'TASK-INF-{task_id}',
            'category': 'Infrastructure & Setup',
            'title': 'Development Environment Setup',
            'description': f'Set up complete development environment for {", ".join(technologies[:3])}',
            'acceptance_criteria': [
                'All required dependencies installed and configured',
                'Development scripts working (build, test, lint)',
                'Team members can run application locally',
                'Environment variables and configuration documented'
            ],
            'estimated_effort': '1-2 days' if complexity == 'low' else '2-3 days',
            'dependencies': [],
            'risk_level': 'Low'
        })

        # CI/CD setup
        task_id = "02d"
        tasks.append({
            'id': f'TASK-INF-{task_id}',
            'category': 'Infrastructure & Setup',
            'title': 'CI/CD Pipeline Configuration',
            'description': 'Configure automated testing and deployment pipeline',
            'acceptance_criteria': [
                'Automated tests run on every push',
                'Code quality checks integrated',
                'Build artifacts generated correctly',
                'Deployment to staging environment automated'
            ],
            'estimated_effort': '2-3 days',
            'dependencies': [f'TASK-INF-{start_id:03d}'],
            'risk_level': 'Medium'
        })

        return tasks

    def _generate_component_tasks(self, analysis: Dict[str, any], start_id: int) -> List[Dict[str, any]]:
        """Generate component implementation tasks"""
        tasks = []
        components = analysis['plan_components']
        technologies = analysis['technologies']
        complexity = analysis['complexity']

        task_id = start_id

        for component in components:
            # Foundation task
            tasks.append({
                'id': f'TASK-CORE-{task_id:03d}',
                'category': 'Core Components',
                'title': f'{component["name"]} - Foundation',
                'description': f'Create basic structure and interfaces for {component["name"]}',
                'acceptance_criteria': [
                    f'Basic class/interface structure for {component["name"]} created',
                    'Unit test skeleton in place',
                    'Component interfaces defined',
                    'Integration points identified'
                ],
                'estimated_effort': '1-2 days' if complexity == 'low' else '2-3 days',
                'dependencies': [f'TASK-INF-{start_id:03d}'],
                'risk_level': 'Low'
            })
            task_id += 1

            # Core logic task
            tasks.append({
                'id': f'TASK-CORE-{task_id:03d}',
                'category': 'Core Components',
                'title': f'{component["name"]} - Core Logic',
                'description': f'Implement main business logic for {component["name"]}',
                'acceptance_criteria': [
                    f'All core functionality of {component["name"]} implemented',
                    'Business logic thoroughly tested',
                    'Error handling and edge cases covered',
                    'Code review completed'
                ],
                'estimated_effort': '3-5 days' if complexity == 'low' else '5-8 days',
                'dependencies': [f'TASK-CORE-{(task_id-1):03d}'],
                'risk_level': 'Medium' if complexity != 'high' else 'High'
            })
            task_id += 1

        return tasks

    def _generate_integration_tasks(self, analysis: Dict[str, any], start_id: int) -> List[Dict[str, any]]:
        """Generate integration tasks"""
        tasks = []
        technologies = analysis['technologies']

        # API integration
        if 'api' in technologies:
            tasks.append({
                'id': f'TASK-INT-{start_id:03d}',
                'category': 'Integration & APIs',
                'title': 'API Endpoints Implementation',
                'description': 'Implement REST/gRPC endpoints according to API design',
                'acceptance_criteria': [
                    'All planned endpoints implemented',
                    'Request/response formats match specifications',
                    'Error handling and status codes correct',
                    'API documentation generated (OpenAPI/Swagger)'
                ],
                'estimated_effort': '3-4 days',
                'dependencies': ['TASK-CORE-001'],  # Depends on first core component
                'risk_level': 'Medium'
            })

        # Component integration testing
        tasks.append({
            'id': f'TASK-INT-{(start_id+1):03d}',
            'category': 'Integration & APIs',
            'title': 'Component Integration Testing',
            'description': 'Test interaction between all implemented components',
            'acceptance_criteria': [
                'All component interfaces work correctly',
                'Data flows properly between components',
                'Integration test coverage > 80%',
                'No critical integration bugs'
            ],
            'estimated_effort': '2-3 days',
            'dependencies': ['TASK-CORE-002'],  # Depends on core logic completion
            'risk_level': 'High'
        })

        return tasks

    def _generate_qa_tasks(self, analysis: Dict[str, any], start_id: int) -> List[Dict[str, any]]:
        """Generate quality assurance tasks"""
        tasks = []
        complexity = analysis['complexity']

        # Unit testing
        tasks.append({
            'id': f'TASK-QA-{start_id:03d}',
            'category': 'Testing & Quality Assurance',
            'title': 'Unit Test Implementation',
            'description': 'Write comprehensive unit tests for all components',
            'acceptance_criteria': [
                f'Code coverage > {"70%" if complexity == "low" else "80%"}',
                'All business logic functions tested',
                'Edge cases and error conditions covered',
                'Tests run in < 30 seconds'
            ],
            'estimated_effort': '3-4 days',
            'dependencies': ['TASK-CORE-002'],
            'risk_level': 'Low'
        })

        # Integration testing
        tasks.append({
            'id': f'TASK-QA-{(start_id+1):03d}',
            'category': 'Testing & Quality Assurance',
            'title': 'Integration & E2E Testing',
            'description': 'Implement integration and end-to-end tests',
            'acceptance_criteria': [
                'Full user journeys tested automatically',
                'API contract testing completed',
                'Cross-browser/device compatibility verified',
                'Performance benchmarks met'
            ],
            'estimated_effort': '3-5 days',
            'dependencies': [f'TASK-QA-{start_id:03d}', 'TASK-INT-001'],
            'risk_level': 'Medium'
        })

        return tasks

    def _generate_operations_tasks(self, analysis: Dict[str, any], start_id: int) -> List[Dict[str, any]]:
        """Generate deployment and operations tasks"""
        tasks = []

        # Production environment setup
        tasks.append({
            'id': f'TASK-OPS-{start_id:03d}',
            'category': 'Deployment & Operations',
            'title': 'Production Environment Setup',
            'description': 'Configure production infrastructure and deployment',
            'acceptance_criteria': [
                'Infrastructure as code implemented',
                'Monitoring and logging configured',
                'Backup and disaster recovery tested',
                'Security hardening applied'
            ],
            'estimated_effort': '2-3 days',
            'dependencies': ['TASK-INF-002'],
            'risk_level': 'Medium'
        })

        # Deployment automation
        tasks.append({
            'id': f'TASK-OPS-{(start_id+1):03d}',
            'category': 'Deployment & Operations',
            'title': 'Deployment Automation',
            'description': 'Implement automated deployment and rollback procedures',
            'acceptance_criteria': [
                'Zero-downtime deployment possible',
                'Automated rollback on failure',
                'Deployment verified in staging first',
                'Post-deployment health checks automated'
            ],
            'estimated_effort': '2-3 days',
            'dependencies': [f'TASK-OPS-{start_id:03d}'],
            'risk_level': 'High'
        })

        return tasks

    def generate_task_content(self, analysis: Dict[str, any], tasks: List[Dict[str, any]]) -> str:
        """Generate the complete tasks content"""
        req_id = analysis['req_id']

        # Load template
        template_path = os.path.join(self.templates_dir, 'tasks-template.md')
        if not os.path.exists(template_path):
            template_content = self._get_fallback_template()
        else:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

        # Generate task sections
        task_sections = self._format_task_sections(tasks)
        dependency_graph = self._generate_dependency_graph(tasks)
        effort_summary = self._calculate_effort_summary(tasks)
        risk_assessment = self._generate_risk_assessment(tasks)
        acceptance_checks = self._generate_acceptance_self_check(tasks)

        # Replace placeholders
        replacements = {
            '[Same as spec/plan, e.g., REQ-001]': req_id,
            '[How tasks are organized - by component, by user story, by technical layer, etc.]': 'Tasks organized by technical layer and component dependencies',
            '[List TASK-XXX items here]': task_sections,
            '[Show dependency graph here]': dependency_graph,
            '[Calculate total effort here]': effort_summary,
            '[Assess risks by task here]': risk_assessment,
            '[Generate self-check template here]': acceptance_checks,
            '[Current Date]': datetime.now().strftime('%Y-%m-%d')
        }

        content = template_content
        for placeholder, replacement in replacements.items():
            content = content.replace(f'[{placeholder}]', replacement)

        return content

    def _get_fallback_template(self) -> str:
        """Fallback template if tasks-template.md is not found"""
        return """# Implementation Tasks

## REQ-ID: [Same as spec/plan, e.g., REQ-001]

## Task Breakdown Strategy
[How tasks are organized - by component, by user story, by technical layer, etc.]

## Task Categories

### 🔧 Infrastructure & Setup
[List TASK-INF-XXX items here]

### 🏗️ Core Components
[List TASK-CORE-XXX items here]

### 🔗 Integration & APIs
[List TASK-INT-XXX items here]

### 🧪 Testing & Quality Assurance
[List TASK-QA-XXX items here]

### 🚀 Deployment & Operations
[List TASK-OPS-XXX items here]

## Task Dependencies Graph
[Show dependency graph here]

## Effort Estimation Summary
[Calculate total effort here]

## Risk Assessment by Task
[Assess risks by task here]

## Acceptance Self-Check Template
[Generate self-check template here]

---
*Generated by Spec Kit v0.0.20 - [Current Date]*"""

    def _format_task_sections(self, tasks: List[Dict[str, any]]) -> str:
        """Format tasks into categorized sections"""
        categories = {}
        for task in tasks:
            category = task['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(task)

        sections = []
        for category, category_tasks in categories.items():
            sections.append(f"### {category}")
            for task in category_tasks:
                sections.append(f"- [ ] **{task['id']}**: {task['title']}")
                sections.append(f"  - **Description**: {task['description']}")
                sections.append("  - **Acceptance Criteria**:")
                for criteria in task['acceptance_criteria']:
                    sections.append(f"    - [ ] {criteria}")
                sections.append(f"  - **Estimated Effort**: {task['estimated_effort']}")
                sections.append(f"  - **Dependencies**: {', '.join(task['dependencies']) if task['dependencies'] else 'None'}")
                sections.append(f"  - **Risk Level**: {task['risk_level']}")
                sections.append("")
            sections.append("")

        return "\n".join(sections)

    def _generate_dependency_graph(self, tasks: List[Dict[str, any]]) -> str:
        """Generate ASCII dependency graph"""
        lines = [
            "```",
            "TASK-INF-001 (Setup)",
        ]

        # Find root tasks (no dependencies)
        root_tasks = [task for task in tasks if not task['dependencies']]

        for root_task in root_tasks:
            lines.append(f"├── {root_task['id']} ({root_task['title'].split(' - ')[0]})")

            # Find dependent tasks
            dependent_tasks = [t for t in tasks if root_task['id'] in t['dependencies']]
            for dep_task in dependent_tasks:
                lines.append(f"│   └── {dep_task['id']} ({dep_task['title'].split(' - ')[0]})")

                # Find tasks that depend on this one
                sub_deps = [t for t in tasks if dep_task['id'] in t['dependencies']]
                for sub_dep in sub_deps:
                    lines.append(f"│       └── {sub_dep['id']} ({sub_dep['title'].split(' - ')[0]})")

        lines.extend([
            "",
            "Note: Arrows show dependency direction (A -> B means A must complete before B)",
            "```"
        ])

        return "\n".join(lines)

    def _calculate_effort_summary(self, tasks: List[Dict[str, any]]) -> str:
        """Calculate total effort estimation"""
        effort_by_category = {}
        total_days = 0

        for task in tasks:
            category = task['category']
            effort = task['estimated_effort']

            # Parse effort (rough estimation)
            if 'days' in effort:
                days = int(effort.split('-')[0]) if '-' in effort else int(effort.split()[0])
            elif 'week' in effort:
                days = (int(effort.split('-')[0]) if '-' in effort else int(effort.split()[0])) * 5
            else:
                days = 1  # fallback

            if category not in effort_by_category:
                effort_by_category[category] = 0
            effort_by_category[category] += days
            total_days += days

        summary_lines = []
        for category, days in effort_by_category.items():
            summary_lines.append(f"- **{category}**: {days} days")

        summary_lines.extend([
            "",
            f"- **Total Estimated Effort**: {total_days} days ({total_days//5} weeks)",
            f"- **Team Size Assumption**: 2-3 developers",
            f"- **Buffer**: +20% for unexpected issues"
        ])

        return "\n".join(summary_lines)

    def _generate_risk_assessment(self, tasks: List[Dict[str, any]]) -> str:
        """Generate risk assessment by task categories"""
        risk_levels = {'High': [], 'Medium': [], 'Low': []}

        for task in tasks:
            risk_levels[task['risk_level']].append(f"{task['id']} ({task['title']})")

        assessment_lines = []
        for level, task_list in risk_levels.items():
            if task_list:
                assessment_lines.append(f"### {level} Risk Tasks")
                for task in task_list:
                    assessment_lines.append(f"- {task}")
                assessment_lines.append("")

        assessment_lines.extend([
            "### Risk Mitigation Strategy",
            "- **High Risk**: Pair programming, early prototyping, frequent reviews",
            "- **Medium Risk**: Regular check-ins, automated testing",
            "- **Low Risk**: Standard development practices",
            "",
            "### Contingency Planning",
            "- Additional 20% time buffer for high-risk tasks",
            "- Alternative implementation approaches identified",
            "- Regular risk assessment and adjustment"
        ])

        return "\n".join(assessment_lines)

    def _generate_acceptance_self_check(self, tasks: List[Dict[str, any]]) -> str:
        """Generate acceptance self-check template"""
        checks = [
            "- [ ] Code compiles without errors/warnings",
            "- [ ] Unit tests pass (coverage > 80%)",
            "- [ ] Integration with dependent components works",
            "- [ ] Security requirements met (no hardcoded secrets)",
            "- [ ] Performance requirements met",
            "- [ ] Accessibility requirements verified (if applicable)",
            "- [ ] Documentation updated",
            "- [ ] Code review completed",
            "- [ ] Acceptance criteria from specification met",
            "- [ ] All dependent tasks completed",
            "- [ ] No critical bugs in manual testing",
            "- [ ] Run `python3 scripts/sdd/acceptance_self_check.py` and verify all checks pass"
        ]

        return "Before marking any task as complete, verify:\n" + "\n".join(checks)

    def create_tasks_file(self, focus_area: str = "") -> str:
        """Create the tasks file and return the path"""
        # Find latest spec and plan
        spec_path, plan_path = self.find_latest_spec_and_plan()
        if not spec_path or not plan_path:
            raise ValueError("Both spec.md and plan.md files required. Run /specify and /plan first.")

        # Analyze requirements
        analysis = self.analyze_requirements(spec_path, plan_path)

        # Generate tasks
        tasks = self.generate_tasks(analysis, focus_area)

        # Generate content
        content = self.generate_task_content(analysis, tasks)

        # Apply quality enhancement
        print("----- Applying quality enhancement to task breakdown...")
        content = self.quality_enhancer.enhance_quality(content, {
            'command': 'tasks',
            'spec_path': spec_path,
            'plan_path': plan_path,
            'focus_area': focus_area,
            'stage': 'tasking'
        })

        # Create tasks file in same directory as spec/plan
        spec_dir = os.path.dirname(spec_path)
        tasks_path = os.path.join(spec_dir, 'tasks.md')

        with open(tasks_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"----- Task breakdown created: {tasks_path}")
        return tasks_path

def main():
    """Main CLI entry point"""
    focus_area = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else ''

    try:
        processor = TasksProcessor()
        tasks_path = processor.create_tasks_file(focus_area)

        print("----- Task breakdown created successfully!")
        print(f"----- Ready for implementation: Run acceptance self-check before starting")
        print(f"----- File: {tasks_path}")

    except Exception as e:
        print(f"----- Error creating task breakdown: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
