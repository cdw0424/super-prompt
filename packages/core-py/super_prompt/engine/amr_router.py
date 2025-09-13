"""
AMR Router - Auto Model Router (medium ↔ high reasoning)
Automatically routes tasks based on complexity analysis.
"""

from enum import Enum
from typing import Dict, Any, Optional
import re


class ReasoningLevel(Enum):
    LIGHT = "light"      # L0 - Simple tasks
    MODERATE = "moderate"  # L1 - Standard tasks
    HEAVY = "heavy"      # H - Complex reasoning tasks


class AMRRouter:
    """
    Auto Model Router that analyzes task complexity and recommends reasoning levels.
    Provides switching templates and maintains routing history.
    """

    def __init__(self):
        self.routing_history = []
        self.complexity_patterns = self._build_patterns()

    def classify_task(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ReasoningLevel:
        """
        Classify task complexity based on input analysis.
        Returns the recommended reasoning level.
        """
        score = 0
        reasons = []

        # Analyze input characteristics
        input_length = len(user_input)
        has_keywords = self._check_keywords(user_input)
        has_complexity_indicators = self._check_complexity_indicators(user_input)
        has_architectural_elements = self._check_architectural_elements(user_input)

        # Scoring logic
        if input_length > 500:
            score += 2
            reasons.append("long_input")

        if has_keywords:
            score += 3
            reasons.append("complex_keywords")

        if has_complexity_indicators:
            score += 2
            reasons.append("complexity_indicators")

        if has_architectural_elements:
            score += 3
            reasons.append("architectural_elements")

        # Context-based adjustments
        if context:
            if context.get("has_failures", False):
                score += 2
                reasons.append("previous_failures")

            if context.get("token_limit_exceeded", False):
                score += 1
                reasons.append("token_pressure")

        # Determine reasoning level
        if score >= 7:
            level = ReasoningLevel.HEAVY
        elif score >= 4:
            level = ReasoningLevel.MODERATE
        else:
            level = ReasoningLevel.LIGHT

        # Record routing decision
        self.routing_history.append({
            "input": user_input[:100] + "..." if len(user_input) > 100 else user_input,
            "score": score,
            "level": level.value,
            "reasons": reasons
        })

        return level

    def get_switch_template(self, current_level: ReasoningLevel, target_level: ReasoningLevel) -> str:
        """Generate model switching template"""
        if current_level == target_level:
            return ""

        if target_level == ReasoningLevel.HEAVY:
            return """/model gpt-5 high
--------router: switch to high (reason=deep_planning)"""
        else:
            return """/model gpt-5 medium
--------router: back to medium (reason=execution)"""

    def should_switch_to_high(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Convenience method to check if high reasoning is needed"""
        return self.classify_task(user_input, context) == ReasoningLevel.HEAVY

    def _build_patterns(self) -> Dict[str, list]:
        """Build pattern dictionaries for complexity analysis"""
        return {
            "complex_keywords": [
                r"\b(architect|design|system|infrastructure|scalability)\b",
                r"\b(security|threat|vulnerability|compliance)\b",
                r"\b(performance|optimization|bottleneck|latency)\b",
                r"\b(migration|refactor|restructure|modernize)\b",
                r"\b(distributed|microservice|orchestration)\b"
            ],
            "complexity_indicators": [
                r"\b(multiple|several|various|complex)\b",
                r"\b(consider|analyze|evaluate|assess)\b",
                r"\b(trade.?off|constraint|limitation)\b",
                r"\b(stakeholder|requirement|specification)\b"
            ],
            "architectural_elements": [
                r"\b(database|schema|migration|model)\b",
                r"\b(api|endpoint|interface|contract)\b",
                r"\b(component|module|service|layer)\b",
                r"\b(integration|deployment|pipeline)\b"
            ]
        }

    def _check_keywords(self, text: str) -> bool:
        """Check for complex keywords"""
        for pattern in self.complexity_patterns["complex_keywords"]:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _check_complexity_indicators(self, text: str) -> bool:
        """Check for complexity indicators"""
        for pattern in self.complexity_patterns["complexity_indicators"]:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _check_architectural_elements(self, text: str) -> bool:
        """Check for architectural elements"""
        for pattern in self.complexity_patterns["architectural_elements"]:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        if not self.routing_history:
            return {"total_decisions": 0}

        total = len(self.routing_history)
        levels = {}
        for decision in self.routing_history:
            level = decision["level"]
            levels[level] = levels.get(level, 0) + 1

        return {
            "total_decisions": total,
            "level_distribution": levels,
            "high_reasoning_ratio": levels.get("heavy", 0) / total if total > 0 else 0
        }