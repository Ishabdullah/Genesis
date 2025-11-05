# 🧬 Genesis - Local AI Workstation

A complete Claude-Code-like environment running entirely in Termux on Android.

## Overview

Genesis is a local AI assistant powered by CodeLlama-7B that runs on your Samsung S24 Ultra. It provides:

- **Code execution**: Write and run Python code safely
- **File operations**: Read, write, and manage files
- **Conversation memory**: Maintains context across interactions
- **Zero cloud dependency**: Everything runs locally

## Architecture

```
Genesis/
├── genesis.py          # Main controller
├── memory.py           # Conversation memory manager
├── executor.py         # Safe code execution
├── tools.py            # File system tools
├── llama.cpp/          # LLM inference engine
├── models/             # LLM model storage
├── runtime/            # Temporary execution files
└── memory.json         # Persistent conversation history
```

## Installation

### Prerequisites

- Termux installed on Android device
- At least 8GB free storage
- CodeLlama model at: `~/storage/downloads/LLM_Models/CodeLlama-7B-Instruct.Q4_K_M.gguf`

### Setup Steps

1. **Run the setup script:**
   ```bash
   cd ~/Genesis
   chmod +x setup_genesis.sh
   ./setup_genesis.sh
   ```

   This will:
   - Install required packages (Python, git, build tools)
   - Clone and build llama.cpp
   - Link your LLM model
   - Set up the Genesis command alias

2. **Reload your shell:**
   ```bash
   source ~/.bashrc
   ```

3. **Launch Genesis:**
   ```bash
   Genesis
   ```

## Usage

### Basic Commands

- `#exit` - Quit Genesis
- `#reset` - Clear conversation memory
- `#help` - Show help information
- `#stats` - Display memory statistics
- `#pwd` - Show current directory

### File Operations

Genesis can perform file operations through natural language:

```
Genesis> Read the file config.json

Genesis> Write a Python script that prints "Hello World" to hello.py

Genesis> List all files in the current directory

Genesis> Show me the contents of /data/data/com.termux/files/home
```

### Code Execution

Ask Genesis to write code and it will execute automatically:

```
Genesis> Write a script to calculate the first 10 Fibonacci numbers
```

Genesis will:
1. Generate Python code
2. Execute it in a safe subprocess
3. Display the output

### Multiline Input

Use backslash (`\`) for multiline prompts:

```
Genesis> Write a Python function that: \
      > 1. Takes a list of numbers \
      > 2. Filters out odd numbers \
      > 3. Returns the sum of even numbers
```

## System Prompt

Genesis uses the following system prompt:

```
You are Genesis, a helpful AI assistant running locally on a Samsung S24 Ultra.
You can execute Python code, read and write files, and help with programming tasks.

When you need to perform actions:
- To execute Python code, wrap it in triple backticks with 'python' language marker
- To read a file, mention "READ: filepath"
- To write a file, mention "WRITE: filepath" followed by content
- To list a directory, mention "LIST: dirpath"
```

## Memory Management

Genesis maintains conversation history in `memory.json`:

- **Automatic saving**: Every interaction is saved
- **Context window**: Last 10 interactions used for context
- **Maximum storage**: 20 most recent conversations
- **Manual reset**: Use `#reset` to clear memory

## Code Execution Safety

Code execution is sandboxed:

- Runs in subprocess with 30s timeout
- Executes in isolated `runtime/` directory
- Captures stdout and stderr
- Handles errors gracefully without crashing

## Performance

Optimized for Samsung S24 Ultra:

- **Model**: CodeLlama-7B Q4_K_M (quantized)
- **Threads**: 4 CPU threads
- **Context**: 2048 tokens
- **Max output**: 512 tokens
- **Temperature**: 0.7

Typical response times:
- Simple queries: 5-15 seconds
- Code generation: 10-30 seconds
- Complex reasoning: 20-45 seconds

## Troubleshooting

### "llama.cpp not found"

Run setup script again or manually build:
```bash
cd ~/Genesis/llama.cpp
make clean && make -j$(nproc)
```

### "Model not found"

Check model path:
```bash
ls -lh ~/Genesis/models/CodeLlama-7B-Instruct.Q4_K_M.gguf
```

If broken, relink:
```bash
ln -sf ~/storage/downloads/LLM_Models/CodeLlama-7B-Instruct.Q4_K_M.gguf \
       ~/Genesis/models/CodeLlama-7B-Instruct.Q4_K_M.gguf
```

### "Python module not found"

Reinstall dependencies:
```bash
pip install --upgrade colorama prompt_toolkit
```

### Slow responses

Reduce context size in `genesis.py`:
```python
"-c", "1024",  # Reduce from 2048
"-n", "256",   # Reduce from 512
```

## Examples

### Example 1: File Analysis

```
Genesis> Read setup_genesis.sh and tell me what it does

[Genesis analyzes the script and explains each section]
```

### Example 2: Code Generation

```
Genesis> Create a Python script that finds all .py files in the current directory \
      > and counts the total lines of code

[Genesis writes and executes the script, showing results]
```

### Example 3: Data Processing

```
Genesis> Write a script that:
1. Creates a list of 100 random numbers
2. Calculates mean, median, and standard deviation
3. Prints the results in a formatted table

[Genesis generates and runs the code, displays statistics]
```

## Advanced Usage

### Custom System Prompt

Edit `genesis.py` and modify the `system_prompt` variable to customize behavior.

### Adjusting LLM Parameters

In `genesis.py`, find the `call_llm` method and adjust:

```python
cmd = [
    self.llama_path,
    "-m", self.model_path,
    "-n", "512",      # Max tokens (increase for longer responses)
    "-t", "4",        # CPU threads (adjust for your device)
    "--temp", "0.7",  # Temperature (lower = more focused)
    "--top-p", "0.9", # Top-p sampling
    "-c", "2048",     # Context size
]
```

### Extending Tools

Add new tools in `tools.py`:

```python
@staticmethod
def your_new_tool(param: str) -> str:
    """Your tool description"""
    # Implementation
    return result
```

Then use in `genesis.py` by adding patterns to `process_tool_calls`.

## File Structure

### genesis.py
Main controller that:
- Manages the interaction loop
- Calls the LLM
- Processes responses
- Executes code and tools

### memory.py
Memory manager that:
- Loads/saves conversation history
- Maintains context window
- Provides statistics

### executor.py
Code executor that:
- Extracts code blocks
- Runs Python in subprocess
- Handles timeouts and errors

### tools.py
File system tools:
- read_file, write_file, append_file
- list_directory, create_directory
- delete_file, delete_directory
- file_info, change_directory

## License

MIT License - Feel free to modify and extend.

## Contributing

This is a personal project, but improvements are welcome:

1. Test thoroughly on your device
2. Document changes clearly
3. Keep code clean and commented
4. Maintain backward compatibility

## Future Enhancements

Potential improvements:

- [ ] Voice input/output integration
- [ ] Web search capability
- [ ] Image analysis with vision models
- [ ] Multi-model support (switch between models)
- [ ] Plugin system for custom tools
- [ ] Better syntax highlighting
- [ ] Session management (save/load sessions)
- [ ] Integration with other Termux tools

## Credits

- Built on [llama.cpp](https://github.com/ggerganov/llama.cpp)
- Powered by [CodeLlama](https://github.com/facebookresearch/codellama)
- Inspired by Claude Code from Anthropic

---

**Version**: 1.0
**Last Updated**: November 2025
**Tested On**: Samsung S24 Ultra, Termux
**Author**: Built with Claude Code
