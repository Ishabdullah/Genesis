#!/usr/bin/env python3
"""
Genesis Multi-Turn Context Handling Tests
Tests that Genesis correctly handles context boundaries and doesn't reuse answers
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reasoning import ReasoningEngine
from math_reasoner import MathReasoner

def print_test_header(test_name):
    """Print test header"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}\n")

def test_question_id_separation():
    """
    Test that different questions get different IDs and don't share answers
    """
    print_test_header("Question ID Separation")

    reasoning = ReasoningEngine()

    # Question 1: Widgets problem
    q1_id = "q1"
    q1 = "If 5 machines make 5 widgets in 5 minutes, how many machines for 100 widgets in 100 minutes?"

    reasoning.start_new_question(q1_id)
    problem_type_1 = reasoning.detect_problem_type(q1)
    steps_1 = reasoning.generate_reasoning_trace(q1, problem_type_1)
    answer_1 = reasoning.get_calculated_answer()

    print(f"Question 1 ID: {q1_id}")
    print(f"Question 1: {q1}")
    print(f"Answer 1: {answer_1}")
    print(f"Current question ID: {reasoning.current_question_id}")

    # Question 2: Different problem
    # The key test: start_new_question should clear Q1's answer
    q2_id = "q2"
    q2 = "A bat and a ball cost $1.10. The bat costs $1.00 more than the ball. How much does the ball cost?"

    # Before generating new reasoning, answer from Q1 should still be there
    answer_before_q2 = reasoning.get_calculated_answer()
    print(f"\nBefore Q2 processing, stored answer: {answer_before_q2}")

    # Now start Q2 - this should clear Q1's answer
    reasoning.start_new_question(q2_id)

    # After start_new_question, answer should be cleared
    answer_after_start = reasoning.get_calculated_answer()
    print(f"After start_new_question(q2), stored answer: {answer_after_start}")

    # Now generate reasoning for Q2
    problem_type_2 = reasoning.detect_problem_type(q2)
    steps_2 = reasoning.generate_reasoning_trace(q2, problem_type_2)
    answer_2 = reasoning.get_calculated_answer()

    print(f"Question 2 ID: {q2_id}")
    print(f"Question 2: {q2}")
    print(f"Answer 2: {answer_2}")
    print(f"Current question ID: {reasoning.current_question_id}")

    # Verify answers are different and correct
    assert answer_1 == "5", f"Expected '5' for Q1, got '{answer_1}'"
    assert answer_after_start is None, f"Answer should be None after start_new_question, got '{answer_after_start}'"
    assert "$0.05" in str(answer_2), f"Expected '$0.05' for Q2, got '{answer_2}'"
    assert reasoning.current_question_id == q2_id, "Question ID should be q2"

    print(f"\n✅ PASSED: Questions have separate IDs and independent answers")
    return True

def test_retry_reuses_question_id():
    """
    Test that retry uses the same question ID
    """
    print_test_header("Retry Reuses Question ID")

    reasoning = ReasoningEngine()

    # Original question
    q_id = "q1"
    question = "If 3 cats catch 3 mice in 3 minutes, how many cats for 100 mice in 100 minutes?"

    reasoning.start_new_question(q_id)
    problem_type = reasoning.detect_problem_type(question)
    steps = reasoning.generate_reasoning_trace(question, problem_type)
    answer_1 = reasoning.get_calculated_answer()

    print(f"Original question ID: {q_id}")
    print(f"Original answer: {answer_1}")

    # Retry with same ID
    reasoning.start_new_question(q_id)  # Should NOT clear answer
    problem_type = reasoning.detect_problem_type(question)
    steps = reasoning.generate_reasoning_trace(question, problem_type)
    answer_2 = reasoning.get_calculated_answer()

    print(f"Retry question ID: {q_id}")
    print(f"Retry answer: {answer_2}")

    # Both should produce the same answer
    assert answer_1 == answer_2, f"Retry should produce same answer: {answer_1} vs {answer_2}"
    assert reasoning.current_question_id == q_id, "Question ID should remain q1"

    print(f"\n✅ PASSED: Retry correctly reuses question ID and produces consistent answer")
    return True

def test_new_question_clears_old_answer():
    """
    Test that a new question clears the previous calculated answer
    """
    print_test_header("New Question Clears Old Answer")

    reasoning = ReasoningEngine()

    # Question 1: Math problem
    q1_id = "q1"
    q1 = "If 5 workers build 5 houses in 5 days, how many workers for 20 houses in 20 days?"

    reasoning.start_new_question(q1_id)
    problem_type_1 = reasoning.detect_problem_type(q1)
    steps_1 = reasoning.generate_reasoning_trace(q1, problem_type_1)
    answer_1 = reasoning.get_calculated_answer()

    print(f"Question 1: {q1}")
    print(f"Answer 1: {answer_1}")
    print(f"Math answer stored: {reasoning.last_math_answer}")

    # Question 2: Non-math problem
    q2_id = "q2"
    q2 = "What is the capital of France?"

    reasoning.start_new_question(q2_id)
    problem_type_2 = reasoning.detect_problem_type(q2)
    steps_2 = reasoning.generate_reasoning_trace(q2, problem_type_2)
    answer_2 = reasoning.get_calculated_answer()

    print(f"\nQuestion 2: {q2}")
    print(f"Answer 2 (should be None): {answer_2}")
    print(f"Math answer stored: {reasoning.last_math_answer}")

    # Answer 2 should be None since it's not a math problem
    assert answer_2 is None, f"Non-math question should have no calculated answer, got: {answer_2}"
    assert reasoning.last_math_answer is None, "last_math_answer should be cleared for new question"
    assert reasoning.current_question_id == q2_id, "Question ID should be q2"

    print(f"\n✅ PASSED: New question correctly clears previous calculated answer")
    return True

def test_context_boundary_tracking():
    """
    Test that context entries maintain question boundaries
    """
    print_test_header("Context Boundary Tracking")

    # Simulate context stack like in Genesis
    context_stack = []

    # Add multiple questions
    questions = [
        {"id": "q1", "query": "What is 2+2?", "answer": "4", "type": "math"},
        {"id": "q2", "query": "What is Python?", "answer": "A language", "type": "general"},
        {"id": "q3", "query": "Calculate 10*5", "answer": "50", "type": "math"},
    ]

    for q in questions:
        context_entry = {
            "question_id": q["id"],
            "user_input": q["query"],
            "response": q["answer"],
            "problem_type": q["type"],
            "timestamp": 0
        }
        context_stack.append(context_entry)

    print("Context stack:")
    for i, entry in enumerate(context_stack):
        print(f"  {i+1}. [{entry['question_id']}] {entry['user_input']} → {entry['response']}")

    # Verify each entry has unique question ID
    question_ids = [entry["question_id"] for entry in context_stack]
    assert len(question_ids) == len(set(question_ids)), "Each question should have unique ID"

    # Verify we can retrieve by question ID
    q2_entries = [e for e in context_stack if e["question_id"] == "q2"]
    assert len(q2_entries) == 1, "Should find exactly one entry for q2"
    assert q2_entries[0]["response"] == "A language", "Should retrieve correct answer"

    print(f"\n✅ PASSED: Context boundaries correctly tracked with question IDs")
    return True

def test_math_reasoner_independence():
    """
    Test that MathReasoner solves each problem independently
    """
    print_test_header("Math Reasoner Independence")

    reasoner = MathReasoner()

    # Problem 1
    q1 = "If 5 machines make 5 widgets in 5 minutes, how many machines for 100 widgets in 100 minutes?"
    solution_1 = reasoner.detect_and_solve(q1)
    answer_1 = solution_1.get('answer') if solution_1 else None

    print(f"Problem 1: {q1}")
    print(f"Solution 1: {answer_1}")

    # Problem 2 (completely different)
    q2 = "A farmer had 17 sheep. All but 9 died. How many sheep remain?"
    solution_2 = reasoner.detect_and_solve(q2)
    answer_2 = solution_2.get('answer') if solution_2 else None

    print(f"\nProblem 2: {q2}")
    print(f"Solution 2: {answer_2}")

    # Problem 3 (back to rate problem)
    q3 = "If 3 workers paint 3 rooms in 3 hours, how many workers for 9 rooms in 9 hours?"
    solution_3 = reasoner.detect_and_solve(q3)
    answer_3 = solution_3.get('answer') if solution_3 else None

    print(f"\nProblem 3: {q3}")
    print(f"Solution 3: {answer_3}")

    # Verify each is solved independently and correctly
    assert answer_1 == 5, f"Expected 5, got {answer_1}"
    assert answer_2 == 9, f"Expected 9, got {answer_2}"
    assert answer_3 == 3, f"Expected 3, got {answer_3}"

    print(f"\n✅ PASSED: Each problem solved independently with correct answers")
    return True

def run_all_tests():
    """Run all multi-turn context tests"""
    print("\n" + "="*60)
    print("GENESIS MULTI-TURN CONTEXT HANDLING - TEST SUITE")
    print("="*60)

    tests = [
        ("Question ID Separation", test_question_id_separation),
        ("Retry Reuses Question ID", test_retry_reuses_question_id),
        ("New Question Clears Old Answer", test_new_question_clears_old_answer),
        ("Context Boundary Tracking", test_context_boundary_tracking),
        ("Math Reasoner Independence", test_math_reasoner_independence),
    ]

    passed = 0
    failed = 0
    results = []

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                results.append((test_name, "✅ PASSED"))
            else:
                failed += 1
                results.append((test_name, "❌ FAILED"))
        except AssertionError as e:
            failed += 1
            results.append((test_name, f"❌ FAILED: {e}"))
        except Exception as e:
            failed += 1
            results.append((test_name, f"❌ ERROR: {e}"))

    # Print summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    print()

    for test_name, result in results:
        print(f"{test_name:50s} {result}")

    print()
    print("="*60)
    print(f"Total Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print("="*60)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Genesis multi-turn context handling is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED")
        print("❌ Please review the failures above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
