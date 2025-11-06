#!/usr/bin/env python3
"""
Genesis Thinking Trace Display
Live display of reasoning process with step-by-step updates
"""

import sys
import time
from typing import List, Optional
from reasoning import ReasoningStep

class ThinkingTrace:
    """Handles live display of reasoning steps"""

    def __init__(self, show_live: bool = True, delay: float = 0.3):
        """
        Initialize thinking trace display

        Args:
            show_live: Whether to show steps live as they're processed
            delay: Delay between steps (seconds) for readability
        """
        self.show_live = show_live
        self.delay = delay
        self.colors = self._init_colors()

    def _init_colors(self) -> dict:
        """Initialize ANSI color codes"""
        return {
            "cyan": "\033[96m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "reset": "\033[0m",
            "bold": "\033[1m",
            "dim": "\033[2m"
        }

    def display_thinking_header(self, source: Optional[str] = None):
        """Display the thinking section header with optional source

        Args:
            source: Source of reasoning ("local", "perplexity", "claude")
        """
        header = "[Thinking...]"
        if source:
            source_labels = {
                "local": "🧬 Local",
                "perplexity": "🔍 Consulting Perplexity",
                "claude": "☁️ Consulting Claude"
            }
            header = f"[Thinking... {source_labels.get(source, source)}]"

        print(f"\n{self.colors['cyan']}{self.colors['bold']}{header}{self.colors['reset']}")
        print(f"{self.colors['dim']}{'─' * 60}{self.colors['reset']}")
        if self.show_live:
            time.sleep(0.1)

    def display_step(self, step: ReasoningStep, show_details: bool = True):
        """
        Display a single reasoning step

        Args:
            step: The reasoning step to display
            show_details: Whether to show calculations and results
        """
        # Step header
        print(f"\n{self.colors['yellow']}Step {step.step_num}:{self.colors['reset']} {step.description}")

        if show_details:
            # Calculation/logic
            if step.calculation:
                print(f"  {self.colors['blue']}→{self.colors['reset']} {step.calculation}")

            # Result
            if step.result:
                print(f"  {self.colors['green']}✓{self.colors['reset']} {step.result}")

        if self.show_live:
            sys.stdout.flush()
            time.sleep(self.delay)

    def display_steps(self, steps: List[ReasoningStep], show_details: bool = True, source: Optional[str] = None):
        """
        Display all reasoning steps

        Args:
            steps: List of reasoning steps
            show_details: Whether to show calculations and results
            source: Source of reasoning ("local", "perplexity", "claude")
        """
        self.display_thinking_header(source)

        for step in steps:
            self.display_step(step, show_details)

        print(f"\n{self.colors['dim']}{'─' * 60}{self.colors['reset']}\n")
        if self.show_live:
            time.sleep(0.2)

    def display_pseudocode(self, pseudocode: str):
        """
        Display pseudocode with formatting

        Args:
            pseudocode: Pseudocode string
        """
        print(f"\n{self.colors['magenta']}{self.colors['bold']}[Pseudocode]{self.colors['reset']}")
        print(f"{self.colors['dim']}{'─' * 60}{self.colors['reset']}")

        for line in pseudocode.split('\n'):
            # Color code different parts
            if line.strip().startswith('FUNCTION') or line.strip().startswith('END'):
                print(f"{self.colors['cyan']}{line}{self.colors['reset']}")
            elif line.strip().startswith('IF') or line.strip().startswith('FOR') or line.strip().startswith('WHILE'):
                print(f"{self.colors['yellow']}{line}{self.colors['reset']}")
            elif line.strip().startswith('RETURN'):
                print(f"{self.colors['green']}{line}{self.colors['reset']}")
            elif line.strip().startswith('//'):
                print(f"{self.colors['dim']}{line}{self.colors['reset']}")
            else:
                print(line)

            if self.show_live:
                sys.stdout.flush()
                time.sleep(0.1)

        print(f"{self.colors['dim']}{'─' * 60}{self.colors['reset']}\n")

    def display_validation_warnings(self, warnings: List[str]):
        """
        Display validation warnings

        Args:
            warnings: List of warning messages
        """
        if not warnings:
            return

        print(f"\n{self.colors['yellow']}⚠ Reasoning Validation Warnings:{self.colors['reset']}")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
        print()

    def display_final_answer(self, answer: str, confidence: Optional[float] = None):
        """
        Display the final answer clearly separated from reasoning

        Args:
            answer: The final answer
            confidence: Optional confidence score (0-1)
        """
        print(f"{self.colors['green']}{self.colors['bold']}Final Answer:{self.colors['reset']}")
        print(f"{self.colors['dim']}{'─' * 60}{self.colors['reset']}")
        print(f"{answer}")

        if confidence is not None:
            if confidence >= 0.9:
                conf_color = self.colors['green']
                conf_label = "High"
            elif confidence >= 0.7:
                conf_color = self.colors['yellow']
                conf_label = "Medium"
            else:
                conf_color = self.colors['yellow']
                conf_label = "Low"

            print(f"\n{self.colors['dim']}Confidence: {conf_color}{conf_label} ({confidence:.2f}){self.colors['reset']}")

        print(f"{self.colors['dim']}{'─' * 60}{self.colors['reset']}\n")

    def display_compact_trace(self, steps: List[ReasoningStep]):
        """
        Display compact version of reasoning (just step descriptions)

        Args:
            steps: List of reasoning steps
        """
        print(f"\n{self.colors['cyan']}[Reasoning Steps]{self.colors['reset']}")
        for step in steps:
            print(f"  {step.step_num}. {step.description}")
        print()

    def display_thinking_animation(self, duration: float = 1.0):
        """
        Display simple thinking animation

        Args:
            duration: Duration of animation in seconds
        """
        animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration
        i = 0

        print(f"\n{self.colors['cyan']}", end='')
        while time.time() < end_time:
            print(f"\r[{animation[i % len(animation)]} Analyzing...]", end='')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        print(f"\r{' ' * 30}\r", end='')  # Clear line
        print(f"{self.colors['reset']}", end='')

    def display_reasoning_summary(self, problem_type: str, step_count: int, has_pseudocode: bool):
        """
        Display summary of reasoning process

        Args:
            problem_type: Type of problem analyzed
            step_count: Number of reasoning steps
            has_pseudocode: Whether pseudocode was generated
        """
        print(f"\n{self.colors['dim']}[Reasoning Summary]{self.colors['reset']}")
        print(f"{self.colors['dim']}Type: {problem_type.replace('_', ' ').title()}{self.colors['reset']}")
        print(f"{self.colors['dim']}Steps: {step_count}{self.colors['reset']}")
        if has_pseudocode:
            print(f"{self.colors['dim']}Pseudocode: Generated{self.colors['reset']}")
        print()
