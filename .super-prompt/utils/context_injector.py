#!/usr/bin/env python3
"""
Context Injector - 컨텍스트 자동 주입 시스템
단계별/명령어별 컨텍스트 자동 주입과 토큰 최적화
"""

import os
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from context_manager import ContextManager, InjectionPolicy, ContextType

class ContextInjector:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.context_manager = ContextManager(project_root)
        
        # 명령어별 컨텍스트 요구사항 정의
        self.command_context_map = {
            # SDD Commands
            "sdd_spec": {
                "required_contexts": ["constitution"],
                "stage": "specify",
                "injection_policy": InjectionPolicy.FULL,
                "max_tokens": 8000
            },
            "sdd_plan": {
                "required_contexts": ["constitution", "spec"],
                "stage": "plan", 
                "injection_policy": InjectionPolicy.SELECTIVE,
                "max_tokens": 12000
            },
            "sdd_tasks": {
                "required_contexts": ["constitution", "spec", "plan"],
                "stage": "tasks",
                "injection_policy": InjectionPolicy.SELECTIVE,
                "max_tokens": 16000
            },
            "sdd_implement": {
                "required_contexts": ["constitution", "spec", "plan", "tasks"],
                "stage": "implement",
                "injection_policy": InjectionPolicy.MINIMAL,
                "max_tokens": 8000  # 구현 시에는 필수만
            },
            # Persona Commands
            "architect": {
                "required_contexts": ["constitution", "spec", "plan"],
                "stage": "auto_detect",
                "injection_policy": InjectionPolicy.SELECTIVE,
                "max_tokens": 16000
            },
            "frontend": {
                "required_contexts": ["constitution", "plan", "tasks"],
                "stage": "auto_detect",
                "injection_policy": InjectionPolicy.SECTIONAL,
                "max_tokens": 12000
            },
            "backend": {
                "required_contexts": ["constitution", "plan", "tasks"],
                "stage": "auto_detect",
                "injection_policy": InjectionPolicy.SECTIONAL,
                "max_tokens": 12000
            },
            "analyzer": {
                "required_contexts": ["constitution", "spec", "plan", "tasks"],
                "stage": "auto_detect",
                "injection_policy": InjectionPolicy.FULL,
                "max_tokens": 20000
            }
        }
        
    def log(self, msg: str):
        print(f"--------context-injector: {msg}")
        
    def inject_context_for_command(self, command: str, query: str, project_id: str = None) -> Tuple[str, Dict[str, Any]]:
        """명령어별 컨텍스트 주입"""
        
        # 프로젝트 ID 자동 감지
        if not project_id:
            project_id = self._detect_project_id(query)
            
        if not project_id:
            project_id = "default"
            
        # 명령어별 컨텍스트 설정 조회
        context_config = self.command_context_map.get(command, {
            "required_contexts": ["constitution"],
            "stage": "auto_detect",
            "injection_policy": InjectionPolicy.SELECTIVE,
            "max_tokens": 12000
        })
        
        # 세션 시작/로드
        session_id = self._ensure_session(project_id, context_config["stage"])
        
        # 컨텍스트 조합
        injected_context = self._build_context(
            project_id=project_id,
            required_contexts=context_config["required_contexts"],
            injection_policy=context_config["injection_policy"],
            max_tokens=context_config["max_tokens"],
            query=query
        )
        
        # 최종 프롬프트 구성
        enhanced_prompt = self._build_enhanced_prompt(
            base_query=query,
            injected_context=injected_context,
            command=command,
            project_id=project_id
        )
        
        # 메타데이터 반환
        metadata = {
            "session_id": session_id,
            "project_id": project_id,
            "command": command,
            "stage": context_config["stage"],
            "injection_policy": context_config["injection_policy"].value,
            "context_tokens": self.context_manager._estimate_tokens(injected_context),
            "total_tokens": self.context_manager._estimate_tokens(enhanced_prompt)
        }
        
        self.log(f"context injected for {command}: {metadata['context_tokens']} context + {metadata['total_tokens'] - metadata['context_tokens']} query tokens")
        
        return enhanced_prompt, metadata
        
    def _detect_project_id(self, query: str) -> Optional[str]:
        """쿼리에서 프로젝트 ID 자동 감지"""
        
        # 명시적 프로젝트 참조 패턴
        patterns = [
            r'project[:\s]+([a-zA-Z0-9_-]+)',
            r'for\s+([a-zA-Z0-9_-]+)\s+project',
            r'@([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
                
        # 기존 프로젝트 목록에서 매칭
        existing_projects = self.context_manager.list_projects()
        for project in existing_projects:
            if project.lower() in query.lower():
                return project
                
        return None
        
    def _ensure_session(self, project_id: str, stage: str) -> str:
        """세션 확보 (기존 세션 로드 또는 새 세션 생성)"""
        
        # 기존 활성 세션 확인
        sessions_dir = self.context_manager.memory_dir / "sessions"
        if sessions_dir.exists():
            for session_file in sessions_dir.glob(f"{project_id}_*.json"):
                session_id = session_file.stem
                if self.context_manager.load_session(session_id):
                    return session_id
                    
        # 새 세션 생성
        if stage == "auto_detect":
            stage = self._detect_current_stage(project_id)
            
        return self.context_manager.start_session(project_id, stage)
        
    def _detect_current_stage(self, project_id: str) -> str:
        """프로젝트의 현재 단계 자동 감지"""
        project_dir = self.context_manager.specs_dir / project_id
        
        if not project_dir.exists():
            return "specify"
            
        # 아티팩트 존재 여부로 단계 판단
        if (project_dir / "tasks.md").exists():
            return "implement"
        elif (project_dir / "plan.md").exists():
            return "tasks"
        elif (project_dir / "spec.md").exists():
            return "plan"
        else:
            return "specify"
            
    def _build_context(self, project_id: str, required_contexts: List[str], injection_policy: InjectionPolicy, max_tokens: int, query: str) -> str:
        """컨텍스트 구성"""
        
        context_parts = []
        used_tokens = 0
        
        # 우선순위별 컨텍스트 로드
        priority_contexts = {
            "constitution": 1,
            "spec": 2, 
            "plan": 3,
            "tasks": 4,
            "memory": 5
        }
        
        # 우선순위별 정렬
        sorted_contexts = sorted(required_contexts, key=lambda x: priority_contexts.get(x, 99))
        
        for context_type in sorted_contexts:
            context_content = self._load_context_content(project_id, context_type, injection_policy, query)
            
            if context_content:
                content_tokens = self.context_manager._estimate_tokens(context_content)
                
                if used_tokens + content_tokens <= max_tokens:
                    context_parts.append(f"# {context_type.upper()}\n\n{context_content}")
                    used_tokens += content_tokens
                else:
                    # 토큰 한계 시 요약
                    remaining_tokens = max_tokens - used_tokens
                    if remaining_tokens > 100:  # 최소 100토큰은 있어야 요약 의미
                        summary = self._summarize_for_tokens(context_content, remaining_tokens)
                        context_parts.append(f"# {context_type.upper()} (Summary)\n\n{summary}")
                        used_tokens += self.context_manager._estimate_tokens(summary)
                    break
                    
        return "\n\n".join(context_parts)
        
    def _load_context_content(self, project_id: str, context_type: str, injection_policy: InjectionPolicy, query: str) -> str:
        """컨텍스트 타입별 컨텐츠 로드"""
        
        if context_type == "constitution":
            return self._load_constitution()
        elif context_type in ["spec", "plan", "tasks"]:
            return self._load_project_artifact(project_id, context_type, injection_policy, query)
        elif context_type == "memory":
            return self._load_memory_artifacts(query)
        else:
            return ""
            
    def _load_constitution(self) -> str:
        """Constitution 로드"""
        constitution_file = self.context_manager.memory_dir / "constitution" / "constitution.md"
        if constitution_file.exists():
            return constitution_file.read_text()
        return ""
        
    def _load_project_artifact(self, project_id: str, artifact_type: str, injection_policy: InjectionPolicy, query: str) -> str:
        """프로젝트 아티팩트 로드"""
        artifact_file = self.context_manager.specs_dir / project_id / f"{artifact_type}.md"
        
        if not artifact_file.exists():
            return ""
            
        content = artifact_file.read_text()
        
        # 주입 정책에 따른 컨텐츠 필터링
        if injection_policy == InjectionPolicy.FULL:
            return content
        elif injection_policy == InjectionPolicy.SELECTIVE:
            return self._extract_relevant_sections(content, query)
        elif injection_policy == InjectionPolicy.SECTIONAL:
            return self._extract_key_sections(content, artifact_type)
        elif injection_policy == InjectionPolicy.MINIMAL:
            return self._extract_essential_info(content, artifact_type)
        else:
            return content
            
    def _load_memory_artifacts(self, query: str) -> str:
        """메모리 아티팩트 로드 (쿼리 관련)"""
        memory_content = []
        
        # Rules 디렉터리 스캔
        rules_dir = self.context_manager.memory_dir / "rules"
        if rules_dir.exists():
            for rule_file in rules_dir.glob("*.md"):
                if self._is_relevant_rule(rule_file.read_text(), query):
                    memory_content.append(f"## {rule_file.stem}\n\n{rule_file.read_text()}")
                    
        return "\n\n".join(memory_content)
        
    def _extract_relevant_sections(self, content: str, query: str) -> str:
        """쿼리 관련 섹션 추출"""
        lines = content.split('\n')
        relevant_sections = []
        current_section = []
        section_header = ""
        
        # 쿼리 키워드 추출
        query_keywords = set(re.findall(r'\b\w+\b', query.lower()))
        
        for line in lines:
            if line.startswith('#'):
                # 이전 섹션 평가
                if current_section and section_header:
                    section_text = '\n'.join(current_section)
                    if self._is_section_relevant(section_text, query_keywords):
                        relevant_sections.extend([section_header] + current_section)
                        
                # 새 섹션 시작
                section_header = line
                current_section = []
            else:
                current_section.append(line)
                
        # 마지막 섹션 처리
        if current_section and section_header:
            section_text = '\n'.join(current_section)
            if self._is_section_relevant(section_text, query_keywords):
                relevant_sections.extend([section_header] + current_section)
                
        return '\n'.join(relevant_sections) if relevant_sections else content[:1000]
        
    def _is_section_relevant(self, section_text: str, query_keywords: set) -> bool:
        """섹션 관련성 판단"""
        section_words = set(re.findall(r'\b\w+\b', section_text.lower()))
        intersection = query_keywords.intersection(section_words)
        return len(intersection) >= 2 or len(intersection) > 0 and len(query_keywords) <= 3
        
    def _extract_key_sections(self, content: str, artifact_type: str) -> str:
        """아티팩트 타입별 핵심 섹션 추출"""
        key_sections = {
            "spec": ["requirements", "goals", "success criteria", "constraints"],
            "plan": ["architecture", "implementation", "technology stack", "milestones"],
            "tasks": ["priority", "dependencies", "acceptance criteria", "estimates"]
        }
        
        target_keywords = key_sections.get(artifact_type, [])
        return self._extract_sections_by_keywords(content, target_keywords)
        
    def _extract_sections_by_keywords(self, content: str, keywords: List[str]) -> str:
        """키워드별 섹션 추출"""
        lines = content.split('\n')
        selected_sections = []
        current_section = []
        section_header = ""
        
        for line in lines:
            if line.startswith('#'):
                # 이전 섹션 평가
                if current_section and section_header:
                    if any(keyword.lower() in section_header.lower() for keyword in keywords):
                        selected_sections.extend([section_header] + current_section)
                        
                section_header = line
                current_section = []
            else:
                current_section.append(line)
                
        # 마지막 섹션
        if current_section and section_header:
            if any(keyword.lower() in section_header.lower() for keyword in keywords):
                selected_sections.extend([section_header] + current_section)
                
        return '\n'.join(selected_sections) if selected_sections else content[:800]
        
    def _extract_essential_info(self, content: str, artifact_type: str) -> str:
        """필수 정보만 추출 (최소 주입용)"""
        lines = content.split('\n')
        essential_lines = []
        
        for line in lines:
            # 헤더와 핵심 문장만
            if (line.startswith('#') or 
                'must' in line.lower() or 
                'requirement' in line.lower() or
                'critical' in line.lower() or
                line.startswith('-') or 
                line.startswith('*')):
                essential_lines.append(line)
                
        result = '\n'.join(essential_lines)
        return result if result else content[:500]
        
    def _is_relevant_rule(self, rule_content: str, query: str) -> bool:
        """규칙 관련성 판단"""
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        rule_words = set(re.findall(r'\b\w+\b', rule_content.lower()))
        intersection = query_words.intersection(rule_words)
        return len(intersection) >= 3
        
    def _summarize_for_tokens(self, content: str, max_tokens: int) -> str:
        """토큰 제한에 맞춰 요약"""
        lines = content.split('\n')
        summary_lines = []
        tokens = 0
        
        # 헤더와 핵심 라인 우선
        priority_lines = [line for line in lines if line.startswith('#') or line.startswith('-') or line.startswith('*')]
        other_lines = [line for line in lines if line not in priority_lines]
        
        # 우선순위 라인부터 추가
        for line in priority_lines + other_lines:
            line_tokens = self.context_manager._estimate_tokens(line)
            if tokens + line_tokens <= max_tokens:
                summary_lines.append(line)
                tokens += line_tokens
            else:
                break
                
        if len(summary_lines) < len(lines):
            summary_lines.append(f"\n[Truncated: showing {len(summary_lines)}/{len(lines)} lines due to token limit]")
            
        return '\n'.join(summary_lines)
        
    def _build_enhanced_prompt(self, base_query: str, injected_context: str, command: str, project_id: str) -> str:
        """최종 강화된 프롬프트 구성"""
        
        context_prefix = ""
        if injected_context:
            context_prefix = f"""# PROJECT CONTEXT

{injected_context}

---

# CURRENT TASK

"""
        
        # 명령어별 특별 지시사항
        command_instructions = {
            "sdd_spec": "Create a comprehensive specification following the project constitution and SDD methodology.",
            "sdd_plan": "Develop an implementation plan based on the specification above, considering architectural patterns and constraints.",
            "sdd_tasks": "Break down the plan into actionable tasks with clear acceptance criteria and dependencies.",
            "sdd_implement": "Implement the specified functionality following the plan and tasks outlined above.",
            "architect": "Provide architectural guidance considering the project context and existing specifications.",
            "frontend": "Focus on frontend implementation following UI/UX best practices and project guidelines.",
            "backend": "Develop backend solutions ensuring reliability, security, and alignment with project architecture.",
            "analyzer": "Analyze the situation thoroughly using all available project context and provide evidence-based insights."
        }
        
        instruction = command_instructions.get(command, "Execute the request considering all available project context.")
        
        enhanced_prompt = f"""{context_prefix}**Instruction**: {instruction}

**Query**: {base_query}

**Project**: {project_id}
**Command**: {command}

Please ensure your response aligns with the project context above and follows the established patterns and constraints."""

        return enhanced_prompt

def main():
    """CLI 테스트 인터페이스"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python context_injector.py <command> <query> [project_id]")
        return
        
    injector = ContextInjector()
    command = sys.argv[1]
    query = sys.argv[2]
    project_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    enhanced_prompt, metadata = injector.inject_context_for_command(command, query, project_id)
    
    print("=== ENHANCED PROMPT ===")
    print(enhanced_prompt)
    print("\n=== METADATA ===")
    print(f"Session ID: {metadata['session_id']}")
    print(f"Project ID: {metadata['project_id']}")
    print(f"Context Tokens: {metadata['context_tokens']}")
    print(f"Total Tokens: {metadata['total_tokens']}")

if __name__ == "__main__":
    main()