#!/usr/bin/env python3
"""Plan Processor - Generate Implementation Plans (Spec Kit v0.0.20)
Creates comprehensive implementation plans based on specifications and constitution.
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

class PlanProcessor:
    """Processor for generating implementation plans"""

    def __init__(self):
        self.templates_dir = "specs/templates/plan"
        self.specs_dir = "specs"
        self.quality_enhancer = QualityEnhancer()  # Quality enhancer for final polish

    def find_latest_spec(self) -> Optional[str]:
        """Find the most recently modified spec file"""
        if not os.path.exists(self.specs_dir):
            return None

        spec_files = []
        for root, dirs, files in os.walk(self.specs_dir):
            for file in files:
                if file == 'spec.md':
                    path = os.path.join(root, file)
                    mtime = os.path.getmtime(path)
                    spec_files.append((path, mtime))

        if not spec_files:
            return None

        return max(spec_files, key=lambda x: x[1])[0]

    def analyze_spec(self, spec_path: str) -> Dict[str, any]:
        """Analyze the spec file to extract key information"""
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()

        analysis = {
            'req_id': self._extract_req_id(content),
            'overview': self._extract_section(content, 'Overview'),
            'scope': self._extract_scope(content),
            'complexity': self._estimate_complexity(content),
            'technologies': self._detect_technologies(content),
            'constraints': self._extract_constraints(content),
            'risks': self._extract_risks(content)
        }

        return analysis

    def _extract_req_id(self, content: str) -> str:
        """Extract REQ-ID from spec"""
        match = re.search(r'## REQ-ID:\s*(REQ-[\w-]+)', content)
        return match.group(1) if match else 'REQ-UNKNOWN'

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract content from a specific section"""
        pattern = rf'## {re.escape(section_name)}\s*\n(.*?)(?=\n## |\n---|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ''

    def _extract_scope(self, content: str) -> Dict[str, List[str]]:
        """Extract scope information"""
        scope = {'in': [], 'out': []}

        # Extract In Scope
        in_scope_match = re.search(r'### In Scope\s*\n(.*?)(?=\n###|\n## |\Z)', content, re.DOTALL)
        if in_scope_match:
            scope['in'] = [line.strip('- ').strip() for line in in_scope_match.group(1).split('\n') if line.strip().startswith('-')]

        # Extract Out of Scope
        out_scope_match = re.search(r'### Out of Scope\s*\n(.*?)(?=\n###|\n## |\Z)', content, re.DOTALL)
        if out_scope_match:
            scope['out'] = [line.strip('- ').strip() for line in out_scope_match.group(1).split('\n') if line.strip().startswith('-')]

        return scope

    def _estimate_complexity(self, content: str) -> str:
        """Estimate implementation complexity"""
        content_lower = content.lower()

        high_indicators = ['distributed', 'real-time', 'microservices', 'enterprise', 'high-performance', 'scalability']
        medium_indicators = ['integration', 'workflow', 'dashboard', 'api', 'database']
        low_indicators = ['form', 'list', 'basic', 'simple', 'static']

        high_count = sum(1 for indicator in high_indicators if indicator in content_lower)
        medium_count = sum(1 for indicator in medium_indicators if indicator in content_lower)
        low_count = sum(1 for indicator in low_indicators if indicator in content_lower)

        if high_count > 0:
            return 'high'
        elif medium_count > 2:
            return 'medium'
        elif low_count > 1:
            return 'low'
        else:
            return 'medium'

    def _detect_technologies(self, content: str) -> List[str]:
        """Detect technology requirements from spec"""
        content_lower = content.lower()
        technologies = []

        tech_map = {
            'web': ['web', 'frontend', 'ui', 'interface', 'website', 'browser'],
            'api': ['api', 'rest', 'graphql', 'endpoint', 'service', 'backend'],
            'mobile': ['mobile', 'app', 'ios', 'android', 'responsive'],
            'data': ['database', 'data', 'storage', 'analytics', 'sql', 'nosql'],
            'auth': ['login', 'auth', 'authentication', 'security', 'oauth', 'jwt'],
            'cloud': ['cloud', 'aws', 'azure', 'gcp', 'serverless'],
            'ai': ['ai', 'ml', 'machine learning', 'intelligence', 'automation']
        }

        for tech, keywords in tech_map.items():
            if any(keyword in content_lower for keyword in keywords):
                technologies.append(tech)

        return technologies

    def _extract_constraints(self, content: str) -> Dict[str, List[str]]:
        """Extract various constraints from spec"""
        constraints = {
            'performance': [],
            'security': [],
            'accessibility': [],
            'technical': []
        }

        # Performance requirements
        perf_section = self._extract_section(content, 'Performance Requirements')
        if perf_section:
            constraints['performance'] = [line.strip() for line in perf_section.split('\n') if line.strip()]

        # Security considerations
        sec_section = self._extract_section(content, 'Security Considerations')
        if sec_section:
            constraints['security'] = [line.strip() for line in sec_section.split('\n') if line.strip()]

        # Accessibility requirements
        acc_section = self._extract_section(content, 'Accessibility Requirements')
        if acc_section:
            constraints['accessibility'] = [line.strip() for line in acc_section.split('\n') if line.strip()]

        return constraints

    def _extract_risks(self, content: str) -> Dict[str, List[str]]:
        """Extract risks from spec"""
        risks = {'technical': [], 'business': []}

        # Technical risks
        tech_risks = self._extract_section(content, 'Technical Risks')
        if tech_risks:
            risks['technical'] = [line.strip('- ').strip() for line in tech_risks.split('\n') if line.strip().startswith('-')]

        # Business risks
        biz_risks = self._extract_section(content, 'Business Risks')
        if biz_risks:
            risks['business'] = [line.strip('- ').strip() for line in biz_risks.split('\n') if line.strip().startswith('-')]

        return risks

    def generate_tech_stack(self, analysis: Dict[str, any]) -> Dict[str, List[str]]:
        """Generate recommended technology stack"""
        technologies = analysis['technologies']
        complexity = analysis['complexity']

        stack = {
            'core': [],
            'frontend': [],
            'backend': [],
            'data': [],
            'infrastructure': [],
            'testing': [],
            'deployment': []
        }

        # Core technologies based on detected needs
        if 'web' in technologies:
            if complexity == 'high':
                stack['frontend'].extend(['React 18+', 'TypeScript 5.0+', 'Next.js 14+'])
            else:
                stack['frontend'].extend(['React 18+', 'TypeScript 5.0+', 'Vite'])
        elif 'mobile' in technologies:
            stack['frontend'].extend(['React Native', 'Expo', 'TypeScript'])

        if 'api' in technologies:
            if complexity == 'high':
                stack['backend'].extend(['Python FastAPI', 'Node.js Express', 'GraphQL'])
            else:
                stack['backend'].extend(['Python FastAPI', 'PostgreSQL', 'Redis'])

        if 'data' in technologies:
            stack['data'].extend(['PostgreSQL 15+', 'Redis 7+', 'pgvector (for AI features)'])

        if 'auth' in technologies:
            stack['backend'].append('OAuth2/JWT authentication')

        if 'cloud' in technologies:
            stack['infrastructure'].extend(['AWS/GCP/Azure', 'Docker', 'Kubernetes'])

        if 'ai' in technologies:
            stack['backend'].extend(['OpenAI API', 'LangChain', 'Pinecone'])

        # Testing stack
        stack['testing'].extend(['Jest', 'React Testing Library', 'pytest', 'Playwright'])

        # Deployment
        stack['deployment'].extend(['GitHub Actions', 'Docker', 'Vercel/Netlify'])

        return stack

    def generate_architecture(self, analysis: Dict[str, any]) -> Dict[str, str]:
        """Generate architecture recommendations"""
        technologies = analysis['technologies']
        complexity = analysis['complexity']

        architecture = {}

        if complexity == 'high' and 'api' in technologies:
            architecture['overview'] = 'Microservices architecture with event-driven communication'
            architecture['components'] = 'API Gateway, Service Mesh, Event Bus, CQRS pattern'
        elif 'web' in technologies and 'api' in technologies:
            architecture['overview'] = 'Modern web application with SPA frontend and RESTful API backend'
            architecture['components'] = 'React SPA, FastAPI backend, PostgreSQL database, Redis cache'
        else:
            architecture['overview'] = 'Standard web application architecture'
            architecture['components'] = 'Frontend framework, Backend API, Database, Caching layer'

        return architecture

    def generate_plan_content(self, analysis: Dict[str, any]) -> str:
        """Generate the complete plan content"""
        req_id = analysis['req_id']

        # Load template
        template_path = os.path.join(self.templates_dir, 'plan-template.md')
        if not os.path.exists(template_path):
            template_content = self._get_fallback_template()
        else:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

        # Generate technology stack
        tech_stack = self.generate_tech_stack(analysis)
        architecture = self.generate_architecture(analysis)

        # Replace placeholders
        replacements = {
            '[Same as spec, e.g., REQ-001]': req_id,
            '[High-level technical approach and architecture decisions]': architecture['overview'],
            '[Core Technologies]': self._format_tech_stack(tech_stack),
            '[Describe key components and their relationships]': self._generate_components(analysis),
            '[Database tables, collections, or data structures]': self._generate_data_schema(analysis),
            '[How data moves through the system]': self._generate_data_flow(analysis),
            '[How to handle data transitions]': self._generate_migration_strategy(analysis),
            '[JSON schemas or examples]': self._generate_api_contracts(analysis),
            '[Authentication & Authorization]': self._generate_security_architecture(analysis),
            '[Scalability]': self._generate_scalability_strategy(analysis),
            '[Optimization Targets]': self._generate_performance_targets(analysis),
            '[Unit Tests]': self._generate_unit_testing(analysis),
            '[Integration Tests]': self._generate_integration_testing(analysis),
            '[End-to-End Tests]': self._generate_e2e_testing(analysis),
            '[Environment Strategy]': self._generate_environments(analysis),
            '[How to safely rollback if issues arise]': self._generate_rollback_plan(analysis),
            '[What to measure]': self._generate_monitoring_strategy(analysis),
            '[Risk: [Description]]': self._generate_risk_mitigation(analysis),
            '[Technical Metrics]': self._generate_tech_metrics(analysis),
            '[Business Metrics]': self._generate_business_metrics(analysis),
            '[Phase 1: Foundation [X weeks]]': self._generate_timeline_phase1(analysis),
            '[Phase 2: Core Features [X weeks]]': self._generate_timeline_phase2(analysis),
            '[Phase 3: Polish & Launch [X weeks]]': self._generate_timeline_phase3(analysis),
            '[Role]: [X] developers with [specific skills]': self._generate_team_roles(analysis),
            '[List any training or knowledge transfer needed]': self._generate_training_needs(analysis),
            '[Development Cost]': self._generate_cost_estimate(analysis),
            '[Current Date]': datetime.now().strftime('%Y-%m-%d')
        }

        content = template_content
        for placeholder, replacement in replacements.items():
            content = content.replace(f'[{placeholder}]', replacement)

        return content

    def _get_fallback_template(self) -> str:
        """Fallback template if plan-template.md is not found"""
        return """# Implementation Plan

## REQ-ID: [Same as spec, e.g., REQ-001]

## Architecture Overview
[High-level technical approach and architecture decisions]

## Technical Stack
### Core Technologies
- Language: [Core Technologies]
- Framework: [Frameworks and libraries]
- Database: [Database systems]
- Infrastructure: [Infrastructure components]

### Supporting Technologies
- Testing: [Testing frameworks]
- CI/CD: [CI/CD tools]
- Monitoring: [Monitoring solutions]
- Security: [Security tools]

## Component Design
[Describe key components and their relationships]

### Component 1: [Name]
- Purpose: [What it does]
- Interface: [APIs, contracts]
- Dependencies: [What it needs]

### Component 2: [Name]
- Purpose: [What it does]
- Interface: [APIs, contracts]
- Dependencies: [What it needs]

## Data Architecture
### Schema Design
[Database tables, collections, or data structures]

### Data Flow
[How data moves through the system]

### Migration Strategy
[How to handle data transitions]

## API Design
### Endpoints
```
GET    /api/v1/[resource]
POST   /api/v1/[resource]
PUT    /api/v1/[resource]/{id}
DELETE /api/v1/[resource]/{id}
```

### Request/Response Formats
[JSON schemas or examples]

## Security Architecture
### Authentication & Authorization
[Authentication & Authorization]

### Data Protection
- Encryption: [At rest, in transit]
- Privacy: [PII handling, GDPR compliance]

## Performance Strategy
### Scalability
[Scalability]

### Optimization Targets
[Optimization Targets]

## Testing Strategy
### Unit Tests
[Unit Tests]

### Integration Tests
[Integration Tests]

### End-to-End Tests
[End-to-End Tests]

## Deployment Strategy
### Environment Strategy
[Environment Strategy]

### Rollback Plan
[How to safely rollback if issues arise]

### Monitoring & Observability
- Metrics: [What to measure]
- Logging: [Log levels, aggregation]
- Alerting: [When to alert]

## Risk Mitigation
### Technical Risks
- Risk: [Description]
  - Mitigation: [Strategy]
  - Contingency: [Plan B]

### Operational Risks
- Risk: [Description]
  - Mitigation: [Strategy]
  - Contingency: [Plan B]

## Success Metrics
### Technical Metrics
- [ ] Code coverage: [X]%
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] Accessibility compliance verified

### Business Metrics
- [ ] Feature adoption rate: [X]%
- [ ] User satisfaction score: [X]/5
- [ ] Error rate: < [X]%

## Timeline & Milestones
### Phase 1: Foundation [X weeks]
- [ ] Component 1 implementation
- [ ] Basic testing framework
- [ ] CI/CD pipeline setup

### Phase 2: Core Features [X weeks]
- [ ] Component 2 implementation
- [ ] Integration testing
- [ ] Performance optimization

### Phase 3: Polish & Launch [X weeks]
- [ ] End-to-end testing
- [ ] Documentation completion
- [ ] Production deployment

## Team Requirements
### Skills Needed
- [Role]: [X] developers with [specific skills]
- [Role]: [X] specialists in [area]

### Training Required
- [List any training or knowledge transfer needed]

## Cost Estimation
### Development Cost
- Labor: [X] developer-weeks
- Infrastructure: [X] months of cloud costs
- Tools/Licenses: [X] one-time costs

### Operational Cost
- Hosting: [X]/month
- Monitoring: [X]/month
- Support: [X]/month

---
*Generated by Spec Kit v0.0.20 - [Current Date]*"""

    def _format_tech_stack(self, stack: Dict[str, List[str]]) -> str:
        """Format technology stack for template"""
        lines = []
        for category, technologies in stack.items():
            if technologies:
                lines.append(f"### {category.title()}")
                for tech in technologies:
                    lines.append(f"- {tech}")
                lines.append("")
        return "\n".join(lines)

    def _generate_components(self, analysis: Dict[str, any]) -> str:
        """Generate component descriptions"""
        technologies = analysis['technologies']
        components = []

        if 'web' in technologies:
            components.append("""### Frontend Component
- Purpose: User interface and interaction handling
- Interface: React components, state management, API calls
- Dependencies: Backend API, UI component library""")

        if 'api' in technologies:
            components.append("""### Backend API Component
- Purpose: Business logic and data processing
- Interface: RESTful endpoints, GraphQL schema
- Dependencies: Database, authentication service""")

        if 'data' in technologies:
            components.append("""### Data Layer Component
- Purpose: Data persistence and retrieval
- Interface: Repository pattern, ORM
- Dependencies: Database connection, migration tools""")

        if 'auth' in technologies:
            components.append("""### Authentication Component
- Purpose: User identity and access control
- Interface: OAuth2 flows, JWT tokens
- Dependencies: User store, external identity providers""")

        return "\n\n".join(components) if components else "Standard component architecture to be defined based on specific requirements."

    def _generate_data_schema(self, analysis: Dict[str, any]) -> str:
        """Generate data schema recommendations"""
        technologies = analysis['technologies']

        if 'data' in technologies:
            return """### Core Tables
- users: User accounts and profiles
- sessions: User sessions and tokens
- audit_log: System activity tracking

### Domain Tables
- [feature]_main: Primary feature entities
- [feature]_metadata: Additional attributes
- [feature]_relationships: Entity connections"""
        else:
            return "Data schema to be defined based on feature requirements."

    def _generate_data_flow(self, analysis: Dict[str, any]) -> str:
        """Generate data flow description"""
        return """1. User requests enter through API endpoints
2. Authentication middleware validates requests
3. Business logic layer processes data
4. Data access layer handles persistence
5. Cache layer serves frequently accessed data
6. Background jobs handle async operations"""

    def _generate_migration_strategy(self, analysis: Dict[str, any]) -> str:
        """Generate migration strategy"""
        return """- Use database migration tools (Alembic, Flyway)
- Implement backward-compatible schema changes
- Test migrations on staging environment first
- Have rollback scripts ready for critical changes"""

    def _generate_api_contracts(self, analysis: Dict[str, any]) -> str:
        """Generate API contract examples"""
        return """### Authentication Endpoints
```json
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

### Resource Endpoints
```json
GET /api/v1/resources
{
  "data": [...],
  "pagination": {...}
}
```"""

    def _generate_security_architecture(self, analysis: Dict[str, any]) -> str:
        """Generate security architecture"""
        if 'auth' in analysis['technologies']:
            return """- OAuth2 Authorization Code flow for web clients
- JWT tokens with RS256 signing
- Role-based access control (RBAC)
- API rate limiting and DDoS protection"""
        else:
            return """- Basic authentication mechanisms
- Input validation and sanitization
- HTTPS everywhere
- Security headers (CSP, HSTS, etc.)"""

    def _generate_scalability_strategy(self, analysis: Dict[str, any]) -> str:
        """Generate scalability strategy"""
        complexity = analysis['complexity']

        if complexity == 'high':
            return """- Horizontal scaling with load balancers
- Database read replicas and sharding
- CDN for static assets
- Microservices architecture for independent scaling"""
        else:
            return """- Vertical scaling for initial deployment
- Database indexing and query optimization
- Caching layer for performance
- Monitoring for scaling triggers"""

    def _generate_performance_targets(self, analysis: Dict[str, any]) -> str:
        """Generate performance targets"""
        return """- API response time: < 200ms for 95% of requests
- Page load time: < 2 seconds
- Database query time: < 50ms average
- Error rate: < 0.1%"""

    def _generate_unit_testing(self, analysis: Dict[str, any]) -> str:
        """Generate unit testing strategy"""
        return """- Test coverage target: 80% minimum
- Unit tests for all business logic functions
- Mock external dependencies
- Run tests on every commit"""

    def _generate_integration_testing(self, analysis: Dict[str, any]) -> str:
        """Generate integration testing strategy"""
        return """- API contract testing
- Database integration tests
- External service mocking
- Component interaction validation"""

    def _generate_e2e_testing(self, analysis: Dict[str, any]) -> str:
        """Generate E2E testing strategy"""
        return """- Critical user journey testing
- Cross-browser compatibility
- Mobile responsiveness testing
- Performance testing under load"""

    def _generate_environments(self, analysis: Dict[str, any]) -> str:
        """Generate environment strategy"""
        return """- Development: Local development with hot reload
- Staging: Production-like environment for testing
- Production: Multi-region deployment with failover"""

    def _generate_rollback_plan(self, analysis: Dict[str, any]) -> str:
        """Generate rollback plan"""
        return """- Blue-green deployment strategy
- Database backup before migrations
- Feature flags for gradual rollout
- Automated rollback scripts ready"""

    def _generate_monitoring_strategy(self, analysis: Dict[str, any]) -> str:
        """Generate monitoring strategy"""
        return """- Application metrics (response times, error rates)
- Infrastructure monitoring (CPU, memory, disk)
- Business metrics (user engagement, conversion)
- Alert thresholds with escalation procedures"""

    def _generate_risk_mitigation(self, analysis: Dict[str, any]) -> str:
        """Generate risk mitigation strategies"""
        risks = analysis['risks']
        mitigations = []

        for risk_type, risk_list in risks.items():
            for risk in risk_list:
                if risk_type == 'technical':
                    mitigations.append(f"""- Risk: {risk}
  - Mitigation: Prototype critical components early
  - Contingency: Alternative technology evaluation""")
                else:
                    mitigations.append(f"""- Risk: {risk}
  - Mitigation: Regular stakeholder communication
  - Contingency: MVP approach with iterative delivery""")

        return "\n\n".join(mitigations) if mitigations else """- Risk: Standard implementation risks
  - Mitigation: Regular code reviews and testing
  - Contingency: Additional development time buffer"""

    def _generate_tech_metrics(self, analysis: Dict[str, any]) -> str:
        """Generate technical success metrics"""
        return """- [ ] Code coverage: > 80%
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] Zero critical vulnerabilities
- [ ] Accessibility compliance: WCAG 2.1 AA"""

    def _generate_business_metrics(self, analysis: Dict[str, any]) -> str:
        """Generate business success metrics"""
        return """- [ ] Feature adoption rate: > 70%
- [ ] User satisfaction score: > 4.0/5
- [ ] Error rate: < 1%
- [ ] Support ticket reduction: > 30%"""

    def _generate_timeline_phase1(self, analysis: Dict[str, any]) -> str:
        """Generate Phase 1 timeline"""
        complexity = analysis['complexity']
        weeks = '4-6' if complexity == 'high' else '2-3'

        return f"""### Phase 1: Foundation [{weeks} weeks]
- [ ] Development environment setup
- [ ] Core architecture components
- [ ] Basic testing framework
- [ ] CI/CD pipeline configuration"""

    def _generate_timeline_phase2(self, analysis: Dict[str, any]) -> str:
        """Generate Phase 2 timeline"""
        complexity = analysis['complexity']
        weeks = '6-8' if complexity == 'high' else '3-4'

        return f"""### Phase 2: Core Features [{weeks} weeks]
- [ ] Primary feature implementation
- [ ] Integration testing
- [ ] Performance optimization
- [ ] Security implementation"""

    def _generate_timeline_phase3(self, analysis: Dict[str, any]) -> str:
        """Generate Phase 3 timeline"""
        complexity = analysis['complexity']
        weeks = '4-6' if complexity == 'high' else '2-3'

        return f"""### Phase 3: Polish & Launch [{weeks} weeks]
- [ ] End-to-end testing
- [ ] Documentation completion
- [ ] Production deployment
- [ ] Monitoring setup"""

    def _generate_team_roles(self, analysis: Dict[str, any]) -> str:
        """Generate team role requirements"""
        technologies = analysis['technologies']
        roles = []

        if 'web' in technologies:
            roles.append("- Frontend Developer: 1-2 developers with React/TypeScript experience")
        if 'api' in technologies:
            roles.append("- Backend Developer: 1-2 developers with Python/Node.js experience")
        if 'data' in technologies:
            roles.append("- Database Developer: 1 developer with SQL/NoSQL experience")
        if 'auth' in technologies:
            roles.append("- Security Specialist: 1 developer with authentication experience")
        if 'ai' in technologies:
            roles.append("- AI/ML Engineer: 1 specialist with relevant experience")

        roles.append("- QA Engineer: 1 engineer with testing expertise")
        roles.append("- DevOps Engineer: 1 engineer with deployment experience")

        return "\n".join(roles)

    def _generate_training_needs(self, analysis: Dict[str, any]) -> str:
        """Generate training requirements"""
        technologies = analysis['technologies']
        training = []

        if 'ai' in technologies:
            training.append("- AI/ML framework training (OpenAI API, LangChain)")
        if 'cloud' in technologies:
            training.append("- Cloud platform certification (AWS, GCP, Azure)")
        if 'microservices' in str(analysis).lower():
            training.append("- Microservices architecture patterns")

        if not training:
            training.append("- Project-specific technology stack familiarization")

        return "\n- ".join([""] + training)

    def _generate_cost_estimate(self, analysis: Dict[str, any]) -> str:
        """Generate cost estimates"""
        complexity = analysis['complexity']

        if complexity == 'high':
            return """### Development Cost
- Labor: 16-24 developer-weeks
- Infrastructure: 6 months of cloud costs ($5K-10K)
- Tools/Licenses: $2K-5K one-time costs"""
        elif complexity == 'medium':
            return """### Development Cost
- Labor: 8-12 developer-weeks
- Infrastructure: 3 months of cloud costs ($2K-5K)
- Tools/Licenses: $1K-2K one-time costs"""
        else:
            return """### Development Cost
- Labor: 4-6 developer-weeks
- Infrastructure: 2 months of cloud costs ($1K-2K)
- Tools/Licenses: $500-1K one-time costs"""

    def create_plan_file(self, additional_context: str = "") -> str:
        """Create the plan file and return the path"""
        # Find latest spec
        spec_path = self.find_latest_spec()
        if not spec_path:
            raise ValueError("No spec.md file found. Run /specify first.")

        # Analyze spec
        analysis = self.analyze_spec(spec_path)

        # Add additional context if provided
        if additional_context:
            analysis['additional_context'] = additional_context

        # Generate content
        content = self.generate_plan_content(analysis)

        # Apply quality enhancement
        print("----- Applying quality enhancement to implementation plan...")
        content = self.quality_enhancer.enhance_quality(content, {
            'command': 'plan',
            'spec_path': spec_path,
            'stage': 'planning',
            'additional_context': additional_context
        })

        # Create plan file in same directory as spec
        spec_dir = os.path.dirname(spec_path)
        plan_path = os.path.join(spec_dir, 'plan.md')

        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"----- Implementation plan created: {plan_path}")
        return plan_path

def main():
    """Main CLI entry point"""
    additional_context = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else ''

    try:
        processor = PlanProcessor()
        plan_path = processor.create_plan_file(additional_context)

        print("----- Implementation plan created successfully!")
        print(f"----- Next: Run /tasks to break down into actionable items")
        print(f"----- File: {plan_path}")

    except Exception as e:
        print(f"----- Error creating implementation plan: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
