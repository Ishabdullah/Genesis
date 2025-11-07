#!/usr/bin/env python3
"""
Test script to verify #correct and #incorrect command parsing
"""

def test_feedback_parsing():
    """Test the feedback command parsing logic"""

    test_cases = [
        "#correct",
        "#incorrect",
        "#correct - good answer",
        "#incorrect - wrong date",
        "#correct — excellent response",
        "#CORRECT",
        "#InCoRrEcT"
    ]

    for user_input in test_cases:
        print(f"\nTesting: '{user_input}'")
        print(f"  Lowercased: '{user_input.lower()}'")
        print(f"  Starts with #correct: {user_input.lower().startswith('#correct')}")
        print(f"  Starts with #incorrect: {user_input.lower().startswith('#incorrect')}")

        # Simulate the parsing logic
        if user_input.lower().startswith("#correct") or user_input.lower().startswith("#incorrect"):
            parts = user_input.split("—", 1) if "—" in user_input else user_input.split(" - ", 1)
            feedback_type = parts[0].strip().lower()
            note = parts[1].strip() if len(parts) > 1 else None
            is_correct = (feedback_type == "#correct")

            print(f"  ✓ MATCHED as feedback command")
            print(f"    feedback_type: '{feedback_type}'")
            print(f"    is_correct: {is_correct}")
            print(f"    note: {note}")
        else:
            print(f"  ✗ NOT MATCHED")

if __name__ == "__main__":
    test_feedback_parsing()
