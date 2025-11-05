#!/usr/bin/env python3
"""
Genesis Reasoning Module
Multi-step reasoning with pseudocode generation and validation
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ReasoningStep:
    """Single reasoning step"""
    step_num: int
    description: str
    calculation: Optional[str] = None
    result: Optional[str] = None

class ReasoningEngine:
    """Handles multi-step reasoning and pseudocode generation"""

    def __init__(self):
        """Initialize reasoning engine"""
        self.current_trace = []
        self.reasoning_patterns = self._load_patterns()

    def _load_patterns(self) -> Dict:
        """Load reasoning patterns for different problem types"""
        return {
            "math_word_problem": {
                "keywords": ["if", "how many", "calculate", "total", "rate", "per"],
                "steps": [
                    "Identify the given information",
                    "Determine what needs to be calculated",
                    "Set up the relationship/formula",
                    "Perform the calculation",
                    "Verify the answer makes sense"
                ]
            },
            "logic_problem": {
                "keywords": ["implies", "if.*then", "therefore", "because", "consequently"],
                "steps": [
                    "Identify the premises",
                    "Identify the conclusion",
                    "Check logical connections",
                    "Validate the reasoning chain",
                    "State the final conclusion"
                ]
            },
            "programming": {
                "keywords": ["write", "function", "code", "implement", "algorithm"],
                "steps": [
                    "Identify input types and constraints",
                    "Determine the required operations",
                    "Design the algorithm/logic",
                    "Consider edge cases",
                    "Implement the solution"
                ]
            },
            "design": {
                "keywords": ["design", "architect", "structure", "system", "plan"],
                "steps": [
                    "Understand requirements",
                    "Identify key components",
                    "Define relationships/interfaces",
                    "Consider scalability and constraints",
                    "Produce design specification"
                ]
            }
        }

    def detect_problem_type(self, query: str) -> str:
        """
        Detect the type of problem to apply appropriate reasoning

        Args:
            query: User's query

        Returns:
            Problem type identifier
        """
        query_lower = query.lower()

        # Check each pattern
        for prob_type, pattern in self.reasoning_patterns.items():
            for keyword in pattern["keywords"]:
                if re.search(keyword, query_lower):
                    return prob_type

        # Default to general reasoning
        return "general"

    def generate_reasoning_trace(self, query: str, problem_type: Optional[str] = None) -> List[ReasoningStep]:
        """
        Generate multi-step reasoning trace for a query

        Args:
            query: User's query
            problem_type: Optional problem type override

        Returns:
            List of reasoning steps
        """
        if problem_type is None:
            problem_type = self.detect_problem_type(query)

        steps = []

        if problem_type == "math_word_problem":
            steps = self._reason_math_problem(query)
        elif problem_type == "logic_problem":
            steps = self._reason_logic_problem(query)
        elif problem_type == "programming":
            steps = self._reason_programming_problem(query)
        elif problem_type == "design":
            steps = self._reason_design_problem(query)
        else:
            steps = self._reason_general(query)

        self.current_trace = steps
        return steps

    def _reason_math_problem(self, query: str) -> List[ReasoningStep]:
        """Generate reasoning for math word problems"""
        steps = []

        # Step 1: Identify given information
        steps.append(ReasoningStep(
            step_num=1,
            description="Identify the given information",
            calculation="Extract numbers and relationships from the problem"
        ))

        # Step 2: Determine what to calculate
        steps.append(ReasoningStep(
            step_num=2,
            description="Determine what needs to be calculated",
            calculation="Identify the target variable or question"
        ))

        # Step 3: Set up relationship
        steps.append(ReasoningStep(
            step_num=3,
            description="Set up the mathematical relationship",
            calculation="Establish formula or equation"
        ))

        # Step 4: Calculate
        steps.append(ReasoningStep(
            step_num=4,
            description="Perform the calculation",
            calculation="Apply the formula with given values"
        ))

        # Step 5: Validate
        steps.append(ReasoningStep(
            step_num=5,
            description="Verify the answer",
            calculation="Check if the result makes logical sense"
        ))

        return steps

    def _reason_logic_problem(self, query: str) -> List[ReasoningStep]:
        """Generate reasoning for logic problems"""
        steps = []

        steps.append(ReasoningStep(
            step_num=1,
            description="Identify the premises (given statements)"
        ))

        steps.append(ReasoningStep(
            step_num=2,
            description="Identify what needs to be proven/concluded"
        ))

        steps.append(ReasoningStep(
            step_num=3,
            description="Check logical connections between premises"
        ))

        steps.append(ReasoningStep(
            step_num=4,
            description="Apply logical rules (transitivity, modus ponens, etc.)"
        ))

        steps.append(ReasoningStep(
            step_num=5,
            description="State the conclusion with justification"
        ))

        return steps

    def _reason_programming_problem(self, query: str) -> List[ReasoningStep]:
        """Generate reasoning for programming problems"""
        steps = []

        steps.append(ReasoningStep(
            step_num=1,
            description="Identify input types and constraints",
            calculation="Determine what data the function/program receives"
        ))

        steps.append(ReasoningStep(
            step_num=2,
            description="Determine required operations",
            calculation="List what needs to be done with the input"
        ))

        steps.append(ReasoningStep(
            step_num=3,
            description="Design the algorithm",
            calculation="Outline the logical flow in pseudocode"
        ))

        steps.append(ReasoningStep(
            step_num=4,
            description="Consider edge cases",
            calculation="Identify boundary conditions and special cases"
        ))

        steps.append(ReasoningStep(
            step_num=5,
            description="Implement the solution",
            calculation="Write the actual code"
        ))

        return steps

    def _reason_design_problem(self, query: str) -> List[ReasoningStep]:
        """Generate reasoning for system design problems"""
        steps = []

        steps.append(ReasoningStep(
            step_num=1,
            description="Understand the requirements",
            calculation="What problem are we solving?"
        ))

        steps.append(ReasoningStep(
            step_num=2,
            description="Identify key components/modules",
            calculation="Break down into logical parts"
        ))

        steps.append(ReasoningStep(
            step_num=3,
            description="Define interfaces and relationships",
            calculation="How do components interact?"
        ))

        steps.append(ReasoningStep(
            step_num=4,
            description="Consider constraints and trade-offs",
            calculation="Performance, scalability, maintainability"
        ))

        steps.append(ReasoningStep(
            step_num=5,
            description="Produce design specification",
            calculation="Document the architecture"
        ))

        return steps

    def _reason_general(self, query: str) -> List[ReasoningStep]:
        """Generate general reasoning steps"""
        steps = []

        steps.append(ReasoningStep(
            step_num=1,
            description="Understand the question",
            calculation="What is being asked?"
        ))

        steps.append(ReasoningStep(
            step_num=2,
            description="Identify relevant information",
            calculation="What facts or data are available?"
        ))

        steps.append(ReasoningStep(
            step_num=3,
            description="Apply logical reasoning",
            calculation="Connect information to reach conclusion"
        ))

        steps.append(ReasoningStep(
            step_num=4,
            description="Formulate the answer",
            calculation="State the conclusion clearly"
        ))

        return steps

    def generate_pseudocode(self, query: str) -> str:
        """
        Generate pseudocode for programming/algorithm problems

        Args:
            query: User's query

        Returns:
            Pseudocode string
        """
        # Extract task from query
        pseudocode_lines = []

        pseudocode_lines.append("PSEUDOCODE:")
        pseudocode_lines.append("──────────────────")

        # Determine if it's about a specific data structure operation
        query_lower = query.lower()

        if "sum" in query_lower and ("even" in query_lower or "odd" in query_lower):
            pseudocode_lines.extend([
                "FUNCTION sum_filtered(list):",
                "  SET total = 0",
                "  FOR each element IN list:",
                "    IF element meets condition:",
                "      ADD element TO total",
                "  RETURN total",
                "END FUNCTION"
            ])
        elif "reverse" in query_lower:
            pseudocode_lines.extend([
                "FUNCTION reverse(input):",
                "  INITIALIZE result as empty",
                "  FOR each element IN input (backwards):",
                "    APPEND element TO result",
                "  RETURN result",
                "END FUNCTION"
            ])
        elif "sort" in query_lower or "order" in query_lower:
            pseudocode_lines.extend([
                "FUNCTION sort(list):",
                "  FOR i FROM 0 TO length(list)-1:",
                "    FOR j FROM i+1 TO length(list):",
                "      IF list[i] > list[j]:",
                "        SWAP list[i] AND list[j]",
                "  RETURN list",
                "END FUNCTION"
            ])
        elif "search" in query_lower or "find" in query_lower:
            pseudocode_lines.extend([
                "FUNCTION search(list, target):",
                "  FOR each element IN list:",
                "    IF element EQUALS target:",
                "      RETURN index of element",
                "  RETURN not found",
                "END FUNCTION"
            ])
        else:
            # Generic pseudocode structure
            pseudocode_lines.extend([
                "FUNCTION solve_problem(input):",
                "  // Step 1: Parse/validate input",
                "  // Step 2: Initialize variables",
                "  // Step 3: Process data",
                "  // Step 4: Handle edge cases",
                "  // Step 5: Return result",
                "END FUNCTION"
            ])

        return "\n".join(pseudocode_lines)

    def validate_reasoning(self, steps: List[ReasoningStep], final_answer: str) -> Tuple[bool, List[str]]:
        """
        Validate reasoning chain for consistency

        Args:
            steps: List of reasoning steps
            final_answer: The proposed answer

        Returns:
            (is_valid, list of warnings/issues)
        """
        warnings = []

        # Check if reasoning has sufficient steps
        if len(steps) < 3:
            warnings.append("Reasoning may be too brief - consider more detailed steps")

        # Check for logical flow
        if not steps:
            warnings.append("No reasoning steps provided")
            return False, warnings

        # Check if calculations are present for math problems
        has_calculations = any(step.calculation for step in steps)
        if not has_calculations and any(word in final_answer.lower() for word in ["number", "calculate", "sum"]):
            warnings.append("Math problem but no explicit calculations shown")

        # Basic consistency check
        if not final_answer.strip():
            warnings.append("Final answer is empty")
            return False, warnings

        # If we have warnings, mark as needing review
        is_valid = len(warnings) == 0

        return is_valid, warnings

    def format_trace_for_display(self, steps: List[ReasoningStep]) -> str:
        """
        Format reasoning trace for terminal display

        Args:
            steps: List of reasoning steps

        Returns:
            Formatted string for display
        """
        lines = []
        lines.append("\n[Thinking...]")
        lines.append("─" * 60)

        for step in steps:
            lines.append(f"\nStep {step.step_num}: {step.description}")
            if step.calculation:
                lines.append(f"  → {step.calculation}")
            if step.result:
                lines.append(f"  ✓ {step.result}")

        lines.append("\n" + "─" * 60)

        return "\n".join(lines)

    def get_last_trace(self) -> List[ReasoningStep]:
        """Get the most recent reasoning trace"""
        return self.current_trace

    def clear_trace(self):
        """Clear current reasoning trace"""
        self.current_trace = []
