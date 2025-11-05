#!/data/data/com.termux/files/usr/bin/bash
# Test llama.cpp directly to diagnose issues

echo "🧬 Testing llama.cpp directly..."
echo ""

cd ~/Genesis

# Check if binary exists
if [ ! -f "llama.cpp/build/bin/llama-cli" ]; then
    echo "❌ llama-cli not found!"
    exit 1
fi

# Check if model exists
if [ ! -f "models/CodeLlama-7B-Instruct.Q4_K_M.gguf" ]; then
    echo "❌ Model not found!"
    exit 1
fi

echo "✓ Binary found: llama.cpp/build/bin/llama-cli"
echo "✓ Model found: models/CodeLlama-7B-Instruct.Q4_K_M.gguf"
echo ""
echo "Testing with simple prompt..."
echo ""

# Test with very simple prompt
./llama.cpp/build/bin/llama-cli \
    -m ./models/CodeLlama-7B-Instruct.Q4_K_M.gguf \
    -p "Write a hello world function in Python." \
    -n 128 \
    -t 8 \
    -c 512 \
    --temp 0.7 \
    -ngl 0

echo ""
echo ""
echo "Test complete. If you see output above, the model is working."
