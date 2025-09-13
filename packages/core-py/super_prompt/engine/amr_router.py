"""
Auto Model Router (AMR) Implementation

Handles complexity classification and model routing decisions:
- L0/L1: Medium complexity tasks
- H: High complexity requiring advanced reasoning
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Pattern
import re
import logging

logger = logging.getLogger(__name__)


class ComplexityLevel(Enum):
    """Complexity levels for AMR routing"""
    L0 = "l0"      # Low complexity
    L1 = "l1"      # Medium complexity
    H = "h"        # High complexity


@dataclass
class RouteDecision:
    """Result of AMR routing decision"""
    complexity: ComplexityLevel
    confidence: float
    reasoning: str
    suggested_flags: List[str]


class AMRRouter:
    """
    Auto Model Router for complexity-based routing

    Analyzes user input and determines appropriate complexity level
    and routing recommendations.
    """

    def __init__(self):
        self.high_complexity_patterns = [
            # Architecture and system design
            r'\b(architect|architecture|system\s+design|scalability)\b',
            r'\b(refactor|refactoring|redesign|modernize)\b',
            r'\b(optimize|optimization|performance|bottleneck)\b',

            # Security and compliance
            r'\b(security|audit|vulnerability|threat|compliance)\b',
            r'\b(encrypt|authentication|authorization)\b',

            # Complex analysis
            r'\b(analyze|analysis|investigate|troubleshoot)\b',
            r'\b(debug|debugging|root\s+cause)\b',

            # Meta-cognitive requests
            r'\b(think|thinking|reason|reasoning|complex)\b',
            r'\b(comprehensive|thorough|detailed|deep)\b',

            # Multi-step operations
            r'\b(plan|planning|strategy|roadmap)\b',
            r'\b(workflow|pipeline|process|methodology)\b',
        ]

        self.medium_complexity_patterns = [
            # Implementation tasks
            r'\b(implement|create|build|develop)\b',
            r'\b(feature|component|module|service)\b',
            r'\b(api|endpoint|database|query)\b',

            # Frontend/UI tasks
            r'\b(ui|ux|component|responsive|design)\b',
            r'\b(css|styling|layout|animation)\b',

            # Documentation and explanation
            r'\b(document|documentation|explain|guide)\b',
            r'\b(example|tutorial|how\s+to)\b',
        ]

        self.low_complexity_patterns = [
            # Simple queries
            r'\b(what|how|why|when|where)\b',
            r'\b(show|list|display|print)\b',
            r'\b(help|usage|syntax)\b',

            # Basic operations
            r'\b(copy|move|rename|delete)\b',
            r'\b(install|setup|configure)\b',
        ]

    def analyze_complexity(self, user_input: str, context: Optional[Dict] = None) -> RouteDecision:
        """
        Analyze user input and determine complexity level

        Args:
            user_input: User's request or command
            context: Additional context (file count, project size, etc.)

        Returns:
            RouteDecision with complexity level and reasoning
        """
        user_input_lower = user_input.lower()

        # Count pattern matches
        high_matches = self._count_pattern_matches(user_input_lower, self.high_complexity_patterns)
        medium_matches = self._count_pattern_matches(user_input_lower, self.medium_complexity_patterns)
        low_matches = self._count_pattern_matches(user_input_lower, self.low_complexity_patterns)

        # Context-based adjustments
        context_score = self._analyze_context(context or {})

        # Calculate scores
        high_score = high_matches * 2 + context_score
        medium_score = medium_matches * 1.5
        low_score = low_matches

        # Determine complexity
        if high_score >= 2 or (high_score >= 1 and context_score >= 1):
            return RouteDecision(
                complexity=ComplexityLevel.H,
                confidence=min(0.9, 0.6 + high_score * 0.1),
                reasoning=f"High complexity detected: {high_matches} high patterns, context score {context_score}",
                suggested_flags=["--ultrathink", "--seq", "--validate"]
            )
        elif medium_score >= 1 or (low_score == 0 and high_score == 0):
            return RouteDecision(
                complexity=ComplexityLevel.L1,
                confidence=min(0.8, 0.5 + medium_score * 0.1),
                reasoning=f"Medium complexity: {medium_matches} medium patterns",
                suggested_flags=["--think", "--c7"]
            )
        else:
            return RouteDecision(
                complexity=ComplexityLevel.L0,
                confidence=min(0.7, 0.4 + low_score * 0.1),
                reasoning=f"Low complexity: {low_matches} simple patterns",
                suggested_flags=[]
            )

    def _count_pattern_matches(self, text: str, patterns: List[str]) -> int:
        """Count how many patterns match in the text"""
        matches = 0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
        return matches

    def _analyze_context(self, context: Dict) -> float:
        """Analyze context for complexity indicators"""
        score = 0.0

        # File count indicator
        file_count = context.get('file_count', 0)
        if file_count > 100:
            score += 1.0
        elif file_count > 20:
            score += 0.5

        # Project size indicator
        project_size = context.get('project_size', 'small')
        if project_size == 'large':
            score += 1.0
        elif project_size == 'medium':
            score += 0.5

        # Error/failure history
        if context.get('recent_failures', 0) > 2:
            score += 0.5

        # Multi-domain operations
        domains = context.get('domains', [])
        if len(domains) > 2:
            score += 0.5

        return score

    def should_route_high(self, user_input: str, context: Optional[Dict] = None) -> bool:
        """Quick check if input should route to high complexity"""
        decision = self.analyze_complexity(user_input, context)
        return decision.complexity == ComplexityLevel.H and decision.confidence > 0.6

    def get_routing_suggestion(self, user_input: str, context: Optional[Dict] = None) -> str:
        """Get human-readable routing suggestion"""
        decision = self.analyze_complexity(user_input, context)

        if decision.complexity == ComplexityLevel.H:
            return f"🧠 High complexity detected (confidence: {decision.confidence:.1%}). Consider using advanced reasoning flags: {', '.join(decision.suggested_flags)}"
        elif decision.complexity == ComplexityLevel.L1:
            return f"⚙️ Medium complexity (confidence: {decision.confidence:.1%}). Standard processing recommended."
        else:
            return f"💡 Low complexity (confidence: {decision.confidence:.1%}). Quick response mode."