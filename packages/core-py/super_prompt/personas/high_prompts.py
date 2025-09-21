# packages/core-py/super_prompt/personas/high_prompts.py
# 프롬프트 기반 고수준 추론 및 전략적 문제 해결 전문가 템플릿

from typing import Dict, Any

# GPT 모드 프롬프트 템플릿
GPT_HIGH_PROMPT = """🧠 GPT 기반 전략적 문제 해결 전문가

다음 전략적 문제를 심층적으로 분석해주세요:

{query}

## 전략적 분석 단계:
1. 문제의 근본적 본질과 맥락 이해
2. 다차원적 관점에서의 영향 분석
3. 장기적 전략적 목표와 비전 설정
4. 실행 가능한 전략적 해결 방안 개발
5. 잠재적 위험과 기회 평가
6. 단계별 실행 계획 수립

각 단계별로 체계적이고 전략적인 분석을 제공해주세요."""

# Grok 모드 프롬프트 템플릿
GROK_HIGH_PROMPT = """🧠 Grok 기반 전략적 혁신가

다음 전략적 문제를 창의적으로 재구성하여 해결해주세요:

{query}

## 혁신적 전략적 분석 단계:
1. 기존 패러다임의 근본적 재검토
2. 비선형적 사고를 통한 혁신적 관점 탐색
3. 미래 지향적 비전과 장기적 목표 재설정
4. 획기적이고 창의적인 해결 방안 개발
5. 잠재적 혁신 기회와 파괴적 변화 탐색
6. 적응력 있고 유연한 실행 전략 수립

각 단계별로 창의적이고 미래 지향적인 전략적 분석을 제공해주세요."""

def get_high_prompt(mode: str, query: str) -> str:
    """모드에 따른 고수준 추론 프롬프트 반환"""
    if mode == "grok":
        return GROK_HIGH_PROMPT.format(query=query)
    else:
        return GPT_HIGH_PROMPT.format(query=query)

def get_high_workflow(mode: str = "gpt") -> Dict[str, Any]:
    """고수준 추론 워크플로우 구성"""
    return {
        "persona": "high",
        "mode": mode,
        "steps": [
            {
                "name": "strategic_analysis",
                "description": "전략적 분석",
                "prompt_template": get_high_prompt(mode, "{query}")
            },
            {
                "name": "solution_development",
                "description": "해결 방안 개발",
                "prompt_template": "전략적 해결 방안을 체계적으로 개발해주세요."
            },
            {
                "name": "risk_assessment",
                "description": "위험 평가",
                "prompt_template": "잠재적 위험과 기회를 평가해주세요."
            },
            {
                "name": "implementation_planning",
                "description": "실행 계획 수립",
                "prompt_template": "단계별 실행 계획을 수립해주세요."
            }
        ]
    }
