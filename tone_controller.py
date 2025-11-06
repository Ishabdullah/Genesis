#!/usr/bin/env python3
"""
Genesis Tone Controller
Dynamic tone detection and response style adjustment
"""

import re
from typing import Dict, Tuple, Optional
from enum import Enum


class ResponseTone(Enum):
    """Available response tones"""
    TECHNICAL = "technical"
    CONVERSATIONAL = "conversational"
    ADVISORY = "advisory"
    CONCISE = "concise"


class VerbosityLevel(Enum):
    """Response verbosity levels"""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class ToneController:
    """Manages dynamic tone detection and response style"""

    def __init__(self):
        """Initialize tone controller"""
        self.current_tone = ResponseTone.CONVERSATIONAL
        self.current_verbosity = VerbosityLevel.MEDIUM
        self.user_preferences = {}

        # Tone detection patterns
        self.tone_patterns = {
            ResponseTone.TECHNICAL: {
                "keywords": [
                    "explain", "implement", "code", "algorithm", "function",
                    "debug", "error", "syntax", "compile", "binary", "variable",
                    "class", "method", "optimization", "complexity", "performance",
                    "architecture", "design pattern", "api", "protocol", "data structure"
                ],
                "explicit": ["be technical", "give me technical", "formally", "precisely"]
            },
            ResponseTone.CONVERSATIONAL: {
                "keywords": [
                    "tell me", "what's", "how's", "story", "chat", "discuss",
                    "opinion", "think", "casual", "simple", "layman", "eli5",
                    "in simple terms", "easy to understand"
                ],
                "explicit": ["casually", "conversationally", "like explaining to a friend", "simply"]
            },
            ResponseTone.ADVISORY: {
                "keywords": [
                    "how do i", "how should i", "what should", "guide", "tutorial",
                    "step by step", "walkthrough", "instructions", "teach", "learn",
                    "best practice", "recommend", "suggest", "advice", "help me"
                ],
                "explicit": ["guide me", "teach me", "show me how", "step by step"]
            },
            ResponseTone.CONCISE: {
                "keywords": [
                    "briefly", "quick", "short", "summarize", "tldr", "in brief",
                    "just tell me", "bottom line", "key points", "overview"
                ],
                "explicit": ["be brief", "short answer", "concise", "quick answer", "tldr"]
            }
        }

        # Verbosity detection patterns
        self.verbosity_patterns = {
            VerbosityLevel.SHORT: ["briefly", "quick", "short", "tldr", "summary", "concise"],
            VerbosityLevel.LONG: ["detailed", "comprehensive", "in depth", "thoroughly", "explain fully", "elaborate"],
            VerbosityLevel.MEDIUM: []  # Default
        }

    def detect_tone(self, query: str, override: Optional[str] = None) -> Tuple[ResponseTone, float]:
        """
        Detect appropriate tone for a query

        Args:
            query: User's query
            override: Optional explicit tone override

        Returns:
            (tone, confidence) tuple
        """
        # Check for explicit override
        if override:
            for tone in ResponseTone:
                if override.lower() in [tone.value, tone.name.lower()]:
                    return tone, 1.0

        query_lower = query.lower()

        # Check for explicit tone indicators in query
        for tone, patterns in self.tone_patterns.items():
            for explicit_phrase in patterns["explicit"]:
                if explicit_phrase in query_lower:
                    self.current_tone = tone
                    return tone, 0.95

        # Score each tone based on keyword matches
        scores = {}
        for tone, patterns in self.tone_patterns.items():
            score = sum(1 for keyword in patterns["keywords"] if keyword in query_lower)
            scores[tone] = score

        # Get highest scoring tone
        if max(scores.values()) == 0:
            # No clear tone detected, use conversational as default
            return ResponseTone.CONVERSATIONAL, 0.5

        best_tone = max(scores.items(), key=lambda x: x[1])
        confidence = min(0.95, best_tone[1] / 10)  # Normalize to 0-0.95

        self.current_tone = best_tone[0]
        return best_tone[0], confidence

    def detect_verbosity(self, query: str, override: Optional[str] = None) -> VerbosityLevel:
        """
        Detect desired verbosity level

        Args:
            query: User's query
            override: Optional explicit verbosity override

        Returns:
            VerbosityLevel
        """
        # Check for explicit override
        if override:
            for level in VerbosityLevel:
                if override.lower() in [level.value, level.name.lower()]:
                    self.current_verbosity = level
                    return level

        query_lower = query.lower()

        # Check for verbosity indicators
        for level, keywords in self.verbosity_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                self.current_verbosity = level
                return level

        # Check for follow-up expansion request
        follow_up_patterns = ["explain further", "more detail", "tell me more", "elaborate", "expand"]
        if any(pattern in query_lower for pattern in follow_up_patterns):
            return VerbosityLevel.LONG

        # Default to medium
        return VerbosityLevel.MEDIUM

    def get_response_template(self, tone: ResponseTone, verbosity: VerbosityLevel) -> Dict:
        """
        Get response formatting template for tone and verbosity

        Args:
            tone: Response tone
            verbosity: Verbosity level

        Returns:
            Template configuration dictionary
        """
        templates = {
            ResponseTone.TECHNICAL: {
                VerbosityLevel.SHORT: {
                    "style": "technical_concise",
                    "max_lines": 10,
                    "include_code": True,
                    "include_examples": False,
                    "format": "bullet_points"
                },
                VerbosityLevel.MEDIUM: {
                    "style": "technical_standard",
                    "max_lines": 30,
                    "include_code": True,
                    "include_examples": True,
                    "format": "structured"
                },
                VerbosityLevel.LONG: {
                    "style": "technical_comprehensive",
                    "max_lines": None,
                    "include_code": True,
                    "include_examples": True,
                    "format": "detailed_sections"
                }
            },
            ResponseTone.CONVERSATIONAL: {
                VerbosityLevel.SHORT: {
                    "style": "casual_brief",
                    "max_lines": 5,
                    "include_code": False,
                    "include_examples": False,
                    "format": "paragraph"
                },
                VerbosityLevel.MEDIUM: {
                    "style": "casual_standard",
                    "max_lines": 15,
                    "include_code": False,
                    "include_examples": True,
                    "format": "paragraph"
                },
                VerbosityLevel.LONG: {
                    "style": "casual_detailed",
                    "max_lines": None,
                    "include_code": False,
                    "include_examples": True,
                    "format": "story_like"
                }
            },
            ResponseTone.ADVISORY: {
                VerbosityLevel.SHORT: {
                    "style": "advisory_quick",
                    "max_lines": 8,
                    "include_code": True,
                    "include_examples": False,
                    "format": "numbered_steps"
                },
                VerbosityLevel.MEDIUM: {
                    "style": "advisory_standard",
                    "max_lines": 25,
                    "include_code": True,
                    "include_examples": True,
                    "format": "step_by_step"
                },
                VerbosityLevel.LONG: {
                    "style": "advisory_comprehensive",
                    "max_lines": None,
                    "include_code": True,
                    "include_examples": True,
                    "format": "tutorial"
                }
            },
            ResponseTone.CONCISE: {
                VerbosityLevel.SHORT: {
                    "style": "minimal",
                    "max_lines": 3,
                    "include_code": False,
                    "include_examples": False,
                    "format": "single_line"
                },
                VerbosityLevel.MEDIUM: {
                    "style": "brief",
                    "max_lines": 7,
                    "include_code": True,
                    "include_examples": False,
                    "format": "bullet_points"
                },
                VerbosityLevel.LONG: {
                    "style": "concise_detailed",
                    "max_lines": 15,
                    "include_code": True,
                    "include_examples": False,
                    "format": "compact_sections"
                }
            }
        }

        return templates.get(tone, {}).get(verbosity, templates[ResponseTone.CONVERSATIONAL][VerbosityLevel.MEDIUM])

    def format_response_header(self, tone: ResponseTone, verbosity: VerbosityLevel) -> str:
        """
        Generate response header indicating tone and verbosity

        Args:
            tone: Response tone
            verbosity: Verbosity level

        Returns:
            Formatted header string
        """
        tone_icons = {
            ResponseTone.TECHNICAL: "🔧",
            ResponseTone.CONVERSATIONAL: "💬",
            ResponseTone.ADVISORY: "📖",
            ResponseTone.CONCISE: "⚡"
        }

        verbosity_labels = {
            VerbosityLevel.SHORT: "Brief",
            VerbosityLevel.MEDIUM: "Standard",
            VerbosityLevel.LONG: "Detailed"
        }

        icon = tone_icons.get(tone, "💬")
        tone_label = tone.value.capitalize()
        verbosity_label = verbosity_labels.get(verbosity, "Standard")

        return f"{icon} [Tone: {tone_label} | Length: {verbosity_label}]"

    def get_system_prompt_modifier(self, tone: ResponseTone, verbosity: VerbosityLevel) -> str:
        """
        Get system prompt modifier for the LLM based on tone

        Args:
            tone: Response tone
            verbosity: Verbosity level

        Returns:
            System prompt addition
        """
        modifiers = {
            ResponseTone.TECHNICAL: {
                VerbosityLevel.SHORT: "Respond technically and concisely. Use precise terminology. Include code only if essential.",
                VerbosityLevel.MEDIUM: "Provide a technical explanation with examples and code where appropriate. Be clear and precise.",
                VerbosityLevel.LONG: "Give a comprehensive technical explanation with detailed examples, code, and edge cases. Be thorough."
            },
            ResponseTone.CONVERSATIONAL: {
                VerbosityLevel.SHORT: "Answer casually and briefly, like explaining to a friend. Keep it simple.",
                VerbosityLevel.MEDIUM: "Explain conversationally with examples. Be friendly and clear without excessive detail.",
                VerbosityLevel.LONG: "Provide a detailed, friendly explanation as if having an in-depth conversation. Use analogies and examples."
            },
            ResponseTone.ADVISORY: {
                VerbosityLevel.SHORT: "Give step-by-step guidance in numbered format. Be direct and actionable.",
                VerbosityLevel.MEDIUM: "Provide clear step-by-step instructions with explanations. Include examples and tips.",
                VerbosityLevel.LONG: "Give comprehensive tutorial-style guidance with detailed steps, examples, and best practices."
            },
            ResponseTone.CONCISE: {
                VerbosityLevel.SHORT: "Answer in 1-2 sentences maximum. Be direct and to the point.",
                VerbosityLevel.MEDIUM: "Provide a brief, focused answer with key points only. No fluff.",
                VerbosityLevel.LONG: "Give a detailed but compact answer. Include important details without unnecessary elaboration."
            }
        }

        return modifiers.get(tone, {}).get(verbosity,
            "Respond clearly and appropriately to the user's question.")

    def set_user_preference(self, preference_name: str, value):
        """
        Set user preference

        Args:
            preference_name: Name of preference
            value: Preference value
        """
        self.user_preferences[preference_name] = value

    def get_user_preference(self, preference_name: str, default=None):
        """Get user preference with default fallback"""
        return self.user_preferences.get(preference_name, default)


# Global instance
_tone_controller_instance = None


def get_tone_controller() -> ToneController:
    """Get or create global ToneController instance"""
    global _tone_controller_instance
    if _tone_controller_instance is None:
        _tone_controller_instance = ToneController()
    return _tone_controller_instance


if __name__ == "__main__":
    # Test the tone controller
    controller = ToneController()

    test_queries = [
        "Explain how binary search works",
        "Tell me a story about AI",
        "How do I set up a Python virtual environment?",
        "Briefly, what is quantum computing?",
        "Be technical: explain async/await"
    ]

    for query in test_queries:
        tone, conf = controller.detect_tone(query)
        verbosity = controller.detect_verbosity(query)
        template = controller.get_response_template(tone, verbosity)
        header = controller.format_response_header(tone, verbosity)

        print(f"\nQuery: {query}")
        print(f"Tone: {tone.value} (confidence: {conf:.2f})")
        print(f"Verbosity: {verbosity.value}")
        print(f"Header: {header}")
        print(f"Template style: {template['style']}")
