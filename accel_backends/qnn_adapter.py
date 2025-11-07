#!/usr/bin/env python3
"""
qnn_adapter.py - Qualcomm QNN (Neural Processing Unit) Backend Adapter

Provides interface to Qualcomm QNN runtime for NPU-accelerated inference.
Handles model compilation, graph loading, and execution on Hexagon DSP/NPU.

Note: Requires Qualcomm QNN SDK (proprietary). Falls back gracefully if unavailable.
"""

import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

BASE_DIR = Path.home() / "Genesis"
QNN_DIR = BASE_DIR / "qnn"
QNN_MODELS_DIR = QNN_DIR / "models"
QNN_CACHE_DIR = QNN_DIR / "cache"

# Create directories
QNN_DIR.mkdir(parents=True, exist_ok=True)
QNN_MODELS_DIR.mkdir(parents=True, exist_ok=True)
QNN_CACHE_DIR.mkdir(parents=True, exist_ok=True)


class QNNNotAvailableError(Exception):
    """Raised when QNN SDK is not installed or accessible"""
    pass


class QNNAdapter:
    """
    Interface to Qualcomm QNN runtime for NPU inference

    Workflow:
    1. Convert GGUF/ONNX model to QNN format (.bin)
    2. Load compiled graph into QNN runtime
    3. Execute inference on Hexagon NPU
    4. Return outputs with same interface as CPU/GPU backends
    """

    def __init__(self):
        self.qnn_sdk_root = self._find_qnn_sdk()
        self.available = self.qnn_sdk_root is not None
        self.loaded_model = None
        self.context = None

        if not self.available:
            raise QNNNotAvailableError(
                "QNN SDK not found. Install from Qualcomm or set QNN_SDK_ROOT environment variable."
            )

    def _find_qnn_sdk(self) -> Optional[Path]:
        """Locate QNN SDK installation"""
        # Check environment variable
        sdk_root = os.environ.get("QNN_SDK_ROOT")
        if sdk_root and Path(sdk_root).exists():
            return Path(sdk_root)

        # Check common installation paths
        candidates = [
            Path.home() / "qnn",
            Path.home() / "qualcomm" / "qnn",
            Path("/opt/qcom/aistack/qnn"),
            Path("/vendor/qcom/qnn"),
        ]

        for candidate in candidates:
            if candidate.exists() and (candidate / "lib").exists():
                return candidate

        return None

    def check_availability(self) -> Dict[str, Any]:
        """Check QNN runtime availability and return details"""
        result = {
            "available": self.available,
            "sdk_root": str(self.qnn_sdk_root) if self.qnn_sdk_root else None,
            "libraries": [],
            "binaries": [],
        }

        if not self.available:
            result["message"] = "QNN SDK not installed"
            return result

        # Check for essential libraries
        lib_dir = self.qnn_sdk_root / "lib" / "aarch64-android"
        if lib_dir.exists():
            libs = ["libQnnHtp.so", "libQnnSystem.so", "libQnnCpu.so"]
            for lib in libs:
                lib_path = lib_dir / lib
                if lib_path.exists():
                    result["libraries"].append(str(lib_path))

        # Check for binaries
        bin_dir = self.qnn_sdk_root / "bin" / "aarch64-android"
        if bin_dir.exists():
            binaries = ["qnn-net-run", "qnn-context-binary-generator"]
            for binary in binaries:
                bin_path = bin_dir / binary
                if bin_path.exists():
                    result["binaries"].append(str(bin_path))

        result["message"] = f"QNN SDK found with {len(result['libraries'])} libraries"
        return result

    def convert_model(
        self,
        input_model: str,
        output_path: Optional[str] = None,
        quantization: str = "INT8",
    ) -> str:
        """
        Convert ONNX/GGUF model to QNN binary format

        Args:
            input_model: Path to input model (ONNX or GGUF)
            output_path: Output path for QNN .bin file
            quantization: Target quantization (INT8, FP16, FP32)

        Returns:
            Path to compiled QNN model
        """
        if not self.available:
            raise QNNNotAvailableError("Cannot convert model without QNN SDK")

        input_path = Path(input_model)
        if not input_path.exists():
            raise FileNotFoundError(f"Model not found: {input_model}")

        # Determine output path
        if output_path is None:
            output_path = QNN_MODELS_DIR / f"{input_path.stem}_qnn_{quantization}.bin"
        else:
            output_path = Path(output_path)

        # Check if already converted
        if output_path.exists():
            print(f"✓ Using cached QNN model: {output_path}")
            return str(output_path)

        # Note: This is a skeleton - actual conversion depends on QNN SDK version
        # Typical workflow:
        # 1. If GGUF → convert to ONNX first
        # 2. Use qnn-onnx-converter to convert ONNX to QNN
        # 3. Use qnn-context-binary-generator to compile graph

        print(f"⚠️  QNN model conversion not yet implemented")
        print(f"   Manual steps:")
        print(f"   1. Convert {input_model} to ONNX if needed")
        print(f"   2. Run: qnn-onnx-converter --input_network model.onnx --output_path qnn_model.cpp")
        print(f"   3. Run: qnn-model-lib-generator -c qnn_model.cpp -b qnn_model.bin")
        print(f"   4. Place result at: {output_path}")

        raise NotImplementedError("QNN model conversion requires manual steps (vendor SDK)")

    def load_model(self, model_path: str) -> bool:
        """
        Load compiled QNN model into runtime

        Args:
            model_path: Path to QNN .bin model file

        Returns:
            True if successful
        """
        if not self.available:
            raise QNNNotAvailableError("Cannot load model without QNN runtime")

        model_file = Path(model_path)
        if not model_file.exists():
            raise FileNotFoundError(f"QNN model not found: {model_path}")

        # TODO: Actual QNN runtime model loading
        # This would use QNN C API or Python bindings if available
        # For now, store the path for later use

        self.loaded_model = str(model_file)
        print(f"✓ QNN model loaded: {model_file.name}")
        return True

    def run_inference(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Run inference on NPU using QNN runtime

        Args:
            prompt: Input prompt text
            max_tokens: Maximum output tokens
            temperature: Sampling temperature

        Returns:
            Dict with output, latency, and metadata
        """
        if not self.available:
            raise QNNNotAvailableError("QNN runtime not available")

        if not self.loaded_model:
            raise RuntimeError("No model loaded. Call load_model() first.")

        # TODO: Implement actual QNN inference
        # Workflow:
        # 1. Tokenize prompt
        # 2. Prepare input tensors
        # 3. Execute graph on NPU via QNN API
        # 4. Decode output tokens
        # 5. Return formatted result

        print(f"⚠️  QNN inference not yet implemented")
        print(f"   This requires:")
        print(f"   - QNN C API bindings or qnn-net-run CLI wrapper")
        print(f"   - Tokenizer integration")
        print(f"   - Tensor shape matching for model")

        raise NotImplementedError("QNN inference requires QNN SDK integration")

    def unload_model(self):
        """Unload model and free NPU resources"""
        if self.loaded_model:
            # TODO: Call QNN cleanup APIs
            self.loaded_model = None
            self.context = None
            print("✓ QNN model unloaded")

    def get_stats(self) -> Dict[str, Any]:
        """Get NPU utilization and performance stats"""
        return {
            "available": self.available,
            "sdk_root": str(self.qnn_sdk_root) if self.qnn_sdk_root else None,
            "loaded_model": self.loaded_model,
            "npu_type": "Hexagon" if self.available else None,
        }


# ============================================================================
# Helper Functions
# ============================================================================

def setup_qnn_environment() -> Dict[str, Any]:
    """
    Setup guide for QNN SDK installation

    Returns instructions and status
    """
    status = {
        "installed": False,
        "instructions": [],
        "links": [],
    }

    try:
        adapter = QNNAdapter()
        status["installed"] = True
        status["details"] = adapter.check_availability()
        return status
    except QNNNotAvailableError:
        pass

    # Provide installation instructions
    status["instructions"] = [
        "Qualcomm QNN SDK Installation (NPU Support)",
        "",
        "⚠️  IMPORTANT: QNN SDK is proprietary and requires Qualcomm account",
        "",
        "Steps:",
        "1. Register at: https://qpm.qualcomm.com/",
        "2. Download QNN SDK for Android (aarch64)",
        "3. Extract to ~/qnn/ or set QNN_SDK_ROOT environment variable",
        "4. Verify libraries exist:",
        "   - libQnnHtp.so (Hexagon NPU)",
        "   - libQnnSystem.so (Runtime)",
        "   - libQnnCpu.so (CPU fallback)",
        "",
        "Alternative (if QNN unavailable):",
        "- Use GPU (Vulkan) acceleration instead",
        "- Use CPU with optimized GGUF quantization",
        "- Enable NNAPI backend (limited LLM support)",
        "",
        "For development/testing:",
        "- Genesis will auto-fallback to GPU or CPU",
        "- NPU support is optional (not required)",
    ]

    status["links"] = [
        "https://qpm.qualcomm.com/ (QNN SDK Download)",
        "https://github.com/ggerganov/llama.cpp/discussions (Community)",
    ]

    return status


def test_qnn_backend():
    """Test QNN adapter availability and provide setup guidance"""
    print("=" * 60)
    print("QNN (NPU) Backend Adapter - Status Check")
    print("=" * 60)
    print()

    try:
        adapter = QNNAdapter()
        print("✓ QNN SDK detected!")
        print()

        details = adapter.check_availability()
        print(f"SDK Root: {details['sdk_root']}")
        print(f"Libraries: {len(details['libraries'])} found")
        for lib in details['libraries']:
            print(f"  - {Path(lib).name}")
        print(f"Binaries: {len(details['binaries'])} found")
        for binary in details['binaries']:
            print(f"  - {Path(binary).name}")
        print()
        print("✓ QNN backend ready (integration pending)")

    except QNNNotAvailableError as e:
        print("✗ QNN SDK not available")
        print()
        setup = setup_qnn_environment()
        print("\n".join(setup["instructions"]))

    print()
    print("=" * 60)


if __name__ == "__main__":
    test_qnn_backend()
