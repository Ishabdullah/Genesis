#!/data/data/com.termux/files/usr/bin/bash
# Genesis Setup Verification Script
# Checks that all components are properly installed

echo "🧬 Genesis Setup Verification"
echo "=============================="
echo ""

errors=0
warnings=0

# Check 1: Core Python files
echo "[1/10] Checking core Python files..."
for file in genesis.py memory.py executor.py tools.py genesis_bridge.py; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file missing"
        ((errors++))
    fi
done
echo ""

# Check 2: Documentation files
echo "[2/10] Checking documentation..."
for file in README.md INSTALL.md QUICK_START.md BRIDGE_GUIDE.md SETUP_COMPLETE.md; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ⚠ $file missing"
        ((warnings++))
    fi
done
echo ""

# Check 3: Scripts
echo "[3/10] Checking scripts..."
for file in setup_genesis.sh test_bridge.sh; do
    if [ -f "$file" ]; then
        if [ -x "$file" ]; then
            echo "  ✓ $file (executable)"
        else
            echo "  ⚠ $file (not executable - run: chmod +x $file)"
            ((warnings++))
        fi
    else
        echo "  ✗ $file missing"
        ((errors++))
    fi
done
echo ""

# Check 4: Python dependencies
echo "[4/10] Checking Python dependencies..."
for module in flask requests colorama; do
    if python -c "import $module" 2>/dev/null; then
        echo "  ✓ $module installed"
    else
        echo "  ✗ $module missing (run: pip install $module)"
        ((errors++))
    fi
done
echo ""

# Check 5: Directory structure
echo "[5/10] Checking directory structure..."
for dir in runtime models; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir/ directory exists"
    else
        echo "  ⚠ $dir/ directory missing (will be created on first run)"
        ((warnings++))
    fi
done
echo ""

# Check 6: llama.cpp
echo "[6/10] Checking llama.cpp..."
if [ -d "llama.cpp" ]; then
    echo "  ✓ llama.cpp directory exists"

    # Check for binary
    found_binary=false
    for binary in llama.cpp/llama-cli llama.cpp/main llama.cpp/build/bin/llama-cli; do
        if [ -f "$binary" ]; then
            echo "  ✓ Binary found: $binary"
            found_binary=true
            break
        fi
    done

    if [ "$found_binary" = false ]; then
        echo "  ✗ llama.cpp binary not found (run setup_genesis.sh to build)"
        ((errors++))
    fi
else
    echo "  ✗ llama.cpp not found (run setup_genesis.sh to install)"
    ((errors++))
fi
echo ""

# Check 7: Model file
echo "[7/10] Checking LLM model..."
model_path="models/CodeLlama-7B-Instruct.Q4_K_M.gguf"
if [ -L "$model_path" ] || [ -f "$model_path" ]; then
    if [ -e "$model_path" ]; then
        size=$(stat -f%z "$model_path" 2>/dev/null || stat -c%s "$model_path" 2>/dev/null || echo "unknown")
        echo "  ✓ Model linked/exists (size: $size bytes)"
    else
        echo "  ✗ Model link is broken"
        ((errors++))
    fi
else
    echo "  ⚠ Model not linked (run setup_genesis.sh or link manually)"
    ((warnings++))
fi
echo ""

# Check 8: Shell alias
echo "[8/10] Checking shell alias..."
if grep -q "alias Genesis=" ~/.bashrc 2>/dev/null || grep -q "alias Genesis=" ~/.zshrc 2>/dev/null; then
    echo "  ✓ Genesis alias configured"
else
    echo "  ⚠ Genesis alias not found (run setup_genesis.sh or add manually)"
    ((warnings++))
fi
echo ""

# Check 9: File permissions
echo "[9/10] Checking file permissions..."
if [ -r "genesis.py" ] && [ -r "memory.py" ] && [ -r "executor.py" ]; then
    echo "  ✓ Core files are readable"
else
    echo "  ✗ Permission issues with core files"
    ((errors++))
fi
echo ""

# Check 10: Python version
echo "[10/10] Checking Python version..."
python_version=$(python --version 2>&1 | cut -d' ' -f2)
echo "  ✓ Python $python_version"
echo ""

# Summary
echo "=============================="
echo "Verification Summary"
echo "=============================="
echo ""

if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    echo "✓ All checks passed! Genesis is ready to use."
    echo ""
    echo "To start Genesis:"
    echo "  Genesis"
    echo ""
    echo "Or run setup first:"
    echo "  ./setup_genesis.sh"
    exit 0
elif [ $errors -eq 0 ]; then
    echo "⚠ Setup is mostly complete with $warnings warning(s)"
    echo ""
    echo "You can proceed, but consider running:"
    echo "  ./setup_genesis.sh"
    exit 0
else
    echo "✗ Found $errors error(s) and $warnings warning(s)"
    echo ""
    echo "Please run the setup script:"
    echo "  ./setup_genesis.sh"
    exit 1
fi
