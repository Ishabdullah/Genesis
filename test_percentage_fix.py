#!/usr/bin/env python3
"""
Quick test to verify the percentage problem solver works correctly
"""

from math_reasoner import MathReasoner

def test_stock_portfolio():
    """Test the exact user's query"""
    reasoner = MathReasoner()

    # User's query: $15,000 increases by 18%, decreases by 12%, increases by 25%
    query = "A stock portfolio worth $15,000 increases by 18% in Q1, then decreases by 12% in Q2, and finally increases by 25% in Q3. What is the final portfolio value and what is the total percentage change from the start?"

    solution = reasoner.detect_and_solve(query)

    if solution:
        print("✓ Query detected as percentage problem")
        print("\nSteps:")
        for step in solution['steps']:
            print(f"\nStep {step.step_num}: {step.description}")
            if step.calculation:
                print(f"  → {step.calculation}")
            if step.result:
                print(f"  = {step.result}")

        print(f"\n✓ Final value: ${solution['final_value']:,.2f}")
        print(f"✓ Total change: {solution['total_change_percentage']:+.2f}%")

        # Verify correctness
        expected_final = 19470.00
        expected_change = 29.80

        assert abs(solution['final_value'] - expected_final) < 0.01, f"Final value incorrect: {solution['final_value']} != {expected_final}"
        assert abs(solution['total_change_percentage'] - expected_change) < 0.01, f"Total change incorrect: {solution['total_change_percentage']} != {expected_change}"

        print("\n✅ All assertions passed!")
        return True
    else:
        print("✗ Query NOT detected as percentage problem - FAILURE!")
        return False

if __name__ == "__main__":
    print("Testing percentage problem solver fix...\n")
    success = test_stock_portfolio()

    if success:
        print("\n" + "="*60)
        print("✅ TEST PASSED - Fix is working correctly!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ TEST FAILED - Fix needs more work")
        print("="*60)
        exit(1)
