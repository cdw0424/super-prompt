# packages/core-py/super_prompt/personas/analyzer_prompts.py
# 프롬프트 기반 근본 원인 분석 전문가 템플릿

from typing import Dict, Any

# GPT 모드 프롬프트 템플릿
GPT_ANALYZER_PROMPT = """🔍 GPT 기반 체계적 분석가

다음 문제를 분석해주세요:

{query}

## 분석 단계:
1. 문제 이해 및 범위 파악
2. 잠재적 원인 식별
3. 해결 방안 제안
4. 예방 조치 권고

각 단계별로 상세한 분석을 제공해주세요."""

# Grok 모드 프롬프트 템플릿
GROK_ANALYZER_PROMPT = """🔍 Grok 기반 창의적 분석가

다음 문제를 혁신적으로 분석해주세요:

{query}

## 혁신적 분석 단계:
1. 문제의 근본적 본질 파악
2. 창의적 원인 가설 수립
3. 비전통적 해결 방안 탐색
4. 장기적 예방 전략 설계

각 단계별로 창의적이고 심층적인 분석을 제공해주세요."""

def get_analyzer_prompt(mode: str, query: str) -> str:
    """모드에 따른 분석가 프롬프트 반환"""
    if mode == "grok":
        return GROK_ANALYZER_PROMPT.format(query=query)
    else:
        return GPT_ANALYZER_PROMPT.format(query=query)

def get_analyzer_workflow(mode: str = "gpt") -> Dict[str, Any]:
    """분석가 워크플로우 구성"""
    return {
        "persona": "analyzer",
        "mode": mode,
        "steps": [
            {
                "name": "problem_analysis",
                "description": "문제 분석",
                "prompt_template": get_analyzer_prompt(mode, "{query}")
            },
            {
                "name": "root_cause_identification",
                "description": "근본 원인 식별",
                "prompt_template": "근본 원인을 체계적으로 식별해주세요."
            },
            {
                "name": "solution_proposal",
                "description": "해결 방안 제안",
                "prompt_template": "구체적인 해결 방안을 제안해주세요."
            }
        ]
    }
