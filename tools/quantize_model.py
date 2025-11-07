#!/usr/bin/env python3
"""
quantize_model.py - Model Quantization Utilities for Genesis

Provides tools to quantize models for optimal performance on different accelerators:
- INT8/INT4 for NPU (Hexagon)
- FP16 for GPU (Vulkan/Adreno)
- Q4_K_M/Q5_K_M for balanced CPU/GPU

Wraps llama.cpp quantization tools and provides recommendations.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = Path.home() / "Genesis"
LLAMA_DIR = BASE_DIR / "llama.cpp"
MODELS_DIR = BASE_DIR / "models"
QUANT_DIR = MODELS_DIR / "quantized"

# Create directories
MODELS_DIR.mkdir(parents=True, exist_ok=True)
QUANT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Quantization Presets
# ============================================================================

QUANT_PRESETS = {
    "npu_optimized": {
        "quant_type": "Q8_0",  # INT8 approximation
        "target": "npu",
        "description": "INT8 quantization for NPU/Hexagon",
        "pros": ["Fastest NPU inference", "Lowest memory", "Best power efficiency"],
        "cons": ["Accuracy loss ~2-3%", "NPU SDK required"],
        "recommended_for": ["Small models (<7B)", "Real-time tasks", "Battery critical"],
    },
    "gpu_optimized": {
        "quant_type": "Q4_K_M",  # FP16-friendly 4-bit
        "target": "gpu",
        "description": "4-bit quantization optimized for GPU",
        "pros": ["Fast GPU inference", "Good accuracy", "Moderate memory"],
        "cons": ["Requires Vulkan support", "Higher battery drain than CPU"],
        "recommended_for": ["Medium models (7B-13B)", "Balanced performance"],
    },
    "cpu_optimized": {
        "quant_type": "Q5_K_M",  # 5-bit for CPU
        "target": "cpu",
        "description": "5-bit quantization for CPU efficiency",
        "pros": ["Universal compatibility", "Good accuracy", "Reliable fallback"],
        "cons": ["Slower than GPU/NPU", "Higher memory than Q4"],
        "recommended_for": ["Fallback mode", "High accuracy needed"],
    },
    "balanced": {
        "quant_type": "Q4_K_M",
        "target": "auto",
        "description": "Balanced 4-bit for CPU/GPU",
        "pros": ["Works on all devices", "Good speed/quality tradeoff"],
        "cons": ["Not optimized for NPU"],
        "recommended_for": ["General use", "Most models"],
    },
    "max_quality": {
        "quant_type": "Q6_K",
        "target": "cpu",
        "description": "6-bit for maximum quality",
        "pros": ["Best accuracy", "Minimal loss"],
        "cons": ["Larger file size", "Slower inference"],
        "recommended_for": ["Quality-critical tasks", "Large context"],
    },
    "minimal_size": {
        "quant_type": "Q4_0",
        "target": "auto",
        "description": "Smallest file size (aggressive 4-bit)",
        "pros": ["Smallest memory footprint", "Fastest loading"],
        "cons": ["Lower accuracy", "Quality degradation"],
        "recommended_for": ["Storage-constrained devices", "Testing"],
    },
}


def get_model_size_gb(model_path: str) -> float:
    """Get model file size in GB"""
    try:
        size_bytes = Path(model_path).stat().st_size
        return size_bytes / (1024 ** 3)
    except Exception:
        return 0.0


def estimate_quantized_size(original_size_gb: float, quant_type: str) -> float:
    """Estimate quantized model size based on quantization type"""
    # Size reduction factors (approximate)
    size_factors = {
        "Q4_0": 0.25,
        "Q4_K_M": 0.27,
        "Q5_0": 0.31,
        "Q5_K_M": 0.33,
        "Q6_K": 0.38,
        "Q8_0": 0.50,
        "F16": 0.50,
        "F32": 1.0,
    }

    factor = size_factors.get(quant_type, 0.30)
    return original_size_gb * factor


def run_quantization(
    input_model: str,
    output_model: str,
    quant_type: str,
) -> Tuple[bool, str]:
    """
    Run llama.cpp quantization tool

    Args:
        input_model: Path to input GGUF model (usually F16 or F32)
        output_model: Path to output quantized model
        quant_type: Quantization type (Q4_K_M, Q5_K_M, Q8_0, etc.)

    Returns:
        (success: bool, message: str)
    """
    input_path = Path(input_model)
    if not input_path.exists():
        return False, f"Input model not found: {input_model}"

    output_path = Path(output_model)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Find quantization tool
    quant_bin = LLAMA_DIR / "build" / "bin" / "llama-quantize"
    if not quant_bin.exists():
        quant_bin = LLAMA_DIR / "llama-quantize"
    if not quant_bin.exists():
        quant_bin = LLAMA_DIR / "build" / "llama-quantize"

    if not quant_bin.exists():
        return False, (
            "llama-quantize not found. Build llama.cpp first:\n"
            "  cd ~/Genesis/llama.cpp && make -j$(nproc)"
        )

    # Run quantization
    cmd = [str(quant_bin), str(input_path), str(output_path), quant_type]

    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes max
            cwd=str(LLAMA_DIR),
        )

        if result.returncode == 0:
            output_size = get_model_size_gb(str(output_path))
            return True, f"✓ Quantized to {quant_type}: {output_size:.2f} GB"
        else:
            return False, f"Quantization failed:\n{result.stderr}"

    except subprocess.TimeoutExpired:
        return False, "Quantization timed out (>10 minutes)"
    except Exception as e:
        return False, f"Error running quantization: {str(e)}"


def generate_model_manifest(
    model_path: str,
    quant_type: str,
    target_device: str,
) -> Dict[str, Any]:
    """
    Generate metadata manifest for quantized model

    Returns JSON-serializable dict with model specs and recommendations
    """
    model_size = get_model_size_gb(model_path)

    # Estimate context size based on model size
    # Rule of thumb: 7B model ~4GB can handle 2048-4096 context
    if model_size < 2.0:
        max_context = 8192
    elif model_size < 4.0:
        max_context = 4096
    elif model_size < 6.0:
        max_context = 2048
    else:
        max_context = 1024

    # Memory footprint estimate (model + context)
    context_memory_gb = (max_context * 2048) / (1024 ** 3)  # rough estimate
    total_memory_gb = model_size + context_memory_gb

    manifest = {
        "model_path": str(model_path),
        "model_name": Path(model_path).stem,
        "quantization": quant_type,
        "target_device": target_device,
        "file_size_gb": round(model_size, 2),
        "estimated_memory_gb": round(total_memory_gb, 2),
        "recommended_context": max_context,
        "recommended_threads": 4 if target_device == "cpu" else 2,
        "recommended_batch": 512,
        "acceleration_hints": {},
    }

    # Device-specific hints
    if target_device == "npu":
        manifest["acceleration_hints"] = {
            "backend": "qnn",
            "precision": "INT8",
            "note": "Requires QNN SDK and model conversion",
        }
    elif target_device == "gpu":
        manifest["acceleration_hints"] = {
            "backend": "vulkan",
            "n_gpu_layers": -1,  # Offload all layers
            "note": "Use --n-gpu-layers 999 to offload all to GPU",
        }
    elif target_device == "cpu":
        manifest["acceleration_hints"] = {
            "backend": "cpu",
            "threads": 4,
            "note": "Adjust threads based on device cores",
        }

    return manifest


def save_manifest(manifest: Dict[str, Any], output_path: Optional[str] = None):
    """Save model manifest to JSON file"""
    if output_path is None:
        model_name = manifest["model_name"]
        output_path = QUANT_DIR / f"{model_name}_manifest.json"

    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"✓ Manifest saved: {output_path}")


def recommend_preset(
    model_size_gb: float,
    target_device: str = "auto",
    priority: str = "balanced",
) -> str:
    """
    Recommend quantization preset based on constraints

    Args:
        model_size_gb: Model size in GB
        target_device: Target device (npu, gpu, cpu, auto)
        priority: Priority (speed, quality, size, balanced)

    Returns:
        Preset name from QUANT_PRESETS
    """
    # Device-specific recommendations
    if target_device == "npu":
        return "npu_optimized"
    elif target_device == "gpu":
        return "gpu_optimized"
    elif target_device == "cpu":
        return "cpu_optimized"

    # Priority-based recommendations
    if priority == "speed":
        return "gpu_optimized" if model_size_gb < 10 else "npu_optimized"
    elif priority == "quality":
        return "max_quality"
    elif priority == "size":
        return "minimal_size"
    else:  # balanced
        return "balanced"


def quantize_model_with_preset(
    input_model: str,
    preset: str = "balanced",
    output_name: Optional[str] = None,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Quantize model using a named preset

    Args:
        input_model: Path to input model
        preset: Preset name from QUANT_PRESETS
        output_name: Optional output filename (auto-generated if None)

    Returns:
        (success: bool, message: str, manifest: dict or None)
    """
    if preset not in QUANT_PRESETS:
        return False, f"Unknown preset: {preset}", None

    config = QUANT_PRESETS[preset]
    quant_type = config["quant_type"]
    target = config["target"]

    # Generate output path
    input_path = Path(input_model)
    if output_name is None:
        output_name = f"{input_path.stem}_{quant_type}.gguf"

    output_path = QUANT_DIR / output_name

    # Run quantization
    success, message = run_quantization(str(input_path), str(output_path), quant_type)

    if not success:
        return False, message, None

    # Generate manifest
    manifest = generate_model_manifest(str(output_path), quant_type, target)
    manifest_path = QUANT_DIR / f"{output_path.stem}_manifest.json"
    save_manifest(manifest, str(manifest_path))

    return True, message, manifest


def print_presets():
    """Print available quantization presets"""
    print("=" * 70)
    print("Available Quantization Presets")
    print("=" * 70)
    print()

    for name, config in QUANT_PRESETS.items():
        print(f"📦 {name.upper()}")
        print(f"   Type: {config['quant_type']}")
        print(f"   Target: {config['target']}")
        print(f"   Description: {config['description']}")
        print(f"   Pros: {', '.join(config['pros'])}")
        print(f"   Cons: {', '.join(config['cons'])}")
        print(f"   Recommended for: {', '.join(config['recommended_for'])}")
        print()


# ============================================================================
# CLI Interface
# ============================================================================

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Quantize models for optimal Genesis performance"
    )
    parser.add_argument(
        "input_model",
        nargs="?",
        help="Path to input GGUF model (F16 or F32)",
    )
    parser.add_argument(
        "--preset",
        default="balanced",
        choices=list(QUANT_PRESETS.keys()),
        help="Quantization preset (default: balanced)",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List all available presets and exit",
    )
    parser.add_argument(
        "--output",
        help="Output model path (auto-generated if not specified)",
    )

    args = parser.parse_args()

    if args.list_presets:
        print_presets()
        sys.exit(0)

    if not args.input_model:
        parser.print_help()
        print("\n")
        print_presets()
        sys.exit(1)

    # Run quantization
    print(f"Input model: {args.input_model}")
    print(f"Preset: {args.preset}")
    print()

    success, message, manifest = quantize_model_with_preset(
        args.input_model,
        args.preset,
        args.output,
    )

    print(message)

    if success and manifest:
        print()
        print("Model Manifest:")
        print(json.dumps(manifest, indent=2))
