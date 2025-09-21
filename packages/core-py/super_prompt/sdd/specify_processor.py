#!/usr/bin/env python3
"""Specify Processor - Generate Feature Specifications (Spec Kit v0.0.20)
Creates comprehensive specifications that serve as source of truth for development.
"""
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class SpecifyProcessor:
    """Processor for generating feature specifications"""

    def __init__(self):
        self.templates_dir = "specs/templates/spec"
        self.specs_dir = "specs"

    def generate_req_id(self, feature_name: str) -> str:
        """Generate a unique REQ-ID for the feature"""
        # Clean feature name for ID generation
        clean_name = re.sub(r'[^\w\s-]', '', feature_name).strip()
        clean_name = re.sub(r'\s+', '-', clean_name).upper()

        # Check existing specs to avoid duplicates
        existing_ids = []
        if os.path.exists(self.specs_dir):
            for root, dirs, files in os.walk(self.specs_dir):
                for file in files:
                    if file.endswith('spec.md'):
                        spec_path = os.path.join(root, file)
                        try:
                            with open(spec_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                id_match = re.search(r'## REQ-ID:\s*(REQ-[\w-]+)', content)
                                if id_match:
                                    existing_ids.append(id_match.group(1))
                        except:
                            pass

        # Generate unique ID
        base_id = f"REQ-{clean_name[:10]}"
        counter = 1
        req_id = base_id
        while req_id in existing_ids:
            req_id = f"{base_id}-{counter}"
            counter += 1

        return req_id

    def parse_user_input(self, user_input: str) -> Dict[str, str]:
        """Parse user input to extract feature details"""
        # Basic NLP to extract key information
        feature_name = user_input.strip()

        # Try to identify technology keywords
        tech_keywords = {
            'web': ['web', 'frontend', 'ui', 'interface', 'website'],
            'api': ['api', 'rest', 'graphql', 'endpoint', 'service'],
            'mobile': ['mobile', 'app', 'ios', 'android'],
            'data': ['database', 'data', 'storage', 'analytics'],
            'auth': ['login', 'auth', 'authentication', 'security', 'oauth'],
            'admin': ['admin', 'management', 'dashboard', 'control']
        }

        detected_tech = []
        for tech, keywords in tech_keywords.items():
            if any(keyword in user_input.lower() for keyword in keywords):
                detected_tech.append(tech)

        # Determine feature type
        feature_type = 'feature'
        if any(word in user_input.lower() for word in ['system', 'platform', 'framework']):
            feature_type = 'system'
        elif any(word in user_input.lower() for word in ['api', 'service', 'microservice']):
            feature_type = 'service'
        elif any(word in user_input.lower() for word in ['component', 'module', 'library']):
            feature_type = 'component'

        return {
            'name': feature_name,
            'type': feature_type,
            'detected_tech': detected_tech,
            'complexity': self._estimate_complexity(user_input)
        }

    def _estimate_complexity(self, user_input: str) -> str:
        """Estimate feature complexity based on keywords"""
        complexity_indicators = {
            'high': ['distributed', 'real-time', 'high-performance', 'scalable', 'enterprise', 'multi-tenant', 'microservices'],
            'medium': ['integration', 'workflow', 'dashboard', 'reporting', 'search', 'filtering'],
            'low': ['form', 'list', 'basic', 'simple', 'page']
        }

        input_lower = user_input.lower()
        for level, indicators in complexity_indicators.items():
            if any(indicator in input_lower for indicator in indicators):
                return level

        return 'medium'  # default

    def generate_spec_content(self, parsed_input: Dict[str, str]) -> str:
        """Generate the complete spec content"""
        req_id = self.generate_req_id(parsed_input['name'])

        # Load template
        template_path = os.path.join(self.templates_dir, 'spec-template.md')
        if not os.path.exists(template_path):
            # Fallback template if file doesn't exist
            template_content = self._get_fallback_template()
        else:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

        # Replace placeholders
        replacements = {
            '[Unique identifier, e.g., REQ-001]': req_id,
            '[Brief description of what this feature does and why it matters]': self._generate_overview(parsed_input),
            '[Describe the user journey - what they want to achieve]': self._generate_user_journey(parsed_input),
            '[Measurable outcome 1]': self._generate_success_criteria(parsed_input)[0],
            '[Measurable outcome 2]': self._generate_success_criteria(parsed_input)[1],
            '[Measurable outcome 3]': self._generate_success_criteria(parsed_input)[2],
            '[Specific, testable condition 1]': self._generate_acceptance_criteria(parsed_input)[0],
            '[Specific, testable condition 2]': self._generate_acceptance_criteria(parsed_input)[1],
            '[Specific, testable condition 3]': self._generate_acceptance_criteria(parsed_input)[2],
            '[List what\'s included]': self._generate_in_scope(parsed_input),
            '[List what\'s explicitly excluded]': self._generate_out_of_scope(parsed_input),
            '[List assumptions that must hold true]': self._generate_assumptions(parsed_input),
            '[List external dependencies or prerequisites]': self._generate_dependencies(parsed_input),
            '[Why this feature matters to users/business]': self._generate_business_value(parsed_input),
            '[List potential technical challenges]': self._generate_technical_risks(parsed_input),
            '[List potential business impact risks]': self._generate_business_risks(parsed_input),
            '[Current Date]': datetime.now().strftime('%Y-%m-%d')
        }

        content = template_content
        for placeholder, replacement in replacements.items():
            content = content.replace(f'[{placeholder}]', replacement)

        return content

    def _get_fallback_template(self) -> str:
        """Fallback template if spec-template.md is not found"""
        return """# Feature Specification

## REQ-ID: [Unique identifier, e.g., REQ-001]

## Overview
[Brief description of what this feature does and why it matters]

## User Journey
[Describe the user journey - what they want to achieve]

### Success Criteria
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]
- [ ] [Measurable outcome 3]

### Acceptance Criteria
- [ ] [Specific, testable condition 1]
- [ ] [Specific, testable condition 2]
- [ ] [Specific, testable condition 3]

## Scope & Boundaries
### In Scope
- [List what's included]

### Out of Scope
- [List what's explicitly excluded]

### Assumptions
- [List assumptions that must hold true]

### Dependencies
- [List external dependencies or prerequisites]

## Business Value
[Why this feature matters to users/business]

## Risk Assessment
### Technical Risks
- [List potential technical challenges]

### Business Risks
- [List potential business impact risks]

## Data Requirements
[If applicable, describe data structures or requirements]

## Security Considerations
[Security requirements or considerations]

## Performance Requirements
[Performance expectations or constraints]

## Accessibility Requirements
[Accessibility standards to meet]

## Internationalization
[i18n requirements if applicable]

## Future Considerations
[How this might evolve or connect to future features]

---
*Generated by Spec Kit v0.0.20 - [Current Date]*"""

    def _generate_overview(self, parsed: Dict[str, str]) -> str:
        """Generate overview description"""
        name = parsed['name']
        tech = ', '.join(parsed['detected_tech']) if parsed['detected_tech'] else 'software'

        return f"Implement {name} to provide {tech} functionality that enhances user experience and system capabilities."

    def _generate_user_journey(self, parsed: Dict[str, str]) -> str:
        """Generate user journey description"""
        name = parsed['name']
        return f"Users need to {name.lower()} through an intuitive interface that guides them step-by-step, ensuring a smooth and efficient experience."

    def _generate_success_criteria(self, parsed: Dict[str, str]) -> List[str]:
        """Generate success criteria"""
        name = parsed['name']
        return [
            f"Users can successfully {name.lower()} without errors",
            f"System performance meets defined benchmarks during {name.lower()}",
            f"User satisfaction scores for {name.lower()} exceed 80%"
        ]

    def _generate_acceptance_criteria(self, parsed: Dict[str, str]) -> List[str]:
        """Generate acceptance criteria"""
        name = parsed['name']
        return [
            f"All core functionality of {name.lower()} is implemented and tested",
            f"Error handling and edge cases for {name.lower()} are properly managed",
            f"Code quality standards are met for {name.lower()} implementation"
        ]

    def _generate_in_scope(self, parsed: Dict[str, str]) -> str:
        """Generate in-scope items"""
        name = parsed['name']
        tech = parsed['detected_tech']
        items = [f"Core {name.lower()} functionality"]

        if 'web' in tech:
            items.append("Web interface and user interactions")
        if 'api' in tech:
            items.append("API endpoints and data contracts")
        if 'auth' in tech:
            items.append("Authentication and authorization logic")
        if 'data' in tech:
            items.append("Data storage and retrieval")

        return '\n- '.join([''] + items)

    def _generate_out_of_scope(self, parsed: Dict[str, str]) -> str:
        """Generate out-of-scope items"""
        return "\n- Third-party integrations beyond core requirements\n- Mobile applications (if not specified)\n- Advanced analytics and reporting\n- Administrative interfaces"

    def _generate_assumptions(self, parsed: Dict[str, str]) -> str:
        """Generate assumptions"""
        return "\n- Required infrastructure and dependencies are available\n- Team has necessary skills and access\n- Stakeholder availability for reviews and feedback\n- Development environment is properly configured"

    def _generate_dependencies(self, parsed: Dict[str, str]) -> str:
        """Generate dependencies"""
        tech = parsed['detected_tech']
        deps = []

        if 'web' in tech:
            deps.append("Web framework (React, Vue, or Angular)")
        if 'api' in tech:
            deps.append("Backend framework (FastAPI, Express, or Django)")
        if 'data' in tech:
            deps.append("Database system (PostgreSQL, MongoDB, or similar)")
        if 'auth' in tech:
            deps.append("Authentication provider (OAuth2, JWT)")

        if not deps:
            deps = ["Development team and tools", "Version control system", "CI/CD pipeline"]

        return '\n- '.join([''] + deps)

    def _generate_business_value(self, parsed: Dict[str, str]) -> str:
        """Generate business value"""
        name = parsed['name']
        complexity = parsed['complexity']

        if complexity == 'high':
            return f"This {name.lower()} delivers significant competitive advantage through enhanced capabilities and improved user experience."
        elif complexity == 'medium':
            return f"This {name.lower()} improves operational efficiency and user satisfaction by providing essential functionality."
        else:
            return f"This {name.lower()} addresses basic user needs and provides foundational functionality for future enhancements."

    def _generate_technical_risks(self, parsed: Dict[str, str]) -> str:
        """Generate technical risks"""
        complexity = parsed['complexity']
        tech = parsed['detected_tech']

        risks = []
        if complexity == 'high':
            risks.append("Complex integration requirements")
        if 'data' in tech:
            risks.append("Data consistency and performance challenges")
        if 'auth' in tech:
            risks.append("Security implementation complexity")
        if 'api' in tech:
            risks.append("API design and versioning considerations")

        if not risks:
            risks = ["Standard implementation risks", "Third-party dependency issues"]

        return '\n- '.join([''] + risks)

    def _generate_business_risks(self, parsed: Dict[str, str]) -> str:
        """Generate business risks"""
        return "\n- Changes in requirements during development\n- Timeline delays affecting delivery\n- Resource constraints or availability issues\n- Integration challenges with existing systems"

    def create_spec_file(self, user_input: str) -> str:
        """Create the spec file and return the path"""
        # Parse input
        parsed_input = self.parse_user_input(user_input)

        # Generate content
        content = self.generate_spec_content(parsed_input)

        # Create directory structure
        feature_name = re.sub(r'[^\w\s-]', '', parsed_input['name']).strip()
        feature_name = re.sub(r'\s+', '_', feature_name).lower()
        spec_dir = os.path.join(self.specs_dir, feature_name)
        os.makedirs(spec_dir, exist_ok=True)

        # Write spec file
        spec_path = os.path.join(spec_dir, 'spec.md')
        with open(spec_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Specification created successfully
        return spec_path

def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        # Usage: /specify [feature description]
        # Example: /specify Create user authentication system
        sys.exit(1)

    user_input = ' '.join(sys.argv[1:])

    try:
        processor = SpecifyProcessor()
        spec_path = processor.create_spec_file(user_input)

        # Specification created successfully
        # Next: Run /plan to create implementation plan

    except Exception as e:
        # Error creating specification
        sys.exit(1)

if __name__ == "__main__":
    main()
