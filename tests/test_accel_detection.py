#!/usr/bin/env python3
"""
test_accel_detection.py - Test Hardware Detection and Benchmarking

Tests acceleration manager's ability to detect CPU, GPU (Vulkan), and NPU (QNN)
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from accel_manager import (
    detect_cpu,
    detect_vulkan,
    detect_qnn,
    get_profile,
    get_battery_level,
    get_cpu_temp,
    micro_benchmark_cpu,
)


def test_cpu_detection():
    """Test CPU hardware detection"""
    print("\n" + "=" * 60)
    print("TEST 1: CPU Detection")
    print("=" * 60)

    try:
        cpu_info = detect_cpu()
        print(f"✓ CPU detected")
        print(f"  Cores (physical): {cpu_info.get('physical_cores')}")
        print(f"  Cores (logical): {cpu_info.get('logical_cores')}")
        print(f"  Architecture: {cpu_info.get('architecture')}")

        if cpu_info.get('frequency_mhz'):
            print(f"  Max frequency: {cpu_info['frequency_mhz']:.0f} MHz")

        assert cpu_info.get("available") is True, "CPU should always be available"
        assert cpu_info.get("physical_cores", 0) > 0, "Must have at least 1 core"

        return True, "CPU detection passed"
    except Exception as e:
        return False, f"CPU detection failed: {str(e)}"


def test_gpu_detection():
    """Test GPU (Vulkan) detection"""
    print("\n" + "=" * 60)
    print("TEST 2: GPU (Vulkan) Detection")
    print("=" * 60)

    try:
        gpu_info = detect_vulkan()
        print(f"  Backend: {gpu_info.get('backend')}")
        print(f"  Available: {gpu_info.get('available')}")

        if gpu_info.get("available"):
            print(f"  ✓ Vulkan GPU detected")
            print(f"  Info: {gpu_info.get('info', 'N/A')[:80]}")
        else:
            print(f"  ⚠️  Vulkan not available (will use CPU fallback)")

        # GPU detection can fail on some devices - that's OK
        return True, "GPU detection completed (availability varies by device)"
    except Exception as e:
        return False, f"GPU detection failed: {str(e)}"


def test_npu_detection():
    """Test NPU (QNN) detection"""
    print("\n" + "=" * 60)
    print("TEST 3: NPU (QNN) Detection")
    print("=" * 60)

    try:
        npu_info = detect_qnn()
        print(f"  Backend: {npu_info.get('backend')}")
        print(f"  Available: {npu_info.get('available')}")

        if npu_info.get("available"):
            print(f"  ✓ QNN NPU detected")
            print(f"  Info: {npu_info.get('info', 'N/A')[:80]}")
        else:
            print(f"  ⚠️  QNN not available (requires vendor SDK)")

        # NPU is optional and requires vendor SDK
        return True, "NPU detection completed (SDK may not be installed)"
    except Exception as e:
        return False, f"NPU detection failed: {str(e)}"


def test_system_monitoring():
    """Test battery and thermal monitoring"""
    print("\n" + "=" * 60)
    print("TEST 4: System Monitoring (Battery & Thermal)")
    print("=" * 60)

    try:
        battery = get_battery_level()
        temp = get_cpu_temp()

        print(f"  Battery level: {battery}%")
        print(f"  CPU temperature: {temp:.1f}°C")

        assert 0 <= battery <= 100, f"Battery level out of range: {battery}"
        assert 0 <= temp <= 120, f"Temperature out of range: {temp}"

        print(f"  ✓ System monitoring functional")
        return True, "System monitoring passed"
    except Exception as e:
        return False, f"System monitoring failed: {str(e)}"


def test_cpu_benchmark():
    """Test CPU microbenchmark"""
    print("\n" + "=" * 60)
    print("TEST 5: CPU Microbenchmark")
    print("=" * 60)

    try:
        bench = micro_benchmark_cpu(size=256)

        if bench.get("success"):
            print(f"  ✓ Benchmark completed")
            print(f"  Size: {bench['size']}x{bench['size']}")
            print(f"  Latency: {bench['latency_s']*1000:.2f} ms")
            print(f"  Performance: {bench['gflops']:.1f} GFLOPS")

            assert bench['latency_s'] > 0, "Latency should be positive"
            assert bench['gflops'] > 0, "GFLOPS should be positive"

            return True, f"CPU benchmark passed ({bench['gflops']:.1f} GFLOPS)"
        else:
            return False, f"CPU benchmark failed: {bench.get('error')}"

    except Exception as e:
        return False, f"CPU benchmark exception: {str(e)}"


def test_profile_generation():
    """Test full acceleration profile generation"""
    print("\n" + "=" * 60)
    print("TEST 6: Acceleration Profile Generation")
    print("=" * 60)

    try:
        print("  Running full hardware detection and benchmarking...")
        profile = get_profile(force_rerun=True)

        print(f"  ✓ Profile generated")
        print(f"  Detected devices: {len(profile.detected)}")
        print(f"  Benchmarked devices: {len(profile.benchmarks)}")
        print(f"  Ranked order: {' > '.join(profile.ranked)}")

        assert len(profile.detected) >= 1, "Should detect at least CPU"
        assert len(profile.benchmarks) >= 1, "Should benchmark at least CPU"
        assert len(profile.ranked) >= 1, "Should rank at least CPU"
        assert "cpu" in profile.ranked, "CPU should always be in ranked list"

        return True, f"Profile generation passed (ranked: {', '.join(profile.ranked)})"

    except Exception as e:
        return False, f"Profile generation failed: {str(e)}"


def test_profile_cache():
    """Test profile caching mechanism"""
    print("\n" + "=" * 60)
    print("TEST 7: Profile Caching")
    print("=" * 60)

    try:
        # First call - should use cache if available
        import time
        t1 = time.time()
        profile1 = get_profile(force_rerun=False)
        elapsed1 = time.time() - t1

        # Second call - should be instant (cached)
        t2 = time.time()
        profile2 = get_profile(force_rerun=False)
        elapsed2 = time.time() - t2

        print(f"  First call: {elapsed1*1000:.1f} ms")
        print(f"  Second call: {elapsed2*1000:.1f} ms")
        print(f"  Cache speedup: {elapsed1/max(elapsed2, 0.001):.1f}x")

        assert elapsed2 < elapsed1 or elapsed2 < 0.1, "Second call should be faster (cached)"
        print(f"  ✓ Caching working correctly")

        return True, "Profile caching passed"

    except Exception as e:
        return False, f"Profile caching failed: {str(e)}"


# ============================================================================
# Test Runner
# ============================================================================

def run_all_tests():
    """Run all acceleration detection tests"""
    print("\n" + "=" * 60)
    print("GENESIS ACCELERATION MANAGER - TEST SUITE")
    print("=" * 60)

    tests = [
        test_cpu_detection,
        test_gpu_detection,
        test_npu_detection,
        test_system_monitoring,
        test_cpu_benchmark,
        test_profile_generation,
        test_profile_cache,
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
