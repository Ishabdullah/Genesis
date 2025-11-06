# 🧬 Super Genesis - Quick Start Guide

## Welcome to Super Genesis!

Your Genesis AI assistant has been upgraded with advanced reasoning, retry functionality, and multi-source knowledge integration.

---

## 🚀 Try It Right Now

### 1. **See Multi-Step Reasoning**

```bash
Genesis> If 5 workers build 5 houses in 5 days, how many workers
         needed to build 20 houses in 20 days?
```

**What you'll see:**
- `[Thinking... 🧬 Local]` - Genesis shows its reasoning
- Step-by-step breakdown of the problem
- Final answer with confidence score

---

### 2. **Test Retry Functionality**

```bash
Genesis> What is the capital of France?
Genesis> try again
```

**What happens:**
- Genesis re-processes your last question
- You'll see: `♻️ Retrying last query: "What is the capital of France?"`

---

### 3. **Use Follow-Up Commands**

```bash
Genesis> Python is a programming language.
Genesis> tell me more
```

**What happens:**
- Genesis uses context from previous interaction
- You'll see: `📚 Using context from previous interaction`

---

### 4. **Try a Programming Problem**

```bash
Genesis> Write a Python function to find the maximum value in a list.
```

**What you'll see:**
- Multi-step reasoning
- **Pseudocode** showing the algorithm
- Final Python implementation

---

### 5. **Check Performance Metrics**

```bash
Genesis> #performance
```

**What you'll see:**
```
🌐 RESPONSE SOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🧬 Local (Genesis):           X
  🔍 Perplexity Research:       X
  ☁️ Claude Fallback:           X
```

---

## 📋 All New Commands

### Retry Commands (Any of these work)
- `try again`
- `recalculate`
- `retry`
- `redo that`
- `do that again`

### Follow-Up Commands (Any of these work)
- `explain further`
- `give an example`
- `tell me more`
- `elaborate`
- `more details`

### Existing Commands
- `#performance` - View performance metrics (now with sources!)
- `#memory` - View learning memory (now with reasoning traces!)
- `#correct` - Mark last response as correct
- `#incorrect` - Mark last response as incorrect
- `#math <expr>` - Quick math calculation
- `#reverse <text>` - Reverse text
- `#verify` - Genesis self-verification

---

## 🔍 Multi-Source Knowledge

When Genesis is uncertain (confidence < 60%), it will automatically:

1. Try **Perplexity** for external research
2. Fall back to **Claude** if Perplexity fails
3. Show you which source provided the answer

**Example:**
```
⚡ Genesis is uncertain (confidence: 0.45)
   Consulting external sources...

[Thinking... 🔍 Consulting Perplexity]
✓ Perplexity consultation successful

Source: 🔍 Perplexity Research
```

---

## 🎯 Problem Types Detected

Genesis automatically detects problem types and applies appropriate reasoning:

1. **Math Word Problems** - Multi-step calculations
2. **Logic Problems** - Premise-conclusion chains
3. **Programming** - Algorithm design with pseudocode
4. **System Design** - Architecture planning
5. **General** - Default reasoning framework

---

## 🧪 Run the Test Suite

Want to see all features in action?

```bash
cd ~/Genesis
./test_super_genesis.sh
```

This runs 10 comprehensive tests showing:
- Multi-step reasoning
- Retry functionality
- Context handling
- Source tracking
- Performance metrics
- And more!

---

## 📖 Full Documentation

For complete details, see:

- **SUPER_GENESIS.md** - Complete feature guide (800+ lines)
- **REASONING_SYSTEM.md** - Reasoning system details
- **SESSION-6-SUMMARY.md** - Implementation summary

---

## 💡 Tips & Tricks

### Get Better Reasoning
Genesis shows more detailed reasoning for:
- Math problems (calculations shown step-by-step)
- Logic problems (premise-conclusion chains)
- Programming (with pseudocode!)

### Use Retry Effectively
- After marking response as `#incorrect`
- To test consistency
- To get alternative phrasing

### Leverage Context
Ask follow-up questions naturally:
- "tell me more"
- "give an example"
- "explain further"

Genesis remembers the last 15 interactions!

### Track Your Sources
Check `#performance` to see:
- How often Genesis answers locally
- When Perplexity was consulted
- When Claude fallback was used

---

## 🎓 Example Session

```bash
Genesis> If 3 cats catch 3 mice in 3 minutes, how many cats
         do you need to catch 100 mice in 100 minutes?

[Thinking... 🧬 Local]
────────────────────────────────────────────────────────────

Step 1: Identify the given information
  → 3 cats catch 3 mice in 3 minutes
  → Need to catch 100 mice in 100 minutes

Step 2: Determine what needs to be calculated
  → Number of cats required

Step 3: Set up the mathematical relationship
  → Rate: 1 cat → 1 mouse per 3 minutes
  → In 100 minutes: 1 cat → ~33 mice

Step 4: Perform the calculation
  → 100 mice ÷ 33 mice/cat = 3 cats

Step 5: Verify the answer
  → 3 cats × 33 mice/cat ≈ 100 mice ✓

────────────────────────────────────────────────────────────

Final Answer:
────────────────────────────────────────────────────────────
3 cats

Confidence: High (0.92)
────────────────────────────────────────────────────────────

Genesis> recalculate
♻️ Retrying last query: "If 3 cats catch 3 mice..."

[... processes again ...]

Genesis> #performance

╔══════════════════════════════════════════════════════════════╗
║           🧬 GENESIS PERFORMANCE METRICS                      ║
╚══════════════════════════════════════════════════════════════╝

📊 OVERALL STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Queries Processed:        2
  • Direct Commands (instant):  0
  • LLM Queries (20-30s):        2

🌐 RESPONSE SOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🧬 Local (Genesis):           2
  🔍 Perplexity Research:       0
  ☁️ Claude Fallback:           0

✅ USER FEEDBACK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Feedback Given:           0
```

---

## 🎉 Enjoy Super Genesis!

You now have:
- ✅ Transparent reasoning
- ✅ Natural retry commands
- ✅ Context-aware conversations
- ✅ Multi-source knowledge
- ✅ Complete source tracking

**Start exploring and see Genesis think step-by-step!**

---

🧬 **Super Genesis: Think, Retry, Consult, Learn!**
