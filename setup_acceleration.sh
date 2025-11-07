#!/usr/bin/env bash
#
# setup_acceleration.sh - Complete GPU/NPU Acceleration Setup for Genesis
#
# This script configures your S24 Ultra for maximum performance with Genesis:
# - GPU (Vulkan) acceleration (automatic)
# - NPU (QNN) detection and guidance (manual SDK required)
# - Environment variables
# - Test validation
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Genesis Acceleration Setup${NC}"
echo -e "${BLUE}Device: Samsung S24 Ultra (Snapdragon 8 Gen 3)${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# ============================================================================
# Step 1: Configure Environment Variables
# ============================================================================

echo -e "${YELLOW}[1/5] Configuring environment variables...${NC}"

# Check if already configured
if grep -q "GENESIS_ACCEL_MODE" ~/.bashrc 2>/dev/null; then
    echo "  ℹ️  Acceleration variables already in ~/.bashrc"
else
    cat >> ~/.bashrc <<'EOF'

# Genesis Hardware Acceleration Settings
export GENESIS_ACCEL_MODE=auto          # Auto-detect best device (auto|gpu|npu|cpu)
export ACCEL_BATTERY_MIN=20             # Minimum battery % for GPU/NPU
export ACCEL_TEMP_MAX=70                # Maximum CPU temp (°C) before fallback

# Auto-detect QNN SDK if present
if [ -d "$HOME/qnn" ]; then
    export QNN_SDK_ROOT="$HOME/qnn"
    export LD_LIBRARY_PATH="$QNN_SDK_ROOT/lib/aarch64-android:$LD_LIBRARY_PATH"
fi

EOF
    echo -e "  ${GREEN}✓${NC} Added acceleration settings to ~/.bashrc"
fi

# Load settings for current session
source ~/.bashrc 2>/dev/null || true

echo ""

# ============================================================================
# Step 2: Verify Vulkan GPU Support
# ============================================================================

echo -e "${YELLOW}[2/5] Verifying Vulkan GPU support...${NC}"

# Check Vulkan library
if [ -f "/system/lib64/libvulkan.so" ]; then
    echo -e "  ${GREEN}✓${NC} Vulkan library found: /system/lib64/libvulkan.so"
else
    echo -e "  ${RED}✗${NC} Vulkan library not found (checking alternatives...)"

    # Check alternative locations
    for lib in /vendor/lib64/libvulkan.so /system/lib/libvulkan.so; do
        if [ -f "$lib" ]; then
            echo -e "  ${GREEN}✓${NC} Found Vulkan at: $lib"
            break
        fi
    done
fi

# Test vulkaninfo if available
if command -v vulkaninfo &> /dev/null; then
    echo "  Running vulkaninfo..."
    vulkaninfo --summary 2>&1 | head -10 || echo "  (vulkaninfo check skipped)"
else
    echo "  ℹ️  vulkaninfo not available (optional)"
fi

echo ""

# ============================================================================
# Step 3: Check NPU (QNN SDK) Status
# ============================================================================

echo -e "${YELLOW}[3/5] Checking NPU (QNN SDK) status...${NC}"

if [ -d "$HOME/qnn" ] && [ -f "$HOME/qnn/lib/aarch64-android/libQnnHtp.so" ]; then
    echo -e "  ${GREEN}✓${NC} QNN SDK detected at: $HOME/qnn"
    echo "  Testing QNN adapter..."
    python3 accel_backends/qnn_adapter.py 2>&1 | grep -E "✓|✗|SDK" || true
else
    echo -e "  ${YELLOW}⚠️${NC}  QNN SDK not installed (optional)"
    echo ""
    echo "  To enable NPU acceleration:"
    echo "  1. See MANUAL_QNN_SETUP.md for installation guide"
    echo "  2. Download from: https://qpm.qualcomm.com/"
    echo "  3. Extract to: ~/qnn/"
    echo ""
    echo "  ${BLUE}Note:${NC} GPU acceleration is already fast enough for most use cases!"
fi

echo ""

# ============================================================================
# Step 4: Run Hardware Detection & Benchmarks
# ============================================================================

echo -e "${YELLOW}[4/5] Running hardware detection and benchmarks...${NC}"
echo ""

python3 accel_manager.py

echo ""

# ============================================================================
# Step 5: Validate Installation
# ============================================================================

echo -e "${YELLOW}[5/5] Validating installation...${NC}"
echo ""

# Run test suite
echo "Running detection tests..."
python3 tests/test_accel_detection.py 2>&1 | tail -20

echo ""

# ============================================================================
# Final Status
# ============================================================================

echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

echo "📊 Acceleration Profile:"
cat tmp/bench_cache/accel_bench.json 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f\"  Ranked devices: {' > '.join(data['ranked'])}\")
    print(f\"  Battery: {data['device_info']['battery_pct']}%\")
    print(f\"  Temperature: {data['device_info']['cpu_temp_c']:.1f}°C\")
    print()
    print('  Benchmarks:')
    for dev, bench in data['benchmarks'].items():
        if bench.get('success'):
            print(f\"    {dev.upper():5s}: {bench['gflops']:6.1f} GFLOPS, {bench['latency_s']*1000:6.1f} ms\")
except:
    pass
" 2>/dev/null || echo "  (Profile will be generated on first run)"

echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""

# Check if Vulkan engine exists
if [ -f "engines/llama-cli_vulkan" ] || [ -f "engines/llama_vulkan" ]; then
    echo -e "  ${GREEN}✓${NC} Vulkan engine ready!"
    echo "  ${BLUE}1.${NC} Launch Genesis with GPU acceleration:"
    echo "     export GENESIS_ACCEL_MODE=gpu"
    echo "     python3 genesis.py"
    echo ""
    echo "  ${BLUE}2.${NC} Or let Genesis auto-select (recommended):"
    echo "     export GENESIS_ACCEL_MODE=auto"
    echo "     python3 genesis.py"
else
    echo -e "  ${YELLOW}⚠️${NC}  Vulkan engine building (check build script progress)"
    echo "  ${BLUE}1.${NC} Wait for build to complete:"
    echo "     tail -f ~/Genesis/build.log"
    echo ""
    echo "  ${BLUE}2.${NC} Or check build status:"
    echo "     ps aux | grep build_llama"
fi

echo ""
echo -e "${BLUE}3.${NC} Test GPU inference (after build completes):"
echo "   engines/llama-cli_vulkan -m models/YourModel.gguf -p \"Hello\" -ngl 999"
echo ""

echo -e "${BLUE}4.${NC} Optimize model for GPU (optional):"
echo "   python3 tools/quantize_model.py models/YourModel.gguf --preset gpu_optimized"
echo ""

echo "📖 Documentation:"
echo "  - README.md § Hardware Acceleration"
echo "  - MANUAL_QNN_SETUP.md (for NPU)"
echo "  - ACCELERATION_SUMMARY.md (quick reference)"
echo ""

echo -e "${GREEN}Your S24 Ultra is ready for accelerated AI! 🚀${NC}"
echo -e "${BLUE}================================================${NC}"
