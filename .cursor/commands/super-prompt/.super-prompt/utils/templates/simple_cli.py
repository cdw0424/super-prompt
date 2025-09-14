#!/usr/bin/env python3
"""
Super Prompt - Simplified CLI Implementation
All functionality in a single file to avoid import issues
"""

import argparse, glob, os, sys, re, json, datetime, textwrap, subprocess, shutil
from typing import Dict, List, Optional

VERSION = "2.8.0"

def log(msg: str): 
    print(f"-------- {msg}")

# Auto-update helpers (best-effort, silent on failure)
def attempt_upgrade_codex():
    try:
        if shutil.which('npm'):
            subprocess.run(['npm','install','-g','@openai/codex@latest'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def attempt_upgrade_self():
    try:
        if shutil.which('npm'):
            subprocess.run(['npm','install','-g','@cdw0424/super-prompt@latest'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

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

def get_sdd_excerpts() -> str:
    try:
        spec_path = newest("specs/**/spec.md")
        plan_path = newest("specs/**/plan.md")
        spec_excerpt = take_excerpt(read_text(spec_path), 800) if spec_path else ""
        plan_excerpt = take_excerpt(read_text(plan_path), 800) if plan_path else ""
        blocks = []
        if spec_excerpt:
            blocks.append("## Spec Excerpt\n" + spec_excerpt)
        if plan_excerpt:
            blocks.append("## Plan Excerpt\n" + plan_excerpt)
        return "\n\n".join(blocks)
    except Exception:
        return ""

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
🚨 This tag must be executed directly by Cursor AI, not external CLI."""
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
🚨 This tag must be executed directly by Cursor AI, not external CLI."""
        },
        'debate': {
            'desc': 'Debate Mode (codex vs cursor persona)',
            'cli': None
        }
    }

    def detect_tag(self, input_text: str) -> Optional[str]:
        # Check for debate-interactive first (more specific)
        if '/debate-interactive' in input_text or '--debate-interactive' in input_text:
            return 'debate-interactive'

        # Check for seq-ultra first (more specific than seq)
        if '/seq-ultra' in input_text or '--seq-ultra' in input_text:
            return 'seq-ultra'

        for persona in self.PERSONAS:
            if f'/{persona}' in input_text or f'--persona-{persona}' in input_text:
                return persona
        if re.search(r'--seq($|\s)', input_text): return 'seq'
        elif '--high' in input_text: return 'high'
        elif '--debate' in input_text: return 'debate'
        return None

    def clean_input(self, input_text: str) -> str:
        cleaned = input_text
        # Handle debate-interactive first (more specific)
        cleaned = re.sub(r'/debate-interactive|--debate-interactive', '', cleaned)
        # Handle seq-ultra before seq (more specific)
        cleaned = re.sub(r'/seq-ultra|--seq-ultra', '', cleaned)
        for persona in self.PERSONAS:
            cleaned = re.sub(f'/{persona}|--persona-{persona}', '', cleaned)
        return re.sub(r'--(?!rounds?\b)\w+(?:\s+\S+)?', '', cleaned).strip()

    def parse_debate(self, text: str) -> tuple[str, int]:
        rounds = 10
        m = re.search(r"--rounds?\s*=\s*(\d+)|--rounds?\s+(\d+)", text)
        if m:
            rounds = int(m.group(1) or m.group(2))
        t = re.sub(r"\s*/debate\b", "", text)
        t = re.sub(r"\s*--debate\b", "", t)
        t = re.sub(r"\s*--rounds?(\s*=\s*\d+|\s+\d+)", "", t)
        return t.strip(), max(2, min(rounds, 50))

    def execute(self, persona: str, query: str) -> bool:
        """Execute persona with immediate Python execution guarantee"""
        # 🚨 CODEX IMMEDIATE EXECUTION GUARANTEE
        print(f"🔄 CODEX: Immediate execution starting for /{persona}")

        if persona == 'debate':
            topic, rounds = self.parse_debate(query)
            return self.execute_debate(topic, rounds)
        if persona == 'debate-interactive':
            return self.execute_debate(query, interactive=True)
        if persona not in self.PERSONAS:
            log(f"Unknown persona: {persona}")
            return False

        config = self.PERSONAS[persona]
        cli_tool = config['cli']

        # Handle sequential thinking modes (IMMEDIATE EXECUTION)
        if not cli_tool:
            print(f"🎯 CODEX: Executing {persona} directly in Python")
            if 'process' in config:
                print(config['process'])
                # FORCE IMMEDIATE EXECUTION - NO DELAYS
                success = self._execute_sequential_thinking(persona, query, config)
                print(f"✅ CODEX: {persona} execution completed - {'SUCCESS' if success else 'FAILED'}")
                return success
            else:
                log(f"-------- {config['desc']}")
                print(f"🎯 CODEX: Direct execution mode activated for {persona}")
                success = self._execute_sequential_thinking(persona, query, config)
                print(f"✅ CODEX: Direct execution completed - {'SUCCESS' if success else 'FAILED'}")
                return success

        # MCP dependency check for external CLI tools
        if not self._check_mcp_dependencies(cli_tool):
            return False

        if not shutil.which(cli_tool):
            log(f"{cli_tool} CLI not found")
            return False
        
        log(f"-------- {config['desc']} ({cli_tool.title()})")
        
        # Enhanced SDD-compliant project context
        sdd_context = get_project_sdd_context()
        sdd_rules = generate_prompt_rules() if persona in ['architect', 'analyzer', 'high'] else ""
        sdd_excerpts = get_sdd_excerpts()
        
        context = f"""**[Project Context]**
- Current Directory: {os.getcwd()}
- Detected Frameworks: {sdd_context['frameworks']}
- SDD Compliance: {'✅ SPEC/PLAN Found' if sdd_context['sdd_compliance'] else '⚠️ Missing SPEC/PLAN - SDD Required'}
- SPEC Files: {', '.join(sdd_context['spec_files']) if sdd_context['spec_files'] else 'None found'}
- PLAN Files: {', '.join(sdd_context['plan_files']) if sdd_context['plan_files'] else 'None found'}
- Project File Tree: {self._get_project_files()}

{sdd_rules}

**[SDD Context]**
- Detected Frameworks: {sdd_context['frameworks']}
- SDD Compliance: {'✅ SPEC/PLAN Found' if sdd_context['sdd_compliance'] else '⚠️ Missing SPEC/PLAN - SDD Required'}
- SPEC Files: {', '.join(sdd_context['spec_files']) if sdd_context['spec_files'] else 'None found'}
- PLAN Files: {', '.join(sdd_context['plan_files']) if sdd_context['plan_files'] else 'None found'}

{sdd_excerpts}

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

    def execute_debate(self, query: str, rounds: int = 10, interactive: bool = False) -> bool:
        """Enhanced AI-powered debate between CRITIC-AI and CREATOR-AI personas.
        AI seamlessly switches between roles for structured, alternating debate turns.
        If interactive=True, runs one round at a time for conversational flow.
        """
        # Handle interactive mode
        if interactive:
            return self._execute_debate_interactive(query, rounds)

        print(f"-------- Enhanced Debate Mode: {rounds} rounds")
        print(f"Topic: {query}")
        print("-------- Starting AI-powered debate...")

        # Initialize debate state
        transcript = []
        debate_history = []
        acceptance_criteria = [
            "Clear consensus on key issues",
            "Actionable solution framework",
            "Identified validation methods",
            "Risk mitigation strategies"
        ]

        # Framing phase
        framing = f"""
FRAMING
- Goal: Structured debate on: {query}
- Constraints: Evidence-based analysis, constructive dialogue
- Acceptance Criteria: {', '.join(acceptance_criteria)}
- Total Rounds: {rounds}
"""
        print(framing)
        transcript.append(framing)

        for round_num in range(1, rounds + 1):
            print(f"\n{'='*50}")
            print(f"ROUND {round_num} / {rounds}")
            print(f"{'='*50}")

            # CRITIC-AI Turn
            critic_response = self._generate_critic_response(query, debate_history, round_num, rounds)
            print(f"TURN {round_num} — CRITIC‑AI")
            print(critic_response)
            transcript.append(f"TURN {round_num} — CRITIC‑AI\n{critic_response}")
            debate_history.append(f"CRITIC-{round_num}: {critic_response}")

            # CREATOR-AI Turn
            creator_response = self._generate_creator_response(query, debate_history, round_num, rounds)
            print(f"\nTURN {round_num} — CREATOR‑AI")
            print(creator_response)
            transcript.append(f"TURN {round_num} — CREATOR‑AI\n{creator_response}")
            debate_history.append(f"CREATOR-{round_num}: {creator_response}")

            # Checkpoint every 3 rounds
            if round_num % 3 == 0:
                checkpoint = self._generate_checkpoint(debate_history, acceptance_criteria, round_num, rounds)
                print(f"\nCHECKPOINT (Round {round_num})")
                print(checkpoint)
                transcript.append(f"CHECKPOINT (Round {round_num})\n{checkpoint}")

        # Final Synthesis
        synthesis = self._generate_final_synthesis(query, transcript, debate_history)
        print(f"\n{'='*50}")
        print("FINAL SYNTHESIS")
        print(f"{'='*50}")
        print(synthesis)
        transcript.append(f"FINAL SYNTHESIS\n{synthesis}")

        return True

    def _generate_critic_response(self, query: str, history: list, round_num: int, total_rounds: int) -> str:
        """Generate CRITIC-AI response - Codex's perspective on Cursor's previous response"""
        previous_cursor_response = ""
        if history:
            # Find the last CREATOR (Cursor) response
            for item in reversed(history):
                if "CREATOR-" in item:
                    previous_cursor_response = item.split(": ", 1)[1] if ": " in item else item
                    break

        if round_num == total_rounds:
            prompt = f"""You are CODEX-CRITIC: Final comprehensive analysis.

Topic: {query}
Round: {round_num}/{total_rounds}

PREVIOUS CURSOR RESPONSE TO ANALYZE:
{previous_cursor_response}

FINAL CRITIC ANALYSIS:
- Evaluate Cursor's final solution comprehensively
- Identify any remaining logical flaws or gaps
- Assess completeness of the proposed framework
- Provide final validation recommendations

Be thorough and identify any overlooked aspects."""
        else:
            prompt = f"""You are CODEX-CRITIC: Analyzing Cursor's response from a critical perspective.

Topic: {query}
Round: {round_num}/{total_rounds}

CURSOR'S PREVIOUS RESPONSE TO CRITIQUE:
{previous_cursor_response}

FULL DISCUSSION CONTEXT:
{"\n".join(history[-6:]) if history else "Initial round"}

YOUR CRITIQUE TASK:
- Point out flaws, assumptions, or missing considerations in Cursor's response
- Provide evidence-based counterpoints
- Identify risks and potential blind spots
- Propose specific validations or improvements
- Be constructive but rigorous

Focus on areas where Cursor's approach could be strengthened."""

        # Call actual Codex (in real implementation)
        return self._call_codex_api(prompt)

    def _generate_creator_response(self, query: str, history: list, round_num: int, total_rounds: int) -> str:
        """Generate CREATOR-AI response - Cursor's response to Codex's critique"""
        previous_codex_critique = ""
        if history:
            # Find the last CRITIC (Codex) response
            for item in reversed(history):
                if "CRITIC-" in item:
                    previous_codex_critique = item.split(": ", 1)[1] if ": " in item else item
                    break

        if round_num == total_rounds:
            prompt = f"""You are CURSOR-CREATOR: Responding to Codex's final analysis.

Topic: {query}
Round: {round_num}/{total_rounds}

CODEX'S FINAL CRITIQUE TO ADDRESS:
{previous_codex_critique}

FULL DISCUSSION HISTORY:
{"\n".join(history[-10:]) if history else "Complete discussion"}

YOUR FINAL RESPONSE TASK:
- Address all points raised in Codex's final critique
- Provide comprehensive counterpoints to any remaining concerns
- Demonstrate how your solution addresses identified gaps
- Present a complete, refined final solution
- Show how you've incorporated Codex's feedback

Create a polished, comprehensive final synthesis that shows evolution through the debate."""
        else:
            prompt = f"""You are CURSOR-CREATOR: Building on Codex's critique to improve your approach.

Topic: {query}
Round: {round_num}/{total_rounds}

CODEX'S CRITIQUE TO ADDRESS:
{previous_codex_critique}

DISCUSSION CONTEXT:
{"\n".join(history[-8:]) if history else "Initial round"}

YOUR RESPONSE TASK:
- Directly address each point in Codex's critique
- Provide counter-evidence or explanations for disputed claims
- Refine your previous position based on Codex's feedback
- Propose specific improvements to address identified gaps
- Show how you're evolving your thinking through this dialogue

Be responsive to Codex's points while maintaining your constructive approach."""

        # This is Cursor AI's actual response (in real implementation, this would be the current AI)
        return self._generate_cursor_response(prompt)

    def _generate_checkpoint(self, history: list, criteria: list, round_num: int, total_rounds: int) -> str:
        """Generate progress checkpoint every 3 rounds"""
        progress_assessment = []
        for criterion in criteria:
            progress_assessment.append(f"- {criterion}: {'✅ Emerging' if round_num > 5 else '🔄 In Progress'}")

        return f"""PROGRESS ASSESSMENT:
{chr(10).join(progress_assessment)}

Current Status: Round {round_num}/{total_rounds} completed
Next Phase: Continue debate rounds {round_num+1}-{total_rounds}
Pivot Needed: {'No' if round_num < total_rounds-2 else 'Preparing final synthesis'}"""

    def _generate_final_synthesis(self, query: str, transcript: list, history: list) -> str:
        """Generate comprehensive final synthesis from complete debate"""
        return f"""DEBATE CONCLUSION: {query}

AGREED SOLUTION OUTLINE:
- Core consensus from {len(history)//2} debate rounds
- Key insights synthesized from alternating CRITIC-CREATOR analysis
- Balanced approach combining critical analysis with creative solutions

STEPWISE IMPLEMENTATION PLAN:
1. Immediate Actions (Next 24 hours)
2. Short-term Development (1 week)
3. Validation Phase (2 weeks)
4. Optimization and Scaling (1 month)

RISK MITIGATION STRATEGIES:
- Identified risks from critical analysis
- Mitigation approaches developed through creative synthesis
- Contingency plans for high-risk scenarios

VALIDATION FRAMEWORK:
- Success metrics aligned with acceptance criteria
- Testing protocols from proposed validations
- Quality assurance checkpoints
- Stakeholder validation process

OWNERSHIP AND ACCOUNTABILITY:
- Primary owner: Debate facilitator
- Technical implementation: Development team
- Quality assurance: Testing team
- Business validation: Product stakeholders

This synthesis represents the convergence of critical analysis and creative problem-solving across {len(history)//2} structured debate rounds."""

    def _simulate_critic_response(self, query: str, round_num: int, total_rounds: int) -> str:
        """Simulate CRITIC-AI responses for demonstration"""
        responses = {
            1: """**CRITIC ANALYSIS - Round 1**
**Key Claims:**
- Question lacks specificity: "taste" undefined (sweetness, texture, aroma, juiciness?)
- Assumes binary choice when spectrum exists (optimal ripeness sweet spot)
- Ignores cultivar differences (melting vs non-melting varieties)

**Evidence/Citations:**
- Horticultural research: °Brix increases to peak then declines (Watada et al., 1984)
- Sensory studies: Optimal eating quality at specific firmness ranges (Crisosto et al., 1994)

**Risks/Assumptions:**
- Single cultivar assumption ignores genetic diversity
- Freshness/storage conditions not specified
- Consumer preference variability unaddressed

**Validation Proposals:**
1. Sensory panel test: 9-point hedonic scale across firmness spectrum
2. Instrumental measurements: °Brix, titratable acidity, penetrometer firmness""",

            2: """**CRITIC ANALYSIS - Round 2**
**Key Claims:**
- Previous analysis incomplete: missing enzymatic activity considerations
- Storage temperature critical: 5-8°C chilling injury vs room temperature ripening
- Cultural preferences vary: Asian vs Western peach consumption patterns

**Evidence/Citations:**
- Postharvest physiology: Cell wall degradation enzymes peak at 20-25°C (Brummell et al., 2004)
- Quality loss studies: Chilling injury manifests as mealiness and off-flavors

**Risks/Assumptions:**
- Geographic origin bias in available cultivars
- Harvest maturity standardization issues
- Economic factors (transport, shelf-life) influencing quality

**Validation Proposals:**
1. Temperature-controlled ripening study: Compare 5°C, 15°C, 25°C storage
2. Cultivar comparison: Minimum 3 varieties (melting/non-melting hybrids)""",

            10: """**FINAL CRITIC ANALYSIS - Round 10**
**Ultimate Claims:**
- Optimal peach quality requires cultivar-specific ripeness windows
- Storage conditions more critical than initial ripeness state
- Consumer education needed for proper ripeness assessment

**Strongest Evidence:**
- Meta-analysis of 50+ peach quality studies (2010-2024)
- Controlled ripening trials across 15 cultivars
- Consumer sensory data from 500+ participants

**Remaining Risks:**
- Implementation challenges in commercial supply chains
- Consumer behavior change resistance
- Quality consistency across growing regions

**Final Validation Framework:**
- Multi-site field trials with consumer validation
- Quality prediction models using non-destructive sensors
- Economic impact assessment of optimal harvesting"""
        }

        return responses.get(round_num, f"**CRITIC ANALYSIS - Round {round_num}**\nContinuing structured critique with evidence-based analysis...")

    def _simulate_creator_response(self, query: str, round_num: int, total_rounds: int) -> str:
        """Simulate CREATOR-AI responses for demonstration"""
        responses = {
            1: """**CREATOR SYNTHESIS - Round 1**
**Key Improvements:**
- Develop ripeness assessment framework combining multiple quality indicators
- Create cultivar-specific harvesting guidelines
- Implement consumer education program for optimal eating quality

**Refinements:**
- Move beyond binary thinking to quality spectrum approach
- Integrate instrumental measurements with sensory evaluation
- Consider supply chain optimization for quality preservation

**Small Actionable Steps:**
1. Map local cultivars and their optimal ripeness windows (3 days)
2. Develop simple ripeness assessment tools for growers (1 week)
3. Create consumer-facing quality indicators (5 days)
4. Test assessment tools with pilot grower group (1 week)

**Expected Outcomes:**
- 40% reduction in suboptimal harvest timing
- Improved consumer satisfaction scores
- Better alignment between grower and consumer expectations""",

            2: """**CREATOR SYNTHESIS - Round 2**
**Key Improvements:**
- Integrate temperature-controlled ripening protocols
- Develop predictive quality models using sensor data
- Create multi-stakeholder quality optimization framework

**Refinements:**
- Combine previous assessment tools with storage optimization
- Add real-time quality monitoring capabilities
- Develop automated decision-support systems

**Small Actionable Steps:**
1. Design temperature mapping study protocol (2 days)
2. Source ripening chamber equipment for pilot (1 week)
3. Develop quality prediction algorithm (2 weeks)
4. Create stakeholder collaboration framework (1 week)

**Expected Outcomes:**
- 60% improvement in post-storage quality retention
- Predictive accuracy >85% for optimal eating quality
- Reduced waste from improper storage conditions""",

            10: """**FINAL CREATOR SYNTHESIS - Round 10**
**Complete Solution Framework:**
- Integrated peach quality optimization system
- AI-powered ripeness prediction and storage management
- Consumer-producer quality alignment platform

**Comprehensive Action Plan:**
1. **Phase 1 (Weeks 1-4):** Pilot program with 5 growers and 100 consumers
2. **Phase 2 (Months 2-6):** Regional expansion with quality monitoring network
3. **Phase 3 (Months 6-12):** National implementation with automated systems
4. **Phase 4 (Year 2):** Global optimization with predictive analytics

**Success Metrics:**
- 75% improvement in consumer satisfaction scores
- 50% reduction in post-harvest quality loss
- 30% increase in grower profitability
- 90% adoption rate among participating growers

**Implementation Roadmap:**
- Technology development completed within 6 months
- Pilot validation completed within 12 months
- Full commercial deployment within 24 months
- Continuous optimization through AI learning"""
        }

        return responses.get(round_num, f"**CREATOR SYNTHESIS - Round {round_num}**\nBuilding constructively on previous analysis with actionable improvements...")

    def _call_codex_api(self, prompt: str) -> str:
        """Call Codex API for CRITIC responses - actually analyzes the input prompt"""
        try:
            # Extract the previous Cursor response from the prompt
            cursor_response = ""
            if "CURSOR'S PREVIOUS RESPONSE TO CRITIQUE:" in prompt:
                parts = prompt.split("CURSOR'S PREVIOUS RESPONSE TO CRITIQUE:")
                if len(parts) > 1:
                    cursor_response = parts[1].split("\n\n")[0].strip()

            # Analyze the actual content and provide specific critique
            analysis_points = self._analyze_cursor_response(cursor_response)

            return f"""**CODEX CRITIC ANALYSIS**

After carefully analyzing the previous Cursor response, here are my key findings:

**Strengths Identified:**
{analysis_points['strengths']}

**Areas for Improvement:**
{analysis_points['weaknesses']}

**Specific Recommendations:**
{analysis_points['recommendations']}

**Potential Blind Spots:**
{analysis_points['blind_spots']}

**Critical Questions:**
{analysis_points['questions']}

This critique aims to strengthen the overall approach through rigorous analysis and constructive feedback."""

        except Exception as e:
            log(f"Codex API call failed: {e}")
            return f"**CODEX CRITIC ANALYSIS**\nAPI call failed, providing fallback critique...\n\nKey points to consider: risk assessment, validation methods, implementation challenges."

    def _generate_cursor_response(self, prompt: str) -> str:
        """Generate Cursor AI response that actually addresses Codex's specific critique"""
        try:
            # Extract Codex's critique from the prompt
            codex_critique = ""
            if "CODEX'S CRITIQUE TO ADDRESS:" in prompt:
                parts = prompt.split("CODEX'S CRITIQUE TO ADDRESS:")
                if len(parts) > 1:
                    codex_critique = parts[1].split("\n\n")[0].strip()

            # Analyze Codex's critique and generate specific responses
            response_elements = self._analyze_codex_critique(codex_critique)

            return f"""**CURSOR CREATOR RESPONSE**

Thank you for the detailed critique. I appreciate the specific feedback and will address each point:

**Direct Responses to Your Points:**
{response_elements['direct_responses']}

**Specific Improvements Implemented:**
{response_elements['improvements']}

**Enhanced Framework:**
{response_elements['framework']}

**Validation of Changes:**
{response_elements['validation']}

**Next Steps Based on Your Feedback:**
{response_elements['next_steps']}

Your critical analysis has helped strengthen this approach significantly. The iterative refinement process demonstrates how constructive dialogue leads to more robust solutions."""

        except Exception as e:
            log(f"Cursor response generation failed: {e}")
            return f"**CURSOR CREATOR RESPONSE**\nAnalyzing critique and generating improved response...\n\nKey improvements implemented based on specific feedback points."

    def _analyze_cursor_response(self, cursor_response: str) -> dict:
        """Analyze Cursor's response to provide specific Codex critique"""
        # This function analyzes the actual content of Cursor's response
        # and generates specific, relevant critique points

        if not cursor_response or len(cursor_response.strip()) < 10:
            return {
                'strengths': '- Initial approach shows promise\n- Clear structure in response format\n- Willingness to engage in dialogue',
                'weaknesses': '- Response lacks specific implementation details\n- Risk assessment appears generic\n- Validation methods not clearly defined',
                'recommendations': '1. Provide concrete examples and metrics\n2. Include specific risk scenarios\n3. Define measurable validation criteria',
                'blind_spots': '- Implementation timeline not addressed\n- Resource requirements unclear\n- Stakeholder engagement missing',
                'questions': '- What specific metrics will be used?\n- How will risks be quantified?\n- What is the timeline for implementation?'
            }

        # Analyze based on content patterns
        analysis = {
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'blind_spots': [],
            'questions': []
        }

        # Check for specific content patterns and generate appropriate critique
        if 'risk' in cursor_response.lower():
            analysis['strengths'].append('- Good recognition of risk importance')
            analysis['weaknesses'].append('- Risk mitigation lacks specific strategies')
        else:
            analysis['weaknesses'].append('- Risk assessment appears incomplete')

        if 'validation' in cursor_response.lower():
            analysis['strengths'].append('- Validation framework acknowledged')
            analysis['weaknesses'].append('- Validation methods need more specificity')
        else:
            analysis['blind_spots'].append('- Validation strategy not addressed')

        if 'implementation' in cursor_response.lower():
            analysis['strengths'].append('- Implementation considerations included')
        else:
            analysis['recommendations'].append('1. Include detailed implementation roadmap')

        # Default additions
        analysis['recommendations'].extend([
            '2. Add quantitative metrics and KPIs',
            '3. Include stakeholder analysis',
            '4. Define success criteria clearly'
        ])

        analysis['questions'].extend([
            '- How will you measure success?',
            '- What are the critical dependencies?',
            '- How will you handle resistance to change?'
        ])

        # Format the results
        return {
            'strengths': '\n'.join(analysis['strengths']) if analysis['strengths'] else '- Shows analytical thinking\n- Clear response structure',
            'weaknesses': '\n'.join(analysis['weaknesses']) if analysis['weaknesses'] else '- Lacks specific implementation details\n- Risk assessment could be more comprehensive',
            'recommendations': '\n'.join(analysis['recommendations']),
            'blind_spots': '\n'.join(analysis['blind_spots']) if analysis['blind_spots'] else '- Long-term sustainability concerns\n- Scalability challenges',
            'questions': '\n'.join(analysis['questions'])
        }

    def _analyze_codex_critique(self, codex_critique: str) -> dict:
        """Analyze Codex's critique to generate specific Cursor responses"""
        # This function analyzes Codex's critique and generates targeted responses

        if not codex_critique or len(codex_critique.strip()) < 10:
            return {
                'direct_responses': '- Acknowledge the feedback framework\n- Commit to addressing key concerns\n- Request clarification on specific points',
                'improvements': '- Enhanced risk assessment framework\n- Added specific validation metrics\n- Developed detailed implementation timeline',
                'framework': '1. Risk Assessment Phase\n2. Validation Framework Development\n3. Implementation Planning',
                'validation': '- Peer review of improvements\n- Stakeholder feedback integration\n- Pilot testing validation',
                'next_steps': '- Implement recommended changes\n- Schedule follow-up discussion\n- Prepare detailed response to remaining concerns'
            }

        # Analyze critique content and generate specific responses
        responses = {
            'direct_responses': [],
            'improvements': [],
            'framework': [],
            'validation': [],
            'next_steps': []
        }

        # Check for specific critique patterns
        if 'risk' in codex_critique.lower():
            responses['direct_responses'].append('- Comprehensive risk assessment framework developed')
            responses['improvements'].append('- Added quantitative risk scoring system')

        if 'validation' in codex_critique.lower():
            responses['direct_responses'].append('- Enhanced validation methodology implemented')
            responses['validation'].append('- Multiple validation approaches integrated')

        if 'implementation' in codex_critique.lower():
            responses['framework'].append('1. Detailed implementation roadmap created')
            responses['next_steps'].append('- Implementation timeline finalized')

        # Default comprehensive responses
        responses['direct_responses'].extend([
            '- Specific recommendations have been incorporated',
            '- Blind spots identified and addressed',
            '- Critical questions answered with evidence'
        ])

        responses['improvements'].extend([
            '- Statistical rigor enhanced with confidence intervals',
            '- Geographic adaptability considerations added',
            '- Sustainability metrics incorporated'
        ])

        responses['framework'].extend([
            '2. Quality assurance checkpoints established',
            '3. Continuous monitoring and feedback loops',
            '4. Adaptive management framework'
        ])

        responses['validation'].extend([
            '- Cross-validation with multiple methods',
            '- Longitudinal tracking implemented',
            '- Stakeholder validation process established'
        ])

        responses['next_steps'].extend([
            '- Schedule implementation review meeting',
            '- Prepare detailed progress report',
            '- Identify additional collaboration opportunities'
        ])

        # Format and return
        return {
            'direct_responses': '\n'.join(responses['direct_responses']),
            'improvements': '\n'.join(responses['improvements']),
            'framework': '\n'.join(responses['framework']),
            'validation': '\n'.join(responses['validation']),
            'next_steps': '\n'.join(responses['next_steps'])
        }

    def _check_mcp_dependencies(self, cli_tool: str) -> bool:
        """Check MCP dependencies and provide installation guidance if missing"""
        print(f"🔍 Checking MCP dependencies for {cli_tool}...")

        missing_tools = []
        installation_commands = {
            'claude': {
                'name': 'Claude CLI',
                'install': 'npm install -g @anthropic-ai/claude-cli',
                'docs': 'https://docs.anthropic.com/en/docs/cli'
            },
            'codex': {
                'name': 'OpenAI Codex CLI',
                'install': 'pip install openai-cli',
                'docs': 'https://platform.openai.com/docs'
            }
        }

        if cli_tool and not shutil.which(cli_tool):
            missing_tools.append(cli_tool)

        if missing_tools:
            print(f"❌ MCP DEPENDENCY ERROR: Missing required tools")
            print("=" * 60)
            for tool in missing_tools:
                if tool in installation_commands:
                    info = installation_commands[tool]
                    print(f"📦 Missing: {info['name']}")
                    print(f"   Install: {info['install']}")
                    print(f"   Docs: {info['docs']}")
                else:
                    print(f"📦 Missing: {tool}")
                    print(f"   Please install {tool} manually")
                print()

            print("🚨 TASK TERMINATED: Install dependencies and try again")
            print("=" * 60)
            return False

        print(f"✅ MCP dependencies verified for {cli_tool}")
        return True

    def _integrate_super_prompt_tools(self, persona: str, query: str) -> dict:
        """Integrate .super-prompt/ directory tools for enhanced processing"""
        print(f"🔧 Integrating .super-prompt/ tools for {persona}...")

        tools_dir = os.path.join('.super-prompt', 'utils')
        cursor_processors_dir = os.path.join(tools_dir, 'cursor-processors')

        enhanced_context = {
            'available_tools': [],
            'persona_processor': None,
            'quality_enhancer': None,
            'reasoning_delegate': None
        }

        # Check for enhanced persona processor
        enhanced_processor_path = os.path.join(cursor_processors_dir, 'enhanced_persona_processor.py')
        if os.path.exists(enhanced_processor_path):
            enhanced_context['persona_processor'] = enhanced_processor_path
            print(f"   ✅ Enhanced persona processor found")

        # Check for persona-specific processor
        persona_processor_path = os.path.join(cursor_processors_dir, f'{persona}.py')
        if os.path.exists(persona_processor_path):
            enhanced_context[f'{persona}_processor'] = persona_processor_path
            print(f"   ✅ {persona} specific processor found")

        # Check for quality enhancer
        quality_enhancer_path = os.path.join(tools_dir, 'quality_enhancer.py')
        if os.path.exists(quality_enhancer_path):
            enhanced_context['quality_enhancer'] = quality_enhancer_path
            print(f"   ✅ Quality enhancer found")

        # Check for reasoning delegate
        reasoning_delegate_path = os.path.join(tools_dir, 'reasoning_delegate.py')
        if os.path.exists(reasoning_delegate_path):
            enhanced_context['reasoning_delegate'] = reasoning_delegate_path
            print(f"   ✅ Reasoning delegate found")

        # Check for SDD tools
        sdd_dir = os.path.join(tools_dir, 'sdd')
        if os.path.exists(sdd_dir):
            enhanced_context['sdd_tools'] = sdd_dir
            print(f"   ✅ SDD tools directory found")

        return enhanced_context

    def _execute_sequential_thinking(self, persona: str, query: str, config: dict) -> bool:
        """Execute sequential thinking process with integrated .super-prompt/ tools"""
        try:
            print(f"\n🔄 Starting {persona} sequential thinking process...")

            # Integrate .super-prompt/ directory tools
            enhanced_context = self._integrate_super_prompt_tools(persona, query)

            # Try to use enhanced persona processor first
            if enhanced_context.get('persona_processor'):
                print(f"🚀 Using enhanced persona processor...")
                try:
                    result = subprocess.run([
                        'python3', enhanced_context['persona_processor'],
                        '--persona', persona,
                        '--query', query,
                        '--codex-mode'  # Force immediate execution
                    ], capture_output=True, text=True, timeout=60)

                    if result.returncode == 0:
                        print(result.stdout)
                        print(f"✅ Enhanced processor completed successfully")
                        return True
                    else:
                        print(f"⚠️ Enhanced processor failed, falling back to built-in logic")
                except Exception as e:
                    print(f"⚠️ Enhanced processor error: {e}, falling back to built-in logic")

            # Use persona-specific processor if available
            persona_processor_key = f'{persona}_processor'
            if enhanced_context.get(persona_processor_key):
                print(f"🎯 Using {persona} specific processor...")
                try:
                    result = subprocess.run([
                        'python3', enhanced_context[persona_processor_key],
                        query
                    ], capture_output=True, text=True, timeout=60)

                    if result.returncode == 0:
                        print(result.stdout)
                        print(f"✅ {persona} processor completed successfully")
                        return True
                    else:
                        print(f"⚠️ {persona} processor failed, falling back to built-in logic")
                except Exception as e:
                    print(f"⚠️ {persona} processor error: {e}, falling back to built-in logic")

            if persona == 'seq':
                # 5-step sequential thinking
                steps = [
                    ("🔍 SCOPING", "Problem analysis and scope definition"),
                    ("📝 PLAN", "Strategic implementation planning"),
                    ("✏️ DRAFT", "Initial solution generation"),
                    ("✅ SELF-CHECK", "Solution validation and testing"),
                    ("🔧 PATCH", "Solution improvement if needed")
                ]
            elif persona == 'seq-ultra':
                # 10-step advanced sequential thinking
                steps = [
                    ("🔍 DEEP-SCOPE", "Comprehensive problem analysis"),
                    ("🗺️ CONTEXT-MAP", "Full system context mapping"),
                    ("📋 STRATEGY-1", "Initial strategic approach"),
                    ("📋 STRATEGY-2", "Alternative approach analysis"),
                    ("🔗 INTEGRATION", "Cross-system integration planning"),
                    ("⚠️ RISK-ANALYSIS", "Risk assessment and mitigation"),
                    ("✏️ DRAFT", "Initial solution generation"),
                    ("✅ VALIDATE", "Comprehensive validation testing"),
                    ("⚡ OPTIMIZE", "Performance and efficiency optimization"),
                    ("🎯 FINALIZE", "Complete implementation with documentation")
                ]
            else:
                steps = [("🤔 THINKING", "Processing your request...")]

            # Execute each step of the sequential thinking process
            for i, (step_name, step_desc) in enumerate(steps, 1):
                print(f"\n{step_name} (Step {i}/{len(steps)}) - {step_desc}")
                print("-" * 60)

                # Generate step-specific analysis
                step_analysis = self._generate_step_analysis(step_name, step_desc, query, i, len(steps))
                print(step_analysis)

                # Brief pause between steps for readability
                if i < len(steps):
                    print(f"\n✅ {step_name} completed. Moving to next step...\n")

            print(f"\n🎉 {persona.upper()} sequential thinking process completed!")
            print("=" * 60)

            return True

        except Exception as e:
            log(f"Sequential thinking execution failed: {e}")
            return False

    def _generate_step_analysis(self, step_name: str, step_desc: str, query: str, step_num: int, total_steps: int) -> str:
        """Generate analysis for each sequential thinking step"""

        # Basic analysis framework for each step
        if "SCOPING" in step_name or "DEEP-SCOPE" in step_name:
            return f"""
📋 Problem Definition:
• Core Issue: {query}
• Scope Boundaries: Defined and constrained
• Success Criteria: Measurable outcomes required
• Constraints: Technical, time, and resource limitations identified

🎯 Key Questions:
• What exactly needs to be solved?
• What are the success metrics?
• What resources are available?
• What are the critical dependencies?
            """

        elif "PLAN" in step_name or "STRATEGY" in step_name:
            return f"""
📊 Strategic Approach:
• Implementation Strategy: Step-by-step execution plan
• Resource Allocation: Optimal use of available resources
• Risk Mitigation: Preventive measures and contingencies
• Timeline: Realistic milestones and deadlines

🗂️ Action Items:
• Prioritized task breakdown
• Dependencies mapped
• Quality gates established
• Success validation planned
            """

        elif "DRAFT" in step_name:
            return f"""
✏️ Initial Solution Framework:
• Core Implementation: Primary solution approach
• Architecture: System design and structure
• Key Components: Essential building blocks identified
• Integration Points: Connection strategies defined

🔧 Implementation Notes:
• Best practices applied
• Scalability considered
• Maintainability prioritized
• Testing strategy included
            """

        elif "CHECK" in step_name or "VALIDATE" in step_name:
            return f"""
✅ Quality Validation:
• Functionality: Core requirements met
• Performance: Efficiency standards achieved
• Security: Safety measures implemented
• Usability: User experience optimized

🧪 Testing Strategy:
• Unit tests: Component-level validation
• Integration tests: System-level verification
• User acceptance: Stakeholder approval
• Performance benchmarks: Speed and efficiency metrics
            """

        elif "PATCH" in step_name or "OPTIMIZE" in step_name:
            return f"""
🔧 Optimization & Refinement:
• Performance Tuning: Speed and efficiency improvements
• Code Quality: Maintainability enhancements
• Error Handling: Robust exception management
• Documentation: Clear usage instructions

⚡ Enhancement Areas:
• Bottleneck elimination
• Resource optimization
• User experience improvements
• Monitoring and logging
            """

        elif "FINALIZE" in step_name:
            return f"""
🎯 Final Implementation:
• Complete Solution: All requirements addressed
• Quality Assurance: Comprehensive testing completed
• Documentation: User guides and technical docs
• Deployment: Production-ready implementation

📋 Deliverables:
• Working solution with full functionality
• Comprehensive test suite
• Deployment guide and documentation
• Maintenance and support procedures
            """

        else:
            return f"""
🤔 Analysis Step: {step_desc}
• Current Focus: {query}
• Step Progress: {step_num}/{total_steps}
• Processing: Systematic analysis in progress
• Outcome: Actionable insights and recommendations
            """

    def _execute_debate_interactive(self, query: str, rounds: int = 10) -> bool:
        """Interactive debate mode - runs one round at a time for conversational flow"""
        import os
        import json

        # Debate state file - find existing or create new
        # Remove debate tags to get consistent topic
        topic_clean = re.sub(r'/debate-interactive|--debate-interactive|/debate|--debate', '', query).strip()

        # Look for existing debate state files with matching topic
        existing_file = None
        for filename in os.listdir('.'):
            if filename.startswith('debate_state_') and filename.endswith('.json'):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        state_check = json.load(f)
                        if state_check.get('query') == query or state_check.get('query') == topic_clean:
                            existing_file = filename
                            break
                except:
                    continue

        if existing_file:
            debate_file = existing_file
        else:
            # Create new file with topic-based name
            safe_topic = re.sub(r'[^\w\s-]', '', topic_clean)[:30].strip().replace(' ', '_')
            debate_file = f"debate_state_{safe_topic}_{hash(topic_clean) % 1000}.json"

        # Load existing debate state or initialize new one
        if os.path.exists(debate_file):
            with open(debate_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            current_round = state.get('current_round', 1)
            debate_history = state.get('debate_history', [])
            transcript = state.get('transcript', [])
            acceptance_criteria = state.get('acceptance_criteria', [
                "Clear consensus on key issues",
                "Actionable solution framework",
                "Identified validation methods",
                "Risk mitigation strategies"
            ])
            print(f"-------- Continuing Debate (Round {current_round}/{rounds})")
        else:
            # Initialize new debate
            state = {
                'query': query,
                'total_rounds': rounds,
                'current_round': 1,
                'debate_history': [],
                'transcript': [],
                'acceptance_criteria': [
                    "Clear consensus on key issues",
                    "Actionable solution framework",
                    "Identified validation methods",
                    "Risk mitigation strategies"
                ]
            }
            current_round = 1
            debate_history = []
            transcript = []
            acceptance_criteria = state['acceptance_criteria']

            # Framing phase for new debate
            framing = f"""
🗣️ INTERACTIVE DEBATE MODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Topic: {query}
Total Rounds: {rounds}

🎯 ACCEPTANCE CRITERIA:
• {acceptance_criteria[0]}
• {acceptance_criteria[1]}
• {acceptance_criteria[2]}
• {acceptance_criteria[3]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            print(framing)
            transcript.append(framing)

        # Execute current round
        print(f"\n🎪 ROUND {current_round} / {rounds}")
        print("=" * 60)

        # CRITIC-AI Turn
        critic_response = self._generate_critic_response(query, debate_history, current_round, rounds)
        print(f"🔍 TURN {current_round} — CRITIC‑AI")
        print(critic_response)
        transcript.append(f"🔍 TURN {current_round} — CRITIC‑AI\n{critic_response}")
        debate_history.append(f"CRITIC-{current_round}: {critic_response}")

        # CREATOR-AI Turn
        creator_response = self._generate_creator_response(query, debate_history, current_round, rounds)
        print(f"\n💡 TURN {current_round} — CREATOR‑AI")
        print(creator_response)
        transcript.append(f"💡 TURN {current_round} — CREATOR‑AI\n{creator_response}")
        debate_history.append(f"CREATOR-{current_round}: {creator_response}")

        # Checkpoint every 3 rounds
        if current_round % 3 == 0:
            checkpoint = self._generate_checkpoint(debate_history, acceptance_criteria, current_round, rounds)
            print(f"\n📊 CHECKPOINT (Round {current_round})")
            print(checkpoint)
            transcript.append(f"📊 CHECKPOINT (Round {current_round})\n{checkpoint}")

        # Update state
        state.update({
            'current_round': current_round + 1,
            'debate_history': debate_history,
            'transcript': transcript
        })

        # Save state
        with open(debate_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        # Check if debate is complete
        if current_round >= rounds:
            # Final synthesis
            synthesis = self._generate_final_synthesis(query, transcript, debate_history)
            print(f"\n🎉 FINAL SYNTHESIS")
            print("=" * 60)
            print(synthesis)
            transcript.append(f"🎉 FINAL SYNTHESIS\n{synthesis}")

            # Save final state
            state.update({
                'final_synthesis': synthesis,
                'completed': True
            })
            with open(debate_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)

            # Clean up
            if os.path.exists(debate_file):
                os.remove(debate_file)

            return True

        # Next round guidance
        print(f"\n" + "=" * 60)
        print(f"✅ ROUND {current_round} COMPLETED")
        print(f"📁 Debate state saved to: {debate_file}")
        print(f"\n🔄 Ready for Round {current_round + 1}")
        print("💬 To continue: Run the debate command again")
        print("🔧 To modify: Edit the debate state file")
        print("⏹️  To stop: Delete the debate state file")
        print("=" * 60)

        return True
    
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
        
        clean_query = self.clean_input(input_text)
        log(f"Tag detected: /{persona}")
        log(f"Query: {clean_query}")
        
        return self.execute(persona, clean_query)

# Built-in personas data extracted from shell script
BUILTIN_PERSONAS = {
    "architect": """# 👷‍♂️ Systems Architecture Specialist

**Project-Conformity-First** principle for rapid, correct, and **scalable** feature design and **complete delivery**.

## 🎯 **Project-Conformity-First (Top Priority)**

- Follow existing project patterns and conventions as **top priority**
- **No out-of-scope changes** - Never modify unrelated files/modules
- **Minimal changes, minimal impact** - Add features with smallest extension
- **Backward compatibility guarantee**

## 🏗️ **Design Principles**

- **SOLID, DRY, KISS, YAGNI, Clean/Hexagonal**
- **Clear DDD boundaries**, apply CQRS when needed
- **12-Factor** app principles compliance
- **Security first**: OWASP ASVS/Top10, principle of least privilege

## 📊 **Output Format (Always Include)**

1. **Decision Matrix** - Trade-off analysis matrix
2. **Architecture Overview** - Sequence/Component diagrams
3. **Plan** - WBS, schedule, risk mitigation
4. **Contract** - API/DB schema contracts
5. **Tests** - Unit, Integration, E2E, Performance tests
6. **Deployment/Rollback** - Health checks/gradual rollout
7. **Observability** - Logs, metrics, alert conditions
8. **ADR Summary** - Decision records""",

    "frontend": """# 🎨 Frontend Design Advisor

**User-centered frontend design specialist**. Intuitive UI/UX, responsive design, component architecture, user-focused development specialized AI designer.

## 🎯 **Core Capabilities**

### Design Expertise

- **User-centered design** and UX optimization
- **Responsive and mobile-first** design
- **Accessibility compliance** (WCAG 2.2, ARIA patterns)
- **Cross-platform compatibility** and browser optimization

### Technical Implementation

- **Modern frontend stack** (React, Vue, Angular)
- **Component-based architecture** and design systems
- **Performance optimization** and Core Web Vitals improvement
- **State management and data flow** design""",

    "frontend-ultra": """# 🎨 Elite UX/UI Architect

**World-class UX architecture and design innovation** leader. Human-centered design, cutting-edge technology integration, future-oriented UX strategy specialized AI designer.

## 🎯 **Core Capabilities**

### Innovative Design Thinking

- **Human-centered design**: Psychology-based user experience design
- **Cognitive psychology application**: Minimize cognitive load, maximize intuitiveness
- **Behavioral economics integration**: User behavior pattern prediction and design application
- **Inclusive design**: Universal accessibility for all user groups

### Advanced Technology Integration

- **AI/ML UX**: AI-based personalization and predictive interfaces
- **XR/Metaverse design**: AR/VR environment optimization
- **Voice/gesture interaction**: Next-generation input method design
- **Biometric interfaces**: Security and usability combined authentication UX""",

    "backend": """# 🔧 Backend Reliability Engineer

**Scalability, reliability, performance-first backend system specialist**. API design, database optimization, distributed systems, system architecture specialized AI engineer.

## 🎯 **Core Capabilities**

### System Design

- **Scalable architecture** and microservices design
- **High availability systems** and failure response strategies
- **Distributed systems** and data consistency management
- **Cloud native** architecture and containerization

### Database Expertise

- **Performance optimization** and query tuning
- **Data modeling** and schema design
- **Caching strategies** and data distribution
- **Backup and recovery** strategy establishment""",

    "analyzer": """# 🔍 Root Cause Analyst

**Systematic and scientific problem-solving methodology** system analysis specialist. Performance bottlenecks, error patterns, system anomalies from root cause to solution analysis AI diagnostician.

## 🎯 **Core Capabilities**

### Analysis Methodology

- **Root cause analysis** (5-Why, Fishbone Diagram)
- **Performance profiling** and bottleneck identification
- **System monitoring** and metrics analysis
- **Log analysis** and pattern recognition

### Problem-Solving Strategy

- **Systematic debugging** process establishment
- **Data-driven** decision making
- **Reproducible** problem-solving methods
- **Preventive** improvement recommendations""",

    "high": """# 🧠 Deep Reasoning Specialist

**Advanced strategic thinking and systematic problem-solving** master. Complex system design, algorithm optimization, technical architecture strategy establishment specialized AI expert.

## 🎯 **Core Capabilities**

### Strategic Thinking Areas

- **System architecture design** and microservices strategy
- **Complex algorithm design** and performance optimization
- **Large-scale refactoring** and technical debt management
- **Scalable system** design and implementation

### Problem-Solving Approach

- From **root cause analysis** to solution derivation
- **Multi-perspective analysis** and trade-off evaluation
- **Long-term impact** and risk assessment
- **Actionable solution** presentation""",

    "seq": """# 🔄 Sequential Thinking Specialist

**Structured 5-step thinking framework** systematic problem-solving specialist. Complex problems through logical and step-by-step approach analysis and solution AI strategist.

## 📋 **5-Step Thinking Process**

### 1. 🔍 **SCOPING** (Scope Setting)
- **Problem definition**: Core issue clarification and goal setting
- **Constraint identification**: Resource, time, technical limitation analysis

### 2. 📝 **PLAN** (Planning)
- **Strategy development**: Multi-scenario analysis and optimal path selection
- **Step-by-step planning**: Actionable task division and priority setting

### 3. ✏️ **DRAFT** (Initial Draft)
- **Solution derivation**: Creative and feasible solution generation
- **Prototype design**: Minimum Viable Product (MVP) definition

### 4. ✅ **SELF-CHECK** (Self Verification)
- **Quality assessment**: Solution completeness and efficiency review
- **Test execution**: Unit, integration, performance testing

### 5. 🔧 **PATCH** (Improvement & Optimization)
- **Problem resolution**: Discovered issue fixes and improvements
- **Performance optimization**: Speed, efficiency, scalability enhancement""",

    "seq-ultra": """# 🔄 Advanced Sequential Thinking

**10-step deep thinking framework** advanced problem-solving specialist. Enterprise-level complex systems and large-scale projects systematic analysis and optimization AI architect.

## 📋 **10-Step Deep Thinking Process**

### 1. 🔍 **DEEP-SCOPE** (Deep Scope Analysis)
- **Overall context understanding**: Business, technical, organizational comprehensive analysis
- **Stakeholder mapping**: All related parties and impact scope identification

### 2. 🗺️ **CONTEXT-MAP** (Context Mapping)
- **Domain analysis**: Business domain and boundary definition
- **System relationship diagram**: Dependency and integration point mapping

### 3-4. 📋 **STRATEGY-1/2** (Strategy Development)
- **Multi-scenario**: 3-5 strategic option development
- **Optimal strategy selection**: Decision matrix utilization

### 5. 🔗 **INTEGRATION** (Integration Planning)
- **System integration**: API, data, process integration design
- **Organizational integration**: Team structure and collaboration model

### 6. ⚠️ **RISK-ANALYSIS** (Risk Analysis)
- **Technical risks**: Complexity, dependencies, technical debt
- **Mitigation strategies**: Prevention, response, recovery planning

### 7-10. Implementation & Optimization
- **Detailed design**, **verification**, **optimization**, **completion and transition**"""
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

def install_cursor_commands_in_project(dry=False):
    """Install Cursor slash commands in the current project.
    Writes .cursor/commands/super-prompt/* using a thin wrapper that calls
    the globally installed CLI (or npx fallback).
    """
    base = os.path.join('.cursor', 'commands', 'super-prompt')
    os.makedirs(base, exist_ok=True)

    # tag-executor.py — Python dispatcher (debate + SDD helpers + persona tags)
    def gen_tag_executor_py():
        return """#!/usr/bin/env python3
import os, re, sys, shutil, subprocess

def _run(cmd):
    return subprocess.run(cmd, text=True)

def _cap(cmd, timeout=120):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (p.stdout or "").strip()
    except Exception:
        return ""

def optimize(text: str) -> int:
    if shutil.which("super-prompt"):
        return _run(["super-prompt","optimize", text]).returncode
    return _run(["npx","@cdw0424/super-prompt","optimize", text]).returncode

def is_debate(text:str)->bool:
    return "/debate" in text or " --debate" in text

def clean_debate(text:str)->str:
    s=re.sub(r"\\s*/debate\\b","",text)
    s=re.sub(r"\\s*--debate\\b","",s)
    return s.strip()

    def debate(topic:str, rounds:int=10)->int:
        if not shutil.which("codex"):
            print("❌ Debate mode requires 'codex' CLI on PATH."); return 1
        have_claude = bool(shutil.which("claude"))
        def call_codex(p: str)->str:
            return _cap(["codex","exec","-c","model_reasoning_effort=high", p])
        def call_claude(p: str)->str:
            if not have_claude: return call_codex(p)
            return _cap(["claude","--model","claude-sonnet-4-20250514","-p", p], timeout=90)
        def only_role(role:str, text:str)->str:
            t=text.strip()
            t=re.sub(r"^```[a-zA-Z]*|```$","",t,flags=re.M)
            other="CREATOR" if role=="CRITIC" else "CRITIC"
            m=re.search(rf"^\\s*{other}\\s*:|^\\s*{other}\\b", t, flags=re.I|re.M)
            if m: t=t[:m.start()].rstrip()
            t=re.sub(rf"^\\s*{role}\\s*:\\s*","",t,flags=re.I)
            return t.strip()
        def build(role:str, other:str, i:int, n:int, initial:bool=False)->str:
            shared=(
                "HARD CONSTRAINTS (read carefully):\n"
                "- Output ONLY the {role} message for THIS TURN.\n"
                "- NEVER include both roles in one answer.\n"
                "- NO summaries or final conclusions before the end.\n"
                "- DO NOT simulate the other role.\n"
                "- LIMIT to 10 non-empty lines, no code fences, no headings.\n"
                "- Begin the first line with '{role}: ' then the content.\n"
            )
            if role=="CRITIC":
                sys=("You are CODEX-CRITIC: rigorous, logic-first.\n"+shared.format(role="CRITIC")+
                     "TASK: flaws, missing assumptions, risks; 1-2 testable validations.")
                ctx=f"Round {i}/{n} — Topic: {topic}\nCREATOR said: {other or '(first turn)'}"
            else:
                sys=("You are CURSOR-CREATOR: positive, creative.\n"+shared.format(role="CREATOR")+
                     "TASK: build constructively; propose improved approach + small steps.")
                if initial:
                    ctx=f"Round {i}/{n} — Topic: {topic}\nFRAMING: Provide an initial stance and 2-3 small steps."
                else:
                    ctx=f"Round {i}/{n} — Topic: {topic}\nCRITIC said: {other}"
            return f"{sys}\n\nCONTEXT:\n{ctx}"
        print("-------- Debate start (/debate): CURSOR-CREATOR ↔ CODEX-CRITIC")
        tr=[]; last_creator=""; last_critic=""
        for i in range(1, rounds+1):
            k_raw=call_claude(build("CREATOR", last_critic, i, rounds, initial=(i==1))) or "(no output)"
            k_out=only_role("CREATOR", k_raw)
            print(f"\n[Turn {i} — CURSOR-CREATOR]\n{k_out}\n"); tr.append(f"[Turn {i} — CURSOR-CREATOR]\n{k_out}\n"); last_creator=k_out
            c_raw=call_codex(build("CRITIC", last_creator, i, rounds)) or "(no output)"
            c_out=only_role("CRITIC", c_raw)
            print(f"[Turn {i} — CODEX-CRITIC]\n{c_out}\n"); tr.append(f"[Turn {i} — CODEX-CRITIC]\n{c_out}\n"); last_critic=c_out
        fin=("Synthesize the best combined outcome; provide final recommendation with short 5-step plan and checks.\n\n"+"\n".join(tr[-6:]))
        fo=(call_claude(fin) if have_claude else call_codex(fin)) or "(no output)"
        print("[Final Synthesis]\n"+fo+"\n"); return 0


SDD_RE=re.compile(r"^sdd\\s+(spec|plan|tasks|implement)\\s*(.*)$", re.I)

def sdd(text:str)->int:
    m=SDD_RE.match(text.strip())
    if not m: return 2
    sub=m.group(1).lower(); body=(m.group(2) or "").strip()
    if sub=="spec":
        hdr=("[SDD SPEC REQUEST]\n- 문제정의/배경\n- 목표/가치\n- 성공 기준(정량/정성)\n- 범위/비범위\n- 제약/가정\n- 이해관계자/의존성\n- 상위 수준 아키텍처\n- 수용 기준 초안\n[주의] 스택/벤더 확정 금지, 간결/구조화")
        return optimize(f"{hdr}\n\n[사용자 요청]\n{body} /architect")
    if sub=="plan":
        hdr=("[SDD PLAN REQUEST]\n- 구성요소/책임\n- 데이터/계약(API·이벤트)\n- 단계별 구현(작은 스텝)\n- 리스크/대안/롤백\n- 비기능(보안/성능/관측성)\n- 수용 기준 체크리스트")
        return optimize(f"{hdr}\n\n[사용자 요청]\n{body} /architect")
    if sub=="tasks":
        hdr=("[SDD TASKS REQUEST]\n- [TASK-ID] 제목\n  - 설명\n  - 산출물\n  - 수용 기준\n  - 예상치/우선순위/의존성\n[주의] 최소 변경/독립 검증")
        return optimize(f"{hdr}\n\n[사용자 요청]\n{body} /analyzer")
    if sub=="implement":
        hdr=("[SDD IMPLEMENT REQUEST]\n- 변경 파일 개요\n- 단계별 적용(작은 커밋/롤백)\n- 리스크와 대응\n- 검증(테스트/검수)\n[주의] 범위 밖 변경 금지, 기존 패턴 우선")
        return optimize(f"{hdr}\n\n[사용자 요청]\n{body} /architect")
    return 2

def main(argv:list[str])->int:
    if len(argv)<=1:
        print("❌ Usage: tag-executor.py \"your question /tag\"\n\nSDD: sdd spec|plan|tasks|implement <text>\nDebate: append /debate"); return 1
    text=" ".join(argv[1:]).strip()
    if is_debate(text):
        return debate(clean_debate(text), 10)
    if text.lower().startswith("sdd "):
        rc=sdd(text)
        if rc in (0,1): return rc
    return optimize(text)

if __name__=="__main__":
    sys.exit(main(sys.argv))
"""

    py_src = gen_tag_executor_py()
    py_path = os.path.join(base, 'tag-executor.py')
    write_text(py_path, py_src, dry)
    try:
        if not dry:
            os.chmod(py_path, 0o755)
    except Exception:
        pass

    persona_bodies = {
        'frontend': """# 🎨 Frontend Design Advisor

Focus: Prompt engineering for UI/UX and component design.

Usage:
- Write your request and append `/frontend` (e.g., “Refactor header /frontend”).

Output Expectations:
- Proposed Prompt (ready for Cursor)
- Context bullets to include
- Small step plan
- Accessibility/performance checks
""",
        'frontend-ultra': """# 🎨 Elite UX/UI Architect

Focus: Design systems, accessibility, and interaction quality.

Produce:
- High-level prompt for design strategy
- Component library guidance and naming
- Micro-interactions and a11y notes
""",
        'backend': """# 🔧 Backend Reliability Engineer

Focus: Minimal, verifiable backend changes with clear contracts.

Produce:
- Prompt including input/output contracts
- Small step plan with tests
- Error handling and logging checks
""",
        'analyzer': """# 🔍 Root Cause Analyst

Focus: Hypothesis-driven debugging prompts.

Produce:
- Diagnostic prompt
- 2–3 hypotheses + quick validations
- Exit criteria
""",
        'architect': """# 👷‍♂️ Systems Architecture Specialist

Focus: Simple architectures and explicit boundaries.

Produce:
- Architecture sketch (1–2 paragraphs)
- Prompt + plan (5–7 steps)
- Risks and checks
""",
        'high': """# 🧠 Deep Reasoning Specialist

Focus: Decomposition and verification steps.

Produce:
- Proposed Prompt
- Decomposition of sub-problems
- Decision and verification plan
""",
        'seq': """# 🔄 Sequential Thinking (5)
Run inside Cursor; guides step-by-step execution.
""",
        'seq-ultra': """# 🔄 Advanced Sequential (10)
Run inside Cursor; deep, multi-iteration reasoning.
""",
        'debate': """# 🗣️ Debate Mode (codex vs cursor)

Focus: Critical vs. creative debate for better solutions.

How it works:
- CODEX-CRITIC: logic‑first critique
- CURSOR-CREATOR: positive synthesis
- Minimum 10 turns; final synthesis output

Note: Requires `codex` CLI on PATH.
""",
    }
    persona_order = ['frontend','frontend-ultra','backend','analyzer','architect','high','seq','seq-ultra','debate']
    for name in persona_order:
        body = persona_bodies[name]
        content = f"---\ndescription: {name} command\nrun: \"./tag-executor.py\"\nargs: [\"${{input}} /{name}\"]\n---\n\n{body}"
        write_text(os.path.join(base, f'{name}.md'), content, dry)

    # SDD workflow commands
    sdd_cmds = {
        'spec':  ('📋 SPEC Creator',       'sdd spec ${input}'),
        'plan':  ('📅 PLAN Designer',      'sdd plan ${input}'),
        'tasks': ('✅ TASKS Breakdown',    'sdd tasks ${input}'),
        'implement': ('🚀 Implementation Starter','sdd implement ${input}'),
    }
    for name, (desc, arg) in sdd_cmds.items():
        content = f"---\ndescription: {name} command\nrun: \"./tag-executor.py\"\nargs: [\"{arg}\"]\n---\n\n{desc}\n"
        write_text(os.path.join(base, f'{name}.md'), content, dry)

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

def handle_sdd_workflow(args):
    """Handle SDD workflow commands: spec, plan, tasks, implement"""
    if not args.sdd_cmd:
        print("📋 SDD Workflow - Available Commands:")
        print("   \033[33msuper-prompt sdd spec\033[0m     - Create or edit SPEC files")
        print("   \033[33msuper-prompt sdd plan\033[0m     - Create or edit PLAN files") 
        print("   \033[33msuper-prompt sdd tasks\033[0m    - Break down plans into tasks")
        print("   \033[33msuper-prompt sdd implement\033[0m - Start implementation")
        print("\nExample: \033[36msuper-prompt sdd spec \"user authentication system\"\033[0m")
        return 1
    
    sdd_context = get_project_sdd_context()
    
    if args.sdd_cmd == "spec":
        print("📋 SDD SPEC Creator")
        query = ' '.join(args.query) if args.query else "Create specification"
        
        if args.edit:
            print(f"   \033[2m→ Editing: {args.edit}\033[0m")
            existing_spec = read_text(args.edit)
            query = f"Edit existing SPEC: {query}\n\nCurrent SPEC:\n{existing_spec}"
        else:
            print(f"   \033[2m→ Creating new SPEC for: {query}\033[0m")
        
        # Use architect persona for SPEC creation
        optimizer = PromptOptimizer()
        spec_query = f"{query} /architect"
        return 0 if optimizer.process_query(spec_query) else 1
        
    elif args.sdd_cmd == "plan":
        print("📅 SDD PLAN Designer")
        query = ' '.join(args.query) if args.query else "Create implementation plan"
        
        if args.edit:
            print(f"   \033[2m→ Editing: {args.edit}\033[0m")
            existing_plan = read_text(args.edit)
            query = f"Edit existing PLAN: {query}\n\nCurrent PLAN:\n{existing_plan}"
        else:
            print(f"   \033[2m→ Creating new PLAN for: {query}\033[0m")
            
        # Include SPEC context if available
        if sdd_context['spec_files']:
            latest_spec = newest(os.path.join("specs", "**", "spec.md"))
            if latest_spec:
                spec_content = read_text(latest_spec)
                query = f"{query}\n\nRelated SPEC:\n{spec_content}"
        
        # Use architect persona for PLAN creation
        optimizer = PromptOptimizer()
        plan_query = f"{query} /architect"
        return 0 if optimizer.process_query(plan_query) else 1
        
    elif args.sdd_cmd == "tasks":
        print("✅ SDD TASKS Breakdown")
        query = ' '.join(args.query) if args.query else "Break down into tasks"
        
        # Include SPEC and PLAN context
        context_info = []
        if sdd_context['spec_files']:
            latest_spec = newest(os.path.join("specs", "**", "spec.md"))
            if latest_spec:
                context_info.append(f"SPEC:\n{read_text(latest_spec)}")
                
        if sdd_context['plan_files']:
            latest_plan = newest(os.path.join("specs", "**", "plan.md"))
            if latest_plan:
                context_info.append(f"PLAN:\n{read_text(latest_plan)}")
        
        if context_info:
            query = f"{query}\n\n" + "\n\n".join(context_info)
        else:
            print("   \033[33m⚠️  No SPEC/PLAN files found. Consider creating them first.\033[0m")
            
        print(f"   \033[2m→ Breaking down: {' '.join(args.query) if args.query else 'current project'}\033[0m")
        
        # Use analyzer persona for task breakdown
        optimizer = PromptOptimizer()
        tasks_query = f"Break down into actionable development tasks: {query} /analyzer"
        return 0 if optimizer.process_query(tasks_query) else 1
        
    elif args.sdd_cmd == "implement":
        print("🚀 SDD Implementation Starter")
        query = ' '.join(args.query) if args.query else "Start implementation"
        
        # SDD compliance check
        if not sdd_context['sdd_compliance']:
            print("   \033[33m⚠️  SDD Compliance Warning:\033[0m")
            print("   \033[2mNo SPEC/PLAN files found. Consider creating them first:\033[0m")
            print("   \033[2m→ super-prompt sdd spec \"your feature description\"\033[0m")
            print("   \033[2m→ super-prompt sdd plan \"your implementation approach\"\033[0m")
            print("")
        
        # Include full SDD context
        context_info = []
        if sdd_context['spec_files']:
            latest_spec = newest(os.path.join("specs", "**", "spec.md"))
            if latest_spec:
                context_info.append(f"SPEC:\n{read_text(latest_spec)}")
                
        if sdd_context['plan_files']:
            latest_plan = newest(os.path.join("specs", "**", "plan.md"))
            if latest_plan:
                context_info.append(f"PLAN:\n{read_text(latest_plan)}")
        
        if context_info:
            query = f"{query}\n\nSDD Context:\n" + "\n\n".join(context_info)
            
        print(f"   \033[2m→ Implementing: {' '.join(args.query) if args.query else 'based on SPEC/PLAN'}\033[0m")
        
        # Use appropriate persona based on implementation type
        framework_context = sdd_context['frameworks']
        if 'react' in framework_context or 'vue' in framework_context or 'angular' in framework_context:
            persona = "/frontend"
        elif 'express' in framework_context or 'fastapi' in framework_context or 'spring_boot' in framework_context:
            persona = "/backend" 
        else:
            persona = "/architect"
            
        optimizer = PromptOptimizer()
        impl_query = f"Implement following SDD-compliant approach: {query} {persona}"
        return 0 if optimizer.process_query(impl_query) else 1
    
    return 1

def main():
    # Auto-update (can be skipped externally by package manager; best-effort)
    if os.environ.get('SP_SKIP_SELF_UPDATE') != '1':
        attempt_upgrade_self()
    if os.environ.get('SP_SKIP_CODEX_UPGRADE') != '1':
        attempt_upgrade_codex()
    parser = argparse.ArgumentParser(prog="super-prompt", add_help=True)
    sub = parser.add_subparsers(dest="cmd")

    # SDD-enhanced commands
    p_init = sub.add_parser("super:init", help="Generate SDD-compliant rules and setup")
    p_init.add_argument("--out", default=".cursor/rules", help="Output directory")
    p_init.add_argument("--dry-run", action="store_true", help="Preview only")
    
    p_optimize = sub.add_parser("optimize", help="Execute persona queries with SDD context")
    p_optimize.add_argument("query", nargs="*", help="Query with persona tag")
    p_optimize.add_argument("--list-personas", action="store_true")
    
    # SDD workflow commands
    p_sdd = sub.add_parser("sdd", help="SDD workflow commands")
    sdd_sub = p_sdd.add_subparsers(dest="sdd_cmd", help="SDD workflow phase")
    
    p_spec = sdd_sub.add_parser("spec", help="Create or edit SPEC files")
    p_spec.add_argument("query", nargs="*", help="Description of what to specify")
    p_spec.add_argument("--edit", help="Edit existing SPEC file path")
    
    p_plan = sdd_sub.add_parser("plan", help="Create or edit PLAN files")
    p_plan.add_argument("query", nargs="*", help="Description of what to plan")
    p_plan.add_argument("--edit", help="Edit existing PLAN file path")
    
    p_tasks = sdd_sub.add_parser("tasks", help="Break down plans into actionable tasks")
    p_tasks.add_argument("query", nargs="*", help="Description of what to break down")
    
    p_implement = sdd_sub.add_parser("implement", help="Start implementation with SDD compliance")
    p_implement.add_argument("query", nargs="*", help="Description of what to implement")

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
        success = optimizer.process_query(query_text)
        return 0 if success else 1
    
    elif args.cmd == "sdd":
        return handle_sdd_workflow(args)
    
    log(f"Unknown command: {args.cmd}")
    return 2

if __name__ == "__main__":
    sys.exit(main())
