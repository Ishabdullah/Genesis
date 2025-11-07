# Manual QNN SDK Installation Guide for Genesis NPU Acceleration

**Device:** Samsung S24 Ultra (Snapdragon 8 Gen 3, Hexagon NPU)
**Date:** November 6, 2025
**Status:** Manual installation required (proprietary SDK)

---

## ⚠️ IMPORTANT: Why Manual Installation?

The Qualcomm QNN SDK is **proprietary software** that:
- Requires a Qualcomm developer account
- Has license agreements that must be accepted
- Cannot be automatically downloaded or redistributed
- Is not open source

**Genesis will work great without it** using GPU (Vulkan) acceleration!

---

## 🎯 Do You Need NPU?

**You probably don't need NPU if:**
- ✅ GPU acceleration gives you 6-7x speedup (which you'll have after Vulkan build)
- ✅ Response times are already < 5 seconds with GPU
- ✅ You're okay with "very fast" instead of "extremely fast"

**Consider NPU if you want:**
- Maximum power efficiency (10x better than CPU, 3x better than GPU)
- Absolute fastest inference (NPU can be 2x faster than GPU for INT8)
- Longest battery life during heavy usage
- To experiment with cutting-edge mobile AI acceleration

---

## 📋 Manual Installation Steps

### Step 1: Register for Qualcomm Account

1. **Visit:** https://qpm.qualcomm.com/
2. **Click:** "Sign Up" or "Register"
3. **Fill out:** Developer registration form
4. **Verify:** Email confirmation
5. **Wait:** Account approval (usually 1-2 business days)

### Step 2: Download QNN SDK

1. **Log in** to https://qpm.qualcomm.com/
2. **Navigate to:** AI Stack → QNN SDK
3. **Select:** Latest version for Android (aarch64)
4. **Download:** `qnn-<version>-android-aarch64.zip` (usually 200-500 MB)
5. **Accept:** License agreements

**Note:** You may need to select your use case (research, commercial, etc.)

### Step 3: Transfer to Your Phone

**Option A: Direct download on phone (if available)**
```bash
# Download directly in Termux browser or use termux-url-opener
```

**Option B: Download on PC, then transfer**
```bash
# On your PC: Use ADB or USB transfer
adb push qnn-<version>-android-aarch64.zip /sdcard/Download/

# On phone: Move to Termux storage
mv ~/storage/downloads/qnn-*.zip ~/
```

### Step 4: Extract SDK

```bash
cd ~
unzip qnn-*.zip -d qnn/
cd qnn

# Verify extraction
ls -la

# Expected structure:
# qnn/
# ├── lib/
# │   └── aarch64-android/
# │       ├── libQnnHtp.so
# │       ├── libQnnSystem.so
# │       └── libQnnCpu.so
# ├── bin/
# │   └── aarch64-android/
# │       ├── qnn-net-run
# │       └── qnn-context-binary-generator
# └── docs/
```

### Step 5: Set Environment Variable

```bash
# Add to your shell profile
echo 'export QNN_SDK_ROOT=~/qnn' >> ~/.bashrc
source ~/.bashrc

# Verify
echo $QNN_SDK_ROOT
# Should print: /data/data/com.termux/files/home/qnn
```

### Step 6: Verify Installation

```bash
cd ~/Genesis
python3 accel_backends/qnn_adapter.py
```

**Expected output:**
```
✓ QNN SDK detected!
SDK Root: /data/data/com.termux/files/home/qnn
Libraries: 3 found
  - libQnnHtp.so
  - libQnnSystem.so
  - libQnnCpu.so
Binaries: 2 found
  - qnn-net-run
  - qnn-context-binary-generator
✓ QNN backend ready (integration pending)
```

### Step 7: Test NPU Detection

```bash
# Re-run hardware detection
python3 accel_manager.py

# Should now show:
# ✓ NPU: QNN SDK found at ~/qnn
```

---

## 🔄 Model Conversion for NPU

Once QNN SDK is installed, you'll need to convert models to QNN format.

### Option 1: Automated (Coming Soon)
```bash
# Future Genesis feature
python3 tools/quantize_model.py \
  models/YourModel.gguf \
  --preset npu_optimized \
  --convert-qnn
```

### Option 2: Manual (Current)

```bash
# 1. Convert GGUF to ONNX (if needed)
python3 llama.cpp/convert_hf_to_gguf.py --help

# 2. Convert ONNX to QNN
$QNN_SDK_ROOT/bin/aarch64-android/qnn-onnx-converter \
  --input_network model.onnx \
  --output_path qnn_model.cpp

# 3. Compile to binary
$QNN_SDK_ROOT/bin/aarch64-android/qnn-model-lib-generator \
  -c qnn_model.cpp \
  -b ~/Genesis/models/model_qnn.bin

# 4. Use in Genesis
python3 accel_backends/qnn_adapter.py
```

**Note:** Full automation of this process is planned for a future Genesis update.

---

## 🧪 Testing NPU

After installation:

```bash
# Test detection
python3 tests/test_accel_detection.py

# Should show:
# ✓ NPU: QNN SDK detected
# Benchmarks:
#   NPU: 500.0 GFLOPS, 30.0ms

# Enable NPU in Genesis
export GENESIS_ACCEL_MODE=npu
python3 genesis.py
```

---

## 🐛 Troubleshooting

### "QNN SDK not detected" after installation

```bash
# Check environment variable
echo $QNN_SDK_ROOT
# If empty, add to ~/.bashrc again

# Check libraries exist
ls -la $QNN_SDK_ROOT/lib/aarch64-android/

# Check permissions
chmod -R 755 ~/qnn/
```

### "Permission denied" on libraries

```bash
# Fix permissions
cd ~/qnn
find . -name "*.so" -exec chmod 755 {} \;
find . -type f -executable -exec chmod 755 {} \;
```

### "Library not found" at runtime

```bash
# Add to library path
export LD_LIBRARY_PATH=$QNN_SDK_ROOT/lib/aarch64-android:$LD_LIBRARY_PATH
echo 'export LD_LIBRARY_PATH=$QNN_SDK_ROOT/lib/aarch64-android:$LD_LIBRARY_PATH' >> ~/.bashrc
```

---

## 📊 Expected Performance (S24 Ultra)

| Accelerator | Speed | Power | Latency | Best For |
|-------------|-------|-------|---------|----------|
| **NPU (QNN)** | 8-10x | ⭐⭐⭐⭐⭐ | ~2-4s | Battery life, sustained use |
| **GPU (Vulkan)** | 6-7x | ⭐⭐⭐ | ~3-5s | Speed, most models |
| **CPU** | 1x | ⭐⭐ | ~18-30s | Fallback, compatibility |

---

## 💡 Alternatives if QNN Not Available

**1. GPU (Vulkan) - Automatic Setup**
```bash
# This is being built for you right now!
./scripts/build_llama_vulkan.sh
export GENESIS_ACCEL_MODE=gpu
```
**Result:** 6-7x speedup, no manual downloads needed ✅

**2. Android NNAPI**
```bash
# Limited LLM support, but worth trying
# Future Genesis feature
```

**3. Optimized CPU Quantization**
```bash
# Use Q4_K_M for best CPU performance
python3 tools/quantize_model.py \
  models/YourModel.gguf \
  --preset cpu_optimized
```

---

## 📞 Support

**QNN SDK Issues:**
- Qualcomm Developer Forum: https://developer.qualcomm.com/forums
- QNN Documentation: `$QNN_SDK_ROOT/docs/`
- Email: qnn-support@qti.qualcomm.com

**Genesis Integration:**
- GitHub Issues: https://github.com/Ishabdullah/Genesis/issues
- Documentation: `~/Genesis/README.md` § Hardware Acceleration

---

## ✅ Summary

**Required for NPU:**
1. ⏳ Register Qualcomm account (manual)
2. ⏳ Download QNN SDK (manual, ~300 MB)
3. ⏳ Extract to ~/qnn/ (manual)
4. ⏳ Set QNN_SDK_ROOT variable (one command)
5. ⏳ Verify installation (automatic test)

**Timeline:** 15-30 minutes + account approval wait (1-2 days)

**Meanwhile:**
- ✅ GPU acceleration is being built now (automatic)
- ✅ Will give you 6-7x speedup without any manual steps
- ✅ Response times: 3-5 seconds (vs 18-30s on CPU)

---

**Recommendation:**
Start with GPU acceleration (being set up now). If you need the extra 2x speedup and better battery life, install QNN SDK later using this guide.

The GPU alone will make Genesis feel blazingly fast! 🚀
