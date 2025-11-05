#!/usr/bin/env python3
"""
Genesis Claude Fallback Test Suite
Tests uncertainty detection and fallback orchestration
"""

import sys
from uncertainty_detector import UncertaintyDetector
from claude_fallback import ClaudeFallback

def print_test_header(test_name):
    """Print test section header"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}\n")

def test_uncertainty_detection():
    """Test the uncertainty detector"""
    print_test_header("Uncertainty Detection")

    detector = UncertaintyDetector()

    test_cases = [
        {
            "name": "Confident Response",
            "response": "To calculate the factorial of a number, use this function:\n```python\ndef factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)\n```",
            "expected_uncertain": False
        },
        {
            "name": "Uncertain Language",
            "response": "I'm not sure about that, but maybe it could work this way...",
            "expected_uncertain": True
        },
        {
            "name": "Empty Response",
            "response": "",
            "expected_uncertain": True
        },
        {
            "name": "Very Short Response",
            "response": "Yes.",
            "expected_uncertain": True
        },
        {
            "name": "Direct Uncertainty",
            "response": "I don't know the answer to that question.",
            "expected_uncertain": True
        },
        {
            "name": "Incomplete Code",
            "response": "Here's the code:\n```python\n...\npass\n```",
            "expected_uncertain": True
        },
        {
            "name": "Repetitive Response",
            "response": "Yes yes yes yes yes yes yes yes yes yes yes yes",
            "expected_uncertain": True
        },
        {
            "name": "Error Response",
            "response": "An error occurred while processing your request. Syntax error detected.",
            "expected_uncertain": True
        }
    ]

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        should_fallback, analysis = detector.should_trigger_fallback(test["response"])

        status = "✓ PASS" if should_fallback == test["expected_uncertain"] else "✗ FAIL"
        if should_fallback == test["expected_uncertain"]:
            passed += 1
        else:
            failed += 1

        print(f"{i}. {test['name']}: {status}")
        print(f"   Response: {test['response'][:50]}{'...' if len(test['response']) > 50 else ''}")
        print(f"   Expected uncertain: {test['expected_uncertain']}")
        print(f"   Detected uncertain: {should_fallback}")
        print(f"   Confidence: {analysis['confidence_score']:.2f}")
        print(f"   Reason: {analysis['reason']}")
        print()

    print(f"Results: {passed}/{len(test_cases)} passed, {failed}/{len(test_cases)} failed\n")

    return failed == 0

def test_fallback_configuration():
    """Test Claude fallback configuration"""
    print_test_header("Fallback Configuration")

    fallback = ClaudeFallback()

    # Test 1: Enable/Disable
    print("1. Testing enable/disable...")
    fallback.disable()
    if not fallback.is_enabled():
        print("   ✓ Disable works")
    else:
        print("   ✗ Disable failed")
        return False

    fallback.enable()
    if fallback.is_enabled():
        print("   ✓ Enable works")
    else:
        print("   ✗ Enable failed")
        return False

    # Test 2: Statistics
    print("\n2. Testing statistics...")
    stats = fallback.get_fallback_stats()
    print(f"   ✓ Statistics retrieved: {stats}")

    # Test 3: Logging
    print("\n3. Testing logging...")
    try:
        fallback.log_fallback_event(
            "test prompt",
            "test local response",
            "test claude response",
            {"confidence_score": 0.3, "reason": "test"}
        )
        print("   ✓ Logging works")
    except Exception as e:
        print(f"   ✗ Logging failed: {e}")
        return False

    # Test 4: Retrain dataset
    print("\n4. Testing retrain dataset...")
    try:
        fallback.add_to_retrain_dataset(
            "test prompt",
            "test local",
            "test claude",
            {"confidence_score": 0.3, "reason": "test"}
        )
        print("   ✓ Retrain dataset works")
    except Exception as e:
        print(f"   ✗ Retrain dataset failed: {e}")
        return False

    print("\n✓ All configuration tests passed\n")
    return True

def test_end_to_end_workflow():
    """Test end-to-end fallback workflow"""
    print_test_header("End-to-End Workflow")

    detector = UncertaintyDetector()
    fallback = ClaudeFallback()

    # Enable fallback
    fallback.enable()

    # Simulate workflow
    user_prompt = "Explain quantum computing"
    local_response = "I'm not sure about the details of quantum computing."

    print(f"User Prompt: {user_prompt}")
    print(f"Local Response: {local_response}")
    print()

    # Step 1: Detect uncertainty
    should_fallback, analysis = detector.should_trigger_fallback(local_response)
    print(f"1. Uncertainty Detection:")
    print(f"   Should fallback: {should_fallback}")
    print(f"   Confidence: {analysis['confidence_score']:.2f}")
    print(f"   Reason: {analysis['reason']}")
    print()

    if should_fallback:
        # Step 2: Check if fallback is enabled
        if fallback.is_enabled():
            print("2. Fallback is enabled, would request Claude assist")
            print()

            # Step 3: Log event
            fallback.log_fallback_event(
                user_prompt,
                local_response,
                None,  # Claude response would be injected
                analysis
            )
            print("3. Event logged successfully")
            print()

            # Step 4: Check stats
            stats = fallback.get_fallback_stats()
            print(f"4. Updated stats: {stats['total_fallbacks']} total fallbacks")
            print()

            print("✓ End-to-end workflow completed successfully\n")
            return True
        else:
            print("✗ Fallback should be enabled but isn't")
            return False
    else:
        print("✗ Should have detected uncertainty but didn't")
        return False

def test_confidence_scoring():
    """Test confidence score calculations"""
    print_test_header("Confidence Scoring")

    detector = UncertaintyDetector()

    test_cases = [
        ("Perfect confident response with detailed code and explanation", 0.8, 1.0),
        ("I'm not sure about that", 0.0, 0.4),
        ("", 0.0, 0.2),
        ("Maybe possibly perhaps I think so", 0.0, 0.3),
    ]

    all_passed = True

    for i, (response, min_score, max_score) in enumerate(test_cases, 1):
        analysis = detector.analyze_response(response)
        score = analysis['confidence_score']

        if min_score <= score <= max_score:
            print(f"✓ Test {i}: Score {score:.2f} in range [{min_score}, {max_score}]")
        else:
            print(f"✗ Test {i}: Score {score:.2f} NOT in range [{min_score}, {max_score}]")
            all_passed = False

    print()
    return all_passed

def main():
    """Run all tests"""
    print("\n🧬 Genesis Claude Fallback Test Suite")
    print("=" * 60)

    results = {
        "Uncertainty Detection": test_uncertainty_detection(),
        "Fallback Configuration": test_fallback_configuration(),
        "Confidence Scoring": test_confidence_scoring(),
        "End-to-End Workflow": test_end_to_end_workflow()
    }

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60 + "\n")

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
