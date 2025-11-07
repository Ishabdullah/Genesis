#!/usr/bin/env python3
"""
test_accel_inference.py - Test Accelerated Inference Workflows

Tests device selection, inference execution, and fallback mechanisms
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from accel_manager import (
    AccelerationManager,
    assign_device,
    get_profile,
)


def test_device_assignment():
    """Test automatic device assignment logic"""
    print("\n" + "=" * 60)
    print("TEST 1: Device Assignment Logic")
    print("=" * 60)

    try:
        # Test with different model types
        test_cases = [
            ("models/test_int8.gguf", "INT8 model should prefer NPU or GPU"),
            ("models/test_q4.gguf", "Q4 model should prefer GPU or CPU"),
            ("models/test_fp16.gguf", "FP16 model should prefer GPU"),
            ("models/test_q5.gguf", "Q5 model should work on CPU"),
        ]

        for model_path, description in test_cases:
            device = assign_device(model_path, preferred="auto")
            print(f"  {Path(model_path).name:25s} → {device:4s} ({description})")

        # Test explicit preference
        device = assign_device("models/test.gguf", preferred="cpu")
        assert device == "cpu", "Explicit CPU preference should be respected"

        print("  ✓ Device assignment working correctly")
        return True, "Device assignment passed"

    except Exception as e:
        return False, f"Device assignment failed: {str(e)}"


def test_acceleration_manager():
    """Test AccelerationManager class"""
    print("\n" + "=" * 60)
    print("TEST 2: AccelerationManager Class")
    print("=" * 60)

    try:
        manager = AccelerationManager()

        # Get profile
        profile = manager.get_profile()
        print(f"  ✓ Profile loaded: {len(profile.ranked)} devices ranked")

        # Get status
        status = manager.get_status()
        print(f"  Battery: {status['battery_pct']}%")
        print(f"  Temperature: {status['cpu_temp_c']:.1f}°C")
        print(f"  Thermal state: {status['thermal_state']}")
        print(f"  Ranked devices: {' > '.join(status['ranked_devices'])}")

        assert status['battery_pct'] >= 0, "Battery should be non-negative"
        assert status['cpu_temp_c'] > 0, "Temperature should be positive"

        print("  ✓ AccelerationManager functional")
        return True, "AccelerationManager passed"

    except Exception as e:
        return False, f"AccelerationManager failed: {str(e)}"


def test_thermal_throttling():
    """Test thermal throttling detection"""
    print("\n" + "=" * 60)
    print("TEST 3: Thermal Throttling Detection")
    print("=" * 60)

    try:
        manager = AccelerationManager()
        status = manager.get_status()

        temp = status['cpu_temp_c']
        thermal_state = status['thermal_state']

        print(f"  Current temperature: {temp:.1f}°C")
        print(f"  Thermal state: {thermal_state}")

        if temp > 70:
            assert thermal_state == "hot", "Should detect hot state at high temp"
            print(f"  ✓ High temperature detected correctly")
        else:
            assert thermal_state == "normal", "Should be normal at safe temp"
            print(f"  ✓ Normal temperature detected correctly")

        return True, f"Thermal detection passed (temp: {temp:.1f}°C, state: {thermal_state})"

    except Exception as e:
        return False, f"Thermal detection failed: {str(e)}"


def test_battery_constraint():
    """Test battery level constraint checking"""
    print("\n" + "=" * 60)
    print("TEST 4: Battery Constraint Handling")
    print("=" * 60)

    try:
        from accel_manager import get_battery_level, DEFAULTS

        battery = get_battery_level()
        threshold = DEFAULTS["battery_threshold_pct"]

        print(f"  Current battery: {battery}%")
        print(f"  Threshold: {threshold}%")

        if battery < threshold:
            print(f"  ⚠️  Battery low - acceleration should be limited to CPU")
            device = assign_device("models/test.gguf", preferred="auto")
            assert device == "cpu", "Low battery should force CPU mode"
            print(f"  ✓ Correctly forced CPU mode")
        else:
            print(f"  ✓ Battery sufficient for acceleration")

        return True, f"Battery constraint passed (battery: {battery}%)"

    except Exception as e:
        return False, f"Battery constraint failed: {str(e)}"


def test_fallback_ranking():
    """Test device ranking and fallback order"""
    print("\n" + "=" * 60)
    print("TEST 5: Device Ranking & Fallback Order")
    print("=" * 60)

    try:
        profile = get_profile()
        ranked = profile.ranked

        print(f"  Ranked devices: {' > '.join(ranked)}")
        print(f"  Primary device: {ranked[0]}")
        print(f"  Fallback chain: {' → '.join(ranked[1:] if len(ranked) > 1 else ['none'])}")

        # CPU should always be in the list as ultimate fallback
        assert "cpu" in ranked, "CPU should always be available as fallback"

        # Validate ranking logic (higher performance first)
        benchmarks = profile.benchmarks
        for i in range(len(ranked) - 1):
            dev1 = ranked[i]
            dev2 = ranked[i + 1]
            gflops1 = benchmarks.get(dev1, {}).get("gflops", 0)
            gflops2 = benchmarks.get(dev2, {}).get("gflops", 0)

            assert gflops1 >= gflops2, f"{dev1} should outperform {dev2}"

        print(f"  ✓ Fallback order correct")
        return True, f"Fallback ranking passed ({len(ranked)} devices)"

    except Exception as e:
        return False, f"Fallback ranking failed: {str(e)}"


def test_performance_comparison():
    """Compare CPU vs GPU/NPU performance estimates"""
    print("\n" + "=" * 60)
    print("TEST 6: Performance Comparison")
    print("=" * 60)

    try:
        profile = get_profile()
        benchmarks = profile.benchmarks

        print("  Device Performance:")
        for device in profile.ranked:
            bench = benchmarks.get(device, {})
            if bench.get("success"):
                gflops = bench['gflops']
                latency_ms = bench['latency_s'] * 1000
                print(f"    {device.upper():5s}: {gflops:6.1f} GFLOPS, {latency_ms:6.1f} ms")
            else:
                print(f"    {device.upper():5s}: Failed")

        # Compare performance
        if "gpu" in benchmarks and "cpu" in benchmarks:
            gpu_gflops = benchmarks["gpu"].get("gflops", 0)
            cpu_gflops = benchmarks["cpu"].get("gflops", 0)

            if gpu_gflops > 0 and cpu_gflops > 0:
                speedup = gpu_gflops / cpu_gflops
                print(f"\n  GPU Speedup: {speedup:.1f}x over CPU")

        print(f"  ✓ Performance comparison complete")
        return True, "Performance comparison passed"

    except Exception as e:
        return False, f"Performance comparison failed: {str(e)}"


# ============================================================================
# Test Runner
# ============================================================================

def run_all_tests():
    """Run all inference tests"""
    print("\n" + "=" * 60)
    print("GENESIS ACCELERATION INFERENCE - TEST SUITE")
    print("=" * 60)

    tests = [
        test_device_assignment,
        test_acceleration_manager,
        test_thermal_throttling,
        test_battery_constraint,
        test_fallback_ranking,
        test_performance_comparison,
    ]

    results = []
    for test_func in tests:
        success, message = test_func()
        results.append((test_func.__name__, success, message))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for name, success, message in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
        if not success:
            print(f"       {message}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests PASSED")
        return 0
    else:
        print(f"✗ {total - passed} test(s) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
