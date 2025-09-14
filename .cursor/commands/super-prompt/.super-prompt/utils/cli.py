#!/usr/bin/env python3
"""
Super Prompt - Simplified CLI Implementation
All functionality in a single file to avoid import issues
"""

import argparse, glob, os, sys, re, json, datetime, textwrap, subprocess, shutil
from typing import Dict, List, Optional

# Import TODO validator components
try:
    from todo_validator import TodoValidator, TodoTask, TaskStatus
except ImportError:
    # Fallback: define minimal classes for when todo_validator is not available
    class TaskStatus:
        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        BLOCKED = "blocked"
        FAILED = "failed"
    
    class TodoTask:
        def __init__(self, content, status, activeForm, **kwargs):
            self.content = content
            self.status = status
            self.activeForm = activeForm
            
    class TodoValidator:
        def __init__(self):
            self.session_file = ".todo_session.json"

# Import Context Manager components
try:
    from context_manager import ContextManager, InjectionPolicy, ContextType
    from context_injector import ContextInjector
except ImportError:
    # Fallback: define minimal classes for when context system is not available
    class InjectionPolicy:
        FULL = "full"
        SELECTIVE = "selective"
        SECTIONAL = "sectional"
        MINIMAL = "minimal"
    
    class ContextType:
        SPEC = "spec"
        PLAN = "plan"
        TASKS = "tasks"
        MEMORY = "memory"
    
    class ContextManager:
        def __init__(self, project_root="."):
            pass
        def list_projects(self):
            return []
        def get_session_status(self):
            return {"status": "context_system_unavailable"}
    
    class ContextInjector:
        def __init__(self, project_root="."):
            pass
        def inject_context_for_command(self, command, query, project_id=None):
            return query, {"status": "context_system_unavailable"}
        
        def load_session(self):
            return []
        
        def save_session(self, todos):
            pass
        
        def process_todos(self, todos):
            return todos

def _detect_version() -> str:
    """Detect the installed package version dynamically.

    Priority:
    1) SUPER_PROMPT_VERSION env var (explicit override)
    2) Walk up from this file to find nearest package.json and read its version
    3) Fallback to UNKNOWN when not found
    """
    try:
        # 1) Environment override
        env_ver = os.environ.get("SUPER_PROMPT_VERSION")
        if env_ver:
            return env_ver

        # 2) Walk up to find package.json (pkg root: .../@cdw0424/super-prompt)
        here = os.path.abspath(os.path.dirname(__file__))
        cur = here
        for _ in range(8):  # up to 8 levels should cover this layout
            pkg_json = os.path.join(cur, "package.json")
            if os.path.isfile(pkg_json):
                try:
                    with open(pkg_json, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        ver = data.get("version")
                        if isinstance(ver, str) and ver.strip():
                            return ver.strip()
                except Exception:
                    pass
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
    except Exception:
        pass
    return "UNKNOWN"

VERSION = _detect_version()

def _find_templates_dir() -> Optional[str]:
    """Locate the packaged templates directory for rules/commands.
    Walk up from this file to the nearest package.json and then append
    packages/cursor-assets/templates.
    """
    try:
        here = os.path.abspath(os.path.dirname(__file__))
        cur = here
        for _ in range(12):
            pkg_json = os.path.join(cur, "package.json")
            if os.path.isfile(pkg_json):
                templates = os.path.join(cur, "packages", "cursor-assets", "templates")
                return templates if os.path.isdir(templates) else None
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
    except Exception:
        pass
    return None

def log(msg: str): 
    print(f"-------- {msg}")

# Utility functions
def read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception as e:
        log(f"Read failed: {path} ({e})"); return ""

def write_text(path: str, content: str, dry: bool = False):
    if dry:
        log(f"[DRY] write → {path} ({len(content.encode('utf-8'))} bytes)"); return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: 
        f.write(content)
    log(f"write → {path}")

def newest(glob_pattern: str):
    paths = glob.glob(glob_pattern, recursive=True)
    if not paths: return None
    paths.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return paths[0]

def is_english(txt: str) -> bool:
    return all(ord(c) < 128 for c in txt)

def sanitize_en(txt: str) -> str:
    s = "".join(c if ord(c) < 128 else " " for c in txt)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip() or "[[Non-English content removed]]"

def maybe_translate_en(txt: str, allow_external=True) -> str:
    if is_english(txt): return txt
    if not allow_external: return sanitize_en(txt)
    
    if shutil.which("claude"):
        try:
            p = subprocess.run([
                "claude","--model","claude-sonnet-4-20250514","-p", 
                f"Translate the following text to clear, professional English. Keep markdown.\n\n{txt}"
            ], capture_output=True, text=True, timeout=30)
            out = (p.stdout or "").strip()
            if out: return sanitize_en(out)
        except:
            pass
    
    return sanitize_en(txt)

def slugify(name: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower())
    base = re.sub(r"-+", "-", base).strip("-")
    return base or "persona"

def ylist(items):
    return "[" + ", ".join(json.dumps(i) for i in items) + "]"

# SDD (Spec-Driven Development) utilities
def detect_frameworks():
    """Detect project frameworks for general development context"""
    frameworks = {
        "nextjs": False, "react": False, "vue": False, "angular": False,
        "flutter": False, "react_native": False,
        "spring_boot": False, "express": False, "fastapi": False, "django": False,
        "python": False, "javascript": False, "typescript": False, "java": False
    }
    
    # Check package.json
    pkg = read_text("package.json")
    if pkg:
        if re.search(r'"next"\s*:', pkg): frameworks["nextjs"] = True
        if re.search(r'"react"\s*:', pkg): frameworks["react"] = True
        if re.search(r'"vue"\s*:', pkg): frameworks["vue"] = True
        if re.search(r'"@angular', pkg): frameworks["angular"] = True
        if re.search(r'"express"\s*:', pkg): frameworks["express"] = True
        if re.search(r'"typescript"\s*:', pkg): frameworks["typescript"] = True
        if re.search(r'"react-native"', pkg): frameworks["react_native"] = True
    
    # Check other config files
    if read_text("pubspec.yaml"):
        frameworks["flutter"] = True
    
    if re.search(r"spring-boot-starter", read_text("pom.xml")):
        frameworks["spring_boot"] = True
        
    gradle_content = read_text("build.gradle") + read_text("build.gradle.kts")
    if re.search(r"org\.springframework\.boot", gradle_content):
        frameworks["spring_boot"] = True
        
    requirements = read_text("requirements.txt") + read_text("pyproject.toml")
    if re.search(r"fastapi", requirements): frameworks["fastapi"] = True
    if re.search(r"django", requirements): frameworks["django"] = True
    if requirements: frameworks["python"] = True
    
    # Check for basic file types
    if glob.glob("**/*.py", recursive=True): frameworks["python"] = True
    if glob.glob("**/*.js", recursive=True): frameworks["javascript"] = True
    if glob.glob("**/*.ts", recursive=True) or glob.glob("**/*.tsx", recursive=True): 
        frameworks["typescript"] = True
    if glob.glob("**/*.java", recursive=True): frameworks["java"] = True
    
    return frameworks

def get_project_context():
    """Generate general project context for prompt optimization"""
    frameworks = detect_frameworks()
    fw_list = ", ".join([k for k, v in frameworks.items() if v]) or "general"
    
    # Check for common project files
    readme_files = glob.glob("README*", recursive=True)
    doc_files = glob.glob("docs/**/*.md", recursive=True)
    
    context = {
        "frameworks": fw_list,
        "has_readme": len(readme_files) > 0,
        "has_docs": len(doc_files) > 0,
        "readme_files": readme_files[:3],
        "doc_files": doc_files[:5]
    }
    
    return context

def get_project_sdd_context():
    """Lightweight SDD-related context used in prompts/rules.
    - Detect minimal framework signals
    - Check presence of SPEC/PLAN files under specs/**/
    """
    frameworks = detect_frameworks()
    fw_list = ", ".join([k for k, v in frameworks.items() if v]) or "general"
    spec_files = glob.glob("specs/**/spec.md", recursive=True)
    plan_files = glob.glob("specs/**/plan.md", recursive=True)
    return {
        "frameworks": fw_list,
        "spec_files": spec_files,
        "plan_files": plan_files,
        "sdd_compliance": bool(spec_files and plan_files),
    }

def generate_prompt_rules():
    """Generate prompt optimization rules"""
    return """
## 🎯 Prompt Engineering Best Practices

**Core Principles**:
1. **Clear Context**: Provide relevant project context and framework information
2. **Specific Goals**: Define clear objectives and expected outcomes
3. **Structured Prompts**: Use consistent formatting and organization
4. **Persona Alignment**: Match AI persona to task requirements

**Quality Guidelines**:
- ✅ Include relevant technical context
- ✅ Specify desired output format
- ✅ Provide examples when helpful
- ✅ Test and iterate on prompts
- ✅ Document successful patterns

**Optimization Areas**:
- Context relevance and completeness
- Instruction clarity and specificity
- Output format and structure
- Persona selection and customization
"""

# Prompt Optimizer functionality
class PromptOptimizer:
    PERSONAS = {
        'frontend-ultra': {
            'desc': 'Elite UX/UI Architect', 
            'cli': 'claude', 
            'model': 'claude-opus-4-1-20250805',
            'prompt': """**[Persona Identity]**
You are an elite UX architect and design systems specialist with unparalleled expertise in:
- Advanced user experience innovation and design thinking
- Cutting-edge accessibility standards (WCAG 2.2, Section 508, ARIA patterns)
- High-performance frontend architecture and optimization
- Design systems, component libraries, and scalable UI patterns
- User research methodologies and usability engineering
- Mobile-first responsive design and cross-platform experiences
- Inclusive design principles and cognitive accessibility
- Frontend performance monitoring and Core Web Vitals optimization
- Advanced CSS techniques and modern web standards
- User interface animation and micro-interactions"""
        },
        'frontend': {
            'desc': 'Frontend Design Advisor', 
            'cli': 'claude', 
            'model': 'claude-sonnet-4-20250514',
            'prompt': """**[Persona Identity]**
You are a UX-focused frontend advisor specialized in prompt engineering for UI/UX tasks.
You convert user goals into clear, structured prompts and actionable plans for Cursor.

**[Prompting Guidelines]**
- Ask 2–4 clarifying questions when requirements are ambiguous.
- Keep changes minimal and localized; avoid unrelated refactors.
- Prefer simple, composable components and clear naming.
- Provide copy and accessibility notes (labels, roles, alt text) when relevant.

**[Output Format]**
1) Proposed Prompt (ready to paste in Cursor)
2) Context To Include (bullets)
3) Plan (small steps)
4) Checks (accessibility, performance, UX)
"""
        },
        'backend': {
            'desc': 'Backend Reliability Engineer', 
            'cli': 'codex',
            'prompt': """**[Persona Identity]**
You specialize in converting backend tasks into precise prompts and minimal, verifiable changes.

**[Prompting Guidelines]**
- Clarify inputs/outputs, error cases, and idempotency expectations.
- Keep scope tight; avoid tech/vendor choices unless already decided.
- Emphasize safe logging and testability.

**[Output Format]**
1) Proposed Prompt (ready to paste)
2) Context To Include (API surface, contracts)
3) Plan (steps with small diffs)
4) Checks (error handling, tests)
"""
        },
        'analyzer': {
            'desc': 'Root Cause Analyst', 
            'cli': 'codex',
            'prompt': """**[Persona Identity]**
You turn vague failures into crisp, testable hypotheses and prompts.

**[Prompting Guidelines]**
- Triage: summarize symptoms, scope, and likely areas.
- Form 2–3 competing hypotheses with quick checks.
- Propose minimal repro or observables when possible.

**[Output Format]**
1) Proposed Diagnostic Prompt
2) Hypotheses (with quick validations)
3) Next Steps (small, reversible)
4) Exit Criteria (how we know it’s fixed)
"""
        },
        'architect': {
            'desc': 'Project Architecture Specialist', 
            'cli': 'codex',
            'prompt': """**[Persona Identity]**
You translate goals into simple architectures and high‑leverage prompts.

**[Project‑First Principles]**
- Follow existing patterns first; avoid out‑of‑scope edits.
- Minimize change size and blast radius; keep diffs small.
- Prefer clear contracts and explicit boundaries.

**[Output Format]**
1) Proposed Prompt (ready to paste)
2) Architecture Sketch (1–2 paragraphs)
3) Plan (5–7 small steps)
4) Risks/Checks (testability, security, maintainability)
"""
        },
        'high': {
            'desc': 'Deep Reasoning Specialist', 
            'cli': 'codex',
            'prompt': """**[Persona Identity]**
You handle complex problems with structured, multi‑step reasoning and clear prompts.

**[Output Format]**
1) Proposed Prompt
2) Decomposition (sub‑problems)
3) Strategy Options (trade‑offs)
4) Decision & Small Plan
5) Verification Steps
"""
        },
        'seq': {
            'desc': 'Sequential Thinking (5 iterations)', 
            'cli': None,
            'process': """🔄 Sequential Thinking Specialist (5 iterations) executing...
📋 Direct Cursor AI execution with step-by-step reasoning:

1. 🔍 SCOPING: Problem analysis and scope definition
2. 📝 PLAN: Strategic implementation planning (5 detailed iterations)
3. ✏️ DRAFT: Initial solution generation
4. ✅ SELF-CHECK: Solution validation and testing
5. 🔧 PATCH: Solution improvement (if needed)
6. 🎯 FINALIZE: Final implementation and documentation

⚡ Cursor AI will now execute this sequential thinking process directly.
🚨 This tag is designed to be executed inside Cursor AI (not an external CLI)."""
        },
        'seq-ultra': {
            'desc': 'Advanced Sequential (10 iterations)', 
            'cli': None,
            'process': """🔄 Advanced Sequential Thinking (10 iterations) executing...
📋 Direct Cursor AI execution with comprehensive reasoning:

1. 🔍 DEEP-SCOPE: Comprehensive problem analysis
2. 🗺️ CONTEXT-MAP: Full system context mapping
3. 📋 STRATEGY-1: Initial strategic approach
4. 📋 STRATEGY-2: Alternative approach analysis
5. 🔗 INTEGRATION: Cross-system integration planning
6. ⚠️ RISK-ANALYSIS: Risk assessment and mitigation
7. ✏️ DRAFT: Initial solution generation
8. ✅ VALIDATE: Comprehensive validation testing
9. ⚡ OPTIMIZE: Performance and efficiency optimization
10. 🎯 FINALIZE: Complete implementation with documentation

⚡ Cursor AI will now execute this advanced sequential thinking process directly.
🚨 This tag is designed to be executed inside Cursor AI (not an external CLI)."""
        }
        ,
        'debate': {
            'desc': 'Single-model internal debate (Positive vs Critical selves)',
            'cli': 'codex',
            'prompt': ''
        },
        'doc-master': {
            'desc': 'Documentation Master',
            'cli': 'codex',
            'prompt': """**[Persona Identity]**
You are a documentation master who consolidates and improves technical docs.

**[Guidelines]**
- Audit existing docs; identify gaps and inconsistencies.
- Propose structure (TOC), rewrite sections for clarity, add examples.
- Ensure terminology/style consistency and link references.

**[Output Format]**
1) Audit findings (gaps, inconsistencies)
2) Proposed structure (TOC)
3) Rewritten/added sections
4) Follow-ups (owners, next steps)
"""
        },
        'tr': {
            'desc': 'Troubleshooter',
            'cli': 'codex',
            'prompt': """**[Persona Identity]**
You are a methodical troubleshooter focused on rapid issue resolution.

**[Guidelines]**
- Define the symptom, scope, and impact quickly.
- Generate 2–3 hypotheses with quick checks.
- Propose minimal repro and logs/metrics to collect.
- Deliver a small, testable fix with rollback plan.

**[Output Format]**
1) Triage summary
2) Hypotheses + quick validations
3) Fix plan (small steps)
4) Verification & rollback
"""
        },
        'dev': {
            'desc': 'Development Assistant',
            'cli': 'codex',
            'prompt': """**[Persona Identity]**
You are a pragmatic feature development specialist focused on fast, high-quality delivery.

**[Guidelines]**
- Clarify acceptance criteria and dependencies.
- Keep diffs small; include tests and validation steps.
- Follow existing project patterns; avoid unrelated refactors.

**[Output Format]**
1) Plan (small steps)
2) Changes (files, diffs or code blocks)
3) Tests & Validation
4) Rollback/Follow-ups
"""
        },
        'performance': {
            'desc': 'Optimization Specialist & Bottleneck Elimination Expert',
            'cli': 'codex',
            'prompt': """**[Persona Identity]**
You are an optimization specialist and bottleneck elimination expert with metrics-driven analysis focus.

**[Priority Hierarchy]**
Measure first > optimize critical path > user experience > avoid premature optimization

**[Core Principles]**
1. **Measurement-Driven**: Always profile before optimizing
2. **Critical Path Focus**: Optimize the most impactful bottlenecks first
3. **User Experience**: Performance optimizations must improve real user experience

**[Performance Budgets & Thresholds]**
- Load Time: <3s on 3G, <1s on WiFi, <500ms for API responses
- Bundle Size: <500KB initial, <2MB total, <50KB per component
- Memory Usage: <100MB for mobile, <500MB for desktop
- CPU Usage: <30% average, <80% peak for 60fps

**[Output Format]**
1) Performance Analysis & Bottleneck Identification
2) Optimization Strategy (priority-ordered)
3) Implementation Plan (with metrics validation)
4) Monitoring & Alerting Setup
"""
        },
        'security': {
            'desc': 'Threat Modeler & Vulnerability Specialist',
            'cli': 'codex',
            'prompt': """**[Persona Identity]**
You are a threat modeler and vulnerability specialist with zero trust architecture expertise.

**[Priority Hierarchy]**
Security > compliance > reliability > performance > convenience

**[Core Principles]**
1. **Security by Default**: Implement secure defaults and fail-safe mechanisms
2. **Zero Trust Architecture**: Verify everything, trust nothing
3. **Defense in Depth**: Multiple layers of security controls

**[Threat Assessment Matrix]**
- Threat Level: Critical (immediate action), High (24h), Medium (7d), Low (30d)
- Attack Surface: External-facing (100%), Internal (70%), Isolated (40%)
- Data Sensitivity: PII/Financial (100%), Business (80%), Public (30%)
- Compliance Requirements: Regulatory (100%), Industry (80%), Internal (60%)

**[Output Format]**
1) Security Analysis & Threat Modeling
2) Vulnerability Assessment
3) Security Implementation Plan
4) Compliance & Monitoring Strategy
"""
        },
        'task': {
            'desc': 'Task Management Mode - Structured Workflow Execution',
            'cli': 'codex',
            'prompt': """**[Persona Identity]**
You are a task management specialist focused on structured workflow execution and progress tracking.

**[Core Principles]**
- **Evidence-Based Progress**: Measurable outcomes
- **Single Focus Protocol**: One active task at a time
- **Real-Time Updates**: Immediate status changes
- **Quality Gates**: Validation before completion

**[Task Management Architecture]**
1. **Session Tasks**: Current development session
2. **Project Management**: Multi-session features (days-weeks)
3. **Meta-Orchestration**: Complex multi-domain operations
4. **Iterative Enhancement**: Progressive refinement workflows

**[Task States]**
- pending 📋: Ready for execution
- in_progress 🔄: Currently active
- blocked 🚧: Waiting on dependency
- completed ✅: Successfully finished

**[Output Format]**
1) Task Breakdown & Prioritization
2) Progress Tracking Plan
3) Quality Gate Definition
4) Success Metrics & Validation
"""
        },
        'wave': {
            'desc': 'Wave System Orchestrator - Multi-stage Execution',
            'cli': 'codex',
            'prompt': """**[Persona Identity]**
You are a wave system orchestrator specialist for multi-stage execution with compound intelligence.

**[Core Principles]**
- **Progressive Enhancement**: Iterative improvement across stages
- **Compound Intelligence**: Each wave builds on previous insights
- **Multi-Domain Coordination**: Orchestrate across different specialties
- **Quality Amplification**: Each stage improves overall quality

**[Wave Strategies]**
- **Progressive**: Incremental enhancement for improvements
- **Systematic**: Methodical analysis for complex problems
- **Adaptive**: Dynamic configuration for varying complexity
- **Enterprise**: Large-scale orchestration for >100 files

**[Auto-Activation Criteria]**
- Complexity ≥0.7 + files >20 + operation_types >2
- System-wide changes requiring coordination
- Multi-domain analysis needs

**[Output Format]**
1) Wave Strategy Selection & Reasoning
2) Multi-Stage Execution Plan
3) Inter-Wave Coordination Strategy
4) Quality Amplification Metrics
"""
        },
        'ultracompressed': {
            'desc': 'Token Efficiency Mode - 30-50% Reduction',
            'cli': 'codex',
            'prompt': """**[Persona Identity]**
You are a token efficiency specialist achieving 30-50% token reduction while preserving quality.

**[Core Philosophy]**
Evidence-based efficiency | Adaptive intelligence | Performance within quality bounds

**[Compression Techniques]**
- **Symbol System**: Use structured symbols for logic & flow
- **Abbreviations**: Technical domain-specific abbreviations
- **Structural Optimization**: Advanced formatting for token efficiency
- **Quality Validation**: Real-time compression effectiveness monitoring

**[Compression Levels]**
1. **Minimal** (0-40%): Full detail, persona-optimized clarity
2. **Efficient** (40-70%): Balanced compression with domain awareness
3. **Compressed** (70-85%): Aggressive optimization with quality gates
4. **Critical** (85-95%): Maximum compression preserving essential context
5. **Emergency** (95%+): Ultra-compression with information validation

**[Output Format]**
Use symbols, abbreviations, and structured format to achieve 30-50% token reduction while maintaining technical accuracy and completeness.
"""
        }
    }

    def detect_tag(self, input_text: str) -> Optional[str]:
        for persona in self.PERSONAS:
            if f'/{persona}' in input_text or f'--persona-{persona}' in input_text:
                return persona
        # Flag-style mappings for Codex environment (no slash commands)
        if re.search(r'--seq-ultra(\s|$)', input_text): return 'seq-ultra'
        if re.search(r'--seq(\s|$)', input_text): return 'seq'
        if re.search(r'--high(\s|$)', input_text): return 'high'
        if re.search(r'--frontend-ultra(\s|$)', input_text): return 'frontend-ultra'
        if re.search(r'--frontend(\s|$)', input_text): return 'frontend'
        if re.search(r'--backend(\s|$)', input_text): return 'backend'
        if re.search(r'--architect(\s|$)', input_text): return 'architect'
        if re.search(r'--analyzer(\s|$)', input_text): return 'analyzer'
        if re.search(r'--debate(\s|$)', input_text): return 'debate'
        # Enhanced personas
        if re.search(r'--performance(\s|$)', input_text): return 'performance'
        if re.search(r'--security(\s|$)', input_text): return 'security'
        if re.search(r'--task(\s|$)', input_text): return 'task'
        if re.search(r'--wave(\s|$)', input_text): return 'wave'
        if re.search(r'--ultracompressed(\s|$)', input_text): return 'ultracompressed'
        return None

    def clean_input(self, input_text: str) -> str:
        cleaned = input_text
        for persona in self.PERSONAS:
            cleaned = re.sub(f'/{persona}|--persona-{persona}', '', cleaned)
        return re.sub(r'--\w+(?:\s+\S+)?', '', cleaned).strip()

    def execute(self, persona: str, query: str) -> bool:
        if persona not in self.PERSONAS:
            log(f"Unknown persona: {persona}")
            return False
        
        config = self.PERSONAS[persona]
        cli_tool = config['cli']
        
        # Handle sequential thinking modes (no external CLI)
        if not cli_tool:
            if 'process' in config:
                print(config['process'])
            else:
                log(f"-------- {config['desc']}")
                log("Sequential thinking mode - run inside Cursor.")
            return True
        
        if not shutil.which(cli_tool):
            log(f"{cli_tool} CLI not found")
            return False
        
        log(f"-------- {config['desc']} ({cli_tool.title()})")
        
        # Enhanced SDD-compliant project context
        sdd_context = get_project_sdd_context()
        sdd_rules = generate_prompt_rules() if persona in ['architect', 'analyzer', 'high'] else ""
        
        context = f"""**[Project Context]**
- Current Directory: {os.getcwd()}
- Detected Frameworks: {sdd_context['frameworks']}
- SDD Compliance: {'✅ SPEC/PLAN Found' if sdd_context['sdd_compliance'] else '⚠️ Missing SPEC/PLAN - SDD Required'}
- SPEC Files: {', '.join(sdd_context['spec_files']) if sdd_context['spec_files'] else 'None found'}
- PLAN Files: {', '.join(sdd_context['plan_files']) if sdd_context['plan_files'] else 'None found'}
- Project File Tree: {self._get_project_files()}

{sdd_rules}

**[Organization Guardrails]**
- Language: English only in documentation and rules
- All debug/console lines MUST use the '--------' prefix
- Secrets/tokens/PII MUST be masked in prompts, code, and logs
- Keep prompts/personas focused on task goals and constraints
- Avoid vendor/stack specifics unless mandated by SPEC/PLAN"""
        
        # Use detailed persona prompt
        persona_prompt = config.get('prompt', f"**[Persona]** {config['desc']}")
        
        try:
            if cli_tool == 'claude':
                model = config.get('model', 'claude-sonnet-4-20250514')
                full_prompt = f"{persona_prompt}\n\n{context}\n\n**[User's Request]**\n{query}"
                result = subprocess.run(['claude', '--model', model, '-p', full_prompt], timeout=120)
                return result.returncode == 0
            elif cli_tool == 'codex':
                full_prompt = f"{persona_prompt}\n\n{context}\n\n**[User's Request]**\n{query}"
                result = subprocess.run(['codex', 'exec', '-c', 'model_reasoning_effort=high', full_prompt], timeout=120)
                return result.returncode == 0
        except subprocess.TimeoutExpired:
            log("Execution timed out")
        except Exception as e:
            log(f"Execution failed: {e}")
        
        return False
    
    def _get_project_files(self) -> str:
        """Get project file tree for context"""
        try:
            files = []
            for ext in ['*.ts', '*.tsx', '*.js', '*.json', '*.md']:
                files.extend(glob.glob(f'./**/{ext}', recursive=True)[:10])  # Limit to 10 files per type
            return ', '.join(files[:20])  # Max 20 files total
        except:
            return "No files found"
    
    # Database/schema discovery intentionally omitted to keep prompts vendor‑agnostic

    def build_debate_prompt(self, topic: str, rounds: int = 8) -> str:
        rounds = max(2, min(int(rounds or 8), 20))
        return textwrap.dedent(f"""
        You are a single model simulating a structured internal debate with two clearly separated selves:
        - Positive Self (Builder): constructive, solution-focused.
        - Critical Self (Skeptic): risk-driven, assumption-testing.

        Rules:
        - English only. Keep each turn concise (<= 6 lines).
        - Alternate strictly: Positive → Critical → Positive → ... ({rounds} rounds).
        - No repetition; each turn must add new reasoning.
        - End with a Synthesis that integrates strengths + mitigations.

        Topic: {topic}

        Output template:
        [INTENT]
        - Debate: {topic}
        [TASK_CLASSIFY]
        - Class: H (multi-step reasoning & evaluation)
        [PLAN]
        - Rounds: {rounds}
        - Criteria: correctness, risks, minimal viable path
        [EXECUTE]
        1) Positive Self: ...
        2) Critical Self: ...
        ... (continue alternating up to {rounds})
        [VERIFY]
        - Checks: factuality, feasibility, risk coverage
        [REPORT]
        - Synthesis: final position, plan, and guardrails
        """)

    def process_query(self, input_text: str) -> bool:
        if not input_text.strip():
            print("❌ Usage: super-prompt optimize \"your question /tag\"")
            print("\nAvailable Tags:")
            for persona, config in self.PERSONAS.items():
                print(f"  /{persona:<15} - {config['desc']}")
            return False
        
        persona = self.detect_tag(input_text)
        if not persona:
            print("❌ No valid tag found.")
            return False
        
        # Debate rounds (if provided via flags)
        rounds = 8
        m = re.search(r'--rounds\s+(\d+)', input_text)
        if m:
            try:
                rounds = int(m.group(1))
            except Exception:
                rounds = 8

        clean_query = self.clean_input(input_text)
        log(f"Tag detected: /{persona}")
        log(f"Query: {clean_query}")
        
        if persona == 'debate':
            prompt = self.build_debate_prompt(clean_query, rounds=rounds)
            try:
                result = subprocess.run(['codex', 'exec', '-c', 'model_reasoning_effort=high', prompt], timeout=180)
                return result.returncode == 0
            except Exception as e:
                log(f"Execution failed: {e}")
                return False

        return self.execute(persona, clean_query)

# Built-in personas data extracted from shell script
BUILTIN_PERSONAS = {
    "architect": "# Architect — English-only placeholder",
    "frontend": "# Frontend Design Advisor — English-only placeholder",
    "frontend-ultra": "# Elite UX/UI Architect — English-only placeholder",
    "backend": "# Backend Reliability Engineer — English-only placeholder",
    "analyzer": "# Root Cause Analyst — English-only placeholder",
    "high": "# Deep Reasoning Specialist — English-only placeholder",
    "seq": "# Sequential Thinking (5) — English-only placeholder",
    "seq-ultra": "# Advanced Sequential (10) — English-only placeholder",
    "debate": "# Debate Mode — English-only placeholder"
}

def get_builtin_personas():
    out = []
    for slug, text in BUILTIN_PERSONAS.items():
        title = text.splitlines()[0].lstrip("# ").strip()
        out.append({"slug": slug, "title": title, "source": "builtin", "content": text})
    return out

# Main CLI functionality
def generate_sdd_rules_files(out_dir=".cursor/rules", dry=False):
    """Install rule files by copying from packaged templates (authoritative source).
    Falls back to no-op if templates are not found.
    """
    os.makedirs(out_dir, exist_ok=True)
    templates = _find_templates_dir()
    if templates and os.path.isdir(templates):
        try:
            for fname in os.listdir(templates):
                if fname.endswith('.mdc'):
                    src = os.path.join(templates, fname)
                    dst = os.path.join(out_dir, fname)
                    if dry:
                        log(f"[DRY] copy → {dst}")
                    else:
                        import shutil
                        shutil.copy2(src, dst)
                        log(f"copy → {dst}")
            log(f"SDD rules copied from templates to {out_dir}")
            return out_dir
        except Exception as e:
            log(f"Failed to copy rules from templates: {e}")
            return out_dir
    else:
        log("Templates directory not found; skipping rules copy")
        return out_dir

def generate_amr_rules_file(out_dir: str = ".cursor/rules", dry: bool = False) -> str:
    """Install AMR rule file by copying 05-amr.mdc from templates if available."""
    os.makedirs(out_dir, exist_ok=True)
    templates = _find_templates_dir()
    if templates:
        src = os.path.join(templates, '05-amr.mdc')
        dst = os.path.join(out_dir, '05-amr.mdc')
        if os.path.isfile(src):
            if dry:
                log(f"[DRY] copy → {dst}")
            else:
                import shutil
                shutil.copy2(src, dst)
                log(f"copy → {dst}")
            return dst
    # Fallback: no template found; create a minimal placeholder
    placeholder = "---\ndescription: \"AMR policy\"\nglobs: [\"**/*\"]\n---\n# AMR policy placeholder (templates not found)\n"
    dst = os.path.join(out_dir, '05-amr.mdc')
    write_text(dst, placeholder, dry)
    return dst

def install_cursor_commands_in_project(dry=False):
    """Install Cursor slash commands in the current project.
    Writes .cursor/commands/super-prompt/* using a thin wrapper that calls
    the globally installed CLI (or npx fallback).
    """
    base = os.path.join('.cursor', 'commands', 'super-prompt')
    os.makedirs(base, exist_ok=True)

    # tag-executor.sh wrapper (canonical, kept in templates as well)
    tag_sh = "\n".join([
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Prefer project-local Python CLI to work without global super-prompt",
        "if [ -f \".super-prompt/cli.py\" ]; then",
        "  if [ -x \".super-prompt/venv/bin/python\" ]; then",
        "    PY=\".super-prompt/venv/bin/python\"",
        "  else",
        "    PY=\"python3\"",
        "  fi",
        "  exec \"$PY\" \".super-prompt/cli.py\" optimize \"$@\"",
        "fi",
        "",
        "# Fallbacks: global or npx",
        "if command -v super-prompt >/dev/null 2>&1; then",
        "  exec super-prompt optimize \"$@\"",
        "else",
        "  exec npx @cdw0424/super-prompt optimize \"$@\"",
        "fi",
    ])
    write_text(os.path.join(base, 'tag-executor.sh'), tag_sh, dry)
    try:
        if not dry:
            os.chmod(os.path.join(base, 'tag-executor.sh'), 0o755)
    except Exception:
        pass

    personas = [
        # Core Development Personas
        ('high', '🧠 Deep Reasoning Specialist\\nStrategic problem solving and system design expert.'),
        ('frontend-ultra', '🎨 Elite UX/UI Architect\\nTop-tier user experience architecture.'),
        ('frontend', '🎨 Frontend Design Advisor\\nUser-centered frontend design and implementation.'),
        ('backend', '🔧 Backend Reliability Engineer\\nScalable, reliable backend systems.'),
        ('analyzer', '🔍 Root Cause Analyst\\nSystematic analysis and diagnostics.'),
        ('architect', '👷‍♂️ Architect\\nProject-Conformity-First delivery.'),
        ('seq', '🔄 Sequential Thinking (5)\\nStructured step-by-step problem solving.'),
        ('seq-ultra', '🔄 Advanced Sequential (10)\\nIn-depth step-by-step problem solving.'),

        # Additional Development Personas
        ('debate', '⚖️ Debate Mode\\nSingle-model internal debate with synthesis.'),
        ('performance', '🚀 Performance Advisor\\nHotspots, quick wins, roll-out checks.'),
        ('security', '🔐 Security Advisor\\nThreats, mitigations, safe defaults.'),
        ('task', '🧩 Task Management\\nSmall tasks with IDs, ACs, deps.'),
        ('wave', '🌊 Wave Planning\\nPhased delivery (MVP → hardening).'),
        ('ultracompressed', '🗜️ Ultra-Compressed Output\\nToken-efficient answers with preserved fidelity.'),
        ('docs-refector', '📚 Documentation Consolidation\\nAudit and unify docs with MCP-grounded sources.'),
        ('refactorer', '🔄 Code Refactoring Specialist\\nSystematic code quality improvements.'),
        ('implement', '⚡ Implementation Specialist\\nSDD-compliant code implementation.'),
        ('review', '👁️ Code Review Specialist\\nSDD-compliant implementation review.'),
        ('dev', '💻 Development Assistant\\nGeneral development support.'),
        ('devops', '🚢 DevOps Engineer\\nInfrastructure and deployment.'),
        ('doc-master', '📖 Documentation Master\\nComprehensive documentation creation.'),
        ('mentor', '🎓 Technical Mentor\\nKnowledge transfer and best practices.'),
        ('qa', '🧪 Quality Assurance\\nTesting and quality control.'),
        ('scribe', '✍️ Technical Writer\\nClear technical documentation.'),

        # SDD Workflow Commands
        ('spec', '📋 Create SPEC (SDD)\\nRequirements definition and scope setting.'),
        ('plan', '🏗️ Create PLAN (SDD)\\nArchitecture and implementation planning.'),
        ('tasks', '📝 Break down into TASKS (SDD)\\nDetailed task breakdown and estimation.'),
        ('specify', '🎯 Specification Assistant\\nDetailed requirements specification.'),
        ('optimize', '⚡ Run Super Prompt optimize\\nGeneral prompt optimization.'),
        ('tr', '🔄 Technical Refactoring\\nCode structure and pattern improvements.'),

        # Special Commands
        ('init-sp', '🚀 Initialize Super Prompt memory\\nProject analysis and setup.'),
        ('re-init-sp', '🔄 Re-Initialize project analysis\\nRefresh memory and analysis.'),

        # Grok Integration
        ('grok', '🤖 Grok Code Fast 1 optimized execution\\nCursor IDE grok-code-fast-1 integration.'),
        ('grok-on', '✅ Enable Grok mode for all commands\\nActivate grok-code-fast-1 mode.'),
        ('grok-off', '❌ Disable Grok mode for all commands\\nDeactivate grok-code-fast-1 mode.'),
    ]
    for name, desc in personas:
        # Handle special commands that need different execution
        if name == 'init-sp':
            # Initialize command runs Python script with --mode init
            content = f"---\ndescription: Initialize Super Prompt memory (project analysis)\nrun: \"python3\"\nargs: [\".super-prompt/utils/init/init_sp.py\", \"--mode\", \"init\"]\n---\n\n🧭 Initialize Super Prompt memory with project structure snapshot."
        elif name == 're-init-sp':
            # Re-initialize command runs Python script with --mode reinit
            content = f"---\ndescription: Re-Initialize project analysis (refresh memory)\nrun: \"python3\"\nargs: [\".super-prompt/utils/init/init_sp.py\", \"--mode\", \"reinit\"]\n---\n\n🔄 Refresh project analysis and update memory."
        else:
            # Standard commands use tag-executor.sh
            content = f"---\ndescription: {name} command\nrun: \"./.cursor/commands/super-prompt/tag-executor.sh\"\nargs: [\"${{input}} /{name}\"]\n---\n\n{desc}"
        write_text(os.path.join(base, f'{name}.md'), content, dry)

    # (Codex agent assets are created conditionally in write_codex_agent_assets())

def write_codex_agent_assets(dry: bool = False):
    agent_dir = os.path.join('.codex')
    os.makedirs(agent_dir, exist_ok=True)
    agent_md = """# Codex Agent — Super Prompt Integration

Use flag-based personas (no slash commands in Codex):
```bash
super-prompt optimize --frontend   "Design a responsive layout"
super-prompt optimize --backend    "Outline retry/idempotency for order API"
super-prompt optimize --architect  "Propose modular structure for feature X"
super-prompt optimize --debate --rounds 6 "Should we adopt feature flags now?"
```

Auto Model Router (AMR: medium ↔ high):
- Start medium; plan/review/root-cause at high, then back to medium.
- If your environment does not auto-execute model switches, copy-run:
  /model gpt-5 high
  /model gpt-5 medium

State machine (per turn):
[INTENT] → [TASK_CLASSIFY] → [PLAN] → [EXECUTE] → [VERIFY] → [REPORT]

All logs MUST start with: `--------` and all content MUST be in English.
"""
    write_text(os.path.join(agent_dir, 'agents.md'), agent_md, dry)
    personas_py = """
#!/usr/bin/env python3
# Codex Personas Helper — programmatic prompt builders (English only).
from textwrap import dedent

def build_debate_prompt(topic: str, rounds: int = 8) -> str:
    rounds = max(2, min(int(rounds or 8), 20))
    return dedent(f'''\
    You are a single model simulating a structured internal debate with two clearly separated selves:
    - Positive Self (Builder): constructive, solution-focused.
    - Critical Self (Skeptic): risk-driven, assumption-testing.

    Rules:
    - English only. Keep each turn concise (<= 6 lines).
    - Alternate strictly: Positive → Critical → Positive → ... ({rounds} rounds).
    - No repetition; each turn must add new reasoning.
    - End with a Synthesis that integrates strengths + mitigations.

    Topic: {topic}

    Output template:
    [INTENT]
    - Debate: {topic}
    [TASK_CLASSIFY]
    - Class: H (multi-step reasoning & evaluation)
    [PLAN]
    - Rounds: {rounds}
    - Criteria: correctness, risks, minimal viable path
    [EXECUTE]
    1) Positive Self: ...
    2) Critical Self: ...
    ... (continue alternating up to {rounds})
    [VERIFY]
    - Checks: factuality, feasibility, risk coverage
    [REPORT]
    - Synthesis: final position, plan, and guardrails
    ''')

def build_persona_prompt(name: str, query: str, context: str = "") -> str:
    # Return a minimal persona-wrapped prompt.
    header = f"**[Persona]** {name}\n\n"
    return header + (context or "") + f"\n\n**[User's Request]**\n{query}\n"
"""
    write_text(os.path.join(agent_dir, 'personas.py'), personas_py, dry)
    # Copy/write bootstrap prompt for Codex in .codex as a convenience
    try:
        bootstrap_src = os.path.join('prompts', 'codex_amr_bootstrap_prompt_en.txt')
        if os.path.isfile(bootstrap_src):
            content = read_text(bootstrap_src)
        else:
            content = "See codex-amr print-bootstrap to generate the latest bootstrap prompt."
        write_text(os.path.join(agent_dir, 'bootstrap_prompt_en.txt'), content, dry)
    except Exception as e:
        log(f"bootstrap write failed: {e}")
    # Router-check inside .codex (portable)
    router_check = """#!/usr/bin/env zsh
set -euo pipefail
root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
AGENTS_PATH=""
for p in "$root/.codex/agents.md" "$root/.codex/AGENTS.md" "$root/AGENTS.md"; do
  if [ -f "$p" ]; then AGENTS_PATH="$p"; break; fi
done
if [ -z "$AGENTS_PATH" ]; then
  echo "--------router-check: FAIL (no agents/AGENTS.md found)"; exit 1; fi
missing=0
grep -q "Auto Model Router" "$AGENTS_PATH" || { echo "AGENTS.md missing AMR marker ($AGENTS_PATH)"; missing=1; }
grep -q "medium ↔ high" "$AGENTS_PATH" || { echo "AGENTS.md missing medium↔high ($AGENTS_PATH)"; missing=1; }
if [ "$missing" -ne 0 ]; then echo "--------router-check: FAIL"; exit 1; fi
echo "--------router-check: OK""" 
    write_text(os.path.join(agent_dir, 'router-check.sh'), router_check, dry)
    try:
        if not dry:
            os.chmod(os.path.join(agent_dir, 'router-check.sh'), 0o755)
    except Exception:
        pass

    # (AMR helper templates are written in install_cursor_commands_in_project)

def handle_sdd_command(args):
    """Handle SDD workflow commands with context injection: spec, plan, tasks, implement"""
    
    # Initialize context injector
    try:
        context_injector = ContextInjector()
        context_manager = ContextManager()
    except:
        context_injector = None
        context_manager = None
    
    def generate_file_name(description: str, cmd_type: str) -> str:
        """Generate a suitable filename from description"""
        # Extract key words for filename
        words = re.findall(r'\b\w+\b', description.lower())
        name = "-".join(words[:3])  # Take first 3 words
        if not name:
            name = "project"
        return f"{name}-{cmd_type}.md"
    
    def ensure_sdd_dir(out_dir: str) -> str:
        """Ensure SDD directory exists"""
        os.makedirs(out_dir, exist_ok=True)
        return out_dir
    
    def create_sdd_prompt(cmd_type: str, description: str, context: dict, project_id: str = None) -> str:
        """Create SDD-specific prompt with context injection"""
        
        # Use context injector if available
        if context_injector and project_id:
            try:
                command_map = {
                    "spec": "sdd_spec",
                    "plan": "sdd_plan", 
                    "tasks": "sdd_tasks",
                    "implement": "sdd_implement"
                }
                command = command_map.get(cmd_type, f"sdd_{cmd_type}")
                enhanced_prompt, metadata = context_injector.inject_context_for_command(command, description, project_id)
                print(f"--------sdd: context injected ({metadata.get('context_tokens', 0)} tokens)")
                return enhanced_prompt
            except Exception as e:
                print(f"--------sdd: context injection failed: {e}")
        
        # Fallback to original prompt format
        base_context = f"""
**[SDD Context]**
- Frameworks: {context['frameworks']}
- Existing SPEC files: {', '.join(context['spec_files']) if context['spec_files'] else 'None'}
- Existing PLAN files: {', '.join(context['plan_files']) if context['plan_files'] else 'None'}
- SDD Compliance: {'✅ SPEC/PLAN Found' if context['sdd_compliance'] else '⚠️ Missing SPEC/PLAN'}

**[Request]**
{description}
"""
        
        if cmd_type == "spec":
            return f"""**[Persona Identity]**
You are an architect specialized in creating detailed SPEC (Specification) documents for Spec-Driven Development.

**[Your Task]**
Create a comprehensive SPEC document that defines WHAT needs to be built, WHY it's needed, and success criteria.

**[SPEC Template Structure]**
# SPEC: [Feature Name]

## Problem Statement
- What problem are we solving?
- Who are the stakeholders?
- What's the current pain point?

## Goals & Success Criteria  
- Primary objectives
- Measurable success metrics
- User value proposition

## Scope & Boundaries
- What's included in this feature
- What's explicitly excluded
- Dependencies and constraints

## User Stories & Use Cases
- Key user workflows
- Edge cases and error scenarios
- Acceptance criteria

## Non-Functional Requirements
- Performance requirements
- Security considerations
- Scalability needs
- Accessibility requirements

{base_context}
"""
        
        elif cmd_type == "plan":
            return f"""**[Persona Identity]**
You are an architect specialized in creating detailed PLAN documents for Spec-Driven Development.

**[Your Task]**
Create a comprehensive PLAN document that defines HOW to build the feature based on existing SPEC requirements.

**[PLAN Template Structure]**
# PLAN: [Feature Name Implementation]

## Architecture Overview
- High-level system design
- Component relationships
- Data flow diagrams

## Technical Approach
- Technology stack decisions
- Framework and library choices
- Integration patterns

## Implementation Strategy
- Phase breakdown
- Milestone definitions
- Risk mitigation strategies

## Data Design
- Database schema changes
- API contract definitions
- Data migration requirements

## Testing Strategy
- Unit testing approach
- Integration testing plan
- E2E testing scenarios

## Security & Performance
- Security implementation
- Performance optimization
- Monitoring and alerting

## Deployment & Operations
- Deployment strategy
- Configuration management
- Rollback procedures

{base_context}
"""
        
        elif cmd_type == "tasks":
            return f"""**[Persona Identity]**
You are an analyzer specialized in breaking down PLAN documents into actionable development tasks.

**[Your Task]**
Break down the implementation plan into specific, actionable development tasks with clear acceptance criteria.

**[TASKS Template Structure]**
# TASKS: [Feature Name]

## Task Breakdown

### Phase 1: Foundation
- [ ] Task ID: FEAT-001
  - **Description**: [Specific task description]
  - **Acceptance Criteria**: [Clear, testable criteria]
  - **Dependencies**: [Other tasks or external dependencies]
  - **Estimate**: [Time estimate]
  - **Priority**: [High/Medium/Low]

### Phase 2: Core Implementation
- [ ] Task ID: FEAT-002
  - **Description**: [Specific task description]
  - **Acceptance Criteria**: [Clear, testable criteria]
  - **Dependencies**: [Other tasks or external dependencies]
  - **Estimate**: [Time estimate]
  - **Priority**: [High/Medium/Low]

### Phase 3: Integration & Testing
- [ ] Task ID: FEAT-003
  - **Description**: [Specific task description]
  - **Acceptance Criteria**: [Clear, testable criteria]
  - **Dependencies**: [Other tasks or external dependencies]
  - **Estimate**: [Time estimate]
  - **Priority**: [High/Medium/Low]

## Task Dependencies Graph
- Visual representation of task relationships
- Critical path identification
- Parallel execution opportunities

## Definition of Done
- Code review completed
- Tests passing
- Documentation updated
- Security review (if applicable)
- Performance benchmarks met

{base_context}
"""
        
        elif cmd_type == "implement":
            return f"""**[Persona Identity]**
You are a senior developer specialized in SDD-compliant implementation.

**[Your Task]**
Provide implementation guidance that follows the established SPEC and PLAN documents.

**[Implementation Guidance]**
Review the existing SPEC and PLAN documents, then provide:

1. **Compliance Check**
   - Verify implementation aligns with SPEC requirements
   - Confirm technical approach matches PLAN decisions
   - Identify any gaps or deviations

2. **Implementation Priority**
   - Suggest implementation order based on dependencies
   - Highlight critical path items
   - Recommend MVP features for early validation

3. **Code Structure**
   - Recommended file/folder organization
   - Key classes/components to implement
   - Interface definitions

4. **Integration Points**
   - External service integrations
   - Database interactions
   - API endpoints

5. **Testing Strategy**
   - Unit tests to implement first
   - Integration test scenarios
   - E2E test cases

6. **Quality Gates**
   - Performance benchmarks
   - Security checkpoints
   - Code review checklist

{base_context}
"""
        
        return base_context
    
    # Extract project ID from description or generate one
    project_id = None
    if context_injector:
        project_id = context_injector._detect_project_id(args.description)
        if not project_id:
            # Generate project ID from description
            words = re.findall(r'\b\w+\b', args.description.lower())
            project_id = "-".join(words[:2]) if len(words) >= 2 else "default-project"
    
    # Get SDD context
    sdd_context = get_project_sdd_context()
    out_dir = ensure_sdd_dir(getattr(args, 'out', 'specs'))
    
    print(f"🚀 SDD {args.sdd_cmd.upper()} Generator")
    print(f"📁 Output directory: {out_dir}")
    print(f"🎯 Description: {args.description}")
    if project_id:
        print(f"📋 Project: {project_id}")
    
    # Generate appropriate prompt with context injection
    prompt = create_sdd_prompt(args.sdd_cmd, args.description, sdd_context, project_id)
    
    # Generate filename
    filename = generate_file_name(args.description, args.sdd_cmd)
    filepath = os.path.join(out_dir, filename)
    
    if args.sdd_cmd == "implement":
        # For implement, just show the prompt and guidance
        print("\n" + "="*60)
        print(prompt)
        print("="*60)
        if hasattr(args, 'validate') and args.validate:
            print("🔍 SDD Compliance Validation:")
            print(f"   SPEC files: {len(sdd_context['spec_files'])} found")
            print(f"   PLAN files: {len(sdd_context['plan_files'])} found")
            print(f"   Compliance: {'✅ Ready' if sdd_context['sdd_compliance'] else '❌ Missing SPEC/PLAN'}")
        return 0
    
    # Execute with appropriate CLI tool
    try:
        cli_tool = 'codex' if shutil.which('codex') else 'claude' if shutil.which('claude') else None
        
        if not cli_tool:
            print("❌ No suitable AI CLI found (codex or claude required)")
            print("💡 Install Codex CLI: npm install -g @openai/codex")
            return 1
            
        print(f"🤖 Using {cli_tool.upper()} CLI...")
        
        if cli_tool == 'codex':
            result = subprocess.run(['codex', 'exec', '-c', 'model_reasoning_effort=high', prompt], timeout=180)
        else:
            result = subprocess.run(['claude', '--model', 'claude-sonnet-4-20250514', '-p', prompt], timeout=120)
            
        if result.returncode == 0:
            print(f"✅ {args.sdd_cmd.upper()} generated successfully!")
            print(f"📝 Consider saving the output to: {filepath}")
            print(f"\n💡 Next steps:")
            
            if args.sdd_cmd == "spec":
                print("   1. Review and refine the SPEC document")
                print("   2. Get stakeholder approval")
                print("   3. Run: super-prompt sdd plan \"[implementation approach]\"")
            elif args.sdd_cmd == "plan":
                print("   1. Review technical approach with team")
                print("   2. Validate architecture decisions")
                print("   3. Run: super-prompt sdd tasks \"[break down implementation]\"")
            elif args.sdd_cmd == "tasks":
                print("   1. Review task breakdown with team")
                print("   2. Estimate and prioritize tasks")
                print("   3. Run: super-prompt sdd implement \"[start implementation]\"")
                
            return 0
        else:
            print("❌ Failed to generate SDD document")
            return 1
            
    except subprocess.TimeoutExpired:
        print("❌ Generation timed out")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

def show_ascii_logo():
    """Display ASCII logo with version info"""
    logo = f"""
\033[36m\033[1m
   ███████╗██╗   ██╗██████╗ ███████╗██████╗ 
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗
   ███████╗██║   ██║██████╔╝█████╗  ██████╔╝
   ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗
   ███████║╚██████╔╝██║     ███████╗██║  ██║
   ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝
   
   ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ████████╗
   ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝
   ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝   ██║   
   ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝    ██║   
   ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║        ██║   
   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝   
\033[0m
\033[2m              Dual IDE Prompt Engineering Toolkit\033[0m
\033[2m                     v{VERSION} | @cdw0424/super-prompt\033[0m
\033[2m                          Made by \033[0m\033[35mDaniel Choi\033[0m
"""
    print(logo)

def main():
    parser = argparse.ArgumentParser(prog="super-prompt", add_help=True)
    sub = parser.add_subparsers(dest="cmd")

    # SDD-enhanced commands
    p_init = sub.add_parser("super:init", help="Generate SDD-compliant rules and setup")
    p_init.add_argument("--out", default=".cursor/rules", help="Output directory")
    p_init.add_argument("--dry-run", action="store_true", help="Preview only")
    
    p_optimize = sub.add_parser("optimize", help="Execute persona queries with SDD context")
    p_optimize.add_argument("query", nargs="*", help="Query or debate topic")
    p_optimize.add_argument("--list-personas", action="store_true")
    # Flag-based personas for Codex environment  
    p_optimize.add_argument("--persona", choices=['frontend','frontend-ultra','backend','analyzer','architect','high','seq','seq-ultra','debate','performance','security','task','wave','ultracompressed'])
    p_optimize.add_argument("--frontend", action="store_true")
    p_optimize.add_argument("--frontend-ultra", action="store_true") 
    p_optimize.add_argument("--backend", action="store_true")
    p_optimize.add_argument("--analyzer", action="store_true")
    p_optimize.add_argument("--architect", action="store_true")
    p_optimize.add_argument("--high", action="store_true")
    p_optimize.add_argument("--seq", action="store_true")
    p_optimize.add_argument("--seq-ultra", action="store_true")
    p_optimize.add_argument("--debate", action="store_true")
    # Enhanced personas
    p_optimize.add_argument("--performance", action="store_true")
    p_optimize.add_argument("--security", action="store_true")
    p_optimize.add_argument("--task", action="store_true")
    p_optimize.add_argument("--wave", action="store_true") 
    p_optimize.add_argument("--ultracompressed", action="store_true")
    p_optimize.add_argument("--rounds", type=int, default=8, help="Debate rounds (2-20)")
    
    # SDD flags for simplified syntax
    p_optimize.add_argument("--sp-sdd-spec", action="store_true", help="SDD: Create or edit SPEC files")
    p_optimize.add_argument("--sp-sdd-plan", action="store_true", help="SDD: Create or edit PLAN files") 
    p_optimize.add_argument("--sp-sdd-tasks", action="store_true", help="SDD: Break down plans into tasks")
    p_optimize.add_argument("--sp-sdd-implement", action="store_true", help="SDD: Start implementation")
    p_optimize.add_argument("--out", default="specs", help="Output directory for SDD files")
    p_optimize.add_argument("--validate", action="store_true", help="Validate SPEC/PLAN compliance")
    
    # Simplified persona flags with --sp-* prefix
    p_optimize.add_argument("--sp-frontend", action="store_true", help="Frontend design advisor")
    p_optimize.add_argument("--sp-frontend-ultra", action="store_true", help="Elite UX/UI architect") 
    p_optimize.add_argument("--sp-backend", action="store_true", help="Backend reliability engineer")
    p_optimize.add_argument("--sp-analyzer", action="store_true", help="Root cause analyst")
    p_optimize.add_argument("--sp-architect", action="store_true", help="Systems architecture specialist")
    p_optimize.add_argument("--sp-high", action="store_true", help="Deep reasoning specialist")
    p_optimize.add_argument("--sp-seq", action="store_true", help="Sequential thinking (5 iterations)")
    p_optimize.add_argument("--sp-seq-ultra", action="store_true", help="Advanced sequential (10 iterations)")
    p_optimize.add_argument("--sp-debate", action="store_true", help="Single-model internal debate")
    p_optimize.add_argument("--sp-dev", action="store_true", help="Development assistant")
    p_optimize.add_argument("--sp-performance", action="store_true", help="Optimization & bottleneck elimination")
    p_optimize.add_argument("--sp-security", action="store_true", help="Threat modeling & vulnerability assessment")
    p_optimize.add_argument("--sp-task", action="store_true", help="Task management & workflow execution")
    p_optimize.add_argument("--sp-wave", action="store_true", help="Multi-stage execution orchestration")
    p_optimize.add_argument("--sp-ultracompressed", action="store_true", help="Token efficiency (30-50% reduction)")
    p_optimize.add_argument("--sp-doc-master", action="store_true", help="Documentation master")
    p_optimize.add_argument("--sp-tr", action="store_true", help="Troubleshooter")

    # AMR commands
    p_amr_rules = sub.add_parser("amr:rules", help="Generate AMR rule file (05-amr.mdc)")
    p_amr_rules.add_argument("--out", default=".cursor/rules", help="Rules directory")
    p_amr_rules.add_argument("--dry-run", action="store_true")

    p_amr_print = sub.add_parser("amr:print", help="Print AMR bootstrap prompt to stdout")
    p_amr_print.add_argument("--path", default="prompts/codex_amr_bootstrap_prompt_en.txt", help="Prompt file path")

    p_amr_qa = sub.add_parser("amr:qa", help="Validate a transcript for AMR/state-machine conformance")
    p_amr_qa.add_argument("file", help="Transcript/text file to check")

    # SDD Workflow commands
    p_sdd = sub.add_parser("sdd", help="Spec-Driven Development workflow")
    sdd_sub = p_sdd.add_subparsers(dest="sdd_cmd")
    
    p_sdd_spec = sdd_sub.add_parser("spec", help="Create or edit SPEC files with architect persona")
    p_sdd_spec.add_argument("description", help="Feature/project description for SPEC generation")
    p_sdd_spec.add_argument("--out", default="specs", help="Output directory for SPEC files")
    
    p_sdd_plan = sdd_sub.add_parser("plan", help="Create or edit PLAN files with architect persona")
    p_sdd_plan.add_argument("description", help="Implementation description for PLAN generation")
    p_sdd_plan.add_argument("--out", default="specs", help="Output directory for PLAN files")
    
    p_sdd_tasks = sdd_sub.add_parser("tasks", help="Break down plans into actionable tasks with analyzer persona")
    p_sdd_tasks.add_argument("description", help="Task breakdown description")
    p_sdd_tasks.add_argument("--out", default="specs", help="Output directory for TASK files")
    
    p_sdd_implement = sdd_sub.add_parser("implement", help="Start implementation with SDD compliance checking")
    p_sdd_implement.add_argument("description", help="Implementation description")
    p_sdd_implement.add_argument("--validate", action="store_true", help="Validate SPEC/PLAN compliance")

    # Codex-only setup (write .codex/* without Cursor assets)
    p_codex_init = sub.add_parser("codex:init", help="Create Codex CLI assets in .codex/ (agents.md, personas.py, bootstrap, router-check)")
    p_codex_init.add_argument("--dry-run", action="store_true")

    # TODO validation system
    p_todo_validate = sub.add_parser("todo:validate", help="Validate TODO task completion and trigger high-mode retries")
    p_todo_validate.add_argument("--auto", action="store_true", help="Run validation automatically after each task")
    p_todo_validate.add_argument("--session-file", default=".todo_session.json", help="TODO session file path")
    
    p_todo_status = sub.add_parser("todo:status", help="Show current TODO session status")
    p_todo_status.add_argument("--session-file", default=".todo_session.json", help="TODO session file path")

    # Context Management System
    p_context_init = sub.add_parser("context:init", help="Initialize context management system for project")
    p_context_init.add_argument("project_id", help="Project identifier")
    p_context_init.add_argument("--stage", default="specify", choices=["specify", "plan", "tasks", "implement"], help="Initial stage")
    
    p_context_status = sub.add_parser("context:status", help="Show current context session status")
    p_context_status.add_argument("--project", help="Project ID to check")
    
    p_context_projects = sub.add_parser("context:projects", help="List all projects with context")
    
    p_context_session = sub.add_parser("context:session", help="Manage context sessions")
    p_context_session.add_argument("action", choices=["start", "load", "switch"], help="Session action")
    p_context_session.add_argument("project_id", help="Project identifier")
    p_context_session.add_argument("--stage", choices=["specify", "plan", "tasks", "implement"], help="Target stage")
    
    p_context_cleanup = sub.add_parser("context:cleanup", help="Clean up old context sessions")
    p_context_cleanup.add_argument("--days", type=int, default=30, help="Remove sessions older than N days")

    args = parser.parse_args()
    if not args.cmd: 
        args.cmd = "super:init"

    if args.cmd == "super:init":
        show_ascii_logo()
        print("\033[33m\033[1m🚀 Initializing project setup...\033[0m\n")
        # Check project SDD status
        sdd_context = get_project_sdd_context()
        print(f"\033[32m✓\033[0m \033[1mStep 1:\033[0m Framework detection completed")
        print(f"   \033[2m→ Detected: {sdd_context['frameworks']}\033[0m")
        print(f"   \033[2m→ SDD Status: {'✅ SPEC/PLAN found' if sdd_context['sdd_compliance'] else '⚠️  Missing SPEC/PLAN'}\033[0m\n")
        
        # Generate SDD rules
        print("\033[36m📋 Generating Cursor rules...\033[0m")
        rules_dir = generate_sdd_rules_files(args.out, args.dry_run)
        print(f"\033[32m✓\033[0m \033[1mStep 2:\033[0m Rule files created")
        print(f"   \033[2m→ Location: {rules_dir}\033[0m\n")
        
        # Install Cursor commands
        print("\033[36m⚡ Setting up Cursor slash commands...\033[0m")
        install_cursor_commands_in_project(args.dry_run)
        print(f"\033[32m✓\033[0m \033[1mStep 3:\033[0m Slash commands installed")
        print("   \033[2m→ Available: /high /frontend-ultra /frontend /backend /analyzer /architect /seq /seq-ultra /debate /performance /security /task /wave /ultracompressed /docs-refector /refactorer /implement /review /dev /devops /doc-master /mentor /qa /scribe /spec /plan /tasks /specify /optimize /tr /init-sp /re-init-sp /grok /grok-on /grok-off\033[0m\n")
        # Optional Codex integration prompt (.codex/*)
        want_codex = os.environ.get('SUPER_PROMPT_INIT_CODEX')
        yn = None
        if want_codex is not None:
            yn = want_codex.lower() in ('1','true','yes','y')
        elif sys.stdin.isatty():
            try:
                ans = input("Extend Codex CLI integration now (.codex assets)? [Y/n] ").strip().lower()
            except Exception:
                ans = ''
            yn = not ans.startswith('n')
        else:
            yn = False
        if yn:
            print("\033[36m📦 Creating .codex agent and helpers...\033[0m")
            write_codex_agent_assets(args.dry_run)
            print(f"\033[32m✓\033[0m \033[1mStep 4:\033[0m Codex agent configured → .codex/")

            # Install flag-only shell handler so "--sp-*" works without a command prefix
            try:
                print("\033[36m🔧 Enabling flag-only mode (sp-setup-shell) ...\033[0m")
                # Try direct binary first
                r = subprocess.run(["sp-setup-shell"], check=False)
                if r.returncode != 0:
                    # Fallback to npx without global install
                    subprocess.run(["npx", "-y", "@cdw0424/super-prompt", "sp-setup-shell"], check=False)
                print("\033[32m✓\033[0m \033[1mFlag-only mode enabled\033[0m → try: \033[33m--sp-analyzer \"...\"\033[0m")
            except Exception as e:
                print(f"\033[33m⚠️  Could not enable flag-only mode automatically ({e}). You can run: sp-setup-shell\033[0m")
        else:
            print("\033[2mSkipping Codex CLI extension (set SUPER_PROMPT_INIT_CODEX=1 to auto-enable)\033[0m")
        
        if not sdd_context['sdd_compliance']:
            print("\033[33m⚠️  Optional SDD Setup:\033[0m")
            print("   \033[2mConsider creating SPEC/PLAN files for structured development:\033[0m")
            print("   \033[2m→ specs/001-project/spec.md (goals, success criteria, scope)\033[0m")
            print("   \033[2m→ specs/001-project/plan.md (architecture, NFRs, constraints)\033[0m\n")
        
        print("\033[32m\033[1m🎉 Setup Complete!\033[0m\n")
        print("\033[35m\033[1m📖 Quick Start:\033[0m")
        print("   \033[2mIn Cursor, type:\033[0m \033[33m/frontend\033[0m \033[2mor\033[0m \033[33m/architect\033[0m \033[2min your prompt\033[0m")
        print("   \033[2mFrom CLI:\033[0m \033[36msuper-prompt optimize \"design strategy /frontend\"\033[0m")
        print("")
        print("\033[32m✨ Ready for next-level prompt engineering!\033[0m")
        return 0
        
    elif args.cmd == "optimize":
        optimizer = PromptOptimizer()
        
        if hasattr(args, 'list_personas') and args.list_personas:
            print("🚀 Super Prompt - Available Personas:")
            for persona, config in optimizer.PERSONAS.items():
                print(f"  /{persona:<15} - {config['desc']}")
            return 0
        
        # Check for SDD flags first
        sdd_flags = ['sp_sdd_spec', 'sp_sdd_plan', 'sp_sdd_tasks', 'sp_sdd_implement']
        active_sdd = [flag for flag in sdd_flags if getattr(args, flag.replace('-', '_'), False)]
        
        if active_sdd:
            if len(active_sdd) > 1:
                print("❌ Only one SDD flag can be used at a time")
                return 1
            
            if not args.query:
                print("❌ Please provide a description for SDD workflow")
                print("Example: super-prompt optimize --sp-sdd-spec \"user authentication system\"")
                return 1
            
            # Convert to SDD args format
            sdd_flag = active_sdd[0]
            sdd_cmd = sdd_flag.replace('sp_sdd_', '')
            
            # Create a mock args object for SDD handling
            class SDDArgs:
                def __init__(self):
                    self.sdd_cmd = sdd_cmd
                    self.description = ' '.join(args.query)
                    self.out = getattr(args, 'out', 'specs')
                    self.validate = getattr(args, 'validate', False)
            
            return handle_sdd_command(SDDArgs())
        
        if not args.query:
            print("🚀 Super Prompt - Persona Query Processor")
            print("❌ Please provide a query with persona tag")
            print("Example: super-prompt optimize \"design strategy /frontend\"")
            return 1
        
        query_text = ' '.join(args.query)
        print("🚀 Super Prompt - Persona Query Processor")
        # Resolve persona override from flags
        if getattr(args, 'persona', None):
            query_text += f" /{args.persona}"
        else:
            # Check simplified --sp-* flags first
            sp_flags_found = False
            for flag, tag in [
                ('sp_frontend_ultra','frontend-ultra'),
                ('sp_frontend','frontend'),
                ('sp_backend','backend'),
                ('sp_analyzer','analyzer'),
                ('sp_architect','architect'),
                ('sp_high','high'),
                ('sp_seq_ultra','seq-ultra'),
                ('sp_seq','seq'),
                ('sp_debate','debate'),
                ('sp_dev','dev'),
                ('sp_performance','performance'),
                ('sp_security','security'),
                ('sp_task','task'),
                ('sp_wave','wave'),
                ('sp_ultracompressed','ultracompressed'),
                ('sp_doc_master','doc-master'),
                ('sp_tr','tr'),
            ]:
                if getattr(args, flag.replace('-', '_'), False):
                    query_text += f" /{tag}"
                    sp_flags_found = True
                    break
            
            # Fall back to original flags if no --sp-* flags found
            if not sp_flags_found:
                for flag, tag in [
                    ('frontend_ultra','frontend-ultra'),
                    ('frontend','frontend'),
                    ('backend','backend'),
                    ('analyzer','analyzer'),
                    ('architect','architect'),
                    ('high','high'),
                    ('seq_ultra','seq-ultra'),
                    ('seq','seq'),
                    ('debate','debate'),
                    ('dev','dev'),
                    # Enhanced personas
                    ('performance','performance'),
                    ('security','security'),
                    ('task','task'),
                    ('wave','wave'),
                    ('ultracompressed','ultracompressed'),
                    ('doc_master','doc-master'),
                    ('tr','tr'),
                ]:
                    if getattr(args, flag, False):
                        query_text += f" /{tag}"
                        break
        if (getattr(args, 'debate', False) or getattr(args, 'sp_debate', False)) and getattr(args, 'rounds', None):
            query_text += f" --rounds {int(args.rounds)}"
        success = optimizer.process_query(query_text)
        return 0 if success else 1
    elif args.cmd == "amr:rules":
        path = generate_amr_rules_file(args.out, getattr(args, 'dry_run', False))
        print(f"AMR rules written: {path}")
        return 0
    elif args.cmd == "amr:print":
        p = getattr(args, 'path', 'prompts/codex_amr_bootstrap_prompt_en.txt')
        data = read_text(p)
        if not data:
            print("No bootstrap prompt found.")
            return 1
        print(data)
        return 0
    elif args.cmd == "amr:qa":
        fp = args.file
        if not os.path.isfile(fp):
            print(f"❌ File not found: {fp}")
            return 2
        txt = read_text(fp)
        ok = True
        # Check sections
        if not re.search(r"^\[INTENT\]", txt, re.M):
            log("Missing [INTENT] section"); ok = False
        if not (re.search(r"^\[PLAN\]", txt, re.M) or re.search(r"^\[EXECUTE\]", txt, re.M)):
            log("Missing [PLAN] or [EXECUTE] section"); ok = False
        # Check log prefix
        if re.search(r"^(router:|run:)", txt, re.M):
            log("Found log lines without '--------' prefix"); ok = False
        # Router switch consistency (if present)
        if "/model gpt-5 high" in txt and "/model gpt-5 medium" not in txt:
            log("High switch found without returning to medium"); ok = False
        print("--------qa: OK" if ok else "--------qa: FAIL")
        return 0 if ok else 1
    elif args.cmd == "sdd":
        if not hasattr(args, 'sdd_cmd') or not args.sdd_cmd:
            print("❌ SDD subcommand required. Use: spec, plan, tasks, or implement")
            return 1
            
        # SDD workflow implementation
        return handle_sdd_command(args)
        
    elif args.cmd == "codex:init":
        write_codex_agent_assets(getattr(args, 'dry_run', False))
        print("--------codex:init: .codex assets created")
        return 0
        
    elif args.cmd == "todo:validate":
        return handle_todo_validate_command(args)
        
    elif args.cmd == "todo:status":
        return handle_todo_status_command(args)
        
    elif args.cmd == "context:init":
        return handle_context_init_command(args)
        
    elif args.cmd == "context:status":
        return handle_context_status_command(args)
        
    elif args.cmd == "context:projects":
        return handle_context_projects_command(args)
        
    elif args.cmd == "context:session":
        return handle_context_session_command(args)
        
    elif args.cmd == "context:cleanup":
        return handle_context_cleanup_command(args)
    
    log(f"Unknown command: {args.cmd}")
    return 2

def handle_todo_validate_command(args):
    """Handle TODO validation command"""
    try:
        validator = TodoValidator()
        validator.session_file = args.session_file
        
        # Load current session
        todos = validator.load_session()
        
        if not todos:
            print("📋 No active TODO session found")
            return 0
        
        print("🔍 Validating TODO tasks...")
        
        # Process and validate todos
        updated_todos = validator.process_todos(todos)
        
        # Save updated session
        validator.save_session(updated_todos)
        
        # Print detailed summary
        completed = len([t for t in updated_todos if t.status == TaskStatus.COMPLETED])
        failed = len([t for t in updated_todos if t.status == TaskStatus.FAILED])
        in_progress = len([t for t in updated_todos if t.status == TaskStatus.IN_PROGRESS])
        pending = len([t for t in updated_todos if t.status == TaskStatus.PENDING])
        
        print(f"\n📊 TODO Validation Summary:")
        print(f"   ✅ Completed: {completed}")
        print(f"   🔄 In Progress: {in_progress}")
        print(f"   📋 Pending: {pending}")
        print(f"   ❌ Failed: {failed}")
        
        # Show failed tasks details
        failed_tasks = [t for t in updated_todos if t.status == TaskStatus.FAILED]
        if failed_tasks:
            print(f"\n❌ Failed Tasks:")
            for task in failed_tasks:
                print(f"   • {task.content[:60]}...")
                print(f"     Attempts: {task.attempt}/{task.max_attempts}")
                print(f"     Error: {task.last_error}")
        
        return 0
        
    except Exception as e:
        print(f"❌ TODO validation failed: {str(e)}")
        return 1

def handle_todo_status_command(args):
    """Handle TODO status command"""
    try:
        validator = TodoValidator()
        validator.session_file = args.session_file
        
        # Load current session
        todos = validator.load_session()
        
        if not todos:
            print("📋 No active TODO session found")
            return 0
        
        print("📋 Current TODO Session Status:")
        print("=" * 50)
        
        for i, task in enumerate(todos, 1):
            status_icon = {
                TaskStatus.PENDING: "📋",
                TaskStatus.IN_PROGRESS: "🔄", 
                TaskStatus.COMPLETED: "✅",
                TaskStatus.BLOCKED: "🚧",
                TaskStatus.FAILED: "❌"
            }
            
            icon = status_icon.get(task.status, "❓")
            print(f"{i:2d}. {icon} {task.content}")
            
            if task.status == TaskStatus.FAILED:
                print(f"     └─ Attempts: {task.attempt}/{task.max_attempts}")
                print(f"     └─ Error: {task.last_error}")
            elif task.attempt > 1:
                print(f"     └─ Attempt: {task.attempt}/{task.max_attempts}")
        
        print("=" * 50)
        
        # Summary stats
        completed = len([t for t in todos if t.status == TaskStatus.COMPLETED])
        total = len(todos)
        progress = (completed / total * 100) if total > 0 else 0
        
        print(f"Progress: {completed}/{total} tasks completed ({progress:.1f}%)")
        
        return 0
        
    except Exception as e:
        print(f"❌ TODO status failed: {str(e)}")
        return 1

def handle_context_init_command(args):
    """Handle context initialization command"""
    try:
        context_manager = ContextManager()
        session_id = context_manager.start_session(args.project_id, args.stage)
        
        print(f"🧠 Context Management System Initialized")
        print(f"📋 Project: {args.project_id}")
        print(f"🎯 Stage: {args.stage}")
        print(f"🔑 Session: {session_id}")
        
        # Show directory structure
        specs_dir = context_manager.specs_dir / args.project_id
        memory_dir = context_manager.memory_dir
        
        print(f"\n📁 Directory Structure:")
        print(f"   ├── specs/{args.project_id}/")
        print(f"   │   ├── spec.md")
        print(f"   │   ├── plan.md")
        print(f"   │   └── tasks.md")
        print(f"   └── memory/")
        print(f"       ├── constitution/constitution.md")
        print(f"       ├── rules/")
        print(f"       └── sessions/")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Create SPEC: super-prompt sdd spec \"your feature description\"")
        print(f"   2. Check status: super-prompt context:status --project {args.project_id}")
        print(f"   3. View projects: super-prompt context:projects")
        
        return 0
        
    except Exception as e:
        print(f"❌ Context initialization failed: {str(e)}")
        return 1

def handle_context_status_command(args):
    """Handle context status command"""
    try:
        context_manager = ContextManager()
        
        if args.project:
            # Show specific project status
            session_started = False
            try:
                sessions_dir = context_manager.memory_dir / "sessions"
                if sessions_dir.exists():
                    for session_file in sessions_dir.glob(f"{args.project}_*.json"):
                        session_id = session_file.stem
                        if context_manager.load_session(session_id):
                            session_started = True
                            break
            except:
                pass
                
            if not session_started:
                context_manager.start_session(args.project, "specify")
                
            status = context_manager.get_session_status()
            
            print(f"🧠 Context Status for Project: {args.project}")
            print(f"📋 Session: {status.get('session_id', 'N/A')}")
            print(f"🎯 Current Stage: {status.get('current_stage', 'N/A')}")
            print(f"📊 Available Artifacts: {', '.join(status.get('artifacts', [])) or 'None'}")
            print(f"🔄 Can Advance: {'✅ Yes' if status.get('can_advance', False) else '❌ No'}")
            print(f"💾 Token Usage: {status.get('token_usage', 'N/A')}")
            print(f"⚙️ Injection Policy: {status.get('injection_policy', 'N/A')}")
            
        else:
            # Show all projects status
            projects = context_manager.list_projects()
            print(f"🧠 Context Management System Status")
            print(f"📋 Total Projects: {len(projects)}")
            
            if projects:
                print(f"\n📁 Projects:")
                for project in projects:
                    artifacts = []
                    project_dir = context_manager.specs_dir / project
                    if (project_dir / "spec.md").exists():
                        artifacts.append("spec")
                    if (project_dir / "plan.md").exists():
                        artifacts.append("plan")
                    if (project_dir / "tasks.md").exists():
                        artifacts.append("tasks")
                    
                    status_icon = "🟢" if len(artifacts) >= 2 else "🟡" if len(artifacts) == 1 else "🔴"
                    print(f"   {status_icon} {project}: {', '.join(artifacts) or 'No artifacts'}")
            else:
                print(f"\n💡 No projects found. Initialize with: super-prompt context:init <project-id>")
        
        return 0
        
    except Exception as e:
        print(f"❌ Context status failed: {str(e)}")
        return 1

def handle_context_projects_command(args):
    """Handle context projects listing command"""
    try:
        context_manager = ContextManager()
        projects = context_manager.list_projects()
        
        print(f"🧠 Context Management - All Projects")
        print(f"=" * 50)
        
        if projects:
            for i, project in enumerate(projects, 1):
                project_dir = context_manager.specs_dir / project
                artifacts = []
                
                # Check artifact status
                artifact_files = ["spec.md", "plan.md", "tasks.md"]
                for artifact_file in artifact_files:
                    if (project_dir / artifact_file).exists():
                        with open(project_dir / artifact_file, 'r') as f:
                            content = f.read()
                            tokens = len(content) // 4  # Rough token estimate
                            artifacts.append(f"{artifact_file.replace('.md', '')} ({tokens}t)")
                
                # Determine stage
                stage = "specify"
                if len(artifacts) >= 3:
                    stage = "implement"
                elif len(artifacts) >= 2:
                    stage = "tasks"
                elif len(artifacts) >= 1:
                    stage = "plan"
                
                stage_icons = {
                    "specify": "📝",
                    "plan": "🏗️",
                    "tasks": "📋",
                    "implement": "⚡"
                }
                
                print(f"{i:2d}. {stage_icons.get(stage, '❓')} {project}")
                print(f"     Stage: {stage}")
                print(f"     Artifacts: {', '.join(artifacts) if artifacts else 'None'}")
                print()
        else:
            print("No projects found.")
            print("\n💡 Create your first project:")
            print("   super-prompt context:init my-project")
        
        return 0
        
    except Exception as e:
        print(f"❌ Context projects listing failed: {str(e)}")
        return 1

def handle_context_session_command(args):
    """Handle context session management command"""
    try:
        context_manager = ContextManager()
        
        if args.action == "start":
            stage = args.stage or "specify"
            session_id = context_manager.start_session(args.project_id, stage)
            print(f"🧠 Context session started")
            print(f"📋 Project: {args.project_id}")
            print(f"🎯 Stage: {stage}")
            print(f"🔑 Session: {session_id}")
            
        elif args.action == "load":
            # Find and load existing session
            sessions_dir = context_manager.memory_dir / "sessions"
            session_found = False
            
            if sessions_dir.exists():
                for session_file in sessions_dir.glob(f"{args.project_id}_*.json"):
                    session_id = session_file.stem
                    if context_manager.load_session(session_id):
                        print(f"🧠 Context session loaded")
                        print(f"📋 Project: {args.project_id}")
                        print(f"🔑 Session: {session_id}")
                        
                        status = context_manager.get_session_status()
                        print(f"🎯 Current Stage: {status.get('current_stage', 'N/A')}")
                        session_found = True
                        break
            
            if not session_found:
                print(f"❌ No session found for project: {args.project_id}")
                print(f"💡 Create new session: super-prompt context:session start {args.project_id}")
                return 1
                
        elif args.action == "switch":
            if not args.stage:
                print("❌ Stage required for switch action")
                return 1
                
            # Load existing session and switch stage
            sessions_dir = context_manager.memory_dir / "sessions"
            session_found = False
            
            if sessions_dir.exists():
                for session_file in sessions_dir.glob(f"{args.project_id}_*.json"):
                    session_id = session_file.stem
                    if context_manager.load_session(session_id):
                        if context_manager.update_stage(args.stage):
                            print(f"🧠 Context stage switched")
                            print(f"📋 Project: {args.project_id}")
                            print(f"🎯 New Stage: {args.stage}")
                            session_found = True
                        else:
                            print(f"❌ Cannot switch to stage '{args.stage}' - missing required artifacts")
                            return 1
                        break
            
            if not session_found:
                print(f"❌ No session found for project: {args.project_id}")
                return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Context session management failed: {str(e)}")
        return 1

def handle_context_cleanup_command(args):
    """Handle context cleanup command"""
    try:
        context_manager = ContextManager()
        context_manager.cleanup_old_sessions(args.days)
        print(f"🧠 Context cleanup completed")
        print(f"🗑️ Removed sessions older than {args.days} days")
        return 0
        
    except Exception as e:
        print(f"❌ Context cleanup failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
