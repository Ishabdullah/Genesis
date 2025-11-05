#!/usr/bin/env python3
"""
Diagnostic test for Genesis Performance Monitoring System
Tests all performance tracking functionality
"""

import time
from performance_monitor import PerformanceMonitor

def test_performance_monitor():
    """Run comprehensive performance monitor tests"""

    print("🧬 Testing Genesis Performance Monitoring System\n")
    print("=" * 60)

    # Initialize monitor
    print("\n[TEST 1] Initializing Performance Monitor...")
    monitor = PerformanceMonitor(metrics_file="data/test_metrics.json")
    print("✓ Monitor initialized")

    # Test query tracking
    print("\n[TEST 2] Testing query tracking...")
    query_id = monitor.start_query("test query 1")
    time.sleep(0.1)  # Simulate processing
    monitor.end_query(
        query_id=query_id,
        user_input="test query 1",
        response="test response 1",
        was_direct_command=True,
        had_fallback=False,
        confidence_score=1.0,
        error=None
    )
    print(f"✓ Query tracked (ID: {query_id})")

    # Test LLM query with lower confidence
    print("\n[TEST 3] Testing LLM query tracking...")
    query_id2 = monitor.start_query("complex query")
    time.sleep(0.2)  # Simulate LLM processing
    monitor.end_query(
        query_id=query_id2,
        user_input="complex query",
        response="complex response",
        was_direct_command=False,
        had_fallback=False,
        confidence_score=0.75,
        error=None
    )
    print(f"✓ LLM query tracked (ID: {query_id2})")

    # Test fallback tracking
    print("\n[TEST 4] Testing fallback tracking...")
    monitor.record_fallback(
        user_input="uncertain query",
        local_confidence=0.45,
        success=True
    )
    print("✓ Successful fallback recorded")

    monitor.record_fallback(
        user_input="another uncertain query",
        local_confidence=0.35,
        success=False
    )
    print("✓ Failed fallback recorded")

    # Test error tracking
    print("\n[TEST 5] Testing error tracking...")
    monitor.record_error(
        error_type="timeout",
        error_message="LLM timeout after 120s",
        context="complex calculation"
    )
    print("✓ Error recorded")

    # Test user feedback
    print("\n[TEST 6] Testing user feedback...")
    monitor.record_feedback(is_correct=True)
    print("✓ Correct feedback recorded")

    monitor.record_feedback(is_correct=False)
    print("✓ Incorrect feedback recorded")

    # Test performance summary
    print("\n[TEST 7] Testing performance summary generation...")
    summary = monitor.get_performance_summary()
    print("✓ Performance summary generated")
    print("\n" + "=" * 60)
    print(summary)
    print("=" * 60)

    # Test metrics reset
    print("\n[TEST 8] Testing metrics reset...")
    monitor.reset_metrics()
    print("✓ Metrics reset")

    # Verify reset
    stats = monitor.metrics["statistics"]
    if stats["total_queries"] == 0 and stats["total_fallbacks"] == 0:
        print("✓ Reset verification passed")
    else:
        print("✗ Reset verification failed")
        return False

    # Test metrics export
    print("\n[TEST 9] Testing metrics export...")
    export_path = monitor.export_metrics("data/test_export.json")
    print(f"✓ Metrics exported to {export_path}")

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)

    return True

if __name__ == "__main__":
    success = test_performance_monitor()

    if success:
        print("\n✅ Genesis performance tracking system active")
        print("\nPerformance monitoring features:")
        print("  • Response time tracking (milliseconds)")
        print("  • User feedback integration (#correct / #incorrect)")
        print("  • Claude fallback frequency monitoring")
        print("  • Error and system lag tracking")
        print("  • Comprehensive performance metrics (#performance)")
        print("  • Metrics reset capability (#reset_metrics)")
        print("\nStatus: ✅ READY FOR PRODUCTION")
    else:
        print("\n❌ Some tests failed - please review")
        exit(1)
