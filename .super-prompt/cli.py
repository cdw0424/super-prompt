#!/usr/bin/env python3
"""
Super Prompt — Project CLI (NPM packaged)

This is the CLI invoked by the Node/NPM distribution via bin/super-prompt.
It orchestrates project setup (super:init, super:upgrade), Cursor assets,
legacy cleanup, and JSON→SQLite migration for memory/ltm.db.

Note: The repository also contains a Python core CLI at
packages/core-py/super_prompt/cli.py (Typer-based) intended for the Python
package (super-prompt-core). The two CLIs target different distribution
channels; do not delete either.
"""

import argparse, glob, os, sys, re, json, datetime, textwrap, subprocess, shutil
from typing import Dict, List, Optional

VERSION = "1.0.0"
CURRENT_CMD: Optional[str] = None  # set in main()

# Scaffold module (loaded at runtime)
scaffold = None

def log(msg: str):
    print(f"-------- {msg}")

def print_core_guidance(context: str = ""):
    print("\n\033[33mℹ️  Core CLI not found in this project.\033[0m")
    if context:
        print(f"   Context: {context}")
    print("   Install Python core (choose one):")
    print("   - pip:   \033[36mpip install super-prompt-core\033[0m")
    print("   - pipx:  \033[36mpipx install super-prompt-core\033[0m")
    print("   Run (examples):")
    print("   - \033[36mpython -m super_prompt.cli optimize \"Design system /architect\"\033[0m")
    print("   - \033[36mpython -m super_prompt.cli sdd spec \"user auth\"\033[0m")
    print("   Windows PowerShell:")
    print("   - \033[36mpython -m pip install super-prompt-core\033[0m")
    print("   - \033[36mpython -m super_prompt.cli optimize \"...\"\033[0m")
    print("   Cursor users: use slash commands (e.g., /architect, /frontend)\n")

# Utility functions
def read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception as e:
        log(f"Read failed: {path} ({e})"); return ""

def _allow_write(path: str) -> bool:
    """Global write protection policy: block .cursor/.codex edits during optimize.
    Allow .codex/reports; allow writes for init/build commands.
    """
    p = path.replace("\\", "/")
    if p.startswith('.codex/reports') or '/.codex/reports/' in p:
        return True
    if CURRENT_CMD in ("super:init", "amr:rules", "codex:init", "install", "personas:init", "personas:build"):
        return True
    if CURRENT_CMD in ("optimize", "analyze", "debug"):
        if p.startswith('.cursor') or '/.cursor/' in p:
            return False
        if p.startswith('.codex') or '/.codex/' in p:
            return False
    return True

def write_text(path: str, content: str, dry: bool = False):
    if dry:
        log(f"[DRY] write → {path} ({len(content.encode('utf-8'))} bytes)"); return
    if not _allow_write(path):
        log(f"write blocked → {path} (policy)")
        return
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
            p = subprocess.run(["claude","--model","claude-sonnet-4-20250514","-p", f"Translate to clear English. Keep markdown.\n\n{txt}"], capture_output=True, text=True, timeout=30)
            out = (p.stdout or "").strip()
            if out: return sanitize_en(out)
        except: pass
    return sanitize_en(txt)

def slugify(name: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower())
    base = re.sub(r"-+", "-", base).strip("-")
    return base or "persona"

def ylist(items):
    return "[" + ", ".join(json.dumps(i) for i in items) + "]"

# Context7 MCP detection and guidance
def detect_context7_mcp() -> bool:
    try:
        if os.environ.get('CONTEXT7_MCP','').lower() in ('1','true','yes','y'):
            return True
        if shutil.which('context7') or shutil.which('c7'):
            return True
        if os.path.isdir(os.path.join(os.getcwd(), '.context7')):
            return True
        home=os.path.expanduser('~')
        if os.path.isdir(os.path.join(home, '.context7')):
            return True
    except Exception:
        pass
    return False

def mcp_usage_block(enabled: bool) -> str:
    if enabled:
        return ("\n**[MCP Integration — Context7]**\n- Detected: ✅\n- Use Context7 MCP to collect only verifiable, project‑real information (code, docs, configs).\n- Cite artifacts (paths/IDs/URLs) and prefer MCP data over assumptions.\n- If a provider is unavailable, state the limitation.\n")
    return ("\n**[MCP Integration — Context7]**\n- Detected: ❌\n- Proceed now with best effort using local context.\n- After this run, set up Context7 MCP for real‑source grounding.\n  Hint: install Context7 MCP (vendor docs), then export CONTEXT7_MCP=1.\n")

def print_mcp_banner():
    on = detect_context7_mcp()
    if on:
        log("Context7 MCP: detected — use MCP providers for real sources (code/docs/configs)")
    else:
        log("Context7 MCP: not detected — proceeding now; install and set CONTEXT7_MCP=1 to ground planning/implementation in real sources")

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
        }
        ,
        'ultracompressed': {
            'desc': 'Ultra‑Compressed Output (30–50% token savings)',
            'cli': 'claude',
            'prompt': """Minimize tokens aggressively while preserving accuracy and structure.
Rules:
- English only; concise bulleting; shorten variable names only if safe.
- Omit trivial narration and boilerplate; keep code fences around code.
- Prefer tables/lists over prose; no redundant headers.
Output: best‑effort minimal form keeping content fidelity."""
        },
        'performance': {
            'desc': 'Performance Tuning Advisor',
            'cli': 'claude',
            'prompt': """Identify performance hotspots and propose low‑risk optimizations.
Include: measurement strategy, quick wins, trade‑offs, rollout checks."""
        },
        'security': {
            'desc': 'Security Hardening Advisor',
            'cli': 'claude',
            'prompt': """Find security risks and propose mitigations.
Cover: authz/authn, input validation, secrets handling, logging, supply chain."""
        },
        'task': {
            'desc': 'Task Breakdown Assistant',
            'cli': 'claude',
            'prompt': """Break scope into small tasks with IDs, ACs, estimates, dependencies.
Assume SDD context (SPEC/PLAN) where present."""
        },
        'wave': {
            'desc': 'Wave Planning (phased delivery)',
            'cli': 'claude',
            'prompt': """Plan delivery in waves: Wave‑1 (MVP), Wave‑2 (enhancements), Wave‑3 (hardening).
Each wave: goals, tasks, risks, exit criteria."""
        }
        ,
        'db-expert': {
            'desc': 'Database Expert (Prisma + 3NF)',
            'cli': 'codex',
            'prompt': """You are a Senior Database Expert. Your job is to design, review, and document database schemas and queries tailored to the service domain, with Prisma as the default ORM.\n\nNon‑Negotiables:\n- Use Context7 MCP to gather real information from codebase/docs/configs. If unavailable, proceed now but call out that full verification requires MCP.\n- English only. All logs start with '--------'.\n- Prefer 3rd Normal Form (3NF) baseline. Deviate only for clear, measured reasons (write the trade‑off).\n- Consistent naming, explicit constraints (PK/FK/UNIQUE/CHECK), indexes for access paths, safe migrations.\n- Produce clean, maintainable DB documentation.\n\nProcess:\n1) Domain Review (MCP): Identify core entities, relationships, cardinalities, and lifecycle.\n2) Normalization: 1NF → 2NF → 3NF. Call out functional dependencies and rationale.\n3) Prisma Schema: Provide a first version with models, relations, indexes, and constraints.\n4) Migrations & Safety: Outline migration steps, rollback path, and data backfill strategy.\n5) Performance: Propose indexes, query patterns, pagination, and hot‑path diagnostics.\n6) Documentation: ERD summary, model meanings, constraints, and example queries.\n\nOutput Format:\n[DOMAIN]\\n- Entities/Relations (with rationale)\\n[SCHEMA]\\n```prisma\\n...\\n```\\n[MIGRATIONS]\\n- Steps, rollback, verification\\n[PERFORMANCE]\\n- Index plan, query plan hints\\n[DOCS]\\n- Overview, glossary, examples\\n[TRADE‑OFFS]\\n- Normalization vs denormalization, partitioning, etc."""
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
        if re.search(r'--sp-analyzer(\s|$)', input_text): return 'analyzer'
        if re.search(r'--debate(\s|$)', input_text): return 'debate'
        if re.search(r'--dev(\s|$)', input_text): return 'dev'
        if re.search(r'--sp-dev(\s|$)', input_text): return 'dev'
        if re.search(r'--tr(\s|$)', input_text): return 'tr'
        if re.search(r'--sp-tr(\s|$)', input_text): return 'tr'
        if re.search(r'--db-expert(\s|$)', input_text): return 'db-expert'
        if re.search(r'--db-refector(\s|$)', input_text): return 'db-expert'
        if re.search(r'--docs-refector(\s|$)', input_text): return 'docs-refector'
        if re.search(r'--ultracompressed(\s|$)', input_text): return 'ultracompressed'
        if re.search(r'--performance(\s|$)', input_text): return 'performance'
        if re.search(r'--security(\s|$)', input_text): return 'security'
        if re.search(r'--task(\s|$)', input_text): return 'task'
        if re.search(r'--wave(\s|$)', input_text): return 'wave'
        return None

    def clean_input(self, input_text: str) -> str:
        cleaned = input_text
        for persona in self.PERSONAS:
            cleaned = re.sub(f'/{persona}|--persona-{persona}', '', cleaned)
        return re.sub(r'--\w+(?:\s+\S+)?', '', cleaned).strip()

    def execute(self, persona: str, query: str, *, safe: bool=False, out_path: Optional[str]=None) -> bool:
        if persona not in self.PERSONAS:
            log(f"Unknown persona: {persona}")
            return False
        
        config = self.PERSONAS[persona]
        cli_tool = config['cli']
        
        # Handle sequential thinking modes (no external CLI)
        if not cli_tool:
            mcp_on = detect_context7_mcp()
            print(mcp_usage_block(mcp_on))
            if 'process' in config:
                print(config['process'])
            else:
                log(f"-------- {config['desc']}")
                log("Sequential thinking mode - run inside Cursor.")
            if not mcp_on:
                log("Context7 MCP not detected — consider installing and setting CONTEXT7_MCP=1 for real‑source grounding")
            return True
        
        if not shutil.which(cli_tool):
            log(f"{cli_tool} CLI not found")
            return False
        
        log(f"-------- {config['desc']} ({cli_tool.title()})")
        
        # Enhanced SDD-compliant project context + MCP guidance
        sdd_context = get_project_sdd_context()
        mcp_on = detect_context7_mcp()
        sdd_rules = generate_prompt_rules() if persona in ['architect', 'analyzer', 'high'] else ""
        
        docs_block = ''
        if persona == 'docs-refector':
            docs_block = f"\n**[Docs Inventory]**\n{self._get_docs_inventory()}\n"

        context = f"""**[Project Context]**
- Current Directory: {os.getcwd()}
- Detected Frameworks: {sdd_context['frameworks']}
- SDD Compliance: {'✅ SPEC/PLAN Found' if sdd_context['sdd_compliance'] else '⚠️ Missing SPEC/PLAN - SDD Required'}
- SPEC Files: {', '.join(sdd_context['spec_files']) if sdd_context['spec_files'] else 'None found'}
- PLAN Files: {', '.join(sdd_context['plan_files']) if sdd_context['plan_files'] else 'None found'}
- Project File Tree: {self._get_project_files()}

{sdd_rules}

{mcp_usage_block(mcp_on)}

{docs_block}

**[Organization Guardrails]**
- Language: English only in documentation and rules
- All debug/console lines MUST use the '--------' prefix
- Secrets/tokens/PII MUST be masked in prompts, code, and logs
- Keep prompts/personas focused on task goals and constraints
- Avoid vendor/stack specifics unless mandated by SPEC/PLAN"""
        
        # Use detailed persona prompt
        persona_prompt = config.get('prompt', f"**[Persona]** {config['desc']}")
        # Allow dev/tr utils to craft persona prompt if available
        if persona in ('dev','tr'):
            try:
                util_path = os.path.join('.super-prompt','utils', f'{persona}.py')
                if os.path.isfile(util_path):
                    spec = _importlib.spec_from_file_location(f'sp_utils_{persona}', util_path)
                    if spec and spec.loader:
                        mod = _importlib.module_from_spec(spec)
                        spec.loader.exec_module(mod)  # type: ignore
                        if hasattr(mod, 'build_prompt'):
                            built = mod.build_prompt(context=context, query=query)
                            if isinstance(built, str) and built.strip():
                                persona_prompt = built
            except Exception:
                pass
        
        try:
            if cli_tool == 'claude':
                model = config.get('model', 'claude-sonnet-4-20250514')
                full_prompt = f"{persona_prompt}\n\n{context}\n\n**[User's Request]**\n{query}"
                if safe or out_path:
                    if out_path:
                        write_text(out_path, full_prompt, dry=False)
                        log(f"Saved analyzer prompt → {out_path}")
                    else:
                        print(full_prompt)
                    return True
                result = subprocess.run(['claude', '--model', model, '-p', full_prompt], timeout=120)
                ok = (result.returncode == 0)
                if not mcp_on and persona in ('architect','high','analyzer','backend','frontend'):
                    log("Context7 MCP not detected — consider installing and setting CONTEXT7_MCP=1 for real‑source grounding")
                return ok
            elif cli_tool == 'codex':
                full_prompt = f"{persona_prompt}\n\n{context}\n\n**[User's Request]**\n{query}"
                if safe or out_path:
                    if out_path:
                        write_text(out_path, full_prompt, dry=False)
                        log(f"Saved analyzer prompt → {out_path}")
                    else:
                        print(full_prompt)
                    return True
                result = subprocess.run(['codex', 'exec', '-c', 'model_reasoning_effort=high', full_prompt], timeout=120)
                ok = (result.returncode == 0)
                if not mcp_on and persona in ('architect','high','analyzer','backend','frontend'):
                    log("Context7 MCP not detected — consider installing and setting CONTEXT7_MCP=1 for real‑source grounding")
                return ok
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

    def _get_docs_inventory(self, limit: int = 120) -> str:
        try:
            pats = ['**/*.md','**/*.mdx','**/*.rst','**/*.adoc','**/*.txt']
            docs = []
            for p in pats:
                docs.extend(glob.glob(p, recursive=True))
            docs = sorted(set(docs))
            items=[]
            for p in docs[:limit]:
                try:
                    mtime=datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%d')
                except Exception:
                    mtime='?'
                items.append(f"- {p} (last modified {mtime})")
            more = '' if len(docs)<=limit else f"\n- ... and {len(docs)-limit} more"
            return "\n".join(items)+more
        except Exception:
            return "(no docs found)"
    
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
    """Generate SDD rule files in Cursor rules directory"""
    import datetime
    
    sdd_context = get_project_sdd_context()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    os.makedirs(out_dir, exist_ok=True)
    
    # 00-organization.mdc
    org_content = f"""---
description: "Organization guardrails — generated {now}"
globs: ["**/*"]
alwaysApply: true
---
# Organization Guardrails
- Language: English only in documentation and rules.
- All debug/console lines MUST use the '--------' prefix.
- Secrets/tokens/PII MUST be masked in prompts, code, and logs.
- Keep prompts/personas focused on task goals and constraints.
- Avoid irrelevant technology choices; follow existing project conventions first.
- Add meaningful tests for critical paths where applicable.
"""
    
    # 10-sdd-core.mdc
    sdd_content = f"""---
description: "SDD core & self-check — generated {now}"
globs: ["**/*"]
alwaysApply: true
---
# Spec-Driven Development (SDD)
1) No implementation before SPEC and PLAN are approved.
2) SPEC: goals/user value/success criteria/scope boundaries — avoid premature stack choices.
3) PLAN: architecture/constraints/NFR/risks/security/data design.
4) TASKS: small, testable units with tracking IDs.
5) Implementation must pass the Acceptance Self‑Check before PR.

## Current SDD Status
- **SPEC Files Found**: {len(sdd_context['spec_files'])} files
- **PLAN Files Found**: {len(sdd_context['plan_files'])} files
- **SDD Compliance**: {'✅ Compliant' if sdd_context['sdd_compliance'] else '❌ Missing SPEC/PLAN files'}

## Acceptance Self‑Check (auto‑draft)
- ✅ Validate success criteria from SPEC
- ✅ Verify agreed non‑functional constraints (performance/security as applicable)
- ✅ Ensure safe logging (no secrets/PII) and consistent output
- ✅ Add regression tests for new functionality
- ✅ Update documentation

## Framework Context
- **Detected Frameworks**: {sdd_context['frameworks']}
- **Project Structure**: SDD-compliant organization required
"""

    # 20-frontend.mdc
    frontend_content = f"""---
description: "Frontend conventions — generated {now}"
globs: ["**/*.tsx", "**/*.ts", "**/*.jsx", "**/*.js", "**/*.dart"]
alwaysApply: false
---
# Frontend Rules (SDD-Compliant)
- Small, reusable components; single responsibility per file.
- Framework-specific patterns: {sdd_context['frameworks']}
- Routing: Follow framework conventions; guard access control.
- Separate networking layer (services/hooks), define DTO/validation schema.
- UI copy: English only; centralize strings.
- Performance and accessibility: measure and improve user‑perceived responsiveness.
- All debug logs: use '--------' prefix.
"""

    # 30-backend.mdc  
    backend_content = f"""---
description: "Backend conventions — generated {now}"
globs: ["**/*.java", "**/*.py", "**/*.js", "**/*.go", "**/*.sql"]
alwaysApply: false
---
# Backend Rules (SDD-Compliant)
- Layers: Controller → Service → Repository. Business logic in Services.
- Logging: '--------' prefix + correlation ID; never log sensitive data.
- Follow framework conventions already used in the project.
- SDD Traceability: SPEC-ID ↔ PLAN-ID ↔ TASK-ID ↔ PR-ID.
"""
    # Write files
    # Write files
    write_text(os.path.join(out_dir, "00-organization.mdc"), org_content, dry)
    write_text(os.path.join(out_dir, "10-sdd-core.mdc"), sdd_content, dry)
    write_text(os.path.join(out_dir, "20-frontend.mdc"), frontend_content, dry)
    write_text(os.path.join(out_dir, "30-backend.mdc"), backend_content, dry)
    
    log(f"SDD rules generated in {out_dir}")
    return out_dir

def generate_amr_rules_file(out_dir: str = ".cursor/rules", dry: bool = False) -> str:
    """Generate a minimal AMR rule file for Cursor to enforce router policy/state machine."""
    os.makedirs(out_dir, exist_ok=True)
    amr_path = os.path.join(out_dir, "05-amr.mdc")
    content = """---
description: "Auto Model Router (AMR) policy and state machine"
globs: ["**/*"]
alwaysApply: true
---
# Auto Model Router (medium ↔ high)
- Default: gpt-5, reasoning=medium.
- Task classes: L0 (light), L1 (moderate), H (heavy reasoning).
- H: switch to high for PLAN/REVIEW, then back to medium for EXECUTION.
- Router switch lines (copy-run if needed):
  - `/model gpt-5 high` → `--------router: switch to high (reason=deep_planning)`
  - `/model gpt-5 medium` → `--------router: back to medium (reason=execution)`

# Output Discipline
- Language: English. Logs start with `--------`.
- Keep diffs minimal; provide exact macOS zsh commands.

# Fixed State Machine
[INTENT] → [TASK_CLASSIFY] → [PLAN] → [EXECUTE] → [VERIFY] → [REPORT]

# Templates (use as needed)
T1 Switch High:
```
/model gpt-5 high
--------router: switch to high (reason=deep_planning)
```
T1 Back Medium:
```
/model gpt-5 medium
--------router: back to medium (reason=execution)
```
T2 PLAN:
```
[Goal]\n- …\n[Plan]\n- …\n[Risk/Trade‑offs]\n- …\n[Test/Verify]\n- …\n[Rollback]\n- …
```
T3 EXECUTE:
```
[Diffs]\n```diff\n--- a/file\n+++ b/file\n@@\n- old\n+ new\n```\n[Commands]\n```bash\n--------run: npm test -- --watchAll=false\n```
```
"""
    write_text(amr_path, content, dry)
    log(f"AMR rules generated in {out_dir}")
    return amr_path

def install_cursor_commands_in_project(dry=False):
    """Install Cursor slash commands in the current project.
    Writes .cursor/commands/super-prompt/* using a thin wrapper that calls
    the globally installed CLI (or npx fallback).
    """
    base = os.path.join('.cursor', 'commands', 'super-prompt')
    os.makedirs(base, exist_ok=True)

    # tag-executor.sh wrapper (strict Python-first routing)
    tag_sh = """#!/usr/bin/env bash
set -euo pipefail

# Join all args as a single input string
INPUT="$*"

# Known persona keys (must match enhanced_personas.yaml)
PERSONAS=(architect security performance backend frontend analyzer qa mentor refactorer devops scribe dev tr doc-master high debate frontend-ultra seq-ultra docs-refector ultracompressed wave task implement plan review spec specify init-sp re-init-sp)

# Try to detect a persona tag like /architect
DETECTED=""
SPECIAL_COMMANDS=("init-sp" "re-init-sp")

# Check for special initialization commands first
for CMD in "${SPECIAL_COMMANDS[@]}"; do
  if [[ "$INPUT" == *"/$CMD"* ]]; then
    DETECTED="$CMD"
    IS_SPECIAL_CMD=true
    break
  fi
done

# If not special command, check regular personas
if [[ -z "$DETECTED" ]]; then
  for P in "${PERSONAS[@]}"; do
    if [[ "$INPUT" == *"/$P"* ]]; then
      DETECTED="$P"
      IS_SPECIAL_CMD=false
      break
    fi
  done
fi

DELEGATE_FLAG=""
if [[ "$INPUT" == *"/delegate"* ]]; then
  INPUT="${INPUT//\/delegate/}"
  DELEGATE_FLAG="--delegate-reasoning"
fi

if [[ -n "$DETECTED" ]]; then
  # Resolve paths
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  PROJECT_ROOT="${SCRIPT_DIR%/.cursor/commands/super-prompt}"

  if [[ "$IS_SPECIAL_CMD" == true ]]; then
    # Handle special initialization commands
    case "$DETECTED" in
      "init-sp")
        MODE="init"
        ;;
      "re-init-sp")
        MODE="reinit"
        ;;
    esac

    INIT_SCRIPT="$PROJECT_ROOT/.super-prompt/utils/init/init_sp.py"
    if command -v python3 >/dev/null 2>&1 && [[ -f "$INIT_SCRIPT" ]]; then
      echo "-------- Special command /$DETECTED detected — executing initialization script"
      exec python3 "$INIT_SCRIPT" --mode "$MODE"
    else
      echo "❌ Python3 not found or init script missing: $INIT_SCRIPT"
      exit 1
    fi
  else
    # Handle regular personas
    CLEANED_INPUT="${INPUT//\/$DETECTED/}"
    PROCESSOR_PATH="$PROJECT_ROOT/.super-prompt/utils/cursor-processors/enhanced_persona_processor.py"

    if command -v python3 >/dev/null 2>&1 && [[ -f "$PROCESSOR_PATH" ]]; then
      echo "-------- Persona detected: /$DETECTED — executing Python processor"
      exec python3 "$PROCESSOR_PATH" --persona "$DETECTED" --user-input "$CLEANED_INPUT" $DELEGATE_FLAG
    fi
  fi
fi

# Fallback: enforce Python core CLI directly (no Node fallback)
# Resolve project root (prefer git toplevel; fallback to CWD)
resolve_project_root() {
  if command -v git >/dev/null 2>&1; then
    if GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null); then
      printf "%s" "$GIT_ROOT"
      return 0
    fi
  fi
  printf "%s" "$(pwd)"
}

PROJECT_ROOT="$(resolve_project_root)"
PROJECT_CLI="$PROJECT_ROOT/.super-prompt/cli.py"

if [[ -f "$PROJECT_CLI" ]]; then
  echo "-------- No persona or processor unavailable — using project Python CLI"
  exec python3 "$PROJECT_CLI" optimize "$@"
fi

# Last resort: use installed wrapper if available (still executes Python)
if command -v super-prompt >/dev/null 2>&1; then
  echo "-------- Using installed super-prompt wrapper as fallback"
  exec super-prompt optimize "$@"
fi

echo "❌ Unable to locate Python CLI (.super-prompt/cli.py) or installed 'super-prompt'"
exit 1
"""
    write_text(os.path.join(base, 'tag-executor.sh'), tag_sh, dry)
    try:
        if not dry:
            os.chmod(os.path.join(base, 'tag-executor.sh'), 0o755)
    except Exception:
        pass

    personas = [
        # Core and reasoning
        ('high', '🧠 Deep Reasoning Specialist\\nStrategic problem solving and system design expert.'),
        ('architect', '👷‍♂️ Architect\\nProject-Conformity-First delivery.'),
        ('analyzer', '🔍 Root Cause Analyst\\nSystematic analysis and diagnostics.'),
        ('debate', '⚖️ Internal Debate (Positive vs Critical)\\nStructured alternating reasoning with synthesis.'),
        ('seq', '🔄 Sequential Thinking (5)\\nStructured step-by-step problem solving.'),
        ('seq-ultra', '🔄 Advanced Sequential (10)\\nIn-depth step-by-step problem solving.'),
        ('ultracompressed', '🗜️ Ultra‑Compressed Output\\nToken‑efficient answers with preserved fidelity.'),

        # Implementation teams
        ('frontend', '🎨 Frontend Design Advisor\\nUser-centered frontend design and implementation.'),
        ('frontend-ultra', '🎨 Elite UX/UI Architect\\nTop-tier user experience architecture.'),
        ('backend', '🔧 Backend Reliability Engineer\\nScalable, reliable backend systems.'),
        ('dev', '🚀 Feature Development Specialist\\nNew feature implementation and delivery specialist.'),
        ('refactorer', '🔧 Code Quality Specialist\\nMaintainability, readability, and tech debt reduction.'),

        # Ops and quality
        ('devops', '🛠️ DevOps Engineer\\nCI/CD, automation, observability, reliability.'),
        ('qa', '✅ Quality Engineer\\nTest automation and quality-driven development.'),
        ('performance', '🚀 Performance Advisor\\nHotspots, quick wins, roll‑out checks.'),
        ('security', '🔐 Security Advisor\\nThreats, mitigations, safe defaults.'),

        # Knowledge and docs
        ('mentor', '🎓 Senior Mentor\\nKnowledge transfer and skill development.'),
        ('scribe', '📝 Technical Writer\\nDeveloper docs, API docs, and communication.'),
        ('doc-master', '📚 Documentation Master\\nDocumentation architecture and verification.'),
        ('docs-refector', '📚 Documentation Consolidation\\nAudit and unify docs with MCP-grounded sources.'),

        # Utilities
        ('task', '🧩 Task Breakdown\\nSmall tasks with IDs, ACs, deps.'),
        ('wave', '🌊 Wave Planning\\nPhased delivery (MVP → hardening).'),
        ('tr', '🔧 Troubleshooter\\nExpert diagnostician for complex issues.'),
        ('specify', '🗂️ Create Feature Specification\\nSpecification First Development.'),
    ]
    for name, desc in personas:
        content = f"---\ndescription: {name} command\nrun: \"./tag-executor.sh\"\nargs: [\"${{input}} /{name}\"]\n---\n\n{desc}"
        write_text(os.path.join(base, f'{name}.md'), content, dry)

    # SDD convenience commands (spec/plan/review/tasks/implement)
    sdd_cmds = [
        (
            'spec',
            'Create SPEC (SDD)',
            "${input} /architect Create a SPEC file for this feature following SDD guidelines: goals, success criteria, scope boundaries, and user value",
        ),
        (
            'plan',
            'Create PLAN (SDD)',
            "${input} /architect Create a PLAN file for this feature following SDD guidelines: architecture, constraints, NFRs, risks, and security considerations",
        ),
        (
            'review',
            'Review against SPEC/PLAN (SDD)',
            "${input} /high Review this implementation against SDD SPEC/PLAN files and provide compliance assessment",
        ),
        (
            'tasks',
            'Break down into TASKS (SDD)',
            "${input} /architect Break work into small, testable tasks with IDs, acceptance criteria, estimates, and dependencies, referencing SPEC/PLAN",
        ),
        (
            'implement',
            'Implement minimal change (SDD)',
            "${input} /high Implement the smallest viable change based on SPEC/PLAN and tasks; output minimal diffs, tests, and docs",
        ),
    ]
    for slug, desc, arg in sdd_cmds:
        content = f"---\ndescription: {desc}\nrun: \"./tag-executor.sh\"\nargs: [\"{arg}\"]\n---\n\n{desc}"
        write_text(os.path.join(base, f'{slug}.md'), content, dry)

    # (Codex agent assets are created conditionally in write_codex_agent_assets())

def write_codex_agent_assets(dry: bool = False):
    agent_dir = os.path.join('.codex')
    os.makedirs(agent_dir, exist_ok=True)
    agent_md = """# Codex Agent — Super Prompt Integration

Use flag-based personas (no slash commands in Codex). Each persona supports a long flag and an `--sp-` alias. The `optimize` verb is optional — you can omit it:

```bash
# Frontend
super-prompt --frontend "Design a responsive layout"
super-prompt --sp-frontend "Design a responsive layout"

# Frontend Ultra
super-prompt --frontend-ultra "Create a design system architecture"
super-prompt --sp-frontend-ultra "Create a design system architecture"

# Backend
super-prompt --backend "Outline retry/idempotency for order API"
super-prompt --sp-backend "Outline retry/idempotency for order API"

# Architect
super-prompt --architect "Propose modular structure for feature X"
super-prompt --sp-architect "Propose modular structure for feature X"

# Analyzer (safe mode supports --out)
super-prompt --analyzer "Audit error handling and logging"
super-prompt --sp-analyzer --out .codex/reports/analysis.md "Audit error handling and logging"

# High reasoning
super-prompt --high "Draft a migration plan with risks"
super-prompt --sp-high "Draft a migration plan with risks"

# Sequential (Cursor-oriented, still routable)
super-prompt --seq "Refactor module into smaller units"
super-prompt --sp-seq "Refactor module into smaller units"

# Sequential Ultra
super-prompt --seq-ultra "Full-stack feature breakdown and plan"
super-prompt --sp-seq-ultra "Full-stack feature breakdown and plan"

# Debate mode
super-prompt --debate --rounds 6 "Should we adopt feature flags now?"
```

## Enhanced Advisors
super-prompt --sp-ultracompressed "Summarize design to minimal token form"
super-prompt --sp-performance "Profile and tune HTTP handler"
super-prompt --sp-security "Review auth flow for common risks"
super-prompt --sp-task "Break feature into tasks"
super-prompt --sp-wave "Propose phased delivery waves"
super-prompt --sp-docs-refector "Audit and consolidate all docs"

## SDD Workflow (flag-based)

Use these convenience flags to drive SDD tasks directly (recommended). The `optimize` verb is optional:

```bash
# Create SPEC draft for a feature (Architect persona)
super-prompt --sp-ssd-spec "User authentication system"

# Create PLAN draft from context (Architect persona)
super-prompt --sp-ssd-plan "User authentication system"

# Review implementation against SPEC/PLAN (High reasoning)
super-prompt --sp-ssd-review "Login refactor PR #123"

# Break work into TASKS (Architect persona)
super-prompt --sp-ssd-tasks "User authentication system"

# Implement minimal change (High reasoning)
super-prompt --sp-ssd-implement "User authentication system — task T-001"
```

Tips:
- Alternative style: `--persona <name>` also works (e.g., `--persona frontend`).
- Logs MUST start with `--------`; keep all content in English.

Auto Model Router (AMR: medium ↔ high):
- Start medium; plan/review/root-cause at high, then back to medium.
- If your environment does not auto-execute model switches, copy-run:
  /model gpt-5 high
  /model gpt-5 medium

State machine (per turn):
[INTENT] → [TASK_CLASSIFY] → [PLAN] → [EXECUTE] → [VERIFY] → [REPORT]

## MCP Integration (Context7)
- Auto‑detects Context7 MCP (env `CONTEXT7_MCP=1`, `context7`/`c7` on PATH, or `.context7/`).
- Planning/implementation personas include an MCP usage block to ground answers in real sources.
- Not detected? The run proceeds and prints a setup hint. After installation, export `CONTEXT7_MCP=1`.
"""
    write_text(os.path.join(agent_dir, 'agents.md'), agent_md, dry)
    # Append YAML personas catalog if present
    try:
        _y = load_personas_from_yaml()
        if _y:
            lines = ["\n## Personas (from YAML manifests)\n"]
            for p in _y:
                slug = p.get('slug') or p.get('name')
                desc = p.get('desc') or p.get('description') or p.get('title') or slug
                lines.append(f"- `{slug}` — {desc}\n")
            with open(os.path.join(agent_dir, 'agents.md'), 'a', encoding='utf-8') as f:
                f.write(''.join(lines))
    except Exception:
        pass
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

def show_ascii_logo():
    """Display ASCII logo with version info"""
    # Resolve installed package version dynamically (fallback to VERSION)
    ver = VERSION
    try:
        from pathlib import Path
        pj = Path(__file__).resolve().parents[1] / 'package.json'
        if pj.exists():
            data = json.loads(pj.read_text(encoding='utf-8'))
            v = (data.get('version') or '').strip()
            if v:
                ver = v
    except Exception:
        pass
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
\033[2m                     v{ver} | @cdw0424/super-prompt\033[0m
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

    # Upgrade: refresh assets, cleanup legacy, migrate sessions
    p_upgrade = sub.add_parser("super:upgrade", help="Upgrade project assets; cleanup legacy; migrate JSON sessions to SQLite")
    p_upgrade.add_argument("--dry-run", action="store_true", help="Preview only")

    # Help: list supported commands and usage
    p_help = sub.add_parser("super:help", help="Show Super Prompt commands and usage")
    
    p_optimize = sub.add_parser("optimize", help="Execute persona queries with SDD context")
    p_optimize.add_argument("query", nargs="*", help="Query or debate topic")
    p_optimize.add_argument("--list-personas", action="store_true")
    # Flag-based personas for Codex environment
    p_optimize.add_argument("--persona", choices=['frontend','frontend-ultra','backend','analyzer','architect','high','seq','seq-ultra','debate','docs-refector','ultracompressed','performance','security','task','wave'])
    p_optimize.add_argument("--frontend", action="store_true")
    p_optimize.add_argument("--frontend-ultra", action="store_true")
    p_optimize.add_argument("--backend", action="store_true")
    p_optimize.add_argument("--analyzer", action="store_true")
    p_optimize.add_argument("--sp-analyzer", action="store_true", help="Alias for --analyzer with safe output mode")
    p_optimize.add_argument("--architect", action="store_true")
    p_optimize.add_argument("--high", action="store_true")
    p_optimize.add_argument("--seq", action="store_true")
    p_optimize.add_argument("--seq-ultra", action="store_true")
    p_optimize.add_argument("--debate", action="store_true")
    p_optimize.add_argument("--dev", action="store_true")
    p_optimize.add_argument("--tr", action="store_true")
    p_optimize.add_argument("--db-expert", action="store_true")
    p_optimize.add_argument("--db-refector", action="store_true")
    p_optimize.add_argument("--docs-refector", action="store_true")
    p_optimize.add_argument("--ultracompressed", action="store_true")
    p_optimize.add_argument("--performance", action="store_true")
    p_optimize.add_argument("--security", action="store_true")
    p_optimize.add_argument("--task", action="store_true")
    p_optimize.add_argument("--wave", action="store_true")

    # New shortcut flags (super-prompt prefix)
    p_optimize.add_argument("--sp-architect", action="store_true", help="Shortcut for architect persona")
    p_optimize.add_argument("--sp-frontend", action="store_true", help="Shortcut for frontend persona")
    p_optimize.add_argument("--sp-frontend-ultra", action="store_true", help="Shortcut for frontend-ultra persona")
    p_optimize.add_argument("--sp-backend", action="store_true", help="Shortcut for backend persona")
    p_optimize.add_argument("--sp-high", action="store_true", help="Shortcut for high persona")
    p_optimize.add_argument("--sp-seq", action="store_true", help="Shortcut for seq persona")
    p_optimize.add_argument("--sp-seq-ultra", action="store_true", help="Shortcut for seq-ultra persona")
    p_optimize.add_argument("--sp-dev", action="store_true", help="Shortcut for Feature Development Specialist")
    p_optimize.add_argument("--sp-tr", action="store_true", help="Shortcut for Troubleshooter")
    p_optimize.add_argument("--sp-db-expert", action="store_true", help="Shortcut for db-expert persona")
    p_optimize.add_argument("--sp-db-refector", action="store_true", help="Alias for db-expert persona")
    p_optimize.add_argument("--sp-docs-refector", action="store_true", help="Shortcut for docs-refector persona")
    p_optimize.add_argument("--sp-ultracompressed", action="store_true", help="Shortcut for ultracompressed persona")
    p_optimize.add_argument("--sp-performance", action="store_true", help="Shortcut for performance persona")
    p_optimize.add_argument("--sp-security", action="store_true", help="Shortcut for security persona")
    p_optimize.add_argument("--sp-task", action="store_true", help="Shortcut for task persona")
    p_optimize.add_argument("--sp-wave", action="store_true", help="Shortcut for wave persona")

    # SDD shortcuts
    p_optimize.add_argument("--sp-ssd-spec", action="store_true", help="SDD SPEC creation shortcut")
    p_optimize.add_argument("--sp-ssd-plan", action="store_true", help="SDD PLAN creation shortcut")
    p_optimize.add_argument("--sp-ssd-review", action="store_true", help="SDD implementation review shortcut")
    p_optimize.add_argument("--sp-ssd-tasks", action="store_true", help="SDD TASKS breakdown shortcut")
    p_optimize.add_argument("--sp-ssd-implement", action="store_true", help="SDD IMPLEMENT execution shortcut")
    p_optimize.add_argument("--rounds", type=int, default=8, help="Debate rounds (2-20)")
    p_optimize.add_argument("--out", help="When used with --sp-analyzer, save prompt to this file (e.g., .codex/reports/analysis.md)")

    # AMR commands
    p_amr_rules = sub.add_parser("amr:rules", help="Generate AMR rule file (05-amr.mdc)")
    p_amr_rules.add_argument("--out", default=".cursor/rules", help="Rules directory")
    p_amr_rules.add_argument("--dry-run", action="store_true")

    p_amr_print = sub.add_parser("amr:print", help="Print AMR bootstrap prompt to stdout")
    p_amr_print.add_argument("--path", default="prompts/codex_amr_bootstrap_prompt_en.txt", help="Prompt file path")

    p_amr_qa = sub.add_parser("amr:qa", help="Validate a transcript for AMR/state-machine conformance")
    p_amr_qa.add_argument("file", help="Transcript/text file to check")

    # SDD workflow commands (explicit subcommands)
    p_sdd = sub.add_parser("sdd", help="SDD workflow shortcuts: spec, plan, review, tasks, implement")
    sdd_sub = p_sdd.add_subparsers(dest="sdd_cmd")
    for sdd_cmd, help_text in [
        ('spec', 'Create SPEC draft'),
        ('plan', 'Create PLAN draft'),
        ('review', 'Review against SPEC/PLAN'),
        ('tasks', 'Break down into TASKS'),
        ('implement', 'Implement minimal change'),
    ]:
        p = sdd_sub.add_parser(sdd_cmd, help=help_text)
        p.add_argument('query', nargs='*', help='Topic or context')

    # Codex-only setup (write .codex/* without Cursor assets)
    p_codex_init = sub.add_parser("codex:init", help="Create Codex CLI assets in .codex/ (agents.md, personas.py, bootstrap, router-check)")
    p_codex_init.add_argument("--dry-run", action="store_true")

    # Smart routing: 'optimize' is the default action.
    raw_argv = sys.argv[1:]
    known_cmds = {"super:init", "super:upgrade", "super:help", "optimize", "amr:rules", "amr:print", "amr:qa", "codex:init", "personas:init", "personas:build", "sdd"}
    if not raw_argv:
        args = parser.parse_args(["optimize", "--list-personas"])
    elif raw_argv and raw_argv[0] in known_cmds:
        args = parser.parse_args(raw_argv)
    else:
        args = parser.parse_args(["optimize", *raw_argv])

    # Set global CURRENT_CMD
    global CURRENT_CMD
    CURRENT_CMD = args.cmd

    # Load scaffold module (runtime import with fallback)
    global scaffold
    try:
        from utils import project_scaffold as scaffold_module
        scaffold = scaffold_module
    except Exception:
        scaffold = None

    if args.cmd == "super:init":
        show_ascii_logo()
        print("\033[33m\033[1m🚀 Initializing project setup...\033[0m\n")
        # Check project SDD status
        sdd_context = get_project_sdd_context()
        print(f"\033[32m✓\033[0m \033[1mStep 1:\033[0m Framework detection completed")
        print(f"   \033[2m→ Detected: {sdd_context['frameworks']}\033[0m")
        print(f"   \033[2m→ SDD Status: {'✅ SPEC/PLAN found' if sdd_context['sdd_compliance'] else '⚠️  Missing SPEC/PLAN'}\033[0m\n")
        
        # Try to delegate core init if available (reduce duplication)
        delegated = False
        try:
            core_cli = os.path.join(os.getcwd(), 'packages', 'core-py', 'super_prompt', 'cli.py')
            if os.path.exists(core_cli):
                print("\033[36m🤝 Delegating init to core CLI (packages/core-py)...\033[0m")
                res = subprocess.run(["python3", core_cli, "init"], check=False)
                delegated = (res.returncode == 0)
        except Exception:
            delegated = False

        if not delegated:
            # Generate SDD rules (fallback)
            print("\033[36m📋 Generating Cursor rules...\033[0m")
            rules_dir = (scaffold.generate_sdd_rules_files(args.out, args.dry_run) if scaffold else generate_sdd_rules_files(args.out, args.dry_run))
            print(f"\033[32m✓\033[0m \033[1mStep 2:\033[0m Rule files created")
            print(f"   \033[2m→ Location: {rules_dir}\033[0m\n")
            
            # Install Cursor commands (fallback)
            print("\033[36m⚡ Setting up Cursor slash commands...\033[0m")
            (scaffold.install_cursor_commands_in_project(args.dry_run) if scaffold else install_cursor_commands_in_project(args.dry_run))
            print(f"\033[32m✓\033[0m \033[1mStep 3:\033[0m Slash commands installed")
            print("   \033[2m→ Available: /frontend /backend /architect /analyzer /seq /seq-ultra /high /frontend-ultra /debate /ultracompressed /performance /security /task /wave /docs-refector /db-expert /spec /plan /review /tasks /implement\033[0m\n")
        else:
            print("\033[32m✓\033[0m \033[1mStep 2/3:\033[0m Delegated to core init (rules & commands)")

        # Step 3.5: Install pinned dev deps for LTM helpers (best-effort)
        try:
            print("\033[36m🧩 Installing dev dependencies (pinned) for LTM helpers...\033[0m")
            pinned = [
                "better-sqlite3@12.2.0",
                "ajv@8.17.1",
                "zod@4.1.8",
                "ioredis@5.7.0",
            ]
            override = os.environ.get('SUPER_PROMPT_LTM_PKGS')
            pkgs = override.split() if override else pinned
            subprocess.run(["npm", "install", "-D", *pkgs], check=False)
            print(f"\033[32m✓\033[0m \033[1mStep 3.5:\033[0m Dev dependencies installed (best-effort)\n")
        except Exception as e:
            print(f"\033[33m⚠️  Skipped dev dependency install: {e}\033[0m\n")

        # Step 3.6: Add /init-sp and /re-init-sp Cursor commands
        try:
            cmd_dir = os.path.join(os.getcwd(), '.cursor', 'commands', 'super-prompt')
            os.makedirs(cmd_dir, exist_ok=True)
            init_sp_md = os.path.join(cmd_dir, 'init-sp.md')
            reinit_sp_md = os.path.join(cmd_dir, 're-init-sp.md')
            init_sp_content = """---
description: Initialize Super Prompt memory (project analysis)
run: "python3"
args: [".super-prompt/utils/init/init_sp.py", "--mode", "init"]
---

🧭 Initialize Super Prompt memory with project structure snapshot.
"""
            reinit_sp_content = """---
description: Re-Initialize project analysis (refresh memory)
run: "python3"
args: [".super-prompt/utils/init/init_sp.py", "--mode", "reinit"]
---

🔄 Refresh project analysis and update memory.
"""
            write_text(init_sp_md, init_sp_content, dry=args.dry_run)
            write_text(reinit_sp_md, reinit_sp_content, dry=args.dry_run)
            print(f"\033[32m✓\033[0m \033[1mStep 3.6:\033[0m Init commands installed (/init-sp, /re-init-sp)\n")
        except Exception as e:
            print(f"\033[33m⚠️  Could not write init commands: {e}\033[0m\n")

        # Step 3.7: Legacy cleanup and JSON→SQLite migration
        try:
            print("\033[36m🧹 Cleaning legacy assets and migrating sessions...\033[0m")
            # Backup existing SQLite DB (non-destructive)
            try:
                db_path = os.path.join(os.getcwd(), 'memory', 'ltm.db')
                if os.path.exists(db_path):
                    bdir = os.path.join(os.getcwd(), 'memory', 'backup')
                    os.makedirs(bdir, exist_ok=True)
                    ts = int(__import__('time').time())
                    bpath = os.path.join(bdir, f'ltm-{ts}.db')
                    shutil.copy2(db_path, bpath)
                    print(f"   \033[2m→ Backed up DB to {bpath}\033[0m")
            except Exception:
                pass
            legacy_dir = os.path.join(os.getcwd(), 'legacy', f"cleanup-{int(__import__('time').time())}")
            os.makedirs(legacy_dir, exist_ok=True)
            # Move old Python command files under Cursor
            sp_cmd_dir = os.path.join(os.getcwd(), '.cursor', 'commands', 'super-prompt')
            moved = 0
            if os.path.isdir(sp_cmd_dir):
                for name in os.listdir(sp_cmd_dir):
                    if name.endswith('.py'):
                        src = os.path.join(sp_cmd_dir, name)
                        dst_dir = os.path.join(legacy_dir, 'cursor-commands')
                        os.makedirs(dst_dir, exist_ok=True)
                        shutil.move(src, os.path.join(dst_dir, name))
                        moved += 1
                # remove deprecated re-init
                dep = os.path.join(sp_cmd_dir, 're-init.md')
                if os.path.exists(dep):
                    dst_dir = os.path.join(legacy_dir, 'deprecated')
                    os.makedirs(dst_dir, exist_ok=True)
                    shutil.move(dep, os.path.join(dst_dir, os.path.basename(dep)))
            if moved:
                print(f"   \033[2m→ Moved {moved} legacy command scripts to {legacy_dir}\033[0m")

            # Migrate JSON sessions → SQLite
            sys.path.append(os.path.join(os.getcwd(), '.super-prompt', 'utils'))
            migrated_files = 0
            try:
                from fallback_memory import MemoryController  # type: ignore
                mem = MemoryController(os.getcwd())
                sessions_dir = os.path.join(os.getcwd(), 'memory', 'sessions')
                if os.path.isdir(sessions_dir):
                    for name in os.listdir(sessions_dir):
                        if not name.endswith('.json'):
                            continue
                        src = os.path.join(sessions_dir, name)
                        try:
                            with open(src, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                        except Exception:
                            continue
                        # import chat history
                        hist = data.get('full_chat_history') or []
                        i = 0
                        while i < len(hist):
                            role = (hist[i].get('role') or '').lower()
                            content = hist[i].get('content') or ''
                            if role == 'user':
                                if i + 1 < len(hist) and (hist[i+1].get('role') or '').lower() == 'assistant':
                                    mem.append_interaction(content, hist[i+1].get('content') or '')
                                    i += 2
                                else:
                                    mem.append_interaction(content, None)
                                    i += 1
                            elif role == 'assistant':
                                mem.append_interaction('', content)
                                i += 1
                            else:
                                i += 1
                        # import key memories and entities
                        ex = {}
                        km = ((data.get('core_memory') or {}).get('key_memories')) or []
                        if isinstance(km, list) and km:
                            ex['key_memories'] = [ (k.get('content') if isinstance(k, dict) else str(k)) for k in km ]
                        ents = ((data.get('core_memory') or {}).get('entities')) or {}
                        if isinstance(ents, dict) and ents:
                            ex['entities'] = ents
                        if ex:
                            mem.update_from_extraction(ex)
                        # move file
                        dst_dir = os.path.join(legacy_dir, 'migrated-sessions')
                        os.makedirs(dst_dir, exist_ok=True)
                        shutil.move(src, os.path.join(dst_dir, name))
                        migrated_files += 1
            except Exception:
                pass
            print(f"\033[32m✓\033[0m \033[1mStep 3.7:\033[0m Legacy cleanup done; migrated {migrated_files} session file(s)\n")
        except Exception as e:
            print(f"\033[33m⚠️  Legacy cleanup/migration skipped: {e}\033[0m\n")
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
        print("   \033[2mFrom CLI:\033[0m \033[36msuper-prompt --frontend \"design strategy\"\033[0m")
        print("")
        print("\033[32m✨ Ready for next-level prompt engineering!\033[0m")
        return 0

    elif args.cmd == "super:upgrade":
        show_ascii_logo()
        print("\033[33m\033[1m🔧 Upgrading project setup...\033[0m\n")

        # 1) Refresh rules
        try:
            print("\033[36m📋 Refreshing Cursor rules...\033[0m")
            rules_dir = generate_sdd_rules_files(".cursor/rules", getattr(args, 'dry_run', False))
            print(f"\033[32m✓\033[0m \033[1mStep 1:\033[0m Rule files refreshed")
            print(f"   \033[2m→ Location: {rules_dir}\033[0m\n")
        except Exception as e:
            print(f"\033[33m⚠️  Rules refresh skipped: {e}\033[0m\n")

        # 2) Update Cursor commands
        try:
            print("\033[36m⚡ Updating Cursor slash commands...\033[0m")
            install_cursor_commands_in_project(getattr(args, 'dry_run', False))
            print(f"\033[32m✓\033[0m \033[1mStep 2:\033[0m Slash commands updated\n")
        except Exception as e:
            print(f"\033[33m⚠️  Command update skipped: {e}\033[0m\n")

        # 3) Ensure pinned dev deps
        try:
            print("\033[36m🧩 Ensuring dev dependencies (pinned) for LTM helpers...\033[0m")
            pinned = [
                "better-sqlite3@12.2.0",
                "ajv@8.17.1",
                "zod@4.1.8",
                "ioredis@5.7.0",
            ]
            override = os.environ.get('SUPER_PROMPT_LTM_PKGS')
            pkgs = override.split() if override else pinned
            subprocess.run(["npm", "install", "-D", *pkgs], check=False)
            print(f"\033[32m✓\033[0m \033[1mStep 3:\033[0m Dev dependencies ensured\n")
        except Exception as e:
            print(f"\033[33m⚠️  Dev dependency install skipped: {e}\033[0m\n")

        # 4) Ensure /init-sp and /re-init-sp
        try:
            cmd_dir = os.path.join(os.getcwd(), '.cursor', 'commands', 'super-prompt')
            os.makedirs(cmd_dir, exist_ok=True)
            init_sp_md = os.path.join(cmd_dir, 'init-sp.md')
            reinit_sp_md = os.path.join(cmd_dir, 're-init-sp.md')
            if not os.path.exists(init_sp_md):
                write_text(init_sp_md, """---
description: Initialize Super Prompt memory (project analysis)
run: "python3"
args: [".super-prompt/utils/init/init_sp.py", "--mode", "init"]
---

🧭 Initialize Super Prompt memory with project structure snapshot.
""", dry=getattr(args, 'dry_run', False))
            if not os.path.exists(reinit_sp_md):
                write_text(reinit_sp_md, """---
description: Re-Initialize project analysis (refresh memory)
run: "python3"
args: [".super-prompt/utils/init/init_sp.py", "--mode", "reinit"]
---

🔄 Refresh project analysis and update memory.
""", dry=getattr(args, 'dry_run', False))
            print(f"\033[32m✓\033[0m \033[1mStep 4:\033[0m Init commands ensured (/init-sp, /re-init-sp)\n")
        except Exception as e:
            print(f"\033[33m⚠️  Could not ensure init commands: {e}\033[0m\n")

        # 5) Legacy cleanup & JSON→SQLite migration
        try:
            print("\033[36m🧹 Cleaning legacy assets and migrating sessions...\033[0m")
            # Backup existing SQLite DB (non-destructive)
            try:
                db_path = os.path.join(os.getcwd(), 'memory', 'ltm.db')
                if os.path.exists(db_path):
                    bdir = os.path.join(os.getcwd(), 'memory', 'backup')
                    os.makedirs(bdir, exist_ok=True)
                    ts = int(__import__('time').time())
                    bpath = os.path.join(bdir, f'ltm-{ts}.db')
                    shutil.copy2(db_path, bpath)
                    print(f"   \033[2m→ Backed up DB to {bpath}\033[0m")
            except Exception:
                pass
            legacy_dir = os.path.join(os.getcwd(), 'legacy', f"cleanup-{int(__import__('time').time())}")
            os.makedirs(legacy_dir, exist_ok=True)
            sp_cmd_dir = os.path.join(os.getcwd(), '.cursor', 'commands', 'super-prompt')
            moved = 0
            if os.path.isdir(sp_cmd_dir):
                for name in os.listdir(sp_cmd_dir):
                    if name.endswith('.py'):
                        src = os.path.join(sp_cmd_dir, name)
                        dst_dir = os.path.join(legacy_dir, 'cursor-commands')
                        os.makedirs(dst_dir, exist_ok=True)
                        shutil.move(src, os.path.join(dst_dir, name))
                        moved += 1
                dep = os.path.join(sp_cmd_dir, 're-init.md')
                if os.path.exists(dep):
                    dst_dir = os.path.join(legacy_dir, 'deprecated')
                    os.makedirs(dst_dir, exist_ok=True)
                    shutil.move(dep, os.path.join(dst_dir, os.path.basename(dep)))
            if moved:
                print(f"   \033[2m→ Moved {moved} legacy command scripts to {legacy_dir}\033[0m")

            # Session migration
            sys.path.append(os.path.join(os.getcwd(), '.super-prompt', 'utils'))
            migrated_files = 0
            try:
                from fallback_memory import MemoryController  # type: ignore
                mem = MemoryController(os.getcwd())
                sessions_dir = os.path.join(os.getcwd(), 'memory', 'sessions')
                if os.path.isdir(sessions_dir):
                    for name in os.listdir(sessions_dir):
                        if not name.endswith('.json'):
                            continue
                        src = os.path.join(sessions_dir, name)
                        try:
                            with open(src, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                        except Exception:
                            continue
                        hist = data.get('full_chat_history') or []
                        i = 0
                        while i < len(hist):
                            role = (hist[i].get('role') or '').lower()
                            content = hist[i].get('content') or ''
                            if role == 'user':
                                if i + 1 < len(hist) and (hist[i+1].get('role') or '').lower() == 'assistant':
                                    mem.append_interaction(content, hist[i+1].get('content') or '')
                                    i += 2
                                else:
                                    mem.append_interaction(content, None)
                                    i += 1
                            elif role == 'assistant':
                                mem.append_interaction('', content)
                                i += 1
                            else:
                                i += 1
                        ex = {}
                        km = ((data.get('core_memory') or {}).get('key_memories')) or []
                        if isinstance(km, list) and km:
                            ex['key_memories'] = [ (k.get('content') if isinstance(k, dict) else str(k)) for k in km ]
                        ents = ((data.get('core_memory') or {}).get('entities')) or {}
                        if isinstance(ents, dict) and ents:
                            ex['entities'] = ents
                        if ex:
                            mem.update_from_extraction(ex)
                        dst_dir = os.path.join(legacy_dir, 'migrated-sessions')
                        os.makedirs(dst_dir, exist_ok=True)
                        shutil.move(src, os.path.join(dst_dir, name))
                        migrated_files += 1
            except Exception:
                pass
            print(f"\033[32m✓\033[0m \033[1mStep 5:\033[0m Legacy cleanup done; migrated {migrated_files} session file(s)\n")
        except Exception as e:
            print(f"\033[33m⚠️  Legacy cleanup/migration skipped: {e}\033[0m\n")

        print("\033[32m\033[1m🎉 Upgrade Complete!\033[0m\n")
        return 0

    elif args.cmd == "super:help":
        show_ascii_logo()
        print("\033[33m\033[1m🧭 Super Prompt — Commands & Usage\033[0m\n")
        # Dynamic environment status
        def has_cmd(cmd):
            try:
                subprocess.run([cmd, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                return True
            except Exception:
                return False
        # Python
        py_ok = sys.version_info >= (3,7)
        print(f"Python: {'✅' if py_ok else '❌'} {sys.version.split()[0]}")
        # SQLite3 & FTS5
        try:
            import sqlite3
            con = sqlite3.connect(":memory:")
            cur = con.cursor()
            fts5_ok = True
            try:
                cur.execute("CREATE VIRTUAL TABLE t_fts USING fts5(content);")
            except Exception:
                fts5_ok = False
            print(f"SQLite3: ✅ module {sqlite3.sqlite_version} | FTS5: {'✅' if fts5_ok else '⚠️  no'}")
        except Exception as e:
            print(f"SQLite3: ❌ ({e})")
        # Codex CLI
        codex_ok = has_cmd('codex')
        print(f"Codex CLI: {'✅' if codex_ok else '⚠️  not found'}")
        print("")
        print("\033[36mSetup\033[0m")
        print("  super-prompt super:init         # Initialize rules, commands; cleanup; migrate JSON→SQLite")
        print("  super-prompt super:upgrade      # Refresh assets; cleanup legacy; migrate JSON→SQLite\n")

        print("\033[36mPersonas (Cursor slash tags)\033[0m")
        print("  /architect /frontend /backend /analyzer /security /performance /mentor /refactorer /qa /devops /scribe /doc-master /dev /tr")
        print("  Tips: add /delegate to force deep reasoning via Codex (GPT-5)\n")

        print("\033[36mSDD Workflow\033[0m")
        print("  /specify     # Create SPEC draft")
        print("  /plan        # Create PLAN draft")
        print("  /tasks       # Create TASK breakdown")
        print("  /implement   # Execute minimal change (with gates)\n")

        print("\033[36mProject Analysis\033[0m")
        print("  /init-sp     # Analyze current project → store in SQLite (memory/ltm.db)")
        print("  /re-init-sp  # Refresh analysis → store in SQLite\n")

        print("\033[36mQuality & Safety\033[0m")
        print("  - Global rules: clarify-or-assume, Plan→Execute→Review, no CoT exposure, log prefix '--------'")
        print("  - Secrets masked (sk-***), minimal diffs, idempotent migrations\n")

        print("\033[36mEnvironment Notes\033[0m")
        print("  - Requires Python 3 & SQLite3 (auto-install attempted on install.js)")
        print("  - Codex CLI auto-updates before deep reasoning delegation\n")

        print("\033[36mExamples\033[0m")
        print("  super-prompt optimize \"Design the system /architect\"")
        print("  super-prompt optimize \"Investigate slowness /analyzer /delegate\"")
        print("  super-prompt super:init   &&  /init-sp")
        print("  npm i -g @cdw0424/super-prompt@latest && super-prompt super:upgrade\n")
        return 0
        
    elif args.cmd == "optimize":
        print_mcp_banner()
        optimizer = PromptOptimizer()
        
        if hasattr(args, 'list_personas') and args.list_personas:
            print("🚀 Super Prompt - Available Personas:")
            for persona, config in optimizer.PERSONAS.items():
                print(f"  /{persona:<15} - {config['desc']}")
            return 0
        
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
            # Original flags
            for flag, tag in [
                ('frontend_ultra','frontend-ultra'),
                ('frontend','frontend'),
                ('backend','backend'),
                ('sp_analyzer','analyzer'),
                ('analyzer','analyzer'),
                ('architect','architect'),
                ('high','high'),
                ('seq_ultra','seq-ultra'),
                ('seq','seq'),
                ('debate','debate'),
                ('docs_refector','docs-refector'),
                ('ultracompressed','ultracompressed'),
                ('performance','performance'),
                ('security','security'),
                ('task','task'),
                ('wave','wave'),
            ]:
                if getattr(args, flag, False):
                    query_text += f" /{tag}"
                    break

            # New shortcut flags (super-prompt prefix)
            for flag, tag in [
                ('sp_architect','architect'),
                ('sp_frontend','frontend'),
                ('sp_frontend_ultra','frontend-ultra'),
                ('sp_backend','backend'),
                ('sp_high','high'),
                ('sp_seq','seq'),
                ('sp_seq_ultra','seq-ultra'),
                ('sp_docs_refector','docs-refector'),
                ('sp_ultracompressed','ultracompressed'),
                ('sp_performance','performance'),
                ('sp_security','security'),
                ('sp_task','task'),
                ('sp_wave','wave'),
            ]:
                if getattr(args, flag, False):
                    query_text += f" /{tag}"
                    break

            # SDD shortcuts with pre-built queries
            if getattr(args, 'sp_ssd_spec', False):
                query_text += " /architect Create a SPEC file for this feature following SDD guidelines: goals, success criteria, scope boundaries, and user value"
            elif getattr(args, 'sp_ssd_plan', False):
                query_text += " /architect Create a PLAN file for this feature following SDD guidelines: architecture, constraints, NFRs, risks, and security considerations"
            elif getattr(args, 'sp_ssd_review', False):
                query_text += " /high Review this implementation against SDD SPEC/PLAN files and provide compliance assessment"
            elif getattr(args, 'sp_ssd_tasks', False):
                query_text += " /architect Break work into small, testable tasks with IDs, acceptance criteria, estimates, and dependencies, referencing SPEC/PLAN"
            elif getattr(args, 'sp_ssd_implement', False):
                query_text += " /high Implement the smallest viable change based on SPEC/PLAN and tasks; output minimal diffs, tests, and docs"
        if getattr(args, 'debate', False) and getattr(args, 'rounds', None):
            query_text += f" --rounds {int(args.rounds)}"
        # Try to delegate optimize to core CLI if available
        try:
            core_cli = os.path.join(os.getcwd(), 'packages', 'core-py', 'super_prompt', 'cli.py')
            if os.path.exists(core_cli):
                res = subprocess.run(["python3", core_cli, "optimize", query_text], check=False)
                if res.returncode == 0:
                    return 0
        except Exception:
            pass

        print("❌ Core CLI not available. Please install/use the core CLI or run via Cursor.")
        print("   - Python core: pip install super-prompt-core && python -m super_prompt.cli optimize ...")
        print("   - Cursor: use slash commands (e.g., /architect, /frontend)")
        return 1
    elif args.cmd == "amr:rules":
        # Delegate to core if available
        try:
            core_cli = os.path.join(os.getcwd(), 'packages', 'core-py', 'super_prompt', 'cli.py')
            if os.path.exists(core_cli):
                res = subprocess.run(["python3", core_cli, "amr-rules", "--out", args.out], check=False)
                if res.returncode == 0:
                    return 0
        except Exception:
            pass
        print("❌ Core CLI not available to generate AMR rules.")
        return 1
    elif args.cmd == "amr:print":
        # Delegate to core if available
        try:
            core_cli = os.path.join(os.getcwd(), 'packages', 'core-py', 'super_prompt', 'cli.py')
            if os.path.exists(core_cli):
                p = getattr(args, 'path', 'prompts/codex_amr_bootstrap_prompt_en.txt')
                res = subprocess.run(["python3", core_cli, "amr-print", "--path", p], check=False)
                if res.returncode == 0:
                    return 0
        except Exception:
            pass
        print("❌ Core CLI not available to print AMR bootstrap.")
        return 1
    elif args.cmd == "amr:qa":
        # Delegate to core if available
        try:
            core_cli = os.path.join(os.getcwd(), 'packages', 'core-py', 'super_prompt', 'cli.py')
            if os.path.exists(core_cli):
                res = subprocess.run(["python3", core_cli, "amr-qa", args.file], check=False)
                if res.returncode == 0:
                    return 0
        except Exception:
            pass
        print("❌ Core CLI not available to run AMR QA.")
        return 1
    elif args.cmd == "codex:init":
        # Delegate to core
        try:
            core_cli = os.path.join(os.getcwd(), 'packages', 'core-py', 'super_prompt', 'cli.py')
            if os.path.exists(core_cli):
                res = subprocess.run(["python3", core_cli, "codex-init"], check=False)
                if res.returncode == 0:
                    return 0
        except Exception:
            pass
        print("❌ Core CLI not available to init Codex assets.")
        return 1
    elif args.cmd == "personas:init":
        # Delegate to core
        try:
            core_cli = os.path.join(os.getcwd(), 'packages', 'core-py', 'super_prompt', 'cli.py')
            if os.path.exists(core_cli):
                argv = ["python3", core_cli, "personas-init"]
                if '--overwrite' in sys.argv:
                    argv.append("--overwrite")
                res = subprocess.run(argv, check=False)
                if res.returncode == 0:
                    return 0
        except Exception:
            pass
        print("❌ Core CLI not available to init personas manifest.")
        return 1
    elif args.cmd == "personas:build":
        # Delegate to core
        try:
            core_cli = os.path.join(os.getcwd(), 'packages', 'core-py', 'super_prompt', 'cli.py')
            if os.path.exists(core_cli):
                res = subprocess.run(["python3", core_cli, "personas-build"], check=False)
                if res.returncode == 0:
                    return 0
        except Exception:
            pass
        print("❌ Core CLI not available to build personas.")
        return 1
    elif args.cmd == 'sdd':
        print_mcp_banner()
        if not getattr(args, 'sdd_cmd', None):
            print("❌ Usage: super-prompt sdd <spec|plan|review|tasks|implement> \"topic...\"")
            return 2
        topic = ' '.join(getattr(args, 'query', [])).strip()
        if not topic:
            print("❌ Provide a topic/context. Example: super-prompt sdd spec \"user authentication\"")
            return 2
        # Try to delegate SDD to core CLI
        try:
            core_cli = os.path.join(os.getcwd(), 'packages', 'core-py', 'super_prompt', 'cli.py')
            if os.path.exists(core_cli):
                res = subprocess.run(["python3", core_cli, "sdd", args.sdd_cmd, topic], check=False)
                if res.returncode == 0:
                    return 0
        except Exception:
            pass
        print("❌ Core CLI not available for SDD commands. Use Cursor or install super-prompt-core.")
        return 1
    
    log(f"Unknown command: {args.cmd}")
    return 2

if __name__ == "__main__":
    sys.exit(main())
