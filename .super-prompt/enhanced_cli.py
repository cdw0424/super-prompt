#!/usr/bin/env python3
"""
Super Prompt - Enhanced CLI Implementation
Enhanced CLI with immediate Python execution guarantee, MCP dependency checking,
and full integration with all .super-prompt/ tools. Works with both Codex and Cursor.
"""

import argparse, glob, os, sys, re, json, datetime, textwrap, subprocess, shutil
from typing import Dict, List, Optional

VERSION = "3.1.73-fixed"

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

def slugify(name: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower())
    base = re.sub(r"-+", "-", base).strip("-")
    return base or "persona"

def ylist(items):
    return "[" + ", ".join(json.dumps(i) for i in items) + "]"

def take_excerpt(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."

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
    """Lightweight SDD-related context used in prompts/rules."""
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

class PromptOptimizer:
    def __init__(self):
        self.personas = self.get_personas()

    def get_personas(self):
        # This is now the single source of truth for personas.
        # It can be expanded to load from a YAML file if needed.
        return {
            'frontend': {'desc': 'Frontend Design Advisor'},
            'backend': {'desc': 'Backend Reliability Engineer'},
            'architect': {'desc': 'Project Architecture Specialist'},
            'dev': {'desc': 'Developer'},
            'devops': {'desc': 'DevOps Engineer'},
            'doc_master': {'desc': 'Documentation Master'},
            'implement': {'desc': 'Implementer'},
            'mentor': {'desc': 'Mentor'},
            'plan': {'desc': 'Planner'},
            'qa': {'desc': 'QA Engineer'},
            'refactorer': {'desc': 'Refactorer'},
            'review': {'desc': 'Reviewer'},
            'scribe': {'desc': 'Scribe'},
            'spec': {'desc': 'Specifier'},
            'specify': {'desc': 'Specify'},
            'tasks': {'desc': 'Task Master'},
            'tr': {'desc': 'Translator'},
            'seq': {'desc': 'Sequential Thinker'},
            'seq-ultra': {'desc': 'Advanced Sequential Thinker'},
            'debate': {'desc': 'Debater'},
            'ultracompressed': {'desc': 'Ultra Compressed'},
            'performance': {'desc': 'Performance Engineer'},
            'security': {'desc': 'Security Engineer'},
            'task': {'desc': 'Task Creator'},
            'wave': {'desc': 'Wave Thinker'},
            'db-expert': {'desc': 'Database Expert'},
            'docs-refector': {'desc': 'Docs Refactorer'},
        }

    def process_query(self, query: str) -> str:
        """
        Takes a raw query, detects the persona, cleans the query,
        and returns a fully formed prompt string for the LLM.
        """
        persona_tag_match = re.search(r"/(?P<persona>\S+)", query)
        if not persona_tag_match:
            return f"Error: No persona tag (e.g., /dev) found in query: '{query}'"

        persona = persona_tag_match.group("persona")
        if persona not in self.personas:
            return f"Error: Unknown persona '/{persona}'"

        clean_query = query.replace(f"/{persona}", "").strip()

        log(f"Preparing prompt for persona: /{persona}")
        
        # Here, you would build the full prompt string based on the persona,
        # the clean_query, and any context. This is a simplified example.
        full_prompt = (
            f"**Persona: {self.personas[persona]['desc']}**\n\n"
            f"**Request:**\n{clean_query}"
        )
        
        return full_prompt

def generate_sdd_rules_files(out_dir=".cursor/rules", dry=False):
    """Generate SDD rule files in Cursor rules directory"""
    report_parts = []
    sdd_context = get_project_sdd_context()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    os.makedirs(out_dir, exist_ok=True)
    
    org_content = f"""---
description: "Organization guardrails — generated {now}"
globs: ["**/*"]
alwaysApply: true
---
# Organization Guardrails
- Language: English only in documentation and rules.
- All debug/console lines MUST use the '--------' prefix.
- Secrets/tokens/PII MUST be masked in prompts, code, and logs.
"""
    
    sdd_content = f"""---
description: "SDD core & self-check — generated {now}"
globs: ["**/*"]
alwaysApply: true
---
# Spec-Driven Development (SDD)
- No implementation before SPEC and PLAN are approved.
- Current SDD Status: {'✅ Compliant' if sdd_context['sdd_compliance'] else '❌ Missing SPEC/PLAN files'}
"""

    write_text(os.path.join(out_dir, "00-organization.mdc"), org_content, dry)
    report_parts.append(f"Wrote {os.path.join(out_dir, '00-organization.mdc')}")
    write_text(os.path.join(out_dir, "10-sdd-core.mdc"), sdd_content, dry)
    report_parts.append(f"Wrote {os.path.join(out_dir, '10-sdd-core.mdc')}")
    
    report_parts.append(f"SDD rules generated in {out_dir}")
    return "\n".join(report_parts)

def install_cursor_commands_in_project(dry=False):
    """Install Cursor slash commands in the current project."""
    report_parts = []
    base = os.path.join('.cursor', 'commands', 'super-prompt')
    os.makedirs(base, exist_ok=True)

    # Critical step: Remove the legacy shell script executor
    legacy_executor_path = os.path.join(base, 'tag-executor.sh')
    if os.path.exists(legacy_executor_path):
        if not dry:
            os.remove(legacy_executor_path)
        report_parts.append(f"DELETED legacy executor: {legacy_executor_path}")
    
    # This function now only creates markdown files pointing to MCP tools
    personas = PromptOptimizer().get_personas()
    for name in personas:
        content = f"""---
description: "Run super-prompt {name} persona"
run: "super-prompt mcp tool {name} --query '$_prompt_'"
---
"""
        path = os.path.join(base, f'{name}.md')
        write_text(path, content, dry)
        report_parts.append(f"Wrote {path}")
        
    return "\n".join(report_parts)

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
\033[2m                     v{VERSION} | @cdw0424/super-prompt\033[0m
"""
    print(logo)

def main(cli_args=None):
    parser = argparse.ArgumentParser(prog="super-prompt", add_help=True)
    sub = parser.add_subparsers(dest="cmd")

    p_init = sub.add_parser("super:init", help="Generate SDD-compliant rules and setup")
    p_init.add_argument("--out", default=".cursor/rules", help="Output directory")
    p_init.add_argument("--dry-run", action="store_true", help="Preview only")
    
    p_mcp = sub.add_parser("mcp:serve", help="Start Super Prompt MCP server over stdio")
    p_mcp.add_argument("--debug", action="store_true", help="Enable verbose logging to stderr")
    
    # Add a new command for the optimizer
    p_optimize = sub.add_parser("optimize", help="Run the prompt optimizer")
    p_optimize.add_argument("query", help="The full query string with a persona tag")

    args = parser.parse_args(cli_args)
    if not args.cmd: 
        parser.print_help()
        return 1

    if args.cmd == "super:init":
        show_ascii_logo()
        print("\\033[33m\\033[1m🚀 Initializing project setup...\\033[0m\\n")
        
        print("\\033[36m📋 Generating Cursor rules...\\033[0m")
        rules_report = generate_sdd_rules_files(args.out, args.dry_run)
        print(rules_report)

        print("\\n\\033[36m📋 Installing Cursor commands...\\033[0m")
        install_report = install_cursor_commands_in_project(args.dry_run)
        print(install_report)
        
        print("\\n\\033[32m\\033[1m🎉 Setup Complete!\\033[0m")
        return 0

    elif args.cmd == "optimize":
        optimizer = PromptOptimizer()
        optimized_prompt = optimizer.process_query(args.query)
        print(optimized_prompt)
        return 0
        
    elif args.cmd == "mcp:serve":
        server_path = os.path.join(os.path.dirname(__file__), "mcp_srv", "server.py")
        if not os.path.exists(server_path):
            print(f"-------- MCP server entry not found at: {server_path}")
            return 2
        if getattr(args, "debug", False):
            os.environ["SUPER_PROMPT_MCP_DEBUG"] = "1"
        os.execv(sys.executable, [sys.executable, server_path])

    return 0

if __name__ == "__main__":
    sys.exit(main())
