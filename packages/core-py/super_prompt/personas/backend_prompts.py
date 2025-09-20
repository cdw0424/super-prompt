# packages/core-py/super_prompt/personas/backend_prompts.py
# 프롬프트 기반 백엔드 개발 전문가 템플릿

from typing import Dict, Any

# GPT 모드 프롬프트 템플릿
GPT_BACKEND_PROMPT = """⚡ GPT 기반 백엔드 전문가

다음 백엔드 문제를 분석해주세요:

{query}

## 백엔드 고려사항:
1. API 설계 및 아키텍처
2. 데이터베이스 최적화
3. 보안 및 성능 고려
4. 확장성 및 유지보수성

전문적인 백엔드 개발 조언을 제공해주세요."""

# Grok 모드 프롬프트 템플릿
GROK_BACKEND_PROMPT = """⚡ Grok 기반 백엔드 혁신가

다음 백엔드 문제를 창의적으로 해결해주세요:

{query}

## 혁신적 백엔드 고려사항:
1. 미래 지향적 API 설계
2. 고성능 데이터베이스 전략
3. 최신 보안 기술 적용
4. 마이크로서비스 혁신

창의적이고 미래 지향적인 백엔드 개발 조언을 제공해주세요."""

def get_backend_prompt(mode: str, query: str) -> str:
    """모드에 따른 백엔드 프롬프트 반환"""
    if mode == "grok":
        return GROK_BACKEND_PROMPT.format(query=query)
    else:
        return GPT_BACKEND_PROMPT.format(query=query)

def get_backend_workflow(mode: str = "gpt") -> Dict[str, Any]:
    """백엔드 워크플로우 구성"""
    return {
        "persona": "backend",
        "mode": mode,
        "steps": [
            {
                "name": "api_design",
                "description": "API 설계",
                "prompt_template": get_backend_prompt(mode, "{query}")
            },
            {
                "name": "database_optimization",
                "description": "데이터베이스 최적화",
                "prompt_template": "데이터베이스 설계 및 최적화 방안을 제시해주세요."
            },
            {
                "name": "security_implementation",
                "description": "보안 구현",
                "prompt_template": "보안 요구사항 및 구현 방안을 분석해주세요."
            }
        ]
    }
