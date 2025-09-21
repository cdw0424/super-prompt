# packages/core-py/super_prompt/personas/frontend_prompts.py
# 프롬프트 기반 프론트엔드 개발 전문가 템플릿

from typing import Dict, Any

# GPT 모드 프롬프트 템플릿
GPT_FRONTEND_PROMPT = """🎨 GPT 기반 프론트엔드 전문가

다음 프론트엔드 문제를 분석해주세요:

{query}

## 프론트엔드 고려사항:
1. UI/UX 디자인 최적화
2. 반응형 디자인 및 접근성
3. 프레임워크 선택 (React, Vue, Angular)
4. 성능 및 사용자 경험 개선

현대적인 프론트엔드 개발 조언을 제공해주세요."""

# Grok 모드 프롬프트 템플릿
GROK_FRONTEND_PROMPT = """🎨 Grok 기반 프론트엔드 혁신가

다음 프론트엔드 문제를 창의적으로 해결해주세요:

{query}

## 혁신적 프론트엔드 고려사항:
1. 차세대 UI/UX 패턴 탐색
2. 혁신적인 상호작용 디자인
3. 최신 프론트엔드 기술 활용
4. 사용자 경험 혁신

창의적이고 미래 지향적인 프론트엔드 개발 조언을 제공해주세요."""

def get_frontend_prompt(mode: str, query: str) -> str:
    """모드에 따른 프론트엔드 프롬프트 반환"""
    if mode == "grok":
        return GROK_FRONTEND_PROMPT.format(query=query)
    else:
        return GPT_FRONTEND_PROMPT.format(query=query)

def get_frontend_workflow(mode: str = "gpt") -> Dict[str, Any]:
    """프론트엔드 워크플로우 구성"""
    return {
        "persona": "frontend",
        "mode": mode,
        "steps": [
            {
                "name": "ui_ux_design",
                "description": "UI/UX 디자인",
                "prompt_template": get_frontend_prompt(mode, "{query}")
            },
            {
                "name": "accessibility",
                "description": "접근성 구현",
                "prompt_template": "접근성 요구사항 및 구현 방안을 분석해주세요."
            },
            {
                "name": "performance_optimization",
                "description": "성능 최적화",
                "prompt_template": "프론트엔드 성능 최적화 방안을 제시해주세요."
            }
        ]
    }
