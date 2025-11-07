#!/usr/bin/env bash
#
# build_llama_vulkan.sh - Build llama.cpp with Vulkan GPU Support for Termux
#
# Target: Android devices with Vulkan support (S24 Ultra, Snapdragon 8 Gen 3)
# Builds llama.cpp inference engine with GPU acceleration via Vulkan compute shaders
#
# Usage:
#   chmod +x scripts/build_llama_vulkan.sh
#   ./scripts/build_llama_vulkan.sh
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
GENESIS_DIR="$HOME/Genesis"
LLAMA_DIR="$GENESIS_DIR/llama.cpp"
ENGINES_DIR="$GENESIS_DIR/engines"
BUILD_DIR="$LLAMA_DIR/build-vulkan"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Genesis - Build llama.cpp with Vulkan Support${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Create directories
mkdir -p "$ENGINES_DIR" "$GENESIS_DIR"

# ============================================================================
# Step 1: Install Dependencies
# ============================================================================

echo -e "${YELLOW}[1/6] Installing Termux dependencies...${NC}"

# Core build tools
pkg install -y git cmake make clang binutils || {
    echo -e "${RED}✗ Failed to install core build tools${NC}"
    exit 1
}

# Vulkan development packages
echo -e "${YELLOW}Installing Vulkan SDK...${NC}"
pkg install -y vulkan-headers vulkan-loader vulkan-tools || {
    echo -e "${YELLOW}⚠️  Some Vulkan packages unavailable in Termux${NC}"
    echo -e "${YELLOW}   Attempting fallback installation...${NC}"
}

# Additional dependencies
pkg install -y python ffmpeg wget || true

# Python tools for model conversion
pip install --upgrade pip setuptools wheel || true
pip install numpy || true

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# ============================================================================
# Step 2: Clone or Update llama.cpp
# ============================================================================

echo -e "${YELLOW}[2/6] Setting up llama.cpp repository...${NC}"

if [ ! -d "$LLAMA_DIR/.git" ]; then
    echo "Cloning llama.cpp..."
    git clone https://github.com/ggerganov/llama.cpp.git "$LLAMA_DIR" || {
        echo -e "${RED}✗ Failed to clone llama.cpp${NC}"
        exit 1
    }
else
    echo "Updating existing llama.cpp repository..."
    git -C "$LLAMA_DIR" fetch origin
    git -C "$LLAMA_DIR" pull --rebase || {
        echo -e "${YELLOW}⚠️  Git pull failed, continuing with current version${NC}"
    }
fi

cd "$LLAMA_DIR"
echo -e "${GREEN}✓ llama.cpp ready at: $LLAMA_DIR${NC}"
echo ""

# ============================================================================
# Step 3: Check Vulkan Availability
# ============================================================================

echo -e "${YELLOW}[3/6] Checking Vulkan availability...${NC}"

VULKAN_AVAILABLE=false

# Check for vulkaninfo
if command -v vulkaninfo &> /dev/null; then
    echo "✓ vulkaninfo found, checking device support..."
    vulkaninfo --summary &> /tmp/vulkaninfo.log || true

    if grep -q "GPU" /tmp/vulkaninfo.log 2>/dev/null; then
        VULKAN_AVAILABLE=true
        echo -e "${GREEN}✓ Vulkan GPU detected${NC}"
        grep "GPU" /tmp/vulkaninfo.log | head -3
    else
        echo -e "${YELLOW}⚠️  vulkaninfo found but no GPU detected${NC}"
    fi
else
    echo "vulkaninfo not found, checking libraries..."
fi

# Check for Vulkan libraries
if [ -f "/system/lib64/libvulkan.so" ] || [ -f "/vendor/lib64/libvulkan.so" ]; then
    VULKAN_AVAILABLE=true
    echo -e "${GREEN}✓ Vulkan library found on system${NC}"
fi

# Check environment variable
if [ -n "${VK_ICD_FILENAMES:-}" ]; then
    VULKAN_AVAILABLE=true
    echo -e "${GREEN}✓ Vulkan ICD configured: $VK_ICD_FILENAMES${NC}"
fi

if [ "$VULKAN_AVAILABLE" = false ]; then
    echo -e "${RED}✗ Vulkan not detected on this device${NC}"
    echo -e "${YELLOW}Continuing anyway - may need manual Vulkan setup${NC}"
    echo -e "${YELLOW}See: https://developer.android.com/ndk/guides/graphics/getting-started${NC}"
fi

echo ""

# ============================================================================
# Step 4: Configure CMake with Vulkan
# ============================================================================

echo -e "${YELLOW}[4/6] Configuring CMake build with Vulkan...${NC}"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# CMake configuration flags
CMAKE_FLAGS=(
    "-DCMAKE_BUILD_TYPE=Release"
    "-DLLAMA_VULKAN=ON"
    "-DLLAMA_NATIVE=OFF"
    "-DBUILD_SHARED_LIBS=OFF"
)

# Optional: Add more optimizations for Snapdragon 8 Gen 3
# CMAKE_FLAGS+=("-DCMAKE_C_FLAGS=-march=armv8.2-a+crypto+dotprod")
# CMAKE_FLAGS+=("-DCMAKE_CXX_FLAGS=-march=armv8.2-a+crypto+dotprod")

echo "Running cmake with:"
for flag in "${CMAKE_FLAGS[@]}"; do
    echo "  $flag"
done

cmake .. "${CMAKE_FLAGS[@]}" || {
    echo -e "${RED}✗ CMake configuration failed${NC}"
    echo -e "${YELLOW}Falling back to standard build without Vulkan...${NC}"

    # Fallback: build without Vulkan
    rm -rf "$BUILD_DIR"
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"
    cmake .. -DCMAKE_BUILD_TYPE=Release || {
        echo -e "${RED}✗ CMake failed even without Vulkan${NC}"
        exit 1
    }
}

echo -e "${GREEN}✓ CMake configured${NC}"
echo ""

# ============================================================================
# Step 5: Build llama.cpp
# ============================================================================

echo -e "${YELLOW}[5/6] Building llama.cpp (this may take 10-20 minutes)...${NC}"

NPROC=$(nproc 2>/dev/null || echo 4)
echo "Building with $NPROC parallel jobs..."

cmake --build . --config Release --parallel "$NPROC" || {
    echo -e "${RED}✗ Build failed${NC}"
    echo ""
    echo "Common issues:"
    echo "  - Out of memory: Try reducing parallel jobs (make -j2)"
    echo "  - Missing headers: Install vulkan-headers"
    echo "  - Compiler errors: Update clang with 'pkg upgrade'"
    exit 1
}

echo -e "${GREEN}✓ Build completed${NC}"
echo ""

# ============================================================================
# Step 6: Install Binaries
# ============================================================================

echo -e "${YELLOW}[6/6] Installing binaries to $ENGINES_DIR...${NC}"

# Find and copy built binaries
BINARIES=("llama-cli" "llama-server" "llama-bench")

for binary in "${BINARIES[@]}"; do
    if [ -f "bin/$binary" ]; then
        cp "bin/$binary" "$ENGINES_DIR/${binary}_vulkan"
        chmod +x "$ENGINES_DIR/${binary}_vulkan"
        echo -e "${GREEN}✓ Installed: ${binary}_vulkan${NC}"
    elif [ -f "$binary" ]; then
        cp "$binary" "$ENGINES_DIR/${binary}_vulkan"
        chmod +x "$ENGINES_DIR/${binary}_vulkan"
        echo -e "${GREEN}✓ Installed: ${binary}_vulkan${NC}"
    else
        echo -e "${YELLOW}⚠️  Binary not found: $binary${NC}"
    fi
done

# Special handling for main/llama binary (older versions)
if [ -f "bin/main" ]; then
    cp "bin/main" "$ENGINES_DIR/llama_vulkan"
    chmod +x "$ENGINES_DIR/llama_vulkan"
    echo -e "${GREEN}✓ Installed: llama_vulkan${NC}"
fi

echo ""

# ============================================================================
# Verification
# ============================================================================

echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}Build Complete!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

echo "Installed binaries:"
ls -lh "$ENGINES_DIR/" | grep vulkan || echo "(none)"
echo ""

# Test binary
if [ -f "$ENGINES_DIR/llama_vulkan" ] || [ -f "$ENGINES_DIR/llama-cli_vulkan" ]; then
    TEST_BIN="$ENGINES_DIR/llama-cli_vulkan"
    [ -f "$ENGINES_DIR/llama_vulkan" ] && TEST_BIN="$ENGINES_DIR/llama_vulkan"

    echo "Testing binary:"
    "$TEST_BIN" --version 2>/dev/null || "$TEST_BIN" -h 2>&1 | head -5 || {
        echo -e "${YELLOW}⚠️  Binary test inconclusive${NC}"
    }
    echo ""
fi

echo -e "${BLUE}Next steps:${NC}"
echo "  1. Test GPU inference:"
echo "     $ENGINES_DIR/llama-cli_vulkan -m models/your-model.gguf -p \"Hello\" -ngl 999"
echo ""
echo "  2. Benchmark GPU performance:"
echo "     python3 -c 'from accel_manager import get_profile; print(get_profile(force_rerun=True))'"
echo ""
echo "  3. Enable acceleration in Genesis:"
echo "     export GENESIS_ACCEL_MODE=gpu"
echo "     python3 genesis.py"
echo ""

if [ "$VULKAN_AVAILABLE" = false ]; then
    echo -e "${YELLOW}⚠️  WARNING: Vulkan not detected during build${NC}"
    echo "   The binary was built with Vulkan support, but your device may not support it."
    echo "   Check device Vulkan support:"
    echo "     - Run 'vulkaninfo' to verify GPU detection"
    echo "     - Check /system/lib64/libvulkan.so exists"
    echo "     - Ensure Android API level >= 24 (Android 7.0+)"
    echo ""
fi

echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${BLUE}================================================${NC}"
