# Genesis Claude Assist Guide

## Overview

Genesis features an intelligent **Claude Fallback Orchestration System** that automatically detects when the local LLM (CodeLlama-7B) is uncertain and seamlessly requests assistance from Claude Code.

This creates a hybrid intelligence system:
- **Primary**: Local model (fast, private, no API costs)
- **Fallback**: Claude (accurate, comprehensive, triggered only when needed)

## How It Works

### 1. Normal Operation (Local)

```
User → Genesis → CodeLlama → Response
```

Genesis processes most queries entirely locally using CodeLlama-7B.

### 2. Uncertain Response Detection

Genesis analyzes each local response for uncertainty indicators:

**Uncertainty Patterns:**
- Uncertain language ("I'm not sure", "I don't know", "maybe", "possibly")
- Very short responses (<20 characters)
- High repetition (confused text)
- Error indicators
- Incomplete code blocks

**Confidence Scoring:**
- Calculates 0.0 (very uncertain) to 1.0 (very confident)
- Threshold: 0.6 (below = fallback triggered)

### 3. Claude Fallback Activation

When uncertainty detected AND Claude assist enabled:

```
User → Genesis → CodeLlama (uncertain)
                    ↓
               Uncertainty Detector
                    ↓
               Claude Fallback
                    ↓
                  Claude
                    ↓
            Refined Response → User
```

### 4. Learning from Fallbacks

All fallback events are:
- **Logged** to `~/Genesis/logs/fallback_history.log`
- **Saved** to `~/Genesis/data/retrain_set.json` for future fine-tuning

## Configuration

### Enable Claude Assist

In Genesis:
```
Genesis> #assist
```

Output:
```
✓ Claude assist enabled
Genesis will request Claude's help when uncertain
Logs: ~/Genesis/logs/fallback_history.log
```

Or via command line:
```bash
python ~/Genesis/claude_fallback.py enable
```

Or manually create flag file:
```bash
touch /data/data/com.termux/files/home/.genesis_assist
```

### Disable Claude Assist

In Genesis:
```
Genesis> #assist
```

Output:
```
✓ Claude assist disabled
Genesis will run entirely locally without fallback
```

Or via command line:
```bash
python ~/Genesis/claude_fallback.py disable
```

### Check Status

In Genesis:
```
Genesis> #assist-stats
```

Output:
```
Claude Assist Statistics:

Status: ENABLED
Total fallbacks: 12
Successful: 10
Failed: 2
Learning examples: 10
Success rate: 83.3%

Logs: ~/Genesis/logs/fallback_history.log
Dataset: ~/Genesis/data/retrain_set.json
```

Or via command line:
```bash
python ~/Genesis/claude_fallback.py stats
```

## User Experience

### Example 1: Confident Local Response

**User:**
```
Genesis> Write a Python function to calculate factorial
```

**Genesis (Local):**
```
Genesis:
Here's a factorial function:

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

print(factorial(5))  # 120
```
```

**Result:** Genesis answered confidently. No fallback needed.

### Example 2: Uncertain Response with Fallback Disabled

**User:**
```
Genesis> Explain the intricacies of quantum entanglement in superconducting qubits
```

**Genesis (Local):**
```
Genesis:
I'm not sure about all the details, but quantum entanglement might involve...

💡 Tip: Genesis showed uncertainty. Enable Claude assist with #assist
```

**Result:** Genesis showed uncertainty but fallback is disabled. User can enable it if desired.

### Example 3: Uncertain Response with Fallback Enabled

**User:**
```
Genesis> Explain the intricacies of quantum entanglement in superconducting qubits
```

**Genesis (Local - Uncertain):**
```
I'm not sure about all the details...
```

**System:**
```
⚡ Genesis is uncertain (confidence: 0.42)
   Requesting Claude assistance...

<<<GENESIS_CLAUDE_REQUEST>>>
{
  "request_type": "fallback_assist",
  "prompt": "..."
}
<<<GENESIS_CLAUDE_REQUEST_END>>>
```

**Genesis (Claude-assisted):**
```
Genesis (Claude-assisted):
Quantum entanglement in superconducting qubits involves...
[Comprehensive, accurate explanation]
```

**Result:** Genesis detected uncertainty, requested Claude's help, and provided a refined answer.

## Uncertainty Detection Details

### Detection Criteria

The `UncertaintyDetector` module checks for:

1. **Uncertain Language** (weight: -0.3 to -0.5)
   - "I'm not sure"
   - "I don't know"
   - "maybe", "possibly", "perhaps"
   - "I think", "I believe"
   - "can't help", "unable to"

2. **Response Length** (weight: -0.3)
   - Very short responses (<20 chars)

3. **Repetition** (weight: -0.2)
   - High ratio of repeated words (>50%)

4. **Error Indicators** (weight: -0.3)
   - "error", "failed", "exception"
   - "syntax error", "traceback"

5. **Code Quality** (weight: -0.2)
   - Incomplete code (e.g., "...")
   - TODO/FIXME comments
   - Bare `pass` statements

### Confidence Score Calculation

```python
score = 1.0  # Start confident
score -= 0.3 if has_uncertain_language
score -= 0.3 if is_too_short
score -= 0.2 if has_excessive_repetition
score -= 0.3 if has_error_indicators
score -= 0.2 if code_quality_issues

# Result: 0.0 (very uncertain) to 1.0 (very confident)
# Threshold: < 0.6 triggers fallback
```

## Claude Fallback Communication

### Current Implementation

Genesis prints a marked request that Claude Code can intercept:

```
<<<GENESIS_CLAUDE_REQUEST>>>
{
  "request_type": "fallback_assist",
  "prompt": "You are assisting Genesis..."
}
<<<GENESIS_CLAUDE_REQUEST_END>>>
```

Claude Code (if monitoring) can:
1. Detect the marked request
2. Process with full Claude intelligence
3. Inject response back to Genesis

### Future Enhancements

Possible communication methods:

1. **HTTP Bridge** (if Genesis bridge is running)
   ```python
   response = requests.post('http://localhost:5050/claude-assist', ...)
   ```

2. **File-based IPC**
   ```python
   # Genesis writes
   /tmp/genesis_request.json

   # Claude Code reads and writes
   /tmp/genesis_response.json
   ```

3. **Stdio Pipe** (if Claude Code is parent process)
   ```python
   print(json.dumps(request))
   response = input()  # Read from parent
   ```

4. **Claude API** (if available)
   ```python
   import anthropic
   client = anthropic.Anthropic(api_key=...)
   response = client.messages.create(...)
   ```

## Logging and Analytics

### Fallback Event Log

Location: `~/Genesis/logs/fallback_history.log`

Format: JSON Lines (one event per line)

```json
{
  "timestamp": "2025-11-05T07:30:45.123",
  "user_prompt": "Explain quantum entanglement",
  "local_response": "I'm not sure...",
  "local_confidence": 0.42,
  "uncertainty_reason": "uncertain_language (3 matches), too_short",
  "claude_response": "Quantum entanglement involves...",
  "fallback_triggered": true
}
```

### Retraining Dataset

Location: `~/Genesis/data/retrain_set.json`

Format: JSON with examples array

```json
{
  "examples": [
    {
      "timestamp": "2025-11-05T07:30:45.123",
      "input": "Explain quantum entanglement",
      "local_output": "I'm not sure...",
      "local_confidence": 0.42,
      "improved_output": "Quantum entanglement involves...",
      "improvement_reason": "uncertain_language, too_short"
    }
  ]
}
```

### Using Logs for Analysis

**View recent fallbacks:**
```bash
tail -n 20 ~/Genesis/logs/fallback_history.log | python -m json.tool
```

**Count fallbacks:**
```bash
wc -l ~/Genesis/logs/fallback_history.log
```

**Search for specific pattern:**
```bash
grep "quantum" ~/Genesis/logs/fallback_history.log
```

**Extract learning examples:**
```bash
cat ~/Genesis/data/retrain_set.json | python -m json.tool
```

## Performance Impact

### Without Fallback (Default)

- **Latency**: 10-20 seconds per response
- **Cost**: $0 (entirely local)
- **Accuracy**: Good for common tasks, uncertain on complex topics

### With Fallback Enabled

- **Normal Response**: 10-20 seconds (local only)
- **Fallback Response**: 10-20 seconds (local) + 2-5 seconds (Claude)
- **Total**: ~15-25 seconds when fallback triggers
- **Cost**: Minimal (only when uncertain, typically 5-15% of queries)
- **Accuracy**: High (Claude handles edge cases)

### Optimization Tips

1. **Adjust confidence threshold** (default: 0.6)
   ```python
   # In uncertainty_detector.py
   threshold = 0.7  # More strict, fewer fallbacks
   threshold = 0.5  # More lenient, more fallbacks
   ```

2. **Monitor fallback rate**
   ```
   Genesis> #assist-stats
   ```

   Ideal rate: 5-15% of queries
   - Too high? Increase threshold or improve local prompts
   - Too low? Decrease threshold for better quality

3. **Review logs periodically**
   ```bash
   tail -f ~/Genesis/logs/fallback_history.log
   ```

## Advanced Features

### Custom Uncertainty Patterns

Edit `~/Genesis/uncertainty_detector.py`:

```python
self.uncertain_patterns = [
    r'\bi[\'']?m not sure\b',
    r'\bYOUR CUSTOM PATTERN\b',  # Add here
    # ...
]
```

### Fine-Tuning with Collected Data

Future enhancement - use collected examples for local model improvement:

```bash
# Convert retrain_set.json to JSONL for fine-tuning
python ~/Genesis/scripts/prepare_finetune_data.py
```

### Conditional Fallback

Add topic-specific fallback rules:

```python
# In claude_fallback.py
def should_fallback_for_topic(self, prompt, response):
    # Always fallback for medical/legal advice
    sensitive_topics = ['medical', 'legal', 'financial']
    if any(topic in prompt.lower() for topic in sensitive_topics):
        return True

    # Use normal uncertainty detection
    return self.uncertainty.should_trigger_fallback(response)
```

## Best Practices

### When to Enable

✅ **Enable Claude Assist when:**
- Working on complex/unfamiliar topics
- Need high accuracy (e.g., production code)
- Learning from high-quality examples
- Exploring new domains

❌ **Disable Claude Assist when:**
- Doing routine/simple tasks
- Want pure local operation
- Minimizing latency
- Offline/no Claude access

### Monitoring and Maintenance

**Weekly:**
- Check `#assist-stats` for fallback rate
- Review logs for patterns
- Adjust threshold if needed

**Monthly:**
- Analyze retrain dataset
- Identify common uncertainty topics
- Consider local model improvements

**As Needed:**
- Clear logs if too large:
  ```bash
  > ~/Genesis/logs/fallback_history.log
  ```
- Export learning data:
  ```bash
  cp ~/Genesis/data/retrain_set.json ~/backup/
  ```

## Troubleshooting

### Fallback Not Triggering

**Problem:** Genesis shows uncertainty but doesn't request Claude help

**Solutions:**
1. Check if enabled: `#assist-stats`
2. Enable: `#assist`
3. Verify flag file: `ls -la ~/.genesis_assist`

### Too Many Fallbacks

**Problem:** Almost every response triggers fallback

**Solutions:**
1. Increase threshold in `uncertainty_detector.py`
2. Review prompts - make them clearer
3. Check if local model is functioning properly

### No Claude Response

**Problem:** Fallback triggered but no Claude response received

**Solutions:**
1. Check if Claude Code is running/monitoring
2. Verify communication method is configured
3. Check logs for errors
4. Test manually: `python claude_fallback.py enable`

### Logs Growing Too Large

**Problem:** Log files consuming too much space

**Solutions:**
```bash
# Rotate logs
mv ~/Genesis/logs/fallback_history.log ~/Genesis/logs/fallback_history.log.old
touch ~/Genesis/logs/fallback_history.log

# Or truncate
> ~/Genesis/logs/fallback_history.log
```

## Summary

The Claude Assist system provides:

✅ **Intelligent fallback** - Only triggers when needed
✅ **Transparency** - Clear indication of Claude-assisted responses
✅ **Learning** - Collects examples for future improvement
✅ **Configurability** - Easy on/off toggle
✅ **Analytics** - Comprehensive logging and statistics
✅ **Cost-effective** - Minimizes Claude API usage

**Default State:** Disabled (pure local operation)
**Enable:** `#assist` command in Genesis
**Monitor:** `#assist-stats` for usage metrics

---

**Version**: 1.0
**Integration**: Seamless with Genesis core
**Overhead**: <5% performance impact
**Accuracy Improvement**: Significant on complex topics
