"""
Tokenizer - Token counting and estimation utilities
"""

import re
from typing import List, Dict, Any


class Tokenizer:
    """
    Token counting and estimation utilities.
    Provides rough token estimation for LLM context budgeting.
    """

    # Rough estimation: 1 token ≈ 4 characters for English text
    CHARS_PER_TOKEN = 4

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count for a text string"""
        if not text:
            return 0

        # Basic estimation: characters / 4
        char_count = len(text)
        estimated_tokens = char_count // Tokenizer.CHARS_PER_TOKEN

        # Adjust for code (more tokens per character)
        if Tokenizer._is_code(text):
            estimated_tokens = int(estimated_tokens * 1.2)

        # Adjust for non-English text
        if Tokenizer._has_non_english(text):
            estimated_tokens = int(estimated_tokens * 1.5)

        return max(1, estimated_tokens)

    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        return len(re.findall(r'\b\w+\b', text))

    @staticmethod
    def split_into_chunks(text: str, max_tokens: int) -> List[str]:
        """Split text into chunks that fit within token limit"""
        if Tokenizer.estimate_tokens(text) <= max_tokens:
            return [text]

        chunks = []
        lines = text.split('\n')
        current_chunk = []
        current_tokens = 0

        for line in lines:
            line_tokens = Tokenizer.estimate_tokens(line)

            if current_tokens + line_tokens > max_tokens and current_chunk:
                # Save current chunk and start new one
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_tokens = line_tokens
            else:
                current_chunk.append(line)
                current_tokens += line_tokens

        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks

    @staticmethod
    def prioritize_chunks(chunks: List[str], max_tokens: int, priorities: List[int] = None) -> List[str]:
        """Select and prioritize chunks within token budget"""
        if not priorities:
            priorities = list(range(len(chunks)))

        # Sort by priority (lower number = higher priority)
        chunk_priority_pairs = list(zip(chunks, priorities))
        chunk_priority_pairs.sort(key=lambda x: x[1])

        selected_chunks = []
        total_tokens = 0

        for chunk, priority in chunk_priority_pairs:
            chunk_tokens = Tokenizer.estimate_tokens(chunk)
            if total_tokens + chunk_tokens <= max_tokens:
                selected_chunks.append(chunk)
                total_tokens += chunk_tokens
            else:
                break

        return selected_chunks

    @staticmethod
    def _is_code(text: str) -> bool:
        """Detect if text appears to be code"""
        code_indicators = [
            'def ', 'class ', 'import ', 'function', 'const ', 'let ', 'var ',
            'if ', 'for ', 'while ', '<html', '<?php', '#include',
            'public ', 'private ', 'protected '
        ]

        text_lower = text.lower()
        code_matches = sum(1 for indicator in code_indicators if indicator in text_lower)

        return code_matches > 2 or '{' in text or '}' in text

    @staticmethod
    def _has_non_english(text: str) -> bool:
        """Check if text contains non-English characters"""
        # Simple check for non-ASCII characters
        return any(ord(char) > 127 for char in text)
