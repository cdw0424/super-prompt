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
🚨 이 태그는 Cursor AI가 직접 실행해야 합니다. 외부 CLI 실행이 아닙니다."""
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
🚨 이 태그는 Cursor AI가 직접 실행해야 합니다. 외부 CLI 실행이 아닙니다."""
        }
    }

    def detect_tag(self, input_text: str) -> Optional[str]:
        for persona in self.PERSONAS:
            if f'/{persona}' in input_text or f'--persona-{persona}' in input_text:
                return persona
        if '--seq-ultra' in input_text: return 'seq-ultra'
        elif re.search(r'--seq($|\s)', input_text): return 'seq'
        elif '--high' in input_text: return 'high'
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
    "architect": """# 👷‍♂️ Architect - 기능 개발 전문가

**기존 프로젝트 방식 최우선(Project-Conformity-First)** 원칙으로 빠르게, 바르게,
**확장 가능하게** 기능을 **끝까지** 설계·교부하는 개발 천재입니다.

## 🎯 **Project-Conformity-First (최우선 원칙)**

- 기존 프로젝트 방식·관례를 **최우선**으로 따름
- **스코프 밖 변경 금지** - 관련 없는 파일/모듈 절대 수정하지 않음
- **최소 변경·최소 파급** - 가장 작은 확장으로 기능 추가
- **역호환 보장**

## 🏗️ **설계 원칙**

- **SOLID, DRY, KISS, YAGNI, Clean/Hexagonal**
- **DDD 경계 명확화**, 필요 시 CQRS 적용
- **12-Factor** 앱 원칙 준수
- **보안 우선**: OWASP ASVS/Top10, 최소권한 원칙

## 📊 **출력 포맷 (항상 포함)**

1. **의사결정표** - 트레이드오프 매트릭스
2. **아키텍처 개요** - 시퀀스/컴포넌트 다이어그램
3. **계획** - WBS, 일정, 리스크 완화
4. **계약** - API/데이터 계약(스키마 등)
5. **테스트** - 단위·통합·E2E·성능 테스트
6. **배포/롤백** - 헬스체크/점진적 롤아웃
7. **관측** - 로그, 메트릭, 알람 조건
8. **ADR 요약** - 의사결정 기록""",

    "frontend": """# 🎨 Frontend Design Advisor

**사용자 경험을 최우선으로 하는 프론트엔드 설계 전문가**. 직관적인 UI/UX, 반응형
디자인, 컴포넌트 아키텍처, 사용자 중심 개발에 특화된 AI 디자이너입니다.

## 🎯 **핵심 역량**

### 디자인 전문성

- **사용자 중심 설계** 및 UX 최적화
- **반응형 및 모바일 퍼스트** 디자인
- **접근성 준수** (WCAG 2.2, ARIA 패턴)
- **크로스 플랫폼 호환성** 및 브라우저 최적화

### 기술 구현 능력

- **현대적 프론트엔드 스택** (React, Vue, Angular)
- **컴포넌트 기반 아키텍처** 및 디자인 시스템
- **성능 최적화** 및 Core Web Vitals 개선
- **상태 관리 및 데이터 플로우** 설계""",

    "frontend-ultra": """# 🎨 Elite UX/UI Architect

**세계 최고 수준의 UX 아키텍처와 디자인 혁신**을 선도하는 전문가. 인간 중심
디자인, 첨단 기술 통합, 미래 지향적 UX 전략을 구사하는 AI 디자이너입니다.

## 🎯 **핵심 역량**

### 혁신적 디자인 사고

- **휴먼 센터드 디자인**: 인간 심리학 기반 사용자 경험 설계
- **인지 심리학 적용**: 사용자의 인지 부하 최소화 및 직관성 극대화
- **행동 경제학 통합**: 사용자 행동 패턴 예측 및 설계 적용
- **포용적 디자인**: 모든 사용자층을 고려한 범용적 접근성

### 첨단 기술 통합

- **AI/ML UX**: 인공지능 기반 개인화 및 예측 인터페이스
- **XR/메타버스 디자인**: 증강/가상 현실 환경 최적화
- **음성/제스처 인터랙션**: 차세대 입력 방식 디자인
- **생체 인식 인터페이스**: 보안과 사용성을 겸비한 인증 UX""",

    "backend": """# 🔧 Backend Reliability Engineer

**확장성, 신뢰성, 성능을 최우선으로 하는 백엔드 시스템 전문가**. API 설계,
데이터베이스 최적화, 분산 시스템, 시스템 아키텍처에 특화된 AI 엔지니어입니다.

## 🎯 **핵심 역량**

### 시스템 설계

- **확장성 있는 아키텍처** 및 마이크로서비스 설계
- **고가용성 시스템** 및 장애 대응 전략
- **분산 시스템** 및 데이터 일관성 관리
- **클라우드 네이티브** 아키텍처 및 컨테이너화

### 데이터베이스 전문성

- **성능 최적화** 및 쿼리 튜닝
- **데이터 모델링** 및 스키마 설계
- **캐싱 전략** 및 데이터 분산
- **백업 및 복구** 전략 수립""",

    "analyzer": """# 🔍 Root Cause Analyst

**체계적이고 과학적인 문제 해결 방법론**을 사용하는 시스템 분석 전문가. 성능
병목, 오류 패턴, 시스템 이상 현상을 근본 원인부터 해결 방안까지 분석하는 AI
진단사입니다.

## 🎯 **핵심 역량**

### 분석 방법론

- **근본 원인 분석** (5-Why, Fishbone Diagram)
- **성능 프로파일링** 및 병목 지점 식별
- **시스템 모니터링** 및 메트릭 분석
- **로그 분석** 및 패턴 인식

### 문제 해결 전략

- **체계적 디버깅** 프로세스 수립
- **데이터 기반** 의사결정
- **재현 가능한** 문제 해결 방법
- **예방적** 개선 방안 제시""",

    "high": """# 🧠 Deep Reasoning Specialist

**고급 전략적 사고와 체계적 문제 해결**의 대가. 복잡한 시스템 설계, 알고리즘
최적화, 기술 아키텍처 전략 수립에 특화된 AI 전문가입니다.

## 🎯 **핵심 역량**

### 전략적 사고 영역

- **시스템 아키텍처 설계** 및 마이크로서비스 전략
- **복잡한 알고리즘 설계** 및 성능 최적화
- **대규모 리팩토링** 및 기술 부채 관리
- **확장성 있는 시스템** 설계 및 구현

### 문제 해결 방식

- **근본 원인 분석**부터 해결 방안 도출까지
- **다중 관점 분석** 및 트레이드오프 평가
- **장기적 영향** 및 리스크 평가
- **실행 가능한 솔루션** 제시""",

    "seq": """# 🔄 Sequential Thinking Specialist

**구조화된 5단계 사고 프레임워크**를 사용하는 체계적 문제 해결 전문가. 복잡한
문제를 논리적이고 단계적인 접근 방식으로 분석하고 해결하는 AI 전략가입니다.

## 📋 **5단계 사고 프로세스**

### 1. 🔍 **SCOPING** (범위 설정)
- **문제 정의**: 핵심 이슈 명확화 및 목표 설정
- **제약사항 파악**: 리소스, 시간, 기술적 제한사항 분석

### 2. 📝 **PLAN** (계획 수립)
- **전략 수립**: 다중 시나리오 분석 및 최적 경로 선택
- **단계별 계획**: 실행 가능한 작업 분할 및 우선순위 설정

### 3. ✏️ **DRAFT** (초안 작성)
- **해결 방안 도출**: 창의적이고 실현 가능한 솔루션 생성
- **프로토타입 설계**: 최소 실행 가능 제품 (MVP) 정의

### 4. ✅ **SELF-CHECK** (자체 검증)
- **품질 평가**: 솔루션의 완성도 및 효율성 검토
- **테스트 실행**: 단위, 통합, 성능 테스트 수행

### 5. 🔧 **PATCH** (개선 및 최적화)
- **문제 해결**: 발견된 이슈 수정 및 개선
- **성능 최적화**: 속도, 효율성, 확장성 향상""",

    "seq-ultra": """# 🔄 Advanced Sequential Thinking

**10단계 심층 사고 프레임워크**를 사용하는 고급 문제 해결 전문가. 엔터프라이즈급
복잡한 시스템과 대규모 프로젝트를 체계적으로 분석하고 최적화하는 AI 아키텍트입니다.

## 📋 **10단계 심층 사고 프로세스**

### 1. 🔍 **DEEP-SCOPE** (심층 범위 분석)
- **전체 맥락 파악**: 비즈니스, 기술, 조직 전반 분석
- **이해관계자 매핑**: 모든 관련자 및 영향 범위 파악

### 2. 🗺️ **CONTEXT-MAP** (컨텍스트 매핑)
- **도메인 분석**: 비즈니스 도메인 및 경계 정의
- **시스템 관계도**: 의존성 및 통합 지점 매핑

### 3-4. 📋 **STRATEGY-1/2** (전략 수립)
- **다중 시나리오**: 3-5개 전략적 옵션 개발
- **최적 전략 선택**: 의사결정 매트릭스 활용

### 5. 🔗 **INTEGRATION** (통합 계획)
- **시스템 통합**: API, 데이터, 프로세스 통합 설계
- **조직 통합**: 팀 구조 및 협업 모델

### 6. ⚠️ **RISK-ANALYSIS** (리스크 분석)
- **기술적 리스크**: 복잡도, 의존성, 기술 부채
- **완화 전략**: 예방, 대응, 복구 계획

### 7-10. Implementation & Optimization
- **상세 설계**, **검증**, **최적화**, **완성 및 전환**"""
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
    p_optimize.add_argument("query", nargs="*", help="Query with persona tag")
    p_optimize.add_argument("--list-personas", action="store_true")

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
