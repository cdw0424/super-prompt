# packages/core-py/super_prompt/personas/architect_prompts.py
# 프롬프트 기반 아키텍처 분석 및 설계 전문가 템플릿

from typing import Dict, Any

# GPT 모드 프롬프트 템플릿
GPT_ARCHITECT_PROMPT = """🏗️ GPT 기반 시스템 설계 전문가

다음 시스템 설계 문제를 분석해주세요:

{query}

## 설계 고려사항:
1. 아키텍처 패턴 평가
2. 확장성 및 유지보수성 분석
3. 기술 스택 최적화 제안
4. 구현 우선순위 설정

전문적인 설계 조언을 제공해주세요."""

# Grok 모드 프롬프트 템플릿
GROK_ARCHITECT_PROMPT = """🏗️ Grok 기반 시스템 설계 전문가

다음 시스템 설계 문제를 창의적으로 분석해주세요:

{query}

## 혁신적 설계 고려사항:
1. 독창적인 아키텍처 패턴 탐색
2. 미래 지향적 확장성 설계
3. 최신 기술 트렌드 활용
4. 혁신적인 해결 방안 제시

창의적이고 미래 지향적인 설계 조언을 제공해주세요."""

def get_architect_prompt(mode: str, query: str) -> str:
    """모드에 따른 아키텍처 프롬프트 반환"""
    if mode == "grok":
        return GROK_ARCHITECT_PROMPT.format(query=query)
    else:
        return GPT_ARCHITECT_PROMPT.format(query=query)

def get_architect_workflow(mode: str = "gpt") -> Dict[str, Any]:
    """아키텍처 워크플로우 구성"""
    return {
        "persona": "architect",
        "mode": mode,
        "steps": [
            {
                "name": "architecture_analysis",
                "description": "시스템 아키텍처 분석",
                "prompt_template": get_architect_prompt(mode, "{query}")
            },
            {
                "name": "design_recommendations",
                "description": "설계 권장사항",
                "prompt_template": "설계 개선사항을 구체적으로 제안해주세요."
            }
        ]
    }
