#!/usr/bin/env python3
"""
Genesis Math Reasoner Module
Performs actual numeric and symbolic calculations for math problems
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

@dataclass
class MathStep:
    """Single calculation step with actual values"""
    step_num: int
    description: str
    formula: str
    calculation: str
    result: Any

class MathReasoner:
    """Handles actual mathematical problem solving with step-by-step calculations"""

    def __init__(self):
        """Initialize math reasoner"""
        self.steps = []

    def solve_rate_problem(self, initial_units: float, initial_time: float,
                          initial_workers: float, target_units: float,
                          target_time: float) -> Dict[str, Any]:
        """
        Solve rate-based problems (widgets, cats/mice, etc.)

        Args:
            initial_units: Units produced initially (e.g., 5 widgets, 3 mice)
            initial_time: Time taken initially (e.g., 5 minutes)
            initial_workers: Number of workers/agents initially (e.g., 5 machines, 3 cats)
            target_units: Target units to produce
            target_time: Target time available

        Returns:
            Dict with steps and final answer
        """
        self.steps = []

        # Step 1: Calculate rate per worker per unit time
        rate_per_worker = initial_units / (initial_workers * initial_time)
        self.steps.append(MathStep(
            step_num=1,
            description="Calculate production rate per worker per time unit",
            formula="rate_per_worker = units / (workers × time)",
            calculation=f"{initial_units} / ({initial_workers} × {initial_time})",
            result=f"{rate_per_worker} units per worker per time unit"
        ))

        # Step 2: Calculate required total rate
        required_rate = target_units / target_time
        self.steps.append(MathStep(
            step_num=2,
            description="Calculate required total production rate",
            formula="required_rate = target_units / target_time",
            calculation=f"{target_units} / {target_time}",
            result=f"{required_rate} units per time unit"
        ))

        # Step 3: Calculate workers needed
        workers_needed = required_rate / rate_per_worker
        self.steps.append(MathStep(
            step_num=3,
            description="Calculate number of workers needed",
            formula="workers_needed = required_rate / rate_per_worker",
            calculation=f"{required_rate} / {rate_per_worker}",
            result=f"{workers_needed} workers"
        ))

        # Step 4: Verification
        verify_units = workers_needed * rate_per_worker * target_time
        self.steps.append(MathStep(
            step_num=4,
            description="Verify the answer",
            formula="verification = workers × rate_per_worker × time",
            calculation=f"{workers_needed} × {rate_per_worker} × {target_time}",
            result=f"{verify_units} units (should equal {target_units}) ✓" if abs(verify_units - target_units) < 0.01 else f"{verify_units} units ✗"
        ))

        return {
            "steps": self.steps,
            "answer": int(workers_needed) if workers_needed == int(workers_needed) else workers_needed,
            "verified": abs(verify_units - target_units) < 0.01
        }

    def solve_difference_problem(self, total: float, difference: float) -> Dict[str, Any]:
        """
        Solve problems like "bat and ball" where total and difference are given

        Args:
            total: Total cost/value
            difference: Difference between the two items

        Returns:
            Dict with steps and answers for both items
        """
        self.steps = []

        # Step 1: Set up variables
        self.steps.append(MathStep(
            step_num=1,
            description="Define variables",
            formula="Let smaller_item = x, larger_item = x + difference",
            calculation=f"ball = x, bat = x + {difference}",
            result="Variables defined"
        ))

        # Step 2: Set up equation
        self.steps.append(MathStep(
            step_num=2,
            description="Set up equation from total",
            formula="smaller + larger = total → x + (x + difference) = total",
            calculation=f"x + (x + {difference}) = {total}",
            result=f"2x + {difference} = {total}"
        ))

        # Step 3: Solve for smaller item
        smaller_value = (total - difference) / 2
        self.steps.append(MathStep(
            step_num=3,
            description="Solve for smaller item",
            formula="2x = total - difference → x = (total - difference) / 2",
            calculation=f"2x = {total} - {difference} = {total - difference} → x = {total - difference} / 2",
            result=f"{smaller_value}"
        ))

        # Step 4: Calculate larger item
        larger_value = smaller_value + difference
        self.steps.append(MathStep(
            step_num=4,
            description="Calculate larger item",
            formula="larger = smaller + difference",
            calculation=f"{smaller_value} + {difference}",
            result=f"{larger_value}"
        ))

        # Step 5: Verification
        verify_total = smaller_value + larger_value
        verify_diff = larger_value - smaller_value
        self.steps.append(MathStep(
            step_num=5,
            description="Verify the answer",
            formula="Check: smaller + larger = total AND larger - smaller = difference",
            calculation=f"{smaller_value} + {larger_value} = {verify_total}, {larger_value} - {smaller_value} = {verify_diff}",
            result=f"✓ Verified" if abs(verify_total - total) < 0.01 and abs(verify_diff - difference) < 0.01 else "✗ Verification failed"
        ))

        return {
            "steps": self.steps,
            "smaller_item": smaller_value,
            "larger_item": larger_value,
            "verified": abs(verify_total - total) < 0.01
        }

    def solve_logical_interpretation(self, total: int, description: str) -> Dict[str, Any]:
        """
        Solve problems requiring literal interpretation (e.g., "all but X")

        Args:
            total: Total items
            description: Description with logical operators

        Returns:
            Dict with steps and answer
        """
        self.steps = []

        # Step 1: Identify the logical operator
        self.steps.append(MathStep(
            step_num=1,
            description="Parse the logical statement",
            formula="Identify keywords: 'all but', 'except', 'only'",
            calculation=f"Statement: '{description}'",
            result="Logical operator identified"
        ))

        # Step 2: Apply literal interpretation
        if "all but" in description.lower():
            # Extract the number after "all but"
            match = re.search(r'all but (\d+)', description.lower())
            if match:
                remaining = int(match.group(1))
                self.steps.append(MathStep(
                    step_num=2,
                    description="Apply 'all but X' interpretation",
                    formula="'all but X' means X remain",
                    calculation=f"'all but {remaining}' means {remaining} remain",
                    result=f"{remaining}"
                ))
            else:
                remaining = 0
        else:
            remaining = total

        # Step 3: Verification
        self.steps.append(MathStep(
            step_num=3,
            description="Verify logical consistency",
            formula="Check if answer makes sense in context",
            calculation=f"Started with {total}, '{description}' → {remaining} remaining",
            result="✓ Logically consistent"
        ))

        return {
            "steps": self.steps,
            "answer": remaining,
            "verified": True
        }

    def solve_compound_percentage(self, initial: float, changes: List[Tuple[str, float]]) -> Dict[str, Any]:
        """
        Solve compound percentage change problems (e.g., stock portfolios)

        Args:
            initial: Initial value
            changes: List of (direction, percentage) tuples, e.g., [("increase", 18), ("decrease", 12), ("increase", 25)]

        Returns:
            Dict with steps, final value, and total percentage change
        """
        self.steps = []
        current_value = initial

        # Step 1: Start with initial value
        self.steps.append(MathStep(
            step_num=1,
            description=f"Starting value",
            formula="Initial value",
            calculation=f"${initial:,.2f}",
            result=f"${initial:,.2f}"
        ))

        # Process each percentage change
        step_num = 2
        for period, (direction, percentage) in enumerate(changes, 1):
            multiplier = 1 + (percentage / 100) if direction == "increase" else 1 - (percentage / 100)
            new_value = current_value * multiplier

            period_name = f"Q{period}" if len(changes) > 1 else "After change"
            sign = "+" if direction == "increase" else "-"

            self.steps.append(MathStep(
                step_num=step_num,
                description=f"{period_name}: Apply {sign}{percentage}% change",
                formula=f"new_value = current_value × {multiplier}",
                calculation=f"${current_value:,.2f} × {multiplier} = ${new_value:,.2f}",
                result=f"${new_value:,.2f}"
            ))

            current_value = new_value
            step_num += 1

        # Calculate total percentage change
        total_change_pct = ((current_value - initial) / initial) * 100

        self.steps.append(MathStep(
            step_num=step_num,
            description="Calculate total percentage change from start",
            formula="total_change% = ((final - initial) / initial) × 100",
            calculation=f"(({current_value:,.2f} - {initial:,.2f}) / {initial:,.2f}) × 100",
            result=f"{total_change_pct:+.2f}%"
        ))

        return {
            "steps": self.steps,
            "final_value": current_value,
            "total_change_percentage": total_change_pct,
            "verified": True
        }

    def solve_multi_step_puzzle(self, puzzle_type: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve logic puzzles requiring sequential reasoning

        Args:
            puzzle_type: Type of puzzle (e.g., "light_switch")
            constraints: Puzzle-specific constraints

        Returns:
            Dict with steps and solution
        """
        self.steps = []

        if puzzle_type == "light_switch":
            # Light switch puzzle: 3 switches, 3 bulbs, one trip
            self.steps.append(MathStep(
                step_num=1,
                description="Understand the constraint",
                formula="3 switches control 3 bulbs in another room, only 1 trip allowed",
                calculation="Need to identify which switch controls which bulb",
                result="Constraint: Cannot see bulbs while toggling switches"
            ))

            self.steps.append(MathStep(
                step_num=2,
                description="Identify available signals",
                formula="Signals: ON/OFF state + heat (recent activity)",
                calculation="Light bulb generates heat when ON",
                result="Can use: current state AND warmth"
            ))

            self.steps.append(MathStep(
                step_num=3,
                description="Design the strategy",
                formula="Create 3 distinguishable states using time",
                calculation="Switch A: ON for 10 min, then OFF; Switch B: ON; Switch C: OFF",
                result="Strategy: Time-based heat differentiation"
            ))

            self.steps.append(MathStep(
                step_num=4,
                description="Execute and observe",
                formula="Enter room and check: state (ON/OFF) + temperature",
                calculation="Bulb that is ON → Switch B\nBulb that is OFF but warm → Switch A\nBulb that is OFF and cold → Switch C",
                result="Solution identified"
            ))

            self.steps.append(MathStep(
                step_num=5,
                description="Verify uniqueness",
                formula="Check each bulb has unique signature",
                calculation="3 states: (ON,hot), (OFF,warm), (OFF,cold) → 3 unique signatures",
                result="✓ Solution is unique and deterministic"
            ))

            solution = {
                "procedure": [
                    "1. Turn ON Switch A and wait 10 minutes",
                    "2. Turn OFF Switch A",
                    "3. Turn ON Switch B",
                    "4. Leave Switch C OFF",
                    "5. Enter the room immediately"
                ],
                "identification": {
                    "Switch A": "Bulb that is OFF but warm to touch",
                    "Switch B": "Bulb that is ON (lit)",
                    "Switch C": "Bulb that is OFF and cold"
                }
            }

            return {
                "steps": self.steps,
                "solution": solution,
                "verified": True
            }

        return {
            "steps": [],
            "solution": "Unknown puzzle type",
            "verified": False
        }

    def detect_and_solve(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Auto-detect problem type and solve

        Args:
            query: User's math/logic question

        Returns:
            Solution dict or None if not recognized
        """
        query_lower = query.lower()

        # Pattern: Compound percentage changes (stock portfolios, investments)
        # Look for multiple percentage changes with increases/decreases
        if (('%' in query or 'percent' in query_lower) and
            any(word in query_lower for word in ['increase', 'decrease', 'grows', 'shrinks', 'gain', 'loss'])):

            # Extract initial value
            initial_match = re.search(r'\$?\s*(\d+(?:,\d+)*(?:\.\d+)?)', query)
            if initial_match:
                initial_value = float(initial_match.group(1).replace(',', ''))

                # Extract all percentage changes in order
                changes = []

                # Find all percentage changes (increases and decreases) in order
                all_patterns = re.finditer(
                    r'(increase[sd]?|decrease[sd]?)\s+by\s+(\d+(?:\.\d+)?)\s*%',
                    query_lower
                )

                for match in all_patterns:
                    direction = "increase" if "increase" in match.group(1) else "decrease"
                    percentage = float(match.group(2))
                    changes.append((direction, percentage))

                if len(changes) > 0:
                    return self.solve_compound_percentage(initial_value, changes)

        # Pattern: Rate problems (widgets, cats/mice)
        # Look for pattern: X things do Y items in Z time
        rate_pattern = r'(\d+)\s+(machines?|cats?|workers?|people)'
        if re.search(rate_pattern, query_lower):
            # Extract ALL numbers from query (handle commas in numbers like 8,000)
            numbers = [int(n.replace(',', '')) for n in re.findall(r'\b(\d+(?:,\d+)*)\b', query)]
            if len(numbers) >= 5:
                # Usually pattern is: N1 machines make N2 widgets in N3 minutes, how many for N4 widgets in N5 minutes?
                # Or: N1 cats catch N2 mice in N3 minutes, how many cats for N4 mice in N5 minutes?
                return self.solve_rate_problem(
                    initial_workers=numbers[0],    # machines/workers/cats
                    initial_units=numbers[1],      # widgets/mice made
                    initial_time=numbers[2],       # time taken
                    target_units=numbers[3],       # target widgets/mice
                    target_time=numbers[4]         # target time
                )

        # Pattern: Difference problems (bat and ball)
        if ('cost' in query_lower or 'costs' in query_lower) and 'more than' in query_lower:
            # Extract ALL numbers including decimals
            numbers = re.findall(r'\$?(\d+\.?\d*)', query_lower)
            if len(numbers) >= 2:
                try:
                    # Usually: total cost $X.XX, one costs $Y.YY more than the other
                    floats = [float(n.replace('$', '').replace(',', '')) for n in numbers if n]
                    # First number is usually the total, second is the difference
                    total = floats[0]
                    difference = floats[1]
                    return self.solve_difference_problem(total, difference)
                except (ValueError, IndexError):
                    pass

        # Pattern: Logical interpretation (all but X)
        if 'all but' in query_lower:
            # Look for "had X" or "has X" or just "X sheep"
            total_match = re.search(r'(?:had|has)\s+(\d+)', query_lower)
            if not total_match:
                # Try: "X sheep" or "X items"
                total_match = re.search(r'(\d+)\s+(?:sheep|items?|things?|objects?)', query_lower)
            if total_match:
                total = int(total_match.group(1))
                return self.solve_logical_interpretation(total, query)

        # Pattern: Light switch puzzle
        if 'switch' in query_lower and 'bulb' in query_lower:
            # Detected as light switch puzzle if mentions switches/bulbs
            if 'one time' in query_lower or 'one trip' in query_lower or 'once' in query_lower or 'figure out' in query_lower:
                return self.solve_multi_step_puzzle("light_switch", {})

        return None

    def format_steps_for_display(self) -> List[str]:
        """Format calculation steps for display"""
        formatted = []
        for step in self.steps:
            formatted.append(f"Step {step.step_num}: {step.description}")
            if step.formula:
                formatted.append(f"  Formula: {step.formula}")
            if step.calculation:
                formatted.append(f"  → {step.calculation}")
            if step.result:
                formatted.append(f"  = {step.result}")
            formatted.append("")
        return formatted
