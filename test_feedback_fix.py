#!/usr/bin/env python3
"""
Test the fixed feedback command parsing logic
"""

def test_feedback_commands():
    """Test all feedback command variations"""

    test_cases = [
        # Valid commands without notes
        ("#correct", True, None),
        ("#incorrect", False, None),
        ("#CORRECT", True, None),
        ("#InCoRrEcT", False, None),

        # Valid commands with notes (space-dash-space separator)
        ("#correct - good answer", True, "good answer"),
        ("#incorrect - wrong date", False, "wrong date"),
        ("#correct - excellent work!", True, "excellent work!"),

        # Valid commands with notes (em dash separator)
        ("#correct — perfect", True, "perfect"),
        ("#incorrect — needs improvement", False, "needs improvement"),

        # Valid commands with notes (hyphen separator)
        ("#correct-note here", True, "note here"),
        ("#incorrect-bad response", False, "bad response"),

        # Invalid - not feedback commands
        ("Is this #correct?", None, None),
        ("What does #incorrect mean?", None, None),
        ("correct", None, None),
        ("incorrect", None, None),
    ]

    print("Testing feedback command parsing:\n")

    for user_input, expected_is_correct, expected_note in test_cases:
        print(f"Input: '{user_input}'")

        # Replicate the logic from genesis.py
        user_input_lower = user_input.lower().strip()

        # Handle #correct and #incorrect feedback commands
        if user_input_lower == "#correct" or user_input_lower.startswith("#correct ") or user_input_lower.startswith("#correct-") or user_input_lower.startswith("#correct—"):
            is_correct = True
        elif user_input_lower == "#incorrect" or user_input_lower.startswith("#incorrect ") or user_input_lower.startswith("#incorrect-") or user_input_lower.startswith("#incorrect—"):
            is_correct = False
        else:
            is_correct = None  # Not a feedback command

        if is_correct is not None:
            # Parse note (support —, " - ", and - separators)
            if "—" in user_input:
                parts = user_input.split("—", 1)
            elif " - " in user_input:
                parts = user_input.split(" - ", 1)
            else:
                # Try splitting on first - after the command
                parts = user_input.split("-", 1)
            note = parts[1].strip() if len(parts) > 1 else None

            print(f"  ✓ Detected as feedback command")
            print(f"  is_correct: {is_correct} (expected: {expected_is_correct})")
            print(f"  note: '{note}' (expected: '{expected_note}')")

            # Verify
            if is_correct == expected_is_correct and note == expected_note:
                print(f"  ✅ PASS")
            else:
                print(f"  ❌ FAIL")
        else:
            print(f"  Not a feedback command (expected: {expected_is_correct})")
            if expected_is_correct is None:
                print(f"  ✅ PASS")
            else:
                print(f"  ❌ FAIL - should have been detected!")

        print()

if __name__ == "__main__":
    test_feedback_commands()
