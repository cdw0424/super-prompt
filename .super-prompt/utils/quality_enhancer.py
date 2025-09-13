#!/usr/bin/env python3
"""
Quality Enhancer - Final Polish Utility for All Commands
고해성사와 더블체크를 통한 최적의 결과물 완성
"""

import os
import sys
from typing import Dict, Any, Optional


class QualityEnhancer:
    """
    모든 커맨드에서 공통적으로 사용하는 퀄리티 향상 유틸리티
    - 고해성사: 작업 과정에서 실수나 개선할 점 자체 검토
    - 더블체크: 최종 결과물 검증
    - 오버엔지니어링 방지: 불필요한 복잡성 제거
    - Context7 MCP 기본 사용: 모든 작업에서 Context7 MCP 도구 우선 활용
    - SDD 원칙 준수: Spec-Driven Development 도구와 원칙 기본 적용
    """

    def __init__(self):
        self.confession_prompt = self._get_confession_prompt()
        self.double_check_prompt = self._get_double_check_prompt()
        self.anti_overengineering_prompt = self._get_anti_overengineering_prompt()
        self.context7_guidance = self._get_context7_guidance()
        self.sdd_guidance = self._get_sdd_guidance()

    def enhance_quality(self, result: str, context: Dict[str, Any] = None) -> str:
        """
        결과물에 퀄리티 향상을 적용
        """
        if not result or not result.strip():
            return result

        context = context or {}

        # 0. Context7 MCP 및 SDD 지침 적용
        context7_sdd_applied = self._apply_context7_sdd_guidance(result, context)

        # 1. 고해성사 적용
        confession_result = self._apply_confession(context7_sdd_applied, context)

        # 2. 더블체크 적용
        double_checked = self._apply_double_check(confession_result, context)

        # 3. 오버엔지니어링 방지 적용
        final_result = self._apply_anti_overengineering(double_checked, context)

        return final_result

    def _apply_context7_sdd_guidance(self, result: str, context: Dict[str, Any]) -> str:
        """
        Context7 MCP 및 SDD 지침 적용
        모든 페르소나가 공통적으로 따라야 하는 기본 지침
        """
        context7_sdd_instruction = f"""
**[기본 지침 - Context7 MCP 및 SDD 준수]**

{self.context7_guidance}

{self.sdd_guidance}

**적용할 결과물:**
{result}

**지침이 적용된 결과물:**
"""
        # 실제 구현에서는 LLM에게 이 프롬프트를 전달하여 지침이 적용된 결과를 얻음
        return result + "\n\n" + context7_sdd_instruction

    def _apply_confession(self, result: str, context: Dict[str, Any]) -> str:
        """
        고해성사: 작업 과정에서 실수나 개선할 점을 스스로 점검
        """
        confession_instruction = f"""
**[고해성사 - 작업 과정 검토]**

다음 작업 결과물을 검토하면서 스스로에게 물어보세요:

{self.confession_prompt}

**원본 결과물:**
{result}

**고해성사 후 개선된 결과물:**
"""

        # 실제 구현에서는 LLM에게 이 프롬프트를 전달하여 개선된 결과를 얻음
        # 여기서는 프롬프트 템플릿만 제공
        return result + "\n\n" + confession_instruction

    def _apply_double_check(self, result: str, context: Dict[str, Any]) -> str:
        """
        더블체크: 최종 결과물의 완성도를 검증
        """
        double_check_instruction = f"""
**[더블체크 - 최종 검증]**

{self.double_check_prompt}

**검증할 결과물:**
{result}

**더블체크 완료:**
"""

        return result + "\n\n" + double_check_instruction

    def _apply_anti_overengineering(self, result: str, context: Dict[str, Any]) -> str:
        """
        오버엔지니어링 방지: 불필요한 복잡성 제거 지시
        """
        anti_overengineering_instruction = f"""
**[오버엔지니어링 방지]**

{self.anti_overengineering_prompt}

**정제할 결과물:**
{result}

**최적화된 최종 결과물:**
"""

        return result + "\n\n" + anti_overengineering_instruction

    def _get_confession_prompt(self) -> str:
        """고해성사 프롬프트"""
        return """
❓ **나는 이 작업에서 어떤 실수를 했는가?**
   - 불필요한 코드/텍스트를 추가했는가?
   - 중요한 부분을 누락했는가?
   - 가독성을 해치는 방식으로 작성했는가?

❓ **이 결과물이 정말 필요한가?**
   - 사용자 요구사항을 정확히 만족시키는가?
   - 불필요한 기능이나 설명을 추가했는가?
   - 핵심만 남기고 불필요한 부분을 제거할 수 있는가?

❓ **더 간단하게 만들 수는 없는가?**
   - 복잡한 개념을 간단하게 설명할 수 있는가?
   - 불필요한 추상화를 제거할 수 있는가?
   - 더 직관적인 방식으로 재구성할 수 있는가?

❓ **미래의 내가 이 코드를 보면 이해하기 쉬운가?**
   - 변수명과 함수명이 명확한가?
   - 주석이 충분하고 도움이 되는가?
   - 코드 구조가 논리적인가?

❓ **이 작업으로 얻는 이익이 노력보다 큰가?**
   - 구현 복잡성과 유지보수 비용을 고려했는가?
   - 정말 필요한 기능인가, 아니면 과도한 욕심인가?
   - 더 간단한 대안을 고려했는가?
"""

    def _get_double_check_prompt(self) -> str:
        """더블체크 프롬프트"""
        return """
🔍 **기능적 완성도 검증:**
□ 요구사항을 100% 만족시키는가?
□ 에러 케이스를 적절히 처리하는가?
□ 사용자 경험이 직관적인가?

🔍 **코드/텍스트 품질 검증:**
□ 가독성이 좋은가?
□ 유지보수가 쉬운 구조인가?
□ 성능상의 문제가 없는가?

🔍 **일관성 검증:**
□ 기존 패턴과 일관된 방식인가?
□ 문서화가 충분한가?
□ 테스트가 가능한가?

🔍 **보안/신뢰성 검증:**
□ 보안 취약점이 없는가?
□ 데이터 유효성 검사가 되는가?
□ 오류 복구 메커니즘이 있는가?

🔍 **최종 검증:**
□ 이 결과물로 실제 프로덕션에서 사용할 수 있는가?
□ 사용자에게 자신 있게 추천할 수 있는가?
□ 미래에 이 결정을 후회하지 않을 것인가?
"""

    def _get_anti_overengineering_prompt(self) -> str:
        """오버엔지니어링 방지 프롬프트"""
        return """
🚫 **오버엔지니어링 방지 규칙:**

⚠️ **하지 말아야 할 것들:**
- 미래에 사용할지도 모른다는 이유로 불필요한 기능을 추가하지 말라
- "유연성"을 핑계로 복잡한 추상화를 만들지 말라
- "확장성"을 위해 현재 필요 없는 인터페이스를 만들지 말라
- "최적화"를 핑계로 읽기 어려운 코드를 작성하지 말라
- "완벽함"을 추구하다가 배포 시점을 놓치지 말라

✅ **해야 할 것들:**
- 현재 문제를 해결하는 가장 간단한 방법을 선택하라
- YAGNI(You Aren't Gonna Need It) 원칙을 따르라
- KISS(Keep It Simple, Stupid) 원칙을 따르라
- 나중에 변경하기 쉬운 코드를 작성하라
- 실제 사용량과 피드백을 보고 개선하라

🎯 **최적화 원칙:**
- 현재 필요한 것만 구현하라
- 복잡성은 실제 필요성이 증명될 때 추가하라
- 간단한 해결책이 80%의 문제를 해결한다
- 나머지 20%는 실제로 발생할 때 해결하라

💡 **기억하라:** 완벽한 코드는 존재하지 않는다.
좋은 코드는 오늘의 문제를 해결하고, 내일의 변경을 용이하게 하는 코드다.
"""

    def _get_context7_guidance(self) -> str:
        """Context7 MCP 기본 사용 지침"""
        return """
🔧 **Context7 MCP 기본 사용 지침:**

⚡ **항상 우선 사용:**
- 모든 작업에서 Context7 MCP 도구를 기본적으로 활용하라
- 라이브러리 검색, 문서 조회, API 탐색 시 Context7 MCP 우선 사용
- 코드 분석, 패턴 탐색, 기술 조사 시 Context7 MCP 활용

📚 **주요 Context7 MCP 도구:**
- `mcp_context7_resolve-library-id`: 라이브러리/패키지 이름으로 ID 확인
- `mcp_context7_get-library-docs`: 라이브러리 문서 및 예제 조회
- `mcp_context7_*`: 기타 Context7 관련 도구들

🎯 **사용 원칙:**
- 새로운 기술이나 라이브러리 도입 시 Context7으로 검증
- 코드 작성 전 관련 Context7 문서 참조
- 모호한 기술적 결정 시 Context7으로 사실 확인
- 최신 정보와 모범 사례 확보를 위해 Context7 우선 활용

⚠️ **주의사항:**
- Context7 정보가 불충분할 경우에만 다른 정보원을 사용
- Context7 결과를 현재 프로젝트 맥락에 맞게 적절히 적용
- Context7에서 제공하는 코드 예제를 프로젝트 표준에 맞게 조정
"""

    def _get_sdd_guidance(self) -> str:
        """SDD (Spec-Driven Development) 도구 및 원칙 준수 지침"""
        return """
📋 **SDD (Spec-Driven Development) 기본 준수 지침:**

🎯 **항상 SDD 원칙 우선:**
- 모든 개발 작업에서 SDD 도구와 워크플로우를 기본적으로 따르라
- 계획 수립 → 구현 → 검증의 구조화된 프로세스 준수
- 요구사항 명확화 → 계획 수립 → 작업 분해 → 구현 → 검증의 단계적 접근

🛠️ **주요 SDD 도구 사용:**
- `/specify`: 기능 명세 작성 및 검증
- `/plan`: 구현 계획 수립 및 아키텍처 검토
- `/tasks`: 세부 작업 분해 및 추적
- SDD 게이트: 품질 게이트 통과 확인
- SDD 템플릿: 표준화된 문서 양식 사용

📝 **SDD 워크플로우 준수:**
1. **Specify 단계**: 요구사항을 명확히 정의하고 승인
2. **Plan 단계**: 기술적 접근방식과 아키텍처 설계
3. **Tasks 단계**: 구현 가능한 세부 작업으로 분해
4. **Implement 단계**: SDD 게이트 통과 후 구현 시작
5. **Verify 단계**: Acceptance Self-Check로 품질 검증

✅ **SDD 품질 게이트:**
- 요구사항 명확성 검증
- 기술적 타당성 검토
- 리스크 평가 및 완화 전략
- 테스트 전략 수립
- 코드 품질 기준 준수

⚠️ **SDD 위반 시 조치:**
- SDD 프로세스 우회가 필요한 경우 명확한 근거 제시
- SDD 원칙과 다른 접근 시 리더 승인 획득
- 예외 상황 발생 시 SDD 원칙 복원 계획 수립

🔄 **지속적 개선:**
- 각 SDD 단계 완료 후 피드백 수집
- SDD 프로세스 효율성 정기 검토
- 새로운 패턴과 모범 사례 SDD 템플릿에 반영
"""


def enhance_result_quality(result: str, context: Dict[str, Any] = None) -> str:
    """
    편의 함수: QualityEnhancer를 사용하여 결과물 품질 향상
    """
    enhancer = QualityEnhancer()
    return enhancer.enhance_quality(result, context)


def main():
    """CLI 인터페이스"""
    import argparse

    parser = argparse.ArgumentParser(description="Quality Enhancer - Final Polish Utility")
    parser.add_argument("--result", "-r", help="Result to enhance")
    parser.add_argument("--confession-only", action="store_true", help="Apply only confession")
    parser.add_argument("--double-check-only", action="store_true", help="Apply only double-check")
    parser.add_argument("--anti-overengineering-only", action="store_true", help="Apply only anti-overengineering")

    args = parser.parse_args()

    if not args.result:
        print("Usage: python quality_enhancer.py --result 'your result here'")
        return

    enhancer = QualityEnhancer()

    if args.confession_only:
        result = enhancer._apply_confession(args.result, {})
    elif args.double_check_only:
        result = enhancer._apply_double_check(args.result, {})
    elif args.anti_overengineering_only:
        result = enhancer._apply_anti_overengineering(args.result, {})
    else:
        result = enhancer.enhance_quality(args.result, {})

    print(result)


if __name__ == "__main__":
    main()
