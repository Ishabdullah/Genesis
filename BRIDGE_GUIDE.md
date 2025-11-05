# Genesis-Claude Code Bridge Guide

## Overview

The Genesis Bridge enables bidirectional collaboration between Claude Code (planning layer) and Genesis (execution layer), allowing seamless on-device code execution and testing.

## Architecture

```
┌─────────────────┐         HTTP/JSON        ┌──────────────────┐
│   Claude Code   │ ←──────────────────────→ │  Genesis Bridge  │
│  (Planning)     │    127.0.0.1:5050        │  (Execution)     │
└─────────────────┘                          └──────────────────┘
                                                      ↓
                                              Python Subprocess
                                              Sandbox (runtime/)
```

## Security Model

- **Localhost only**: Bridge accepts connections from 127.0.0.1 only
- **API key authentication**: All requests require `X-Genesis-Key: localonly` header
- **Code sandboxing**: Executes in isolated subprocess with 20s timeout
- **Input validation**: Blocks dangerous imports and operations
- **Request logging**: All activity logged to `bridge_log.txt`

## Starting the Bridge

### From Genesis Interactive Mode

```bash
Genesis
```

Then type:
```
Genesis> #bridge
```

The bridge starts on http://127.0.0.1:5050

### Standalone Mode

For testing without Genesis interactive mode:

```bash
cd ~/Genesis
python genesis_bridge.py
```

## API Endpoints

### POST /run

Execute Python code and return output.

**Request:**
```bash
curl -X POST http://127.0.0.1:5050/run \
  -H "Content-Type: application/json" \
  -H "X-Genesis-Key: localonly" \
  -d '{"code": "print(\"Hello World\")"}'
```

**Response (Success):**
```json
{
  "output": "Hello World",
  "success": true,
  "return_code": 0
}
```

**Response (Error):**
```json
{
  "output": "STDERR:\nNameError: name 'undefined_var' is not defined",
  "success": false,
  "return_code": 1
}
```

**Response (Security Rejection):**
```json
{
  "error": "Code rejected: Potentially unsafe operation detected: import socket",
  "output": ""
}
```

### GET /status

Check bridge status and configuration.

**Request:**
```bash
curl http://127.0.0.1:5050/status
```

**Response:**
```json
{
  "status": "running",
  "host": "127.0.0.1",
  "port": 5050,
  "runtime_dir": "runtime"
}
```

### GET /health

Simple health check.

**Request:**
```bash
curl http://127.0.0.1:5050/health
```

**Response:**
```json
{
  "healthy": true
}
```

## Claude Code Integration

### Basic Usage from Claude Code

Claude Code can execute Python code on Genesis by making HTTP requests:

```python
import requests

def execute_on_genesis(code: str) -> dict:
    """Execute code via Genesis Bridge"""
    url = "http://127.0.0.1:5050/run"
    headers = {
        "Content-Type": "application/json",
        "X-Genesis-Key": "localonly"
    }
    data = {"code": code}

    response = requests.post(url, headers=headers, json=data, timeout=30)
    return response.json()

# Example usage
result = execute_on_genesis('print("Hello from Claude Code!")')
print(result['output'])
```

### Using Bash from Claude Code

Claude Code can use bash commands directly:

```bash
# Test connection
curl -X POST http://127.0.0.1:5050/run \
  -H "Content-Type: application/json" \
  -H "X-Genesis-Key: localonly" \
  -d '{"code":"import sys; print(sys.version)"}'

# Run a complex script
curl -X POST http://127.0.0.1:5050/run \
  -H "Content-Type: application/json" \
  -H "X-Genesis-Key: localonly" \
  -d @code_payload.json
```

### Workflow Example

1. **Claude Code Plans**: Analyzes task and generates Python code
2. **Claude Code Sends**: POSTs code to Genesis Bridge
3. **Genesis Executes**: Runs code in sandbox, captures output
4. **Genesis Responds**: Returns output to Claude Code
5. **Claude Code Adapts**: Adjusts plan based on results

## Code Execution Rules

### Allowed Operations

- ✓ Math and calculations
- ✓ String manipulation
- ✓ Data structures (lists, dicts, sets)
- ✓ File operations within ~/Genesis
- ✓ Standard library imports (json, datetime, math, etc.)
- ✓ Print statements and logging

### Blocked Operations

- ✗ Network operations (socket, requests, urllib)
- ✗ System calls (os.system, subprocess.Popen)
- ✗ Dangerous eval/exec
- ✗ File access outside ~/Genesis
- ✗ Access to /etc, /sys, /proc

### Execution Limits

- **Timeout**: 20 seconds maximum
- **Working Directory**: ~/Genesis/runtime
- **Output Capture**: stdout + stderr combined
- **Return Codes**: 0 = success, non-zero = error

## Testing the Bridge

### Quick Test

```bash
cd ~/Genesis
./test_bridge.sh
```

This runs a comprehensive test suite covering:
1. Health check
2. Status verification
3. Simple code execution
4. Math calculations
5. Error handling
6. Security (API key validation)

### Manual Testing

```bash
# Test 1: Hello World
curl -X POST http://127.0.0.1:5050/run \
  -H "Content-Type: application/json" \
  -H "X-Genesis-Key: localonly" \
  -d '{"code":"print(\"Hello World\")"}'

# Test 2: Math
curl -X POST http://127.0.0.1:5050/run \
  -H "Content-Type: application/json" \
  -H "X-Genesis-Key: localonly" \
  -d '{"code":"print(sum(range(1, 101)))"}'

# Test 3: File Write
curl -X POST http://127.0.0.1:5050/run \
  -H "Content-Type: application/json" \
  -H "X-Genesis-Key: localonly" \
  -d '{"code":"with open(\"test.txt\", \"w\") as f: f.write(\"test\")\nprint(\"File written\")"}'

# Test 4: Error Handling
curl -X POST http://127.0.0.1:5050/run \
  -H "Content-Type: application/json" \
  -H "X-Genesis-Key: localonly" \
  -d '{"code":"1/0"}'
```

## Monitoring and Logging

### View Bridge Logs

```bash
# Tail logs in real-time
tail -f ~/Genesis/bridge_log.txt

# View last 20 requests
tail -n 20 ~/Genesis/bridge_log.txt | python -m json.tool

# Count total requests
wc -l ~/Genesis/bridge_log.txt
```

### Log Format

Each log entry is a JSON object:

```json
{
  "timestamp": "2025-11-05T06:30:45.123456",
  "success": true,
  "code_length": 25,
  "output_length": 11,
  "code_preview": "print(\"Hello World\")",
  "output_preview": "Hello World"
}
```

## Troubleshooting

### Bridge Won't Start

**Problem**: "Address already in use"

**Solution**: Another process is using port 5050
```bash
# Find the process
lsof -i :5050
# Or use a different port (edit genesis_bridge.py)
```

**Problem**: "Module 'flask' not found"

**Solution**: Install Flask
```bash
pip install flask
```

### Connection Refused

**Problem**: curl returns "Connection refused"

**Solution**: Ensure bridge is running
```bash
# Check if Genesis is running
ps aux | grep genesis

# Start bridge
Genesis
#bridge
```

### Unauthorized (401)

**Problem**: Request returns 401 error

**Solution**: Include API key header
```bash
# Wrong - missing header
curl -X POST http://127.0.0.1:5050/run -d '{...}'

# Right - includes header
curl -X POST http://127.0.0.1:5050/run \
  -H "X-Genesis-Key: localonly" \
  -d '{...}'
```

### Code Rejected (400)

**Problem**: "Code rejected: Potentially unsafe operation"

**Solution**: Remove blocked operations
```python
# Blocked
import socket

# Allowed
import json
```

### Execution Timeout

**Problem**: Code times out after 20s

**Solution**: Optimize code or split into smaller chunks
- Reduce iterations
- Use more efficient algorithms
- Break into multiple requests

## Advanced Usage

### Multiline Code

```bash
curl -X POST http://127.0.0.1:5050/run \
  -H "Content-Type: application/json" \
  -H "X-Genesis-Key: localonly" \
  -d '{
    "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nfor i in range(10):\n    print(fibonacci(i))"
  }'
```

### Using JSON Files

Create `payload.json`:
```json
{
  "code": "import json\ndata = {'status': 'ok'}\nprint(json.dumps(data))"
}
```

Execute:
```bash
curl -X POST http://127.0.0.1:5050/run \
  -H "Content-Type: application/json" \
  -H "X-Genesis-Key: localonly" \
  -d @payload.json
```

### Batch Testing

```bash
# Create test suite
for test in test1.json test2.json test3.json; do
  echo "Running $test..."
  curl -X POST http://127.0.0.1:5050/run \
    -H "Content-Type: application/json" \
    -H "X-Genesis-Key: localonly" \
    -d @$test
  echo ""
done
```

## Performance

Typical response times on Samsung S24 Ultra:

| Operation | Time |
|-----------|------|
| Simple print | 50-100ms |
| Math calculation | 50-150ms |
| File I/O | 100-200ms |
| Complex computation | 1-5s |
| Timeout limit | 20s |

Network overhead: ~10-20ms (localhost only)

## Security Best Practices

1. **Never expose externally**: Bridge is localhost-only by design
2. **Rotate API key**: Change "localonly" to custom value if needed
3. **Monitor logs**: Check bridge_log.txt for suspicious activity
4. **Sandbox isolation**: Code runs in runtime/ directory only
5. **Timeout protection**: 20s limit prevents infinite loops
6. **Input validation**: Dangerous patterns blocked automatically

## Customization

### Change API Key

Edit `genesis_bridge.py`:
```python
bridge = GenesisBridge(api_key='your-secret-key')
```

Update requests:
```bash
curl ... -H "X-Genesis-Key: your-secret-key" ...
```

### Change Port

Edit `genesis_bridge.py`:
```python
bridge = GenesisBridge(port=8080)
```

### Adjust Timeout

Edit `genesis_bridge.py`, find `_execute_code`:
```python
def _execute_code(self, code: str, timeout: int = 30):  # Increase from 20
```

### Add Custom Endpoints

In `genesis_bridge.py`, add to `_setup_routes`:
```python
@self.app.route('/custom', methods=['POST'])
def custom_endpoint():
    # Your custom logic
    return jsonify({'result': 'ok'})
```

## Integration Patterns

### Pattern 1: Code Generation + Execution

```
Claude Code:
1. Generate Python function
2. POST to /run
3. Parse output
4. Adjust if needed
5. Repeat until correct
```

### Pattern 2: Test-Driven Development

```
Claude Code:
1. Write test cases
2. Send to Genesis
3. Analyze failures
4. Generate fixes
5. Re-test
```

### Pattern 3: Data Processing Pipeline

```
Claude Code:
1. Generate data transformation code
2. Execute on Genesis
3. Validate results
4. Chain multiple transformations
5. Produce final output
```

## Future Enhancements

Possible improvements:

- [ ] WebSocket support for streaming output
- [ ] Multiple sandboxes for parallel execution
- [ ] GPU access for ML workloads
- [ ] File upload/download endpoints
- [ ] Session management for stateful execution
- [ ] Metrics dashboard
- [ ] Rate limiting
- [ ] HTTPS support (for remote access)

## Summary

The Genesis Bridge provides a secure, localhost-only HTTP interface for Claude Code to execute Python code on Genesis. It enables collaborative development where Claude Code handles planning and Genesis handles execution, all without leaving your device.

---

**Bridge Version**: 1.0
**Protocol**: HTTP/JSON
**Security**: API key + localhost-only
**Performance**: <100ms typical latency
**Tested On**: Samsung S24 Ultra, Termux
