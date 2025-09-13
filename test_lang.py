#!/usr/bin/env python3
"""
Simple test script for language detection
"""

import unicodedata

def detect_language(text: str) -> str:
    """Detect the primary language of the input text (English/Korean)"""
    if not text.strip():
        return "en"

    # Count Korean characters (Hangul syllables)
    korean_chars = 0
    english_chars = 0

    for char in text:
        if unicodedata.category(char).startswith('Lo'):  # Letters, other
            # Check if it's Hangul (Korean)
            name = unicodedata.name(char, '')
            if 'HANGUL' in name:
                korean_chars += 1
            elif char.isascii() and char.isalpha():
                english_chars += 1

    # Simple heuristic: if more Korean characters than English, assume Korean
    # Also check for common Korean particles and endings
    korean_indicators = ['이', '가', '을', '를', '은', '는', '에', '에서', '으로', '로',
                       '하다', '요', '다', '고', '며', '면서', '지만', '과', '와']

    has_korean_indicators = any(indicator in text for indicator in korean_indicators)

    if korean_chars > english_chars or has_korean_indicators:
        return "ko"
    else:
        return "en"

if __name__ == "__main__":
    test_cases = [
        "Please implement a new feature",
        "새로운 기능을 구현해주세요",
        "Please implement 새로운 기능",
        "프로젝트 검수해줘",
        "Add user authentication",
        "사용자 인증을 추가해 주세요",
        "",
        "Hello world",
        "안녕하세요 세계"
    ]

    for test in test_cases:
        result = detect_language(test)
        print(f"'{test}' -> {result}")
