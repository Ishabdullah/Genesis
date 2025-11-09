#!/usr/bin/env python3
"""
accel_manager.py - Hardware Acceleration Manager for Genesis

Manages GPU (Vulkan), NPU (QNN), and CPU acceleration for local LLM inference.
Provides auto-detection, benchmarking, workload mapping, and safe fallback.

Target: Snapdragon 8 Gen 3 (S24 Ultra) with Adreno 750 GPU and Hexagon NPU
"""

import os
import json
import time
import platform
import subprocess
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

# Genesis base directory
BASE_DIR = Path.home() / "Genesis"
TMP_DIR = BASE_DIR / "tmp"
BENCH_DIR = TMP_DIR / "bench_cache"
ENGINES_DIR = BASE_DIR / "engines"
BENCH_PATH = BENCH_DIR / "accel_bench.json"

# Create directories
TMP_DIR.mkdir(parents=True, exist_ok=True)
BENCH_DIR.mkdir(parents=True, exist_ok=True)
ENGINES_DIR.mkdir(parents=True, exist_ok=True)

# Configuration defaults
DEFAULTS = {
    "battery_threshold_pct": 20,          # Min battery for GPU/NPU
    "temp_threshold_c": 70,                # Max CPU temp for acceleration
    "retry_attempts": 2,
    "benchmark_iters": 3,
    "micro_op_size": 256,                  # Matrix size for microbenchmark
    "bench_cache_hours": 24,               # Recache benchmark after 24h
    "thermal_check_interval": 5,           # Check temperature every 5 inferences
    "npu_min_quant": "INT8",              # NPU prefers INT8 quantization
    "gpu_preferred_quant": "FP16",        # GPU works well with FP16
}


class AccelProfile:
    """Stores detected hardware capabilities and benchmark results"""

    def __init__(self):
        self.timestamp = time.time()
        self.detected = {}
        self.benchmarks = {}
        self.ranked = []
        self.device_info = {}
        self.thermal_state = "normal"
        self.battery_level = 100


def run_cmd(cmd: List[str], timeout: int = 10) -> Tuple[int, str, str]:
    """Run a shell command safely and return (returncode, stdout, stderr)"""
    try:
        if isinstance(cmd, str):
            cmd = cmd.split()
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(BASE_DIR)
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def get_battery_level() -> int:
    """Get current battery level percentage (Android via Termux API)"""
    try:
        rc, out, err = run_cmd(["termux-battery-status"], timeout=3)
        if rc == 0 and out:
            import json
            battery_data = json.loads(out)
            return battery_data.get("percentage", 100)
    except Exception:
        pass

    # Fallback: use psutil on regular Linux (if available)
    if PSUTIL_AVAILABLE:
        try:
            battery = psutil.sensors_battery()
            if battery:
                return int(battery.percent)
        except Exception:
            pass

    return 100  # Assume full if can't detect


def get_cpu_temp() -> float:
    """Get CPU temperature (Celsius) for thermal throttling detection"""
    try:
        # Android thermal zones
        thermal_zones = Path("/sys/class/thermal")
        if thermal_zones.exists():
            for zone in thermal_zones.glob("thermal_zone*"):
                temp_file = zone / "temp"
                if temp_file.exists():
                    temp_millidegrees = int(temp_file.read_text().strip())
                    return temp_millidegrees / 1000.0
    except Exception:
        pass

    # Fallback: psutil (if available)
    if PSUTIL_AVAILABLE:
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        return entries[0].current
        except Exception:
            pass

    return 50.0  # Safe default


def detect_cpu() -> Dict[str, Any]:
    """Detect CPU cores, frequency, and architecture"""
    try:
        if PSUTIL_AVAILABLE:
            cores_physical = psutil.cpu_count(logical=False) or os.cpu_count() or 1
            cores_logical = psutil.cpu_count(logical=True) or cores_physical
        else:
            cores_physical = os.cpu_count() or 1
            cores_logical = cores_physical

        # CPU frequency
        freq = None
        if PSUTIL_AVAILABLE:
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    freq = cpu_freq.max or cpu_freq.current
            except Exception:
                pass

        # CPU architecture
        arch = platform.machine()

        return {
            "type": "cpu",
            "available": True,
            "physical_cores": cores_physical,
            "logical_cores": cores_logical,
            "frequency_mhz": freq,
            "architecture": arch,
            "platform": platform.platform(),
        }
    except Exception as e:
        return {
            "type": "cpu",
            "available": True,
            "error": str(e),
            "physical_cores": 4,
            "logical_cores": 8,
        }


def detect_vulkan() -> Dict[str, Any]:
    """Detect Vulkan GPU availability via vulkaninfo or driver files"""
    result = {
        "type": "gpu",
        "backend": "vulkan",
        "available": False,
        "info": "",
    }

    # Check for vulkaninfo binary
    rc, out, err = run_cmd(["which", "vulkaninfo"], timeout=2)
    if rc == 0 and out:
        # vulkaninfo exists, try to run it
        rc2, out2, err2 = run_cmd(["vulkaninfo", "--summary"], timeout=5)
        if rc2 == 0:
            result["available"] = True
            result["info"] = out2[:500]  # First 500 chars

            # Try to extract GPU name
            for line in out2.split('\n'):
                if 'GPU' in line or 'Device' in line:
                    result["device_name"] = line.strip()
                    break
        else:
            result["info"] = f"vulkaninfo failed: {err2}"
    else:
        # Check for Vulkan ICD files (Installable Client Driver)
        rc3, out3, err3 = run_cmd(["sh", "-c", "echo $VK_ICD_FILENAMES || true"])
        if out3.strip():
            result["available"] = True
            result["info"] = f"VK_ICD_FILENAMES: {out3}"
        else:
            # Check common Android Vulkan library locations
            vulkan_libs = [
                "/system/lib64/libvulkan.so",
                "/vendor/lib64/libvulkan.so",
                "/system/lib/libvulkan.so",
            ]
            for lib in vulkan_libs:
                if Path(lib).exists():
                    result["available"] = True
                    result["info"] = f"Vulkan library found: {lib}"
                    break

    return result


def detect_qnn() -> Dict[str, Any]:
    """Detect Qualcomm QNN (NPU) runtime availability"""
    result = {
        "type": "npu",
        "backend": "qnn",
        "available": False,
        "info": "",
    }

    # Check for QNN runtime binaries
    qnn_binaries = ["qnn-net-run", "qnnrt", "qnn-context-binary-generator"]
    for binary in qnn_binaries:
        rc, out, err = run_cmd(["which", binary], timeout=2)
        if rc == 0 and out:
            result["available"] = True
            result["info"] = f"Found QNN binary: {binary} at {out}"
            result["binary"] = out
            return result

    # Check for QNN libraries
    qnn_lib_paths = [
        "/vendor/lib64/libQnnHtp.so",
        "/vendor/lib64/libQnnSystem.so",
        "/system/lib64/libQnnHtp.so",
        str(Path.home() / "qnn" / "lib" / "aarch64-android"),
    ]

    for lib_path in qnn_lib_paths:
        if Path(lib_path).exists():
            result["available"] = True
            result["info"] = f"QNN library found: {lib_path}"
            result["library_path"] = lib_path
            return result

    # Check environment variables
    rc, out, err = run_cmd(["sh", "-c", "echo $QNN_SDK_ROOT || true"])
    if out.strip():
        result["available"] = True
        result["info"] = f"QNN_SDK_ROOT: {out}"
    else:
        result["info"] = "QNN runtime not detected. Install Qualcomm QNN SDK for NPU support."

    return result


def micro_benchmark_cpu(size: int = 256) -> Dict[str, Any]:
    """CPU matmul microbenchmark using NumPy"""
    try:
        import numpy as np

        # Warmup
        a = np.random.rand(size, size).astype(np.float32)
        b = np.random.rand(size, size).astype(np.float32)
        _ = np.dot(a, b)

        # Actual benchmark
        times = []
        for _ in range(DEFAULTS["benchmark_iters"]):
            t0 = time.perf_counter()
            _ = np.dot(a, b)
            t1 = time.perf_counter()
            times.append(t1 - t0)

        avg_time = sum(times) / len(times)
        ops = 2 * (size ** 3)  # 2n^3 operations for matmul
        gflops = (ops / avg_time) / 1e9

        return {
            "device": "cpu",
            "size": size,
            "latency_s": avg_time,
            "gflops": gflops,
            "success": True,
        }
    except Exception as e:
        return {
            "device": "cpu",
            "size": size,
            "latency_s": 1.0,
            "gflops": 0.0,
            "success": False,
            "error": str(e),
        }


def micro_benchmark_gpu(size: int = 256) -> Dict[str, Any]:
    """GPU matmul microbenchmark (mocked until llama.cpp Vulkan backend ready)"""
    # TODO: Replace with actual Vulkan compute benchmark when engine is built
    # For now, estimate based on typical Adreno 750 performance
    return {
        "device": "gpu",
        "backend": "vulkan",
        "size": size,
        "latency_s": 0.05,  # Mock: ~50ms for 256x256 matmul
        "gflops": 300.0,    # Mock: Adreno 750 can do ~300 GFLOPS FP32
        "success": True,
        "note": "Mocked until Vulkan engine available",
    }


def micro_benchmark_npu(size: int = 256) -> Dict[str, Any]:
    """NPU matmul microbenchmark (mocked until QNN adapter ready)"""
    # TODO: Replace with actual QNN inference benchmark
    return {
        "device": "npu",
        "backend": "qnn",
        "size": size,
        "latency_s": 0.03,  # Mock: ~30ms (NPU is faster for INT8)
        "gflops": 500.0,    # Mock: Hexagon can do ~500 GFLOPS INT8
        "success": True,
        "note": "Mocked until QNN adapter available",
    }


def run_benchmarks(force_rerun: bool = False) -> AccelProfile:
    """Run hardware detection and microbenchmarks, cache results"""
    profile = AccelProfile()

    # Detect hardware
    print("🔍 Detecting hardware acceleration capabilities...")
    profile.detected["cpu"] = detect_cpu()
    profile.detected["gpu"] = detect_vulkan()
    profile.detected["npu"] = detect_qnn()

    # Get system state
    profile.battery_level = get_battery_level()
    cpu_temp = get_cpu_temp()
    profile.device_info = {
        "battery_pct": profile.battery_level,
        "cpu_temp_c": cpu_temp,
        "platform": platform.platform(),
    }

    # Determine thermal state
    if cpu_temp > DEFAULTS["temp_threshold_c"]:
        profile.thermal_state = "hot"
    else:
        profile.thermal_state = "normal"

    # Run benchmarks
    print("⚡ Running microbenchmarks...")
    size = DEFAULTS["micro_op_size"]

    # CPU always available
    profile.benchmarks["cpu"] = micro_benchmark_cpu(size)

    # GPU if Vulkan available
    if profile.detected["gpu"].get("available"):
        profile.benchmarks["gpu"] = micro_benchmark_gpu(size)

    # NPU if QNN available
    if profile.detected["npu"].get("available"):
        profile.benchmarks["npu"] = micro_benchmark_npu(size)

    # Rank devices by performance (GFLOPS descending)
    ranked = sorted(
        [(k, v.get("gflops", 0.0)) for k, v in profile.benchmarks.items()],
        key=lambda x: x[1],
        reverse=True,
    )
    profile.ranked = [device for device, _ in ranked]

    # Save to disk
    try:
        cache_data = {
            "timestamp": profile.timestamp,
            "detected": profile.detected,
            "benchmarks": profile.benchmarks,
            "ranked": profile.ranked,
            "device_info": profile.device_info,
            "thermal_state": profile.thermal_state,
        }
        with open(BENCH_PATH, "w") as f:
            json.dump(cache_data, f, indent=2)
        print(f"✓ Benchmark profile saved to {BENCH_PATH}")
    except Exception as e:
        print(f"⚠️  Warning: Failed to save benchmark profile: {e}")

    return profile


def get_profile(force_rerun: bool = False) -> AccelProfile:
    """Get acceleration profile; use cache if recent, else re-benchmark"""
    # Check cache validity
    if BENCH_PATH.exists() and not force_rerun:
        try:
            with open(BENCH_PATH, "r") as f:
                cache_data = json.load(f)

            cache_age = time.time() - cache_data.get("timestamp", 0)
            max_age = DEFAULTS["bench_cache_hours"] * 3600

            if cache_age < max_age:
                # Valid cache
                profile = AccelProfile()
                profile.timestamp = cache_data["timestamp"]
                profile.detected = cache_data["detected"]
                profile.benchmarks = cache_data["benchmarks"]
                profile.ranked = cache_data["ranked"]
                profile.device_info = cache_data.get("device_info", {})
                profile.thermal_state = cache_data.get("thermal_state", "normal")
                profile.battery_level = get_battery_level()
                return profile
        except Exception as e:
            print(f"⚠️  Cache read error: {e}, re-running benchmarks...")

    # Re-run benchmarks
    return run_benchmarks(force_rerun)


def assign_device(model_path: str, preferred: str = "auto") -> str:
    """
    Choose best device for a model based on:
    - User preference (if not "auto")
    - Model quantization type
    - Device availability and performance
    - Battery and thermal state
    """
    profile = get_profile()
    ranked = profile.ranked

    # Respect explicit preference
    if preferred != "auto" and preferred in ranked:
        return preferred

    # Check battery and thermal constraints
    battery = get_battery_level()
    temp = get_cpu_temp()

    if battery < DEFAULTS["battery_threshold_pct"] or temp > DEFAULTS["temp_threshold_c"]:
        # Force CPU to save battery/reduce heat
        return "cpu"

    # Heuristic based on model quantization
    model_lower = model_path.lower()

    # INT8/Q4/Q8 quantization → prefer NPU > GPU > CPU
    if any(q in model_lower for q in ["int8", "q4_", "q8_", "int4"]):
        for device in ["npu", "gpu", "cpu"]:
            if device in ranked:
                return device

    # FP16 or larger models → prefer GPU > CPU
    if "fp16" in model_lower or "f16" in model_lower:
        for device in ["gpu", "cpu"]:
            if device in ranked:
                return device

    # Default: use fastest available device
    return ranked[0] if ranked else "cpu"


def run_inference(
    model_path: str,
    prompt: str,
    timeout: int = 30,
    device_hint: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Run LLM inference with acceleration, automatic fallback on failure

    Args:
        model_path: Path to GGUF model file
        prompt: Input prompt text
        timeout: Max inference time in seconds
        device_hint: Explicit device ("cpu"|"gpu"|"npu"|"auto")
        extra_args: Additional CLI args for llama.cpp

    Returns:
        Dict with keys: device, success, output, latency_s, diagnostics
    """
    device = device_hint or assign_device(model_path, preferred="auto")
    profile = get_profile()
    diagnostics = {"attempts": [], "chosen_device": device}

    # Build engine command
    if device == "cpu":
        engine_path = ENGINES_DIR / "llama_cpu"
        # Use existing llama.cpp build
        if not engine_path.exists():
            engine_path = BASE_DIR / "llama.cpp" / "llama-cli"
    elif device == "gpu":
        engine_path = ENGINES_DIR / "llama_vulkan"
    elif device == "npu":
        # NPU uses QNN adapter (not direct CLI)
        diagnostics["error"] = "NPU inference not yet implemented"
        return fallback_inference(model_path, prompt, timeout, profile, diagnostics)
    else:
        engine_path = BASE_DIR / "llama.cpp" / "llama-cli"

    # Check engine exists
    if not Path(engine_path).exists():
        diagnostics["error"] = f"Engine not found: {engine_path}"
        return fallback_inference(model_path, prompt, timeout, profile, diagnostics)

    # Build command
    cmd = [
        str(engine_path),
        "-m", str(model_path),
        "-p", prompt,
        "-n", "256",
        "-t", "4",
        "--temp", "0.7",
    ]

    if extra_args:
        cmd.extend(extra_args)

    # Run inference
    try:
        t0 = time.perf_counter()
        rc, out, err = run_cmd(cmd, timeout=timeout)
        t1 = time.perf_counter()

        if rc == 0 and out:
            return {
                "device": device,
                "success": True,
                "output": out,
                "latency_s": t1 - t0,
                "diagnostics": diagnostics,
            }
        else:
            diagnostics["error"] = err or "No output from engine"
            diagnostics["returncode"] = rc
    except Exception as e:
        diagnostics["exception"] = str(e)

    # Fallback to next best device
    return fallback_inference(model_path, prompt, timeout, profile, diagnostics)


def fallback_inference(
    model_path: str,
    prompt: str,
    timeout: int,
    profile: AccelProfile,
    diagnostics: Dict[str, Any],
) -> Dict[str, Any]:
    """Try alternative devices in ranked order"""
    for device in profile.ranked:
        if device == diagnostics.get("chosen_device"):
            continue  # Skip already-tried device

        attempt = {"device": device, "timestamp": time.time()}
        diagnostics["attempts"].append(attempt)

        # Recursive call with explicit device
        result = run_inference(
            model_path=model_path,
            prompt=prompt,
            timeout=timeout,
            device_hint=device,
        )

        if result.get("success"):
            return result
        else:
            attempt["error"] = result.get("diagnostics", {}).get("error", "Unknown")

    # All devices failed
    return {
        "device": "none",
        "success": False,
        "output": None,
        "diagnostics": diagnostics,
    }


# ============================================================================
# Public API
# ============================================================================

def get_acceleration_manager():
    """Singleton accessor for integration with Genesis"""
    return AccelerationManager()


class AccelerationManager:
    """Facade for acceleration management"""

    def __init__(self):
        self.profile = None
        self.inference_count = 0

    def get_profile(self, force_rerun: bool = False) -> AccelProfile:
        """Get current acceleration profile"""
        self.profile = get_profile(force_rerun)
        return self.profile

    def assign_device(self, model_path: str, preferred: str = "auto") -> str:
        """Choose best device for a model"""
        return assign_device(model_path, preferred)

    def run_inference(
        self,
        model_path: str,
        prompt: str,
        timeout: int = 30,
        device_hint: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Run accelerated inference with fallback"""
        self.inference_count += 1

        # Periodic thermal check
        if self.inference_count % DEFAULTS["thermal_check_interval"] == 0:
            temp = get_cpu_temp()
            if temp > DEFAULTS["temp_threshold_c"]:
                print(f"⚠️  High temperature ({temp:.1f}°C), forcing CPU mode")
                device_hint = "cpu"

        return run_inference(model_path, prompt, timeout, device_hint, extra_args)

    def get_status(self) -> Dict[str, Any]:
        """Get current acceleration status"""
        if not self.profile:
            self.profile = get_profile()

        return {
            "ranked_devices": self.profile.ranked,
            "battery_pct": get_battery_level(),
            "cpu_temp_c": get_cpu_temp(),
            "thermal_state": self.profile.thermal_state,
            "inference_count": self.inference_count,
        }


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("Genesis Hardware Acceleration Manager")
    print("=" * 60)
    print()

    # Run full detection and benchmark
    profile = get_profile(force_rerun=True)

    print()
    print("📊 ACCELERATION PROFILE")
    print("=" * 60)
    print(f"Ranked devices: {' > '.join(profile.ranked)}")
    print(f"Battery level: {profile.battery_level}%")
    print(f"Thermal state: {profile.thermal_state}")
    print()

    print("Hardware Detection:")
    for device_type, info in profile.detected.items():
        available = "✓" if info.get("available") else "✗"
        print(f"  {available} {device_type.upper()}: {info.get('info', 'N/A')[:60]}")
    print()

    print("Benchmarks:")
    for device, bench in profile.benchmarks.items():
        if bench.get("success"):
            print(f"  {device.upper()}: {bench['gflops']:.1f} GFLOPS, {bench['latency_s']*1000:.1f}ms")
        else:
            print(f"  {device.upper()}: Failed - {bench.get('error', 'Unknown')}")
    print()

    print(f"✓ Profile saved to: {BENCH_PATH}")
    print("=" * 60)
