#!/data/data/com.termux/files/usr/bin/bash
# Genesis Environment Setup Script
# This script sets up a complete Claude-Code-like AI workstation in Termux

set -e  # Exit on any error

echo "🧬 Genesis Setup — Building Local AI Workstation"
echo "================================================"
echo ""

# Step 1: Update and install core packages
echo "[1/6] Installing core packages..."
pkg update -y && pkg upgrade -y
pkg install git python python-pip nodejs clang cmake wget curl vim nano build-essential -y

echo ""
echo "[2/6] Installing Python dependencies..."
pip install --upgrade pip
pip install colorama prompt_toolkit flask requests

# Step 2: Create Genesis directory structure
echo ""
echo "[3/6] Creating Genesis directory structure..."
cd ~
mkdir -p ~/Genesis/runtime
mkdir -p ~/Genesis/models
cd ~/Genesis

# Step 3: Clone and build llama.cpp
echo ""
echo "[4/6] Cloning and building llama.cpp..."
if [ -d "llama.cpp" ]; then
    echo "llama.cpp already exists, pulling latest changes..."
    cd llama.cpp
    git pull
    cd ..
else
    git clone https://github.com/ggerganov/llama.cpp
fi

cd llama.cpp
echo "Building llama.cpp (this may take 5-10 minutes)..."
make clean
make -j$(nproc)
cd ..

# Step 4: Link the LLM model
echo ""
echo "[5/6] Linking LLM model..."
LLM_SOURCE="$HOME/storage/downloads/LLM_Models/CodeLlama-7B-Instruct.Q4_K_M.gguf"
LLM_TARGET="./models/CodeLlama-7B-Instruct.Q4_K_M.gguf"

if [ -f "$LLM_SOURCE" ]; then
    ln -sf "$LLM_SOURCE" "$LLM_TARGET"
    echo "✓ Model linked successfully"
else
    echo "⚠ Warning: Model not found at $LLM_SOURCE"
    echo "Please ensure the model exists at that location"
fi

# Step 5: Set up shell alias
echo ""
echo "[6/6] Setting up Genesis command alias..."

# Determine which shell config to use
if [ -f ~/.bashrc ]; then
    SHELL_CONFIG=~/.bashrc
elif [ -f ~/.zshrc ]; then
    SHELL_CONFIG=~/.zshrc
else
    SHELL_CONFIG=~/.bashrc
    touch $SHELL_CONFIG
fi

# Add alias if not already present
if ! grep -q "alias Genesis=" "$SHELL_CONFIG"; then
    echo "" >> "$SHELL_CONFIG"
    echo "# Genesis AI Workstation" >> "$SHELL_CONFIG"
    echo "alias Genesis='cd ~/Genesis && python genesis.py'" >> "$SHELL_CONFIG"
    echo "✓ Added Genesis alias to $SHELL_CONFIG"
else
    echo "✓ Genesis alias already exists in $SHELL_CONFIG"
fi

# Step 6: Create initial memory file
echo '{"conversations": [], "context": {}}' > memory.json

echo ""
echo "================================================"
echo "✓ Genesis setup complete!"
echo ""
echo "To start Genesis, run:"
echo "  source $SHELL_CONFIG"
echo "  Genesis"
echo ""
echo "Or restart your Termux session and type: Genesis"
echo "================================================"
