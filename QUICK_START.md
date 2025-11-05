# Genesis Quick Start Guide

## Installation (One-Time Setup)

```bash
cd ~/Genesis
chmod +x setup_genesis.sh
./setup_genesis.sh
source ~/.bashrc
```

Wait 10-15 minutes for setup to complete.

## Launch Genesis

```bash
Genesis
```

## Essential Commands

| Command | Description |
|---------|-------------|
| `#exit` | Quit Genesis |
| `#reset` | Clear memory |
| `#help` | Show help |
| `#stats` | Memory stats |
| `#pwd` | Current directory |

## Example Usage

### 1. Simple Code Execution

```
Genesis> Write a Python script to print "Hello, World!"
```

Genesis will generate and execute the code automatically.

### 2. File Operations

```
Genesis> Read the file config.json

Genesis> List all files in /data/data/com.termux/files/home

Genesis> Write a script to test.py that calculates factorial
```

### 3. Complex Tasks

```
Genesis> Create a Python function that:
1. Takes a list of numbers
2. Filters out duplicates
3. Returns sorted unique values
```

### 4. Multiline Input

Use backslash (`\`) to continue:

```
Genesis> Write a script that: \
      > 1. Reads a CSV file \
      > 2. Calculates averages \
      > 3. Outputs results
```

## First Run

When you launch Genesis for the first time:

1. **Model loads** (30-45 seconds first response)
2. **Subsequent responses** (10-20 seconds typical)
3. **Memory persists** between sessions

## Tips

- Be specific in your requests
- Ask for code in triple backticks when needed
- Use file paths clearly
- Check `#stats` periodically
- Use `#reset` if context gets confused

## Troubleshooting

**Slow responses?**
- First response is always slower (model loading)
- Reduce prompt complexity
- Clear memory with `#reset`

**Code won't execute?**
- Check syntax in generated code
- Try asking for simpler version
- Review error messages

**File operations fail?**
- Verify file paths exist
- Check permissions
- Use absolute paths when possible

## Learn More

- Full documentation: `cat ~/Genesis/README.md`
- Installation help: `cat ~/Genesis/INSTALL.md`
- Code examples in README.md

## System Architecture

```
User Input → Genesis Controller → LLM (CodeLlama)
                ↓
         Response Processing
                ↓
    ┌───────────┴───────────┐
    ↓           ↓           ↓
File Tools   Code Exec   Memory
```

Everything runs locally. No internet required after setup.

---

**Quick Start Time**: 2 minutes (after installation)
**Typical Response**: 10-20 seconds
**Memory Limit**: Last 20 conversations
