#!/usr/bin/env python3
"""
Context Manager - Spec Kit 기반 컨텍스트 유지 시스템
대화 컨텍스트를 파일로 외부화하여 버전관리하고, 단계별 게이팅으로 컨텍스트 드리프트 차단
"""

import json
import os
import glob
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

class ContextType(Enum):
    SPEC = "spec"
    PLAN = "plan" 
    TASKS = "tasks"
    MEMORY = "memory"
    SESSION = "session"
    RULES = "rules"

class InjectionPolicy(Enum):
    FULL = "full"          # 전체 컨텍스트 주입
    SELECTIVE = "selective" # 선별적 주입
    SECTIONAL = "sectional" # 섹션별 주입
    MINIMAL = "minimal"     # 최소 주입

@dataclass
class ContextArtifact:
    type: ContextType
    path: str
    content: str
    checksum: str
    last_modified: float
    tags: List[str]
    priority: int = 1  # 1=highest, 5=lowest
    size_tokens: int = 0

@dataclass
class ContextSession:
    session_id: str
    project_id: str
    current_stage: str  # specify/plan/tasks/implement
    active_contexts: List[str]
    context_history: List[Dict]
    injection_policy: InjectionPolicy
    token_budget: int = 32000
    used_tokens: int = 0

class ContextManager:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.specs_dir = self.project_root / "specs"
        self.memory_dir = self.project_root / "memory"
        self.context_cache = {}
        self.session: Optional[ContextSession] = None
        
        # 디렉터리 구조 초기화
        self._ensure_directory_structure()
        
    def log(self, msg: str):
        print(f"--------context-manager: {msg}")
        
    def _ensure_directory_structure(self):
        """필수 디렉터리 구조 생성"""
        dirs = [
            self.specs_dir,
            self.memory_dir,
            self.memory_dir / "constitution",
            self.memory_dir / "rules",
            self.memory_dir / "sessions"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # constitution.md 기본 파일 생성
        constitution_file = self.memory_dir / "constitution" / "constitution.md"
        if not constitution_file.exists():
            constitution_file.write_text("""# Project Constitution

## Core Principles
- **Spec-First Development**: All features start with specification
- **Context Preservation**: Maintain design intent across all stages
- **Quality Gates**: Each stage validates against previous stages
- **Incremental Refinement**: Build complexity progressively

## Development Rules
- SPEC → PLAN → TASKS → IMPLEMENT workflow mandatory
- No implementation without approved plan
- All decisions documented with rationale
- Context artifacts version controlled

## Quality Standards
- Code quality: maintainable, testable, documented
- Security: secure by default, defense in depth
- Performance: optimize for user experience
- Accessibility: WCAG 2.1 AA compliance minimum
""")

    def _calculate_checksum(self, content: str) -> str:
        """컨텐츠 체크섬 계산"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _estimate_tokens(self, content: str) -> int:
        """대략적인 토큰 수 추정 (1토큰 ≈ 4글자)"""
        return len(content) // 4

    def create_spec_artifact(self, project_id: str, spec_content: str, tags: List[str] = None) -> str:
        """SPEC 아티팩트 생성"""
        if tags is None:
            tags = []
            
        spec_dir = self.specs_dir / project_id
        spec_dir.mkdir(parents=True, exist_ok=True)
        
        spec_file = spec_dir / "spec.md"
        spec_file.write_text(spec_content)
        
        checksum = self._calculate_checksum(spec_content)
        tokens = self._estimate_tokens(spec_content)
        
        artifact = ContextArtifact(
            type=ContextType.SPEC,
            path=str(spec_file),
            content=spec_content,
            checksum=checksum,
            last_modified=time.time(),
            tags=tags,
            priority=1,
            size_tokens=tokens
        )
        
        self._cache_artifact(artifact)
        self.log(f"spec artifact created: {spec_file} ({tokens} tokens)")
        return str(spec_file)

    def create_plan_artifact(self, project_id: str, plan_content: str, tags: List[str] = None) -> str:
        """PLAN 아티팩트 생성"""
        if tags is None:
            tags = []
            
        spec_dir = self.specs_dir / project_id
        spec_dir.mkdir(parents=True, exist_ok=True)
        
        plan_file = spec_dir / "plan.md"
        plan_file.write_text(plan_content)
        
        checksum = self._calculate_checksum(plan_content)
        tokens = self._estimate_tokens(plan_content)
        
        artifact = ContextArtifact(
            type=ContextType.PLAN,
            path=str(plan_file),
            content=plan_content,
            checksum=checksum,
            last_modified=time.time(),
            tags=tags,
            priority=1,
            size_tokens=tokens
        )
        
        self._cache_artifact(artifact)
        self.log(f"plan artifact created: {plan_file} ({tokens} tokens)")
        return str(plan_file)

    def create_tasks_artifact(self, project_id: str, tasks_content: str, tags: List[str] = None) -> str:
        """TASKS 아티팩트 생성"""
        if tags is None:
            tags = []
            
        spec_dir = self.specs_dir / project_id
        spec_dir.mkdir(parents=True, exist_ok=True)
        
        tasks_file = spec_dir / "tasks.md" 
        tasks_file.write_text(tasks_content)
        
        checksum = self._calculate_checksum(tasks_content)
        tokens = self._estimate_tokens(tasks_content)
        
        artifact = ContextArtifact(
            type=ContextType.TASKS,
            path=str(tasks_file),
            content=tasks_content,
            checksum=checksum,
            last_modified=time.time(),
            tags=tags,
            priority=2,
            size_tokens=tokens
        )
        
        self._cache_artifact(artifact)
        self.log(f"tasks artifact created: {tasks_file} ({tokens} tokens)")
        return str(tasks_file)

    def create_memory_artifact(self, name: str, content: str, artifact_type: str = "rules") -> str:
        """메모리 아티팩트 생성 (constitution, rules, 기타)"""
        memory_subdir = self.memory_dir / artifact_type
        memory_subdir.mkdir(parents=True, exist_ok=True)
        
        memory_file = memory_subdir / f"{name}.md"
        memory_file.write_text(content)
        
        checksum = self._calculate_checksum(content)
        tokens = self._estimate_tokens(content)
        
        artifact = ContextArtifact(
            type=ContextType.MEMORY,
            path=str(memory_file),
            content=content,
            checksum=checksum,
            last_modified=time.time(),
            tags=[artifact_type, name],
            priority=1,
            size_tokens=tokens
        )
        
        self._cache_artifact(artifact)
        self.log(f"memory artifact created: {memory_file} ({tokens} tokens)")
        return str(memory_file)

    def _cache_artifact(self, artifact: ContextArtifact):
        """아티팩트 캐시에 저장"""
        self.context_cache[artifact.path] = artifact

    def start_session(self, project_id: str, stage: str = "specify", injection_policy: InjectionPolicy = InjectionPolicy.SELECTIVE) -> str:
        """컨텍스트 세션 시작"""
        session_id = f"{project_id}_{int(time.time())}"
        
        self.session = ContextSession(
            session_id=session_id,
            project_id=project_id,
            current_stage=stage,
            active_contexts=[],
            context_history=[],
            injection_policy=injection_policy,
            token_budget=32000,
            used_tokens=0
        )
        
        # 세션 파일 저장 (enum을 문자열로 변환)
        session_data = asdict(self.session)
        session_data['injection_policy'] = self.session.injection_policy.value
        session_file = self.memory_dir / "sessions" / f"{session_id}.json"
        session_file.write_text(json.dumps(session_data, indent=2))
        
        self.log(f"context session started: {session_id} (stage={stage})")
        return session_id

    def load_session(self, session_id: str) -> bool:
        """기존 세션 로드"""
        session_file = self.memory_dir / "sessions" / f"{session_id}.json"
        
        if not session_file.exists():
            self.log(f"session not found: {session_id}")
            return False
            
        try:
            session_data = json.loads(session_file.read_text())
            # enum 값을 다시 변환
            if 'injection_policy' in session_data:
                session_data['injection_policy'] = InjectionPolicy(session_data['injection_policy'])
            self.session = ContextSession(**session_data)
            self.log(f"session loaded: {session_id}")
            return True
        except Exception as e:
            self.log(f"failed to load session: {e}")
            return False

    def get_context_for_stage(self, stage: str, max_tokens: int = 16000) -> str:
        """단계별 컨텍스트 조합 및 주입"""
        if not self.session:
            return ""
            
        # 단계별 필수 컨텍스트 정의
        required_contexts = {
            "specify": ["constitution"],
            "plan": ["constitution", "spec"],
            "tasks": ["constitution", "spec", "plan"],
            "implement": ["constitution", "spec", "plan", "tasks"]
        }
        
        contexts_to_load = required_contexts.get(stage, [])
        injected_contexts = []
        total_tokens = 0
        
        # Constitution 먼저 로드 (최우선)
        if "constitution" in contexts_to_load:
            constitution = self._load_constitution()
            if constitution:
                tokens = self._estimate_tokens(constitution)
                if total_tokens + tokens <= max_tokens:
                    injected_contexts.append(f"## Project Constitution\n\n{constitution}")
                    total_tokens += tokens
        
        # 프로젝트별 아티팩트 로드
        project_artifacts = self._discover_project_artifacts(self.session.project_id)
        
        for context_type in ["spec", "plan", "tasks"]:
            if context_type in contexts_to_load and context_type in project_artifacts:
                artifact = project_artifacts[context_type]
                
                if self.session.injection_policy == InjectionPolicy.SELECTIVE:
                    content = self._extract_selective_content(artifact, stage)
                else:
                    content = artifact.content
                    
                tokens = self._estimate_tokens(content)
                if total_tokens + tokens <= max_tokens:
                    injected_contexts.append(f"## {context_type.upper()}\n\n{content}")
                    total_tokens += tokens
                else:
                    # 토큰 한계 시 요약
                    summary = self._summarize_content(content, max_tokens - total_tokens)
                    injected_contexts.append(f"## {context_type.upper()} (Summary)\n\n{summary}")
                    total_tokens += self._estimate_tokens(summary)
        
        self.session.used_tokens = total_tokens
        self._save_session()
        
        final_context = "\n\n".join(injected_contexts)
        self.log(f"context assembled for {stage}: {total_tokens} tokens")
        return final_context

    def _load_constitution(self) -> str:
        """Constitution 로드"""
        constitution_file = self.memory_dir / "constitution" / "constitution.md"
        if constitution_file.exists():
            return constitution_file.read_text()
        return ""

    def _discover_project_artifacts(self, project_id: str) -> Dict[str, ContextArtifact]:
        """프로젝트 아티팩트 발견"""
        artifacts = {}
        project_dir = self.specs_dir / project_id
        
        if not project_dir.exists():
            return artifacts
            
        # 기본 아티팩트 로드
        for artifact_type in ["spec", "plan", "tasks"]:
            artifact_file = project_dir / f"{artifact_type}.md"
            if artifact_file.exists():
                content = artifact_file.read_text()
                artifacts[artifact_type] = ContextArtifact(
                    type=ContextType(artifact_type),
                    path=str(artifact_file),
                    content=content,
                    checksum=self._calculate_checksum(content),
                    last_modified=artifact_file.stat().st_mtime,
                    tags=[artifact_type],
                    priority=1,
                    size_tokens=self._estimate_tokens(content)
                )
        
        return artifacts

    def _extract_selective_content(self, artifact: ContextArtifact, stage: str) -> str:
        """선별적 컨텐츠 추출"""
        content = artifact.content
        
        # 단계별 중요 섹션 추출 로직
        if stage == "plan" and artifact.type == ContextType.SPEC:
            # PLAN 단계에서는 SPEC의 핵심 요구사항만
            return self._extract_requirements_section(content)
        elif stage == "tasks" and artifact.type == ContextType.PLAN:
            # TASKS 단계에서는 PLAN의 아키텍처 결정만
            return self._extract_architecture_section(content)
        elif stage == "implement":
            # IMPLEMENT 단계에서는 태스크 관련 부분만
            return self._extract_task_relevant_content(content)
            
        return content

    def _extract_requirements_section(self, content: str) -> str:
        """요구사항 섹션 추출"""
        lines = content.split('\n')
        in_requirements = False
        requirements = []
        
        for line in lines:
            if '# Requirements' in line or '## Requirements' in line:
                in_requirements = True
                requirements.append(line)
            elif in_requirements and line.startswith('#'):
                break
            elif in_requirements:
                requirements.append(line)
                
        return '\n'.join(requirements) if requirements else content[:1000]

    def _extract_architecture_section(self, content: str) -> str:
        """아키텍처 섹션 추출"""
        lines = content.split('\n')
        in_architecture = False
        architecture = []
        
        for line in lines:
            if 'Architecture' in line and line.startswith('#'):
                in_architecture = True
                architecture.append(line)
            elif in_architecture and line.startswith('#') and 'Architecture' not in line:
                break
            elif in_architecture:
                architecture.append(line)
                
        return '\n'.join(architecture) if architecture else content[:1000]

    def _extract_task_relevant_content(self, content: str) -> str:
        """태스크 관련 컨텐츠 추출"""
        # 현재 태스크와 관련된 부분만 추출
        return content[:1500]  # 구현 단계에서는 최소한으로

    def _summarize_content(self, content: str, max_tokens: int) -> str:
        """컨텐츠 요약 (토큰 한계 시)"""
        lines = content.split('\n')
        summary_lines = []
        tokens = 0
        
        for line in lines:
            line_tokens = self._estimate_tokens(line)
            if tokens + line_tokens <= max_tokens:
                summary_lines.append(line)
                tokens += line_tokens
            else:
                break
                
        if len(summary_lines) < len(lines):
            summary_lines.append(f"\n... (truncated, showing {len(summary_lines)}/{len(lines)} lines)")
            
        return '\n'.join(summary_lines)

    def _save_session(self):
        """세션 상태 저장"""
        if self.session:
            session_data = asdict(self.session)
            session_data['injection_policy'] = self.session.injection_policy.value
            session_file = self.memory_dir / "sessions" / f"{self.session.session_id}.json"
            session_file.write_text(json.dumps(session_data, indent=2))

    def update_stage(self, new_stage: str) -> bool:
        """단계 전환 (게이팅 체크 포함)"""
        if not self.session:
            self.log("no active session")
            return False
            
        # 단계 전환 게이팅 규칙
        stage_flow = ["specify", "plan", "tasks", "implement"]
        current_index = stage_flow.index(self.session.current_stage) if self.session.current_stage in stage_flow else -1
        new_index = stage_flow.index(new_stage) if new_stage in stage_flow else -1
        
        if new_index <= current_index:
            # 이전 단계로 돌아가는 것은 허용
            self.session.current_stage = new_stage
            self._save_session()
            self.log(f"stage updated: {new_stage}")
            return True
        elif new_index == current_index + 1:
            # 다음 단계로 진행 - 아티팩트 존재 확인
            if self._validate_stage_artifacts(self.session.current_stage):
                self.session.current_stage = new_stage
                self._save_session()
                self.log(f"stage updated: {new_stage}")
                return True
            else:
                self.log(f"stage transition blocked: missing artifacts for {self.session.current_stage}")
                return False
        else:
            self.log(f"invalid stage transition: {self.session.current_stage} -> {new_stage}")
            return False

    def _validate_stage_artifacts(self, stage: str) -> bool:
        """단계별 필수 아티팩트 존재 확인"""
        project_dir = self.specs_dir / self.session.project_id
        
        required_files = {
            "specify": [],  # specify 단계는 아티팩트 요구사항 없음
            "plan": ["spec.md"],
            "tasks": ["spec.md", "plan.md"],
            "implement": ["spec.md", "plan.md", "tasks.md"]
        }
        
        for required_file in required_files.get(stage, []):
            if not (project_dir / required_file).exists():
                return False
                
        return True

    def get_session_status(self) -> Dict[str, Any]:
        """세션 상태 반환"""
        if not self.session:
            return {"status": "no_session"}
            
        project_artifacts = self._discover_project_artifacts(self.session.project_id)
        
        return {
            "session_id": self.session.session_id,
            "project_id": self.session.project_id,
            "current_stage": self.session.current_stage,
            "artifacts": list(project_artifacts.keys()),
            "token_usage": f"{self.session.used_tokens}/{self.session.token_budget}",
            "injection_policy": self.session.injection_policy.value,
            "can_advance": self._validate_stage_artifacts(self.session.current_stage)
        }

    def list_projects(self) -> List[str]:
        """프로젝트 목록 반환"""
        if not self.specs_dir.exists():
            return []
            
        projects = [d.name for d in self.specs_dir.iterdir() if d.is_dir()]
        return sorted(projects)

    def cleanup_old_sessions(self, days: int = 30):
        """오래된 세션 정리"""
        sessions_dir = self.memory_dir / "sessions"
        if not sessions_dir.exists():
            return
            
        cutoff_time = time.time() - (days * 24 * 3600)
        cleaned = 0
        
        for session_file in sessions_dir.glob("*.json"):
            if session_file.stat().st_mtime < cutoff_time:
                session_file.unlink()
                cleaned += 1
                
        if cleaned > 0:
            self.log(f"cleaned {cleaned} old sessions (older than {days} days)")

def main():
    """CLI 테스트 인터페이스"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python context_manager.py <command> [args...]")
        return
        
    cm = ContextManager()
    command = sys.argv[1]
    
    if command == "init":
        project_id = sys.argv[2] if len(sys.argv) > 2 else "default"
        session_id = cm.start_session(project_id)
        print(f"Session started: {session_id}")
        
    elif command == "status":
        status = cm.get_session_status()
        print(json.dumps(status, indent=2))
        
    elif command == "projects":
        projects = cm.list_projects()
        print("Projects:", projects)
        
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        cm.cleanup_old_sessions(days)
        
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()