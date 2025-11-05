# Genesis Installation Guide

Quick installation instructions for Genesis AI Workstation.

## Pre-Installation Checklist

- [ ] Termux installed and updated
- [ ] At least 8GB free storage
- [ ] CodeLlama model downloaded to: `~/storage/downloads/LLM_Models/CodeLlama-7B-Instruct.Q4_K_M.gguf`
- [ ] Stable internet connection (for initial setup only)

## Installation Steps

### Step 1: Navigate to Genesis Directory

```bash
cd ~/Genesis
```

All Genesis files should already be present:
- `setup_genesis.sh` - Setup script
- `genesis.py` - Main controller
- `memory.py` - Memory manager
- `executor.py` - Code executor
- `tools.py` - File system tools
- `README.md` - Full documentation

### Step 2: Make Setup Script Executable

```bash
chmod +x setup_genesis.sh
```

### Step 3: Run Setup

```bash
./setup_genesis.sh
```

This will take 10-15 minutes and will:

1. **Update Termux packages** (2-3 min)
   - Updates pkg database
   - Installs git, python, nodejs, build tools

2. **Install Python dependencies** (1 min)
   - colorama (for colored output)
   - prompt_toolkit (for better input handling)

3. **Build llama.cpp** (5-10 min)
   - Clones the repository
   - Compiles optimized binaries
   - This is the longest step

4. **Link LLM model** (instant)
   - Creates symlink to your model
   - Verifies model exists

5. **Configure shell alias** (instant)
   - Adds `Genesis` command to your shell

### Step 4: Reload Shell Configuration

```bash
source ~/.bashrc
```

Or restart Termux.

### Step 5: Verify Installation

```bash
Genesis
```

You should see:

```
============================================================
🧬 Genesis — Local AI Workstation
Powered by CodeLlama-7B running on Samsung S24 Ultra
============================================================

Commands: #exit (quit) | #reset (clear memory) | #help (show help)

✓ System ready

Genesis>
```

## Testing Genesis

### Test 1: Basic Interaction

```
Genesis> Hello, what can you do?
```

Expected: Genesis introduces itself and explains capabilities.

### Test 2: Simple Math

```
Genesis> Write a Python script to calculate 2 + 2
```

Expected: Genesis writes and executes code, shows result "4".

### Test 3: File Operations

```
Genesis> List files in the current directory
```

Expected: Genesis shows directory listing.

### Test 4: Code Generation

```
Genesis> Create a function that checks if a number is prime
```

Expected: Genesis generates working prime-checking code.

## Troubleshooting Installation

### Problem: "pkg: command not found"

**Solution**: You're not in Termux. Open Termux app and try again.

### Problem: "Permission denied" when running setup

**Solution**: Make script executable:
```bash
chmod +x setup_genesis.sh
```

### Problem: Build fails with "clang: not found"

**Solution**: Install build tools manually:
```bash
pkg install clang make cmake -y
```

### Problem: "No space left on device"

**Solution**: Free up space:
```bash
# Check available space
df -h

# Clean package cache
pkg clean

# Remove unnecessary files
apt autoremove -y
```

You need at least 8GB free.

### Problem: Model file not found

**Solution**: Check model location:
```bash
ls -lh ~/storage/downloads/LLM_Models/
```

If model is elsewhere, update path in setup script or create manual symlink:
```bash
ln -sf /path/to/your/model.gguf ~/Genesis/models/CodeLlama-7B-Instruct.Q4_K_M.gguf
```

### Problem: Python imports fail

**Solution**: Reinstall Python dependencies:
```bash
pip install --upgrade pip
pip install colorama prompt_toolkit
```

### Problem: llama.cpp build fails

**Solution**: Try building with fewer parallel jobs:
```bash
cd ~/Genesis/llama.cpp
make clean
make -j2  # Use only 2 threads instead of all cores
```

### Problem: "Genesis: command not found"

**Solution**: Alias not loaded. Reload shell:
```bash
source ~/.bashrc
```

Or use full path:
```bash
cd ~/Genesis && python genesis.py
```

## Manual Installation (If Setup Script Fails)

If the automated setup doesn't work, follow these manual steps:

### 1. Install Packages

```bash
pkg update && pkg upgrade -y
pkg install git python python-pip clang cmake wget -y
```

### 2. Install Python Packages

```bash
pip install colorama prompt_toolkit
```

### 3. Create Directory Structure

```bash
mkdir -p ~/Genesis/runtime
mkdir -p ~/Genesis/models
cd ~/Genesis
```

### 4. Clone and Build llama.cpp

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make clean
make -j$(nproc)
cd ..
```

### 5. Link Model

```bash
ln -sf ~/storage/downloads/LLM_Models/CodeLlama-7B-Instruct.Q4_K_M.gguf \
       ./models/CodeLlama-7B-Instruct.Q4_K_M.gguf
```

### 6. Create Memory File

```bash
echo '{"conversations": [], "context": {}}' > memory.json
```

### 7. Add Alias

```bash
echo 'alias Genesis="cd ~/Genesis && python genesis.py"' >> ~/.bashrc
source ~/.bashrc
```

### 8. Test

```bash
Genesis
```

## Post-Installation

### Verify All Components

```bash
# Check Genesis files
ls -lh ~/Genesis/

# Check llama.cpp binary
ls -lh ~/Genesis/llama.cpp/llama-cli

# Check model link
ls -lh ~/Genesis/models/

# Check Python can import modules
python -c "import memory, executor, tools; print('✓ All modules OK')"
```

All should show files without errors.

### First Run Checklist

When you run Genesis for the first time:

- [ ] Header displays correctly
- [ ] "System ready" message appears
- [ ] `Genesis>` prompt shows
- [ ] Can type commands
- [ ] `#help` shows help menu
- [ ] `#exit` exits cleanly

### Performance Check

Test response time:

```
Genesis> What is 2+2?
```

First response may take 30-45 seconds (model loading).
Subsequent responses should be 10-20 seconds.

If responses take > 60 seconds, see README.md for optimization tips.

## Updating Genesis

To update Genesis code without reinstalling:

```bash
cd ~/Genesis
# Update Python files as needed
# No need to rebuild llama.cpp unless version changes
```

To update llama.cpp:

```bash
cd ~/Genesis/llama.cpp
git pull
make clean
make -j$(nproc)
```

## Uninstallation

To remove Genesis:

```bash
# Remove Genesis directory
rm -rf ~/Genesis

# Remove alias from shell config
sed -i '/alias Genesis=/d' ~/.bashrc

# Reload shell
source ~/.bashrc
```

Model file will remain in original location.

## Getting Help

If installation fails:

1. Check error messages carefully
2. Verify prerequisites are met
3. Try manual installation steps
4. Check storage space: `df -h`
5. Verify model exists: `ls -lh ~/storage/downloads/LLM_Models/`

## Next Steps

Once installed:

1. Read `README.md` for full documentation
2. Try example prompts
3. Explore file operations
4. Test code generation
5. Customize system prompt if desired

---

**Installation Time**: ~15 minutes
**Disk Space Required**: ~8GB
**Tested On**: Samsung S24 Ultra, Termux 0.118+
