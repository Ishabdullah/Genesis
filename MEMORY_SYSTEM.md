# 🧬 Genesis Memory & Learning System

## Overview

Genesis includes a **persistent memory and learning system** that stores conversations, performance metrics, user feedback, and learned improvements across sessions - enabling continuous learning and personalization.

---

## ✅ Features

### 1. Persistent Memory Storage

**Conversation Memory:**
- Stores complete conversation history with timestamps
- Includes user input and Genesis responses
- Metadata: response time, confidence scores, fallback usage
- Auto-truncation to prevent bloat (500 char inputs, 1000 char responses)

**Learning Log:**
- Records all learning events (feedback, corrections, adaptations)
- Tracks improvements and system changes
- Stores last 500 learning entries
- Timestamped for historical analysis

**Performance History:**
- Complete record of response times
- Accuracy tracking (user feedback)
- Claude fallback usage
- Error logs
- Stores last 1000 performance records

**User Preferences:**
- Communication style preferences
- Verbosity settings
- Topic preferences
- Feedback patterns

---

### 2. Intelligent Auto-Pruning

**Automatic Memory Management:**
- Triggers at 80% of max conversations (default: 800/1000)
- Keeps 70% after pruning (700 conversations retained)
- Non-blocking background operation
- Logs pruning events for transparency

**Scoring Algorithm:**
Conversations are scored and prioritized based on:

1. **Age Factor (0-10 points)**
   - Newer conversations score higher
   - Formula: `(max_age_days - age_days) / max_age_days * 10`
   - 90-day maximum retention (configurable)

2. **Length Factor (0-5 points)**
   - Longer responses indicate deeper exchanges
   - Formula: `min(response_len / 100, 5)`
   - Rewards substantial conversations

3. **Metadata Bonuses:**
   - Correct feedback: **+5 points**
   - Claude fallback used: **+3 points** (valuable learning)
   - Errors: **-2 points** (less valuable)

**Result:** High-quality, recent, valuable conversations are retained; old, short, error-prone conversations are pruned.

---

## 📊 Commands

### View Memory Summary
```bash
Genesis> #memory
```

**Displays:**
- Total conversations stored (current / max)
- Learning entries count
- Performance records count
- Memory age (oldest conversation)
- Storage size (MB)
- Average response time
- Learned accuracy percentage
- Recent improvements
- Auto-pruning configuration
- Storage file locations

### Manual Pruning
```bash
Genesis> #prune_memory
```

Manually trigger memory pruning to optimize storage immediately.

### Export Memory Backup
```bash
Genesis> #export_memory
```

Creates timestamped backup of all memory data:
- `~/Genesis/data/memory/exports/genesis_memory_backup_YYYYMMDD_HHMMSS.json`

**Includes:**
- All conversation memory
- Complete learning log
- Performance history
- User preferences

---

## 📈 Memory Report Example

```
╔══════════════════════════════════════════════════════════════╗
║        🧠 GENESIS MEMORY & LEARNING SYSTEM                    ║
╚══════════════════════════════════════════════════════════════╝

📚 PERSISTENT MEMORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Conversations Stored:           342 / 1000
Learning Entries:               87
Performance Records:            342
Memory Age:                     15 days
Storage Size:                   2.45 MB

📈 PERFORMANCE HISTORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average Response Time:          3,245.67 ms
Learned Accuracy:               91.2%
Records Tracked:                342

🎓 LEARNING LOG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Learning Entries:         87
Recent Improvements:            12

⚙️ AUTO-PRUNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Max Conversations:              1000
Max Age:                        90 days
Prune Threshold:                80%
Next Prune At:                  800 conversations

💾 STORAGE LOCATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Conversations:                  data/memory/conversation_memory.json
Learning Log:                   data/memory/learning_log.json
Performance:                    data/memory/performance_history.json
Preferences:                    data/memory/user_preferences.json

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Commands: #memory | #prune_memory | #export_memory
```

---

## 📁 Data Storage

### File Structure
```
~/Genesis/
└── data/
    └── memory/
        ├── conversation_memory.json    # Conversation history
        ├── learning_log.json           # Learning events
        ├── performance_history.json    # Performance metrics
        ├── user_preferences.json       # User settings
        └── exports/                    # Memory backups
            └── genesis_memory_backup_*.json
```

### Data Formats

**conversation_memory.json:**
```json
{
  "conversations": [
    {
      "timestamp": "2025-11-05T13:24:39.331",
      "user_input": "list files in home directory",
      "assistant_response": "📂 /data/data/com.termux/files/home\n[file listing]",
      "metadata": {
        "was_direct_command": true,
        "confidence_score": 1.0,
        "had_fallback": false
      }
    }
  ]
}
```

**learning_log.json:**
```json
{
  "entries": [
    {
      "timestamp": "2025-11-05T14:30:22.445",
      "type": "feedback",
      "description": "User marked response as correct",
      "feedback": "correct",
      "improvement": "Validated direct command execution"
    }
  ]
}
```

**performance_history.json:**
```json
{
  "history": [
    {
      "timestamp": "2025-11-05T15:10:05.123",
      "response_time_ms": 245.67,
      "accuracy": true,
      "claude_fallback": false,
      "error": null
    }
  ]
}
```

**user_preferences.json:**
```json
{
  "style": "default",
  "verbosity": "normal",
  "topics": {},
  "feedback_patterns": {}
}
```

---

## 🔄 How It Works

### 1. Conversation Storage

When you interact with Genesis:

```python
# After every interaction (direct commands and LLM responses)
self.learning.add_conversation(
    user_input="your query",
    assistant_response="Genesis response",
    metadata={
        "was_direct_command": True/False,
        "confidence_score": 0.0-1.0,
        "had_fallback": True/False
    }
)
```

### 2. Auto-Pruning Trigger

When conversations reach 800 (80% of 1000):

```python
if len(conversations) >= max_conversations * prune_threshold:
    self._prune_conversations()
```

### 3. Pruning Process

1. Score each conversation (age + length + metadata)
2. Sort by score (highest = most valuable)
3. Keep top 70% (700 conversations)
4. Log pruning event
5. Save updated memory

### 4. Learning Events

Genesis logs improvements:

```python
self.learning.add_learning_entry(
    event_type="feedback",
    description="User marked response as correct",
    feedback="correct",
    improvement="Validated approach"
)
```

---

## 💡 Usage Tips

### Best Practices

**1. Regular Memory Review**
```bash
Genesis> #memory  # Check weekly
```
Monitor:
- Memory growth rate
- Accuracy trends
- Pruning frequency

**2. Export Important Sessions**
```bash
Genesis> #export_memory  # Before major changes
```
Good times to export:
- Before system updates
- After successful project completion
- When changing workflows

**3. Manual Pruning**
```bash
Genesis> #prune_memory  # When needed
```
Use when:
- Storage approaching limit
- After experimental sessions
- To remove old conversations

### Understanding Memory Age

- **< 30 days:** Fresh memory, highly relevant
- **30-60 days:** Mature memory, still valuable
- **60-90 days:** Old memory, pruning candidate
- **> 90 days:** Automatically pruned

---

## 🎯 Benefits

### 1. Continuous Learning
Genesis learns from:
- User feedback (#correct / #incorrect)
- Successful interactions
- Error patterns
- Claude fallback triggers

### 2. Personalization
Over time, Genesis adapts to:
- Your communication style
- Preferred command formats
- Common tasks and workflows
- Error handling preferences

### 3. Performance Optimization
Memory helps Genesis:
- Respond faster (cached patterns)
- Avoid repeated mistakes
- Improve accuracy over time
- Self-optimize behavior

### 4. Privacy
- **100% local storage** (no cloud sync)
- Complete data control
- Easy export and backup
- Transparent data management

---

## 🔧 Configuration

### Memory Settings

Edit `learning_memory.py` initialization:

```python
self.learning = LearningMemory(
    memory_dir="data/memory",       # Storage location
    max_conversations=1000,         # Maximum conversations
    max_age_days=90,                # Maximum age (days)
    prune_threshold=0.8             # Prune at 80% capacity
)
```

**Recommended Settings:**

| Use Case | max_conversations | max_age_days | prune_threshold |
|----------|-------------------|--------------|-----------------|
| Light use | 500 | 60 | 0.8 |
| Normal use | 1000 | 90 | 0.8 |
| Heavy use | 2000 | 120 | 0.85 |
| Research | 5000 | 180 | 0.9 |

---

## 📊 Memory Analytics

### Get Recent Learning
```python
from learning_memory import LearningMemory

learning = LearningMemory()
recent = learning.get_recent_learning(count=10)
for entry in recent:
    print(f"{entry['timestamp']}: {entry['description']}")
```

### Get Relevant Context
```python
# Find conversations similar to current query
context = learning.get_relevant_context("Python scripting", max_results=5)
for conv in context:
    print(f"Q: {conv['user_input']}")
    print(f"A: {conv['assistant_response']}\n")
```

### Export for Analysis
```python
export_path = learning.export_memory("analysis_backup.json")
# Analyze with external tools
```

---

## 🚀 Advanced Features

### Custom Learning Events

Log custom events:

```python
self.learning.add_learning_entry(
    event_type="custom",
    description="Discovered new optimization",
    improvement="Reduced response time by 20%"
)
```

### User Preference Updates

Store preferences:

```python
self.learning.update_user_preference("verbosity", "concise")
self.learning.update_user_preference("code_style", "pythonic")
```

### Memory Statistics

Get detailed stats:

```python
summary = learning.get_memory_summary()
print(summary)  # Full formatted report
```

---

## 🆘 Troubleshooting

### Memory Growing Too Fast

**Symptom:** Frequent auto-pruning, large storage size

**Solutions:**
1. Reduce `max_conversations` setting
2. Lower `max_age_days` for more aggressive pruning
3. Manually prune: `#prune_memory`
4. Check for runaway conversation loops

### Memory Not Updating

**Symptom:** #memory shows no new conversations

**Check:**
1. Verify data directory exists and is writable:
   ```bash
   ls -la ~/Genesis/data/memory/
   ```
2. Check file permissions:
   ```bash
   chmod 755 ~/Genesis/data/memory/
   chmod 644 ~/Genesis/data/memory/*.json
   ```
3. Review error logs

### Pruning Too Aggressive

**Symptom:** Important conversations being removed

**Solutions:**
1. Increase `prune_threshold` to 0.9 (prune at 90%)
2. Increase `max_conversations` to 2000+
3. Export before pruning: `#export_memory`
4. Mark important conversations with positive feedback

---

## 📚 Technical Details

### Module: `learning_memory.py`
- **Size:** ~413 lines
- **Dependencies:** `json`, `datetime`, `pathlib`, `threading`, `statistics`
- **Thread-safe:** Yes (uses `Lock`)
- **Storage:** JSON files (lightweight, portable)

### Performance Impact
- **Memory:** < 10 MB typical (depends on conversation count)
- **CPU:** Negligible (async I/O, pruning only when needed)
- **Disk:** ~2-5 MB per 1000 conversations
- **Startup:** < 100 ms (loads existing memory)

### Pruning Performance
- **1000 conversations:** ~50-100 ms
- **5000 conversations:** ~200-400 ms
- **Non-blocking:** Doesn't slow down interactions

---

## 🎓 Examples

### Example 1: Track Learning Progress

```bash
Genesis> #memory
[Shows 50 conversations, 72% accuracy]

# Use Genesis for 1 week, provide feedback...

Genesis> #memory
[Shows 250 conversations, 89% accuracy]
```

**Result:** Genesis learned from feedback and improved accuracy by 17%

### Example 2: Recover from Mistake

```bash
Genesis> write buggy code
[Genesis writes code with error]

Genesis> #incorrect
✗ Last response marked as incorrect

[Genesis logs the mistake]
[Future similar queries benefit from this feedback]
```

### Example 3: Export Project Memory

```bash
# After completing a project
Genesis> #export_memory
✓ Memory exported to data/memory/exports/genesis_memory_backup_20251105_143022.json

# Backup contains all conversations and learning from the project
# Can be imported later or analyzed externally
```

### Example 4: Monitor Memory Growth

```bash
# Day 1
Genesis> #memory
Conversations Stored: 45 / 1000
Storage Size: 0.52 MB

# Day 30
Genesis> #memory
Conversations Stored: 673 / 1000
Storage Size: 3.21 MB

# Day 60 (auto-pruned)
Genesis> #memory
Conversations Stored: 724 / 1000  # Stayed under 800 due to pruning
Storage Size: 3.45 MB
```

---

## ✅ Testing

### Test Memory System
```bash
cd ~/Genesis
python -c "
from learning_memory import LearningMemory
import time

# Initialize
memory = LearningMemory()

# Add test conversation
memory.add_conversation(
    'test query',
    'test response',
    {'confidence_score': 0.95}
)

# Check summary
print(memory.get_memory_summary())
"
```

**Expected:** Memory summary with 1 conversation stored

---

## 🎯 Summary

Genesis Learning & Memory System provides:

✅ Persistent conversation storage across sessions
✅ Intelligent auto-pruning based on value scoring
✅ Complete learning event log
✅ Performance history tracking
✅ User preference storage
✅ Thread-safe concurrent access
✅ Lightweight JSON storage
✅ Easy backup and export
✅ Privacy-focused (100% local)
✅ Continuous improvement capability

**No configuration needed** - works automatically from first use!

---

**Commands Quick Reference:**
- `#memory` - View memory system summary
- `#prune_memory` - Manually trigger pruning
- `#export_memory` - Export memory backup

---

**Status:** ✅ Production Ready
**Module:** `learning_memory.py`
**Storage:** `~/Genesis/data/memory/`
**Documentation:** This file

---

🧬 **Genesis: Learning AI. Improving AI. Remembering AI.**
