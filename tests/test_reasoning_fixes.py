#!/usr/bin/env python3
"""
Genesis Reasoning Fixes Test Suite
Tests the four logic puzzles and math problem-solving accuracy
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from math_reasoner import MathReasoner
from reasoning import ReasoningEngine

def test_widgets_problem():
    """Test: 5 machines make 5 widgets in 5 minutes, how many for 100 widgets in 100 minutes?"""
    print("\n" + "="*60)
    print("TEST 1: Widgets Problem (Rate Calculation)")
    print("="*60)

    query = "If 5 machines can make 5 widgets in 5 minutes, how many machines are needed to make 100 widgets in 100 minutes?"

    reasoner = MathReasoner()
    solution = reasoner.detect_and_solve(query)

    print(f"\nQuery: {query}")
    print("\nReasoning Steps:")
    for line in reasoner.format_steps_for_display():
        print(line)

    expected_answer = 5
    actual_answer = solution.get('answer') if solution else None

    print(f"\nExpected Answer: {expected_answer} machines")
    print(f"Actual Answer: {actual_answer} machines")

    assert actual_answer == expected_answer, f"FAIL: Expected {expected_answer}, got {actual_answer}"
    assert solution.get('verified') == True, "FAIL: Answer not verified"

    print("\n✅ TEST 1 PASSED")
    return True

def test_sheep_problem():
    """Test: Farmer has 17 sheep, all but 9 run away, how many left?"""
    print("\n" + "="*60)
    print("TEST 2: Sheep Problem (Logical Interpretation)")
    print("="*60)

    query = "A farmer has 17 sheep and all but 9 run away. How many are left?"

    reasoner = MathReasoner()
    solution = reasoner.detect_and_solve(query)

    print(f"\nQuery: {query}")
    print("\nReasoning Steps:")
    for line in reasoner.format_steps_for_display():
        print(line)

    expected_answer = 9
    actual_answer = solution.get('answer') if solution else None

    print(f"\nExpected Answer: {expected_answer} sheep")
    print(f"Actual Answer: {actual_answer} sheep")

    assert actual_answer == expected_answer, f"FAIL: Expected {expected_answer}, got {actual_answer}"

    print("\n✅ TEST 2 PASSED")
    return True

def test_bat_and_ball():
    """Test: Bat and ball cost $1.10, bat costs $1 more than ball, how much is ball?"""
    print("\n" + "="*60)
    print("TEST 3: Bat and Ball Problem (Difference Equation)")
    print("="*60)

    query = "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?"

    reasoner = MathReasoner()
    solution = reasoner.detect_and_solve(query)

    print(f"\nQuery: {query}")
    print("\nReasoning Steps:")
    for line in reasoner.format_steps_for_display():
        print(line)

    expected_answer = 0.05
    actual_answer = solution.get('smaller_item') if solution else None

    print(f"\nExpected Answer: ${expected_answer:.2f}")
    print(f"Actual Answer: ${actual_answer:.2f}" if actual_answer else "None")

    assert abs(actual_answer - expected_answer) < 0.01, f"FAIL: Expected ${expected_answer:.2f}, got ${actual_answer:.2f}"
    assert solution.get('verified') == True, "FAIL: Answer not verified"

    print("\n✅ TEST 3 PASSED")
    return True

def test_light_switch_puzzle():
    """Test: 3 switches, 3 bulbs, one trip to identify which controls which"""
    print("\n" + "="*60)
    print("TEST 4: Light Switch Puzzle (Sequential Logic)")
    print("="*60)

    query = "You have 3 light switches outside a room and 3 light bulbs inside. Each switch controls one bulb. You can only enter the room one time. How do you figure out which switch controls which bulb?"

    reasoner = MathReasoner()
    solution = reasoner.detect_and_solve(query)

    print(f"\nQuery: {query}")
    print("\nReasoning Steps:")
    for line in reasoner.format_steps_for_display():
        print(line)

    print("\nSolution:")
    if solution and 'solution' in solution:
        sol = solution['solution']
        if isinstance(sol, dict):
            if 'procedure' in sol:
                print("\nProcedure:")
                for step in sol['procedure']:
                    print(f"  {step}")
            if 'identification' in sol:
                print("\nIdentification:")
                for switch, bulb in sol['identification'].items():
                    print(f"  {switch}: {bulb}")

    assert solution is not None, "FAIL: No solution found"
    assert solution.get('verified') == True, "FAIL: Solution not verified"
    assert 'procedure' in solution.get('solution', {}), "FAIL: No procedure in solution"

    print("\n✅ TEST 4 PASSED")
    return True

def test_retry_functionality():
    """Test: Retry mechanism works correctly"""
    print("\n" + "="*60)
    print("TEST 5: Retry Functionality")
    print("="*60)

    # This would need to be tested in the full Genesis system
    # For now, just verify the reasoning engine can generate traces multiple times

    reasoning_engine = ReasoningEngine()

    query = "If 3 cats catch 3 mice in 3 minutes, how many cats do you need to catch 100 mice in 100 minutes?"

    # First attempt
    print("\n--- First Attempt ---")
    steps1 = reasoning_engine.generate_reasoning_trace(query, "math_word_problem")
    answer1 = reasoning_engine.get_calculated_answer()
    print(f"Answer: {answer1}")

    # Retry (should produce same result)
    print("\n--- Retry ---")
    steps2 = reasoning_engine.generate_reasoning_trace(query, "math_word_problem")
    answer2 = reasoning_engine.get_calculated_answer()
    print(f"Answer: {answer2}")

    assert answer1 == answer2, f"FAIL: Retry produced different answer: {answer1} vs {answer2}"
    assert answer1 == "3", f"FAIL: Expected 3, got {answer1}"

    print("\n✅ TEST 5 PASSED")
    return True

def test_metacognitive_reasoning():
    """Test: Metacognitive reasoning template applies correctly"""
    print("\n" + "="*60)
    print("TEST 6: Metacognitive Reasoning Template")
    print("="*60)

    reasoning_engine = ReasoningEngine()

    # Test feedback query
    query = "#incorrect — wrong calculation in step 3"
    problem_type = reasoning_engine.detect_problem_type(query)

    print(f"\nQuery: {query}")
    print(f"Detected Problem Type: {problem_type}")

    assert problem_type == "metacognitive", f"FAIL: Expected 'metacognitive', got '{problem_type}'"

    steps = reasoning_engine.generate_reasoning_trace(query, problem_type)

    print("\nReasoning Steps:")
    for step in steps:
        print(f"  Step {step.step_num}: {step.description}")

    assert len(steps) == 4, f"FAIL: Expected 4 steps, got {len(steps)}"
    assert "feedback" in steps[0].description.lower() or "meta" in steps[0].description.lower(), \
        "FAIL: First step should address feedback"

    print("\n✅ TEST 6 PASSED")
    return True

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("GENESIS REASONING FIXES - TEST SUITE")
    print("="*60)

    tests = [
        ("Widgets Problem", test_widgets_problem),
        ("Sheep Problem", test_sheep_problem),
        ("Bat and Ball Problem", test_bat_and_ball),
        ("Light Switch Puzzle", test_light_switch_puzzle),
        ("Retry Functionality", test_retry_functionality),
        ("Metacognitive Reasoning", test_metacognitive_reasoning)
    ]

    passed = 0
    failed = 0
    errors = []

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            failed += 1
            errors.append((test_name, str(e)))
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   {str(e)}")
        except Exception as e:
            failed += 1
            errors.append((test_name, f"ERROR: {str(e)}"))
            print(f"\n💥 TEST ERROR: {test_name}")
            print(f"   {str(e)}")

    # Final summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    print(f"\nTotal Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    if errors:
        print("\nFailed Tests:")
        for test_name, error_msg in errors:
            print(f"  - {test_name}: {error_msg}")

    print("\n" + "="*60)

    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Genesis reasoning & retry fixes complete.")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - Review errors above")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
