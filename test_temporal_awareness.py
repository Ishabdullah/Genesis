#!/usr/bin/env python3
"""
Genesis Temporal Awareness Test Suite
Tests for time-based fallback, temporal detection, and web search
"""

import sys
import time
from time_sync import TimeSync, get_time_sync
from reasoning import ReasoningEngine
from websearch import WebSearch


class TemporalTests:
    """Test suite for temporal awareness features"""

    def __init__(self):
        """Initialize test suite"""
        self.time_sync = TimeSync()
        self.reasoning = ReasoningEngine()
        self.reasoning.set_time_sync(self.time_sync)
        self.websearch = WebSearch()
        self.passed = 0
        self.failed = 0

    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        color = "\033[92m" if passed else "\033[91m"
        reset = "\033[0m"

        print(f"{color}{status}{reset} - {test_name}")
        if message:
            print(f"      {message}")

        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def test_time_sync_basic(self):
        """Test basic time synchronization"""
        print("\n=== Test 1: Time Sync Basic Functionality ===")

        # Test device time retrieval
        current_time = self.time_sync.get_device_time()
        self.log_test(
            "Device time retrieval",
            current_time is not None and len(current_time) > 0,
            f"Time: {current_time}"
        )

        # Test date retrieval
        current_date = self.time_sync.get_device_date()
        self.log_test(
            "Device date retrieval",
            current_date is not None and len(current_date) == 10,
            f"Date: {current_date}"
        )

        # Test knowledge cutoff check
        is_post_cutoff = self.time_sync.is_after_knowledge_cutoff()
        self.log_test(
            "Knowledge cutoff detection",
            is_post_cutoff == True,  # Should be true in 2025
            f"Post-cutoff: {is_post_cutoff}"
        )

    def test_temporal_query_detection(self):
        """Test temporal query detection"""
        print("\n=== Test 2: Temporal Query Detection ===")

        test_queries = [
            ("Who is the president right now?", True, "Current event query"),
            ("What is the latest AI breakthrough?", True, "Latest/recent query"),
            ("What are emerging AI safety researchers in 2025?", True, "Emerging/2025 query"),
            ("What is 2 + 2?", False, "Math query (not temporal)"),
            ("Explain Python decorators", False, "Conceptual query (not temporal)")
        ]

        for query, expected_temporal, description in test_queries:
            analysis = self.reasoning.detect_temporal_uncertainty(query)
            is_temporal = analysis.get("time_sensitive", False)

            self.log_test(
                f"'{description}'",
                is_temporal == expected_temporal,
                f"Expected: {expected_temporal}, Got: {is_temporal}"
            )

    def test_query_classification(self):
        """Test query classification with metadata"""
        print("\n=== Test 3: Query Classification ===")

        test_queries = [
            ("Who is the current president?", "web_research"),
            ("What's the most recently discovered exoplanet?", "web_research"),
            ("Calculate 15 * 23", "math_logic"),
            ("Write a Python function to reverse a string", "code_generation")
        ]

        for query, expected_type in test_queries:
            result = self.reasoning.classify_query(query)
            if len(result) == 3:
                query_type, confidence, metadata = result
            else:
                query_type, confidence = result
                metadata = {}

            self.log_test(
                f"Classification: '{query[:40]}...'",
                query_type == expected_type,
                f"Expected: {expected_type}, Got: {query_type} (confidence: {confidence:.2f})"
            )

    def test_websearch_functionality(self):
        """Test web search module"""
        print("\n=== Test 4: WebSearch Functionality ===")

        # Test cache
        cache_test = self.websearch.cache.get("test_query_nonexistent")
        self.log_test(
            "Cache returns None for non-existent query",
            cache_test is None,
            "Cache working correctly"
        )

        # Test search (simple query)
        print("   Testing live web search (may take 10-15 seconds)...")
        try:
            success, answer, confidence = self.websearch.search(
                "Python programming language",
                use_cache=False
            )

            self.log_test(
                "WebSearch returns result",
                success == True,
                f"Confidence: {confidence:.2f}"
            )

            self.log_test(
                "WebSearch answer is non-empty",
                len(answer) > 0,
                f"Answer length: {len(answer)} chars"
            )

        except Exception as e:
            self.log_test(
                "WebSearch execution",
                False,
                f"Error: {e}"
            )

    def test_temporal_metadata(self):
        """Test temporal metadata generation"""
        print("\n=== Test 5: Temporal Metadata ===")

        metadata = self.time_sync.get_temporal_metadata()

        required_keys = [
            "current_datetime",
            "current_date",
            "timezone",
            "knowledge_cutoff",
            "is_post_cutoff"
        ]

        for key in required_keys:
            self.log_test(
                f"Metadata contains '{key}'",
                key in metadata,
                f"Value: {metadata.get(key)}"
            )

    def test_president_query(self):
        """Test the specific 'Who is the president?' query"""
        print("\n=== Test 6: President Query (Real-World Test) ===")

        query = "Who is the president of the United States right now?"

        # Check temporal detection
        analysis = self.reasoning.detect_temporal_uncertainty(query)

        self.log_test(
            "Query detected as time-sensitive",
            analysis.get("time_sensitive") == True,
            f"Temporal analysis: {analysis}"
        )

        self.log_test(
            "Should trigger fallback",
            analysis.get("should_trigger_fallback") == True,
            "Fallback will be triggered for live data"
        )

    def test_time_difference_calculation(self):
        """Test time difference calculations"""
        print("\n=== Test 7: Time Difference Calculations ===")

        # Create a timestamp from 2 hours ago
        import datetime
        past = datetime.datetime.now() - datetime.timedelta(hours=2)
        past_iso = past.isoformat()

        diff = self.time_sync.get_time_difference(past_iso)

        self.log_test(
            "Time difference calculated",
            "hours" in diff,
            f"Hours ago: {diff.get('hours', 0):.1f}"
        )

        self.log_test(
            "Staleness detection works",
            diff.get("is_stale") == True,  # >1 hour is stale
            f"Is stale: {diff.get('is_stale')}"
        )

    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*60)
        print("Genesis Temporal Awareness Test Suite")
        print("="*60)

        self.test_time_sync_basic()
        self.test_temporal_query_detection()
        self.test_query_classification()
        self.test_temporal_metadata()
        self.test_president_query()
        self.test_time_difference_calculation()

        # Optional: Only run if network available
        print("\n=== Optional Network Tests ===")
        print("(These tests require internet connection)")
        user_input = input("Run network tests? (y/n): ").lower()
        if user_input == 'y':
            self.test_websearch_functionality()

        # Summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        total = self.passed + self.failed
        if total > 0:
            success_rate = (self.passed / total) * 100
            print(f"Success Rate: {success_rate:.1f}%")

        if self.failed == 0:
            print("\n✓ All tests passed! Genesis temporal awareness is working correctly.")
        else:
            print(f"\n⚠ {self.failed} test(s) failed. Please review the output above.")

        return self.failed == 0


if __name__ == "__main__":
    tests = TemporalTests()
    success = tests.run_all_tests()
    sys.exit(0 if success else 1)
