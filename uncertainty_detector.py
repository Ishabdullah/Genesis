#!/usr/bin/env python3
"""
Genesis Uncertainty Detection Module
Analyzes local LLM responses to determine confidence level
and whether Claude fallback is needed
"""

import re
from typing import Tuple, Dict, Any

class UncertaintyDetector:
    """Detects when local LLM responses show uncertainty or low confidence"""

    def __init__(self):
        """Initialize uncertainty detector with patterns and thresholds"""

        # Uncertain keywords and phrases
        self.uncertain_patterns = [
            r"\bi['\"]?m not sure\b",
            r"\bi don['\"]?t know\b",
            r'\bpossibly\b',
            r'\bmaybe\b',
            r'\bperhaps\b',
            r'\bmight be\b',
            r'\bcould be\b',
            r'\bi think\b',
            r'\bi believe\b',
            r'\bunsure\b',
            r'\buncertain\b',
            r"\bcan['\"]?t help\b",
            r"\bdon['\"]?t have enough information\b",
            r'\bnot confident\b',
            r'\bneed more context\b',
            r'\bclarify\b',
            r'\bnot clear\b',
            r'\bapologies.*cannot\b',
            r'\bsorry.*unable\b',
            r'\bi apologize.*cannot\b',
            r'\bthis is beyond my\b',
            r'\btoo complex for me\b',
            r'\bstruggling to\b',
            r'\bdifficult to\b',
            r'\bneed help with\b',
            r'\bcannot complete\b',
            r'\bunable to handle\b',
        ]

        # Error patterns that indicate Genesis needs Claude
        self.error_patterns = [
            r'⚠',  # Any warning/error symbol
            r'Error:',
            r'Failed:',
            r'timeout',
            r'not found',
            r'cannot access',
            r'permission denied',
        ]

        # Compile patterns for efficiency
        self.error_regex = re.compile(
            '|'.join(self.error_patterns),
            re.IGNORECASE
        )

        # Compile patterns for efficiency
        self.uncertain_regex = re.compile(
            '|'.join(self.uncertain_patterns),
            re.IGNORECASE
        )

        # Response quality thresholds
        self.min_response_length = 20  # Very short responses may indicate uncertainty
        self.max_repetition_ratio = 0.5  # High repetition suggests confusion

    def analyze_response(self, response: str) -> Dict[str, Any]:
        """
        Analyze a response for uncertainty indicators

        Args:
            response: The LLM response text to analyze

        Returns:
            Dictionary with uncertainty analysis results
        """
        if not response or not response.strip():
            return {
                'uncertain': True,
                'confidence_score': 0.0,
                'reason': 'empty_response',
                'details': 'Response is empty or whitespace only'
            }

        response_clean = response.strip()

        # Check 1: Uncertain language patterns
        uncertain_matches = self.uncertain_regex.findall(response_clean.lower())
        has_uncertain_language = len(uncertain_matches) > 0

        # Check 2: Response length
        is_too_short = len(response_clean) < self.min_response_length

        # Check 3: Repetition detection
        repetition_ratio = self._calculate_repetition_ratio(response_clean)
        has_excessive_repetition = repetition_ratio > self.max_repetition_ratio

        # Check 4: Error indicators
        has_error_indicators = self._check_error_indicators(response_clean)

        # Check 5: Code generation quality (if response contains code)
        code_quality_issues = self._check_code_quality(response_clean)

        # Calculate overall confidence score (0.0 = uncertain, 1.0 = confident)
        confidence_score = self._calculate_confidence_score(
            has_uncertain_language=has_uncertain_language,
            is_too_short=is_too_short,
            has_excessive_repetition=has_excessive_repetition,
            has_error_indicators=has_error_indicators,
            code_quality_issues=code_quality_issues,
            uncertain_match_count=len(uncertain_matches)
        )

        # Determine if uncertain (threshold: 0.6)
        uncertain = confidence_score < 0.6

        # Build reason and details
        reasons = []
        if has_uncertain_language:
            reasons.append(f'uncertain_language ({len(uncertain_matches)} matches)')
        if is_too_short:
            reasons.append(f'too_short ({len(response_clean)} chars)')
        if has_excessive_repetition:
            reasons.append(f'repetition ({repetition_ratio:.2f})')
        if has_error_indicators:
            reasons.append('error_indicators')
        if code_quality_issues:
            reasons.append('code_quality_issues')

        return {
            'uncertain': uncertain,
            'confidence_score': confidence_score,
            'reason': ', '.join(reasons) if reasons else 'confident',
            'details': {
                'uncertain_language': has_uncertain_language,
                'uncertain_matches': uncertain_matches,
                'too_short': is_too_short,
                'response_length': len(response_clean),
                'repetition_ratio': repetition_ratio,
                'error_indicators': has_error_indicators,
                'code_quality_issues': code_quality_issues
            }
        }

    def _calculate_repetition_ratio(self, text: str) -> float:
        """
        Calculate how repetitive the text is

        Args:
            text: Text to analyze

        Returns:
            Ratio of repeated words to total words (0.0 to 1.0)
        """
        words = text.lower().split()
        if len(words) < 5:
            return 0.0

        # Count unique words vs total words
        unique_words = set(words)
        repetition_ratio = 1.0 - (len(unique_words) / len(words))

        return repetition_ratio

    def _check_error_indicators(self, text: str) -> bool:
        """
        Check for error or failure indicators

        Args:
            text: Text to check

        Returns:
            True if error indicators found
        """
        error_patterns = [
            r'\berror\b',
            r'\bfailed\b',
            r'\bfailure\b',
            r'\bexception\b',
            r'\btraceback\b',
            r'\bstack trace\b',
            r'\bsyntax error\b',
            r'\bcannot\s+\w+\s+this\b',
        ]

        for pattern in error_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _check_error_indicators(self, text: str) -> bool:
        """
        Check if response contains error indicators showing Genesis struggled

        Args:
            text: Text to check

        Returns:
            True if error indicators found
        """
        # Check for compiled error patterns
        if self.error_regex.search(text):
            return True

        # Check for specific error patterns
        error_indicators = [
            r'LLM timeout',
            r'LLM error',
            r'execution failed',
            r'⚠',  # Warning symbol
            r'✗',  # X mark
            r'SyntaxError',
            r'NameError',
            r'TypeError',
            r'ValueError',
            r'Exception',
            r'Traceback',
        ]

        for pattern in error_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _check_code_quality(self, text: str) -> bool:
        """
        Check for code quality issues in responses containing code

        Args:
            text: Text to check

        Returns:
            True if code quality issues detected
        """
        # Extract code blocks
        code_blocks = re.findall(r'```(?:python)?\s*\n(.*?)```', text, re.DOTALL)

        if not code_blocks:
            return False  # No code to check

        for code in code_blocks:
            # Check for incomplete code indicators
            incomplete_indicators = [
                r'\.\.\.+',  # Ellipsis indicating omitted code
                r'#\s*TODO',  # TODO comments
                r'#\s*FIXME',  # FIXME comments
                r'pass\s*$',  # Bare pass statement at end
                r'^\s*$',  # Empty code block
            ]

            for pattern in incomplete_indicators:
                if re.search(pattern, code, re.MULTILINE):
                    return True

        return False

    def _calculate_confidence_score(
        self,
        has_uncertain_language: bool,
        is_too_short: bool,
        has_excessive_repetition: bool,
        has_error_indicators: bool,
        code_quality_issues: bool,
        uncertain_match_count: int
    ) -> float:
        """
        Calculate overall confidence score

        Args:
            Various uncertainty indicators

        Returns:
            Confidence score from 0.0 (very uncertain) to 1.0 (very confident)
        """
        score = 1.0

        # Deduct for each uncertainty indicator
        if has_uncertain_language:
            score -= min(0.4 + (uncertain_match_count * 0.1), 0.6)

        if is_too_short:
            score -= 0.4

        if has_excessive_repetition:
            score -= 0.3

        if has_error_indicators:
            score -= 0.4

        if code_quality_issues:
            score -= 0.3

        # Clamp to [0.0, 1.0]
        return max(0.0, min(1.0, score))

    def should_trigger_fallback(
        self,
        response: str,
        override_threshold: float = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Determine if Claude fallback should be triggered

        Args:
            response: The LLM response to analyze
            override_threshold: Optional custom confidence threshold

        Returns:
            Tuple of (should_fallback: bool, analysis: dict)
        """
        analysis = self.analyze_response(response)

        threshold = override_threshold if override_threshold is not None else 0.6
        should_fallback = analysis['confidence_score'] < threshold

        return should_fallback, analysis


# Standalone testing
if __name__ == "__main__":
    detector = UncertaintyDetector()

    # Test cases
    test_responses = [
        ("I'm not sure about that, but maybe it could work.", "Uncertain language"),
        ("To calculate the factorial, use recursion:\n```python\ndef factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)\n```", "Confident response"),
        ("", "Empty response"),
        ("Yes.", "Too short"),
        ("I don't know the answer to that question.", "Direct uncertainty"),
        ("Here's the code:\n```python\n...\npass\n```", "Incomplete code"),
    ]

    print("🧬 Uncertainty Detection Test Results\n")

    for i, (response, description) in enumerate(test_responses, 1):
        should_fallback, analysis = detector.should_trigger_fallback(response)

        print(f"Test {i}: {description}")
        print(f"Response: {response[:50]}{'...' if len(response) > 50 else ''}")
        print(f"Confidence: {analysis['confidence_score']:.2f}")
        print(f"Fallback: {'YES' if should_fallback else 'NO'}")
        print(f"Reason: {analysis['reason']}")
        print()
