#!/usr/bin/env python3
"""
Super Prompt - Simplified CLI Implementation
All functionality in a single file to avoid import issues
"""

import argparse, glob, os, sys, re, json, datetime, textwrap, subprocess, shutil
from typing import Dict, List, Optional

VERSION = "1.0.0"

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

    # tag-executor.sh wrapper
    tag_sh = """#!/usr/bin/env bash
set -euo pipefail
if command -v super-prompt >/dev/null 2>&1; then
  exec super-prompt optimize "$@"
else
  exec npx @cdw0424/super-prompt optimize "$@"
fi
"""
    write_text(os.path.join(base, 'tag-executor.sh'), tag_sh, dry)
    try:
        if not dry:
            os.chmod(os.path.join(base, 'tag-executor.sh'), 0o755)
    except Exception:
        pass

    personas = [
        ('high', '🧠 Deep Reasoning Specialist\\nStrategic problem solving and system design expert.'),
        ('frontend-ultra', '🎨 Elite UX/UI Architect\\nTop-tier user experience architecture.'),
        ('frontend', '🎨 Frontend Design Advisor\\nUser-centered frontend design and implementation.'),
        ('backend', '🔧 Backend Reliability Engineer\\nScalable, reliable backend systems.'),
        ('analyzer', '🔍 Root Cause Analyst\\nSystematic analysis and diagnostics.'),
        ('architect', '👷‍♂️ Architect\\nProject-Conformity-First delivery.'),
        ('seq', '🔄 Sequential Thinking (5)\\nStructured step-by-step problem solving.'),
        ('seq-ultra', '🔄 Advanced Sequential (10)\\nIn-depth step-by-step problem solving.'),
    ]
    for name, desc in personas:
        content = f"---\ndescription: {name} command\nrun: \"./tag-executor.sh\"\nargs: [\"${{input}} /{name}\"]\n---\n\n{desc}"
        write_text(os.path.join(base, f'{name}.md'), content, dry)

    # Codex agent config (flag-based personas, English only)
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
    write_text(os.path.join(agent_dir, 'agent.md'), agent_md, dry)

    # Provide AMR helper templates as static commands (no runner required)
    amr_plan_md = """---
description: AMR PLAN template
---
/model gpt-5 high
--------router: switch to high (reason=deep_planning)

[Goal]
- …
[Plan]
- …
[Risk/Trade‑offs]
- …
[Test/Verify]
- Commands:
  ```bash
  npm ci
  npm test -- --watchAll=false
  ```
[Rollback]
- …
"""
    write_text(os.path.join(base, 'amr-plan.md'), amr_plan_md, dry)

    amr_exec_md = """---
description: AMR EXECUTION template
---
/model gpt-5 medium
--------router: back to medium (reason=execution)

[Diffs]
```diff
--- a/path
+++ b/path
@@
- old
+ new
```
[Commands]
```bash
--------run: npm run build && npm test -- --watchAll=false
```
"""
    write_text(os.path.join(base, 'amr-exec.md'), amr_exec_md, dry)

def show_ascii_logo():
    """Display ASCII logo with version info"""
    logo = """
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
\033[2m              Cursor-first Prompt Engineering Toolkit\033[0m
\033[2m                     v1.0.4 | @cdw0424/super-prompt\033[0m
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
    p_optimize.add_argument("--persona", choices=['frontend','frontend-ultra','backend','analyzer','architect','high','seq','seq-ultra','debate'])
    p_optimize.add_argument("--frontend", action="store_true")
    p_optimize.add_argument("--frontend-ultra", action="store_true")
    p_optimize.add_argument("--backend", action="store_true")
    p_optimize.add_argument("--analyzer", action="store_true")
    p_optimize.add_argument("--architect", action="store_true")
    p_optimize.add_argument("--high", action="store_true")
    p_optimize.add_argument("--seq", action="store_true")
    p_optimize.add_argument("--seq-ultra", action="store_true")
    p_optimize.add_argument("--debate", action="store_true")
    p_optimize.add_argument("--rounds", type=int, default=8, help="Debate rounds (2-20)")

    # AMR commands
    p_amr_rules = sub.add_parser("amr:rules", help="Generate AMR rule file (05-amr.mdc)")
    p_amr_rules.add_argument("--out", default=".cursor/rules", help="Rules directory")
    p_amr_rules.add_argument("--dry-run", action="store_true")

    p_amr_print = sub.add_parser("amr:print", help="Print AMR bootstrap prompt to stdout")
    p_amr_print.add_argument("--path", default="prompts/codex_amr_bootstrap_prompt_en.txt", help="Prompt file path")

    p_amr_qa = sub.add_parser("amr:qa", help="Validate a transcript for AMR/state-machine conformance")
    p_amr_qa.add_argument("file", help="Transcript/text file to check")

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
        print("   \033[2m→ Available: /frontend /backend /architect /analyzer /seq /seq-ultra /high /frontend-ultra\033[0m\n")
        
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
            ]:
                if getattr(args, flag, False):
                    query_text += f" /{tag}"
                    break
        if getattr(args, 'debate', False) and getattr(args, 'rounds', None):
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
    
    log(f"Unknown command: {args.cmd}")
    return 2

if __name__ == "__main__":
    sys.exit(main())
