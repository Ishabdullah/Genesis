#!/usr/bin/env python3
"""
Genesis Reasoning Module
Multi-step reasoning with pseudocode generation and validation
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from math_reasoner import MathReasoner

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
        self.math_reasoner = MathReasoner()
        self.last_math_answer = None
        self.last_math_solution = None
        self.current_question_id = None  # Track current question being processed
        self.time_sync = None  # Will be initialized by Genesis
        self.knowledge_cutoff = "2023-12-31"  # CodeLlama-7B knowledge cutoff

    def start_new_question(self, question_id: str):
        """
        Mark the start of a new question - clears previous answers

        Args:
            question_id: Unique identifier for this question
        """
        if self.current_question_id != question_id:
            # New question - clear previous calculated answers
            self.last_math_answer = None
            self.last_math_solution = None
            self.current_question_id = question_id
            self.current_trace = []

    def _load_patterns(self) -> Dict:
        """Load reasoning patterns for different problem types"""
        return {
            "math_word_problem": {
                "keywords": ["if", "how many", "how much", "calculate", "total", "rate", "per", "cost", "all but", "machines?.*package", "required", "needs? to"],
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
            },
            "metacognitive": {
                "keywords": ["#incorrect", "#correct", "limitation", "how do you", "what can you", "explain yourself", "retry", "try again"],
                "steps": [
                    "Understand the meta-question or feedback",
                    "Identify relevant system capabilities or issues",
                    "Explain reasoning, limitation, or corrective action",
                    "Provide actionable next steps"
                ]
            }
        }

    def classify_query(self, query: str) -> tuple:
        """
        Classify query into intent categories for routing to appropriate handler

        Args:
            query: User's query

        Returns:
            Tuple of (query_type, confidence_score, metadata)
        """
        query_lower = query.lower()

        # Temporal/time-sensitive keywords
        temporal_keywords = [
            "latest", "newest", "recent", "recently", "current", "currently",
            "now", "today", "this year", "2025", "2024", "emerging",
            "new", "just", "most recent", "up-to-date", "trending",
            "breaking", "modern", "contemporary", "present"
        ]

        # Web research keywords
        web_research_keywords = [
            "latest", "2025", "2024", "published", "papers", "studies",
            "advancements", "research", "published in", "recent", "news",
            "current", "today", "this year", "breakthrough", "development"
        ]

        # Code generation keywords
        code_gen_keywords = [
            "write", "script", "code", "python", "recursive", "visualize",
            "implement", "function", "class", "algorithm", "program",
            "java", "javascript", "c++", "create a"
        ]

        # Follow-up patterns
        follow_up_keywords = [
            "try again", "recalculate", "retry", "redo that", "do that again",
            "explain further", "give an example", "tell me more", "elaborate",
            "more details"
        ]

        # Math/logic keywords
        math_keywords = [
            "if", "how many", "how much", "calculate", "total", "rate",
            "per", "cost", "all but", "solve", "compute"
        ]

        # Count keyword matches for each category
        temporal_score = sum(1 for kw in temporal_keywords if kw in query_lower)
        web_score = sum(1 for kw in web_research_keywords if kw in query_lower)
        code_score = sum(1 for kw in code_gen_keywords if kw in query_lower)
        follow_up_score = sum(1 for kw in follow_up_keywords if kw in query_lower)
        math_score = sum(1 for kw in math_keywords if kw in query_lower)

        # Has numbers and relational words? Boost math score
        if re.search(r'\d+', query) and any(word in query_lower for word in ["more", "less", "than", "equal", "divide", "multiply"]):
            math_score += 2

        # Check for time-sensitive patterns
        time_sensitive = temporal_score > 0
        time_sensitive = time_sensitive or any(word in query_lower for word in [
            "who is", "what is", "president", "currently", "right now"
        ])

        # Metadata about the query
        metadata = {
            "time_sensitive": time_sensitive,
            "temporal_score": temporal_score,
            "needs_live_data": time_sensitive or web_score >= 2
        }

        # Determine category with confidence
        if follow_up_score > 0:
            return ("follow_up", 0.9, metadata)
        elif web_score >= 2 or temporal_score >= 2:
            return ("web_research", 0.85, metadata)
        elif (web_score == 1 or temporal_score == 1) and len(query.split()) > 10:
            return ("web_research", 0.75, metadata)
        elif code_score >= 2:
            return ("code_generation", 0.85, metadata)
        elif code_score == 1 and ("write" in query_lower or "create" in query_lower):
            return ("code_generation", 0.80, metadata)
        elif math_score >= 2:
            return ("math_logic", 0.85, metadata)
        elif re.search(r'\d+.*\d+', query):  # Multiple numbers
            return ("math_logic", 0.70, metadata)
        else:
            return ("conceptual", 0.60, metadata)

    def detect_problem_type(self, query: str) -> str:
        """
        Detect the type of problem to apply appropriate reasoning

        Args:
            query: User's query

        Returns:
            Problem type identifier
        """
        query_lower = query.lower()

        # Priority check for metacognitive queries (feedback, self-reflection)
        if query_lower.startswith('#incorrect') or query_lower.startswith('#correct'):
            return "metacognitive"

        # Check each pattern with priority
        pattern_priority = ["metacognitive", "math_word_problem", "logic_problem", "programming", "design", "general"]

        for prob_type in pattern_priority:
            if prob_type in self.reasoning_patterns:
                pattern = self.reasoning_patterns[prob_type]
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
        elif problem_type == "metacognitive":
            steps = self._reason_metacognitive(query)
        else:
            steps = self._reason_general(query)

        self.current_trace = steps
        return steps

    def _reason_math_problem(self, query: str) -> List[ReasoningStep]:
        """Generate reasoning for math word problems with ACTUAL calculations"""
        steps = []

        # Try to use math reasoner for automatic solving
        solution = self.math_reasoner.detect_and_solve(query)

        if solution and 'steps' in solution:
            # Convert MathStep objects to ReasoningStep objects
            for math_step in solution['steps']:
                steps.append(ReasoningStep(
                    step_num=math_step.step_num,
                    description=math_step.description,
                    calculation=math_step.calculation if math_step.calculation else math_step.formula,
                    result=str(math_step.result) if math_step.result else None
                ))
            # Store the actual answer for later use
            self.last_math_answer = solution.get('answer') or solution.get('smaller_item')
            self.last_math_solution = solution
        else:
            # Fall back to generic template with emphasis on showing work
            steps.append(ReasoningStep(
                step_num=1,
                description="Identify the given information",
                calculation="Extract all numbers and relationships from the problem statement"
            ))

            steps.append(ReasoningStep(
                step_num=2,
                description="Determine what needs to be calculated",
                calculation="Identify the unknown variable and what formula applies"
            ))

            steps.append(ReasoningStep(
                step_num=3,
                description="Set up the mathematical relationship",
                calculation="Write out the equation with variables defined"
            ))

            steps.append(ReasoningStep(
                step_num=4,
                description="Perform the calculation step-by-step",
                calculation="Show all arithmetic operations with intermediate results"
            ))

            steps.append(ReasoningStep(
                step_num=5,
                description="Verify the answer",
                calculation="Substitute back into original constraints to check correctness"
            ))
            self.last_math_answer = None

        return steps

    def _reason_logic_problem(self, query: str) -> List[ReasoningStep]:
        """Generate reasoning for logic problems"""
        steps = []

        steps.append(ReasoningStep(
            step_num=1,
            description="Extracting premises",
            calculation="Identifying all given statements and conditions from the problem"
        ))

        steps.append(ReasoningStep(
            step_num=2,
            description="Clarifying the goal",
            calculation="Determining what conclusion needs to be proven or derived"
        ))

        steps.append(ReasoningStep(
            step_num=3,
            description="Analyzing logical connections",
            calculation="Examining how premises relate to each other and to the desired conclusion"
        ))

        steps.append(ReasoningStep(
            step_num=4,
            description="Applying logical rules",
            calculation="Using logical inference rules (transitivity, modus ponens, contradiction, etc.)"
        ))

        steps.append(ReasoningStep(
            step_num=5,
            description="Stating conclusion with proof",
            calculation="Presenting the final conclusion with step-by-step logical justification"
        ))

        return steps

    def _reason_programming_problem(self, query: str) -> List[ReasoningStep]:
        """Generate reasoning for programming problems"""
        steps = []

        steps.append(ReasoningStep(
            step_num=1,
            description="Analyzing input requirements",
            calculation="Examining the data types and constraints specified in the problem"
        ))

        steps.append(ReasoningStep(
            step_num=2,
            description="Planning required operations",
            calculation="Breaking down the problem into logical operations"
        ))

        steps.append(ReasoningStep(
            step_num=3,
            description="Designing algorithm structure",
            calculation="Creating step-by-step logical flow for the solution"
        ))

        steps.append(ReasoningStep(
            step_num=4,
            description="Identifying edge cases",
            calculation="Considering boundary conditions and special scenarios"
        ))

        steps.append(ReasoningStep(
            step_num=5,
            description="Implementing solution",
            calculation="Translating algorithm into working code"
        ))

        return steps

    def _reason_design_problem(self, query: str) -> List[ReasoningStep]:
        """Generate reasoning for system design problems"""
        steps = []

        steps.append(ReasoningStep(
            step_num=1,
            description="Analyzing requirements",
            calculation="Examining the core problem and objectives to be addressed"
        ))

        steps.append(ReasoningStep(
            step_num=2,
            description="Identifying system components",
            calculation="Breaking down the system into logical modules and services"
        ))

        steps.append(ReasoningStep(
            step_num=3,
            description="Defining component interactions",
            calculation="Establishing interfaces, APIs, and data flow between components"
        ))

        steps.append(ReasoningStep(
            step_num=4,
            description="Evaluating constraints and trade-offs",
            calculation="Balancing performance, scalability, and maintainability requirements"
        ))

        steps.append(ReasoningStep(
            step_num=5,
            description="Creating design specification",
            calculation="Documenting the complete architecture with diagrams and details"
        ))

        return steps

    def _reason_metacognitive(self, query: str) -> List[ReasoningStep]:
        """Generate reasoning for metacognitive/feedback queries"""
        steps = []

        steps.append(ReasoningStep(
            step_num=1,
            description="Analyzing meta-question or feedback",
            calculation="Determining if this is feedback on a previous response, a capability inquiry, or a retry request"
        ))

        steps.append(ReasoningStep(
            step_num=2,
            description="Identifying relevant system capabilities",
            calculation="Mapping to Genesis features: memory systems, reasoning engine, external sources, or known limitations"
        ))

        steps.append(ReasoningStep(
            step_num=3,
            description="Diagnosing the issue or request",
            calculation="For feedback: categorizing error type. For capability questions: listing relevant features like persistent memory, pruning, context handling, fallback chain"
        ))

        steps.append(ReasoningStep(
            step_num=4,
            description="Formulating response strategy",
            calculation="Preparing actionable next steps: retry with corrections, explain limitations with workarounds, or describe capabilities with examples"
        ))

        return steps

    def _reason_general(self, query: str) -> List[ReasoningStep]:
        """Generate general reasoning steps"""
        steps = []

        steps.append(ReasoningStep(
            step_num=1,
            description="Parsing the question",
            calculation="Analyzing the query to identify the core information request"
        ))

        steps.append(ReasoningStep(
            step_num=2,
            description="Gathering relevant information",
            calculation="Accessing available facts, data, and context from knowledge base and memory"
        ))

        steps.append(ReasoningStep(
            step_num=3,
            description="Applying logical reasoning",
            calculation="Connecting information through logical inference to derive conclusions"
        ))

        steps.append(ReasoningStep(
            step_num=4,
            description="Formulating complete answer",
            calculation="Synthesizing findings into a clear, coherent response"
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

    def set_time_sync(self, time_sync):
        """
        Set time synchronization module

        Args:
            time_sync: TimeSync instance
        """
        self.time_sync = time_sync

    def detect_temporal_uncertainty(self, query: str) -> Dict:
        """
        Detect if query requires temporal awareness or live data

        Args:
            query: User's query

        Returns:
            Dictionary with temporal analysis
        """
        # Classify the query
        query_type, confidence, metadata = self.classify_query(query)

        # Check if we have time sync
        is_post_cutoff = False
        current_date = None

        if self.time_sync:
            is_post_cutoff = self.time_sync.is_after_knowledge_cutoff()
            current_date = self.time_sync.get_device_date()

        # Determine if temporal uncertainty exists
        temporal_uncertain = metadata.get("time_sensitive", False) and is_post_cutoff

        return {
            "time_sensitive": metadata.get("time_sensitive", False),
            "needs_live_data": metadata.get("needs_live_data", False),
            "temporal_uncertain": temporal_uncertain,
            "is_post_cutoff": is_post_cutoff,
            "current_date": current_date,
            "knowledge_cutoff": self.knowledge_cutoff,
            "should_trigger_fallback": temporal_uncertain or metadata.get("needs_live_data", False)
        }

    def get_calculated_answer(self) -> Optional[str]:
        """
        Get the calculated answer from math reasoner if available

        Returns:
            Calculated answer as string or None
        """
        if self.last_math_answer is not None:
            # Format the answer nicely
            if self.last_math_solution:
                # Check solution type
                if 'solution' in self.last_math_solution:
                    # Logic puzzle solution
                    sol = self.last_math_solution['solution']
                    if isinstance(sol, dict) and 'procedure' in sol:
                        # Format procedure list
                        return "\n".join(sol['procedure']) + "\n\n" + \
                               "Identification:\n" + \
                               "\n".join(f"  {k}: {v}" for k, v in sol.get('identification', {}).items())
                    return str(sol)
                elif 'smaller_item' in self.last_math_solution:
                    # Difference problem (bat and ball)
                    return f"${self.last_math_solution['smaller_item']:.2f}"
            return str(self.last_math_answer)
        return None
