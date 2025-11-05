# Genesis Honest Communication System

## 🎯 Purpose

Genesis now **honestly communicates** when it cannot complete a task reliably, whether Claude is available or not.

---

## 🤝 Honest AI Philosophy

**Genesis will ALWAYS tell you when:**
1. ❌ It's uncertain about a response
2. ❌ It cannot reach Claude for help
3. ❌ A task exceeds its capabilities
4. ❌ The response may be unreliable

**NO false confidence. NO guessing. NO pretending.**

---

## 📋 Three Scenarios

### Scenario 1: Genesis is Confident ✅
```
Genesis> write hello world in python

[Thinking...]

Genesis:
print("Hello World!")

[Executing Code Block 1]
✓ Execution successful:
Hello World!
```

**Status**: Genesis is confident, task completed successfully.

---

### Scenario 2: Genesis is Uncertain + Claude Available ⚡
```
Genesis> Explain quantum entanglement and implement a simulation

[Thinking...]

⚡ Genesis is uncertain (confidence: 0.42)
   Requesting Claude assistance...

Genesis (Claude-assisted):
[Comprehensive explanation]
[Working quantum simulation code]
```

**Status**: Genesis recognized limitations, requested Claude help, task completed successfully.

---

### Scenario 3: Genesis is Uncertain + Claude NOT Available ⚠️

#### 3A: When Claude Assist is Enabled but Unreachable
```
Genesis> Explain advanced machine learning architectures

[Thinking...]

⚡ Genesis is uncertain (confidence: 0.38)
   Requesting Claude assistance...

⚠ Unable to reach Claude Code for assistance
Genesis cannot complete this task reliably.

Reasons:
  • Task complexity exceeds Genesis capabilities
  • Confidence score: 0.38 (< 0.60 threshold)
  • Claude Code is not available for fallback

Suggestions:
  1. Try a simpler version of your request
  2. Break the task into smaller steps
  3. Use direct commands (ls, git, find, grep)
  4. Set up Claude API key: export ANTHROPIC_API_KEY=your_key
  5. Ensure Claude Code bridge is running

Showing Genesis's uncertain response (use with caution):

Genesis (uncertain):
[Genesis's attempt - may be incomplete or incorrect]
```

**Status**: Genesis tried, failed to reach Claude, honestly admits it cannot complete the task reliably.

#### 3B: When Claude Assist is Disabled
```
Genesis> Implement a complex neural network

[Thinking...]

Genesis:
[Uncertain response with partial implementation]

⚠ Genesis is uncertain about this response
Confidence score: 0.45 (< 0.60 threshold)

Genesis cannot complete this task reliably without Claude assistance.

Options:
  1. Enable Claude assist: #assist
  2. Try a simpler version of your request
  3. Break the task into smaller steps
  4. Use direct commands when possible (ls, git, find)

The response above should be used with caution.
```

**Status**: Genesis provides response but clearly warns it's uncertain and suggests enabling Claude assist.

---

## 🔍 How Uncertainty is Detected

Genesis analyzes every response for:

### 1. Uncertain Language (25+ patterns)
- "I'm not sure"
- "I don't know"
- "maybe", "perhaps", "possibly"
- "I think", "I believe"
- "cannot complete"
- "struggling to"
- "beyond my capabilities"

### 2. Error Indicators
- ⚠ Warning symbols
- "Error:", "Failed:", "Timeout"
- "Not found", "Cannot access"
- "Permission denied"
- Python exceptions (SyntaxError, NameError, etc.)

### 3. Code Quality Issues
- Incomplete code (ellipsis: `...`)
- TODO/FIXME comments in generated code
- Empty code blocks
- Bare `pass` statements

### 4. Response Quality
- Too short (< 20 characters)
- Excessive repetition (> 50% repeated text)
- Empty or whitespace-only responses

### 5. Confidence Scoring
```
Score = 1.0 (start)
  - 0.4 per uncertain phrase (max -0.6)
  - 0.4 if too short
  - 0.3 if repetitive
  - 0.4 if has error indicators
  - 0.3 if code quality issues

Threshold: < 0.60 = uncertain
```

**Example Scoring:**
- Response with "I'm not sure" + error: 1.0 - 0.4 - 0.4 = **0.2** (very uncertain)
- Normal response: **1.0** (confident)
- Slightly unsure response with "maybe": 1.0 - 0.4 = **0.6** (threshold)

---

## 🔗 Claude Connection Methods

Genesis tries **3 methods** to reach Claude (in order):

### Method 1: Bridge Server
```python
# Checks if Claude Code bridge is running
POST http://127.0.0.1:5050/claude_assist
```

**Status**: ✅ If bridge running, ❌ if not

### Method 2: Claude API
```python
# Checks for ANTHROPIC_API_KEY environment variable
ANTHROPIC_API_KEY=sk-ant-...
```

**Status**: ✅ If key set, ❌ if not

### Method 3: File Communication
```python
# Writes request to /tmp/genesis_needs_claude.txt
# Waits 30s for Claude to write /tmp/claude_response.txt
```

**Status**: ✅ If Claude monitoring, ❌ if timeout

---

## 📊 Transparency Levels

Genesis provides **full transparency** about its confidence:

| Confidence | Status | Color | Action |
|------------|--------|-------|--------|
| 0.90 - 1.00 | Very confident | Green | Proceed normally |
| 0.60 - 0.89 | Somewhat confident | Yellow | Proceed with caution |
| 0.40 - 0.59 | Uncertain | Orange | Request Claude help |
| 0.00 - 0.39 | Very uncertain | Red | Must have Claude help |

---

## 💡 User Guidance

### When Genesis is Uncertain

**DO:**
✅ Enable Claude assist: `#assist`
✅ Simplify your request
✅ Break task into smaller steps
✅ Use direct commands (ls, git, find, grep)
✅ Set up Claude API key if available

**DON'T:**
❌ Trust uncertain responses for critical tasks
❌ Ignore confidence warnings
❌ Expect complex tasks without Claude
❌ Use Genesis for tasks beyond its 7B model capabilities

---

## 🔧 Setup Claude Connection

### Option 1: Claude API (Recommended)
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
echo 'export ANTHROPIC_API_KEY=sk-ant-your-key-here' >> ~/.bashrc
```

### Option 2: Bridge Server
```bash
# In separate terminal
Genesis
Genesis> #bridge

# Bridge runs on http://127.0.0.1:5050
```

### Option 3: File Monitoring
Claude Code can monitor `/tmp/genesis_needs_claude.txt` and respond to `/tmp/claude_response.txt`

---

## 📈 Benefits

### For Users:
1. **Trust** - Know when to trust responses
2. **Transparency** - See confidence scores
3. **Guidance** - Clear next steps when uncertain
4. **Safety** - No false confidence on critical tasks

### For Development:
1. **Logging** - All uncertain responses logged
2. **Learning** - Build training dataset from Claude responses
3. **Metrics** - Track confidence scores over time
4. **Improvement** - Identify model weaknesses

---

## 📝 Logging

All interactions are logged:

### Fallback History: `~/Genesis/logs/fallback_history.log`
```json
{
  "timestamp": "2025-11-05T10:30:00",
  "user_prompt": "Explain quantum computing",
  "local_response": "Quantum computing uses...",
  "confidence_score": 0.35,
  "claude_available": true,
  "claude_response": "Comprehensive explanation..."
}
```

### Retraining Dataset: `~/Genesis/data/retrain_set.json`
```json
{
  "examples": [
    {
      "prompt": "User request",
      "local_attempt": "Genesis response",
      "correct_response": "Claude response",
      "confidence": 0.35
    }
  ]
}
```

---

## 🎯 Real Examples

### Example 1: Simple Task (No Fallback Needed)
```
Genesis> list files in home directory

Genesis:
📂 /data/data/com.termux/files/home
[Complete listing - instant, confident]
```

### Example 2: Code Generation (Confident)
```
Genesis> write factorial function

Genesis:
def factorial(n):
    return 1 if n <= 1 else n * factorial(n-1)

[Executes successfully - confident]
```

### Example 3: Complex Task (Needs Claude)
```
Genesis> Implement a transformer architecture with attention mechanism

⚡ Genesis is uncertain (confidence: 0.25)
   Requesting Claude assistance...

⚠ Unable to reach Claude Code for assistance
Genesis cannot complete this task reliably.

[Shows warnings and suggestions]
[Shows uncertain response with disclaimer]
```

### Example 4: Error Handling
```
Genesis> read nonexistent-file.txt

Genesis:
⚠ File not found: nonexistent-file.txt

[No confidence issue - this is expected behavior, not uncertainty]
```

---

## 🔄 Fallback Flow

```
User Request
    ↓
Genesis processes
    ↓
Analyze confidence
    ↓
< 0.60? ──No──> Return response
    ↓ Yes
Claude assist enabled?
    ↓ Yes         ↓ No
Try reach Claude  Show warning
    ↓                ↓
Success?          Return uncertain response
    ↓ Yes  ↓ No      with disclaimer
Return Claude    Show error
response         Show uncertain response
                 with disclaimer
```

---

## ✅ Summary

**Genesis will ALWAYS:**
- ✅ Tell you when it's uncertain
- ✅ Show confidence scores
- ✅ Attempt to reach Claude when needed
- ✅ Inform you if Claude is unreachable
- ✅ Provide clear guidance on next steps
- ✅ Warn when responses may be unreliable
- ✅ Log all uncertain interactions
- ✅ Be honest about its limitations

**Genesis will NEVER:**
- ❌ Pretend to be confident when uncertain
- ❌ Hide failures or limitations
- ❌ Give false confidence on critical tasks
- ❌ Silently fail without user notification

---

**This is honest AI. This is transparent AI. This is trustworthy AI.**

🧬 **Genesis: When I don't know, I'll tell you.**

---

**Version**: Honest Communication System
**Status**: ✅ Implemented and tested
**Repository**: https://github.com/Ishabdullah/Genesis.git
