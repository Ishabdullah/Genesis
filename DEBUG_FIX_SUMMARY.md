# Genesis Debug Output Fix - Summary

**Date:** 2025-11-06
**Branch:** `claude/debug-genesis-output-011CUs8vyEoX172RV7jsz4y5`
**Issue:** Genesis was generating incorrect math answers with debug text, tool commands, and extra Q&A pairs

---

## Problem Description

When asked: *"A pharmaceutical factory has 8 machines that can package 8,000 tablets in 8 hours. The factory needs to package 50,000 tablets in 10 hours. How many machines are required?"*

**Expected Answer:** 40 machines
**Genesis Output:** Wrong answer with debug text, tool instructions, and extra Q&A pairs

### Issues Found:

1. **Tool instructions leaking into model output**
   - Prompt contained: "LIST: /path", "READ: /path/file", "SEARCH: pattern"
   - Model echoed these and Genesis tried to execute them as commands
   - Result: "⚠ File not found: /path/file to read a file"

2. **Model generating extra Q&A content**
   - No stop tokens configured
   - Model continued generating after it should stop
   - Created nonsense Q1-Q6 with wrong calculations

3. **Calculated answer getting buried**
   - Math reasoner correctly calculated 40 machines
   - But LLM response with garbage obscured the correct answer
   - Priority chain didn't skip LLM when math answer was ready

4. **Debug formatting visible to users**
   - "Step 1:", "Final Answer:", "Confidence: High" displayed
   - These are internal reasoning traces but appeared as final output

---

## Root Cause Analysis

### File: `genesis.py`

**Line 256-272:** Tool instructions in prompt
```python
tool_instructions = """You are Genesis. Be direct, concise, and focused.

Available tools:
- LIST: /path - list directory
- READ: /path/file - read file
- SEARCH: pattern in /path - search content
```
→ These were meant as internal guidance but model echoed them

**Line 895:** LLM called even when math answer ready
```python
response = self.call_llm(user_input)
```
→ Should skip LLM when math reasoner has deterministic answer

**Line 284-300:** No stop tokens
→ Model rambled generating extra content

---

## Fixes Applied

### 1. Removed Tool Instructions from Model Output (genesis.py:256-265)

**Before:**
```python
tool_instructions = """You are Genesis. Be direct, concise, and focused.

Available tools:
- LIST: /path - list directory
- READ: /path/file - read file
- SEARCH: pattern in /path - search content
```

**After:**
```python
tool_instructions = """You are Genesis, a helpful AI assistant. Answer the user's question directly and concisely.

Rules:
1. Answer the user's CURRENT question only
2. Be brief and action-oriented
3. For math problems: state the final answer clearly
4. For code: write clean, working code
5. Do NOT include file paths, tool commands, or placeholder text
6. Do NOT generate example Q&A pairs
```

### 2. Skip LLM When Math Answer Ready (genesis.py:894-911)

**Added:**
```python
# Check if math reasoner already calculated the answer
calculated_answer = self.reasoning.get_calculated_answer()
used_calculated_answer = False

if calculated_answer:
    # We have a deterministic math answer - skip LLM call
    response = f"{calculated_answer}"
    response_source = "local_calculated"
    used_calculated_answer = True
else:
    # Need LLM for non-math or unsolved problems
    response_source = "local"
    response = self.call_llm(user_input)
```

### 3. Added Stop Tokens (genesis.py:293-299)

**Added to llama.cpp command:**
```python
"--stop", "Q1:",  # Stop if model starts generating Q&A
"--stop", "Q2:",
"--stop", "LIST:",  # Stop if model outputs tool commands
"--stop", "READ:",
"--stop", "SEARCH:",
"--stop", "[File",  # Stop if model tries to show file operations
"--stop", "[Directory"
```

**Also adjusted parameters:**
- Temperature: 0.5 → 0.3 (more focused)
- Max tokens: 250 → 150 (prevent rambling)

### 4. Skip Uncertainty Check for Calculated Answers (genesis.py:915-929)

**Added:**
```python
# Skip uncertainty check if we used calculated answer (it's deterministic)
if used_calculated_answer:
    should_fallback = False
    uncertainty_analysis = {"confidence_score": 1.0}
else:
    should_fallback, uncertainty_analysis = self.uncertainty.should_trigger_fallback(response)
```

### 5. Prevent response_source Overwriting (genesis.py:934-936)

**Fixed:**
```python
# Don't overwrite response_source if already set (e.g., "local_calculated")
if not used_calculated_answer:
    response_source = "local"
```

---

## How It Works Now

### For Math Problems:

1. **User asks math question** → Genesis detects it's a math problem
2. **Math reasoner calculates answer** → Uses rate formula: 40 machines
3. **Reasoning trace displays steps** → Shows calculation process
4. **LLM call is skipped** → Uses calculated answer directly
5. **Final answer displayed** → Clean output: "40"

### Math Reasoner Detection:

The pharmaceutical tablets problem matches the rate problem pattern:

```python
# Pattern: X workers do Y items in Z time
rate_pattern = r'(\d+)\s+(machines?|cats?|workers?|people)'

# Extracted numbers: [8, 8000, 8, 50000, 10]
# Calculation:
# - rate_per_worker = 8000 / (8 × 8) = 125 tablets/machine/hour
# - required_rate = 50000 / 10 = 5000 tablets/hour
# - workers_needed = 5000 / 125 = 40 machines ✓
```

---

## Testing Checklist

### Before Testing:
1. Ensure llama.cpp is built and model is available
2. Verify Genesis can start without errors
3. Check that math_reasoner.py and reasoning.py are working

### Test Cases:

#### Test 1: Pharmaceutical Tablets Problem
**Input:**
```
A pharmaceutical factory has 8 machines that can package 8,000 tablets
in 8 hours. The factory needs to package 50,000 tablets in 10 hours.
How many machines are required?
```

**Expected Output:**
```
[Thinking... 🧬 Local]
────────────────────────────────────────────────────────────

Step 1: Calculate production rate per worker per time unit
  → 8000 / (8 × 8)
  ✓ 125.0 units per worker per time unit

Step 2: Calculate required total production rate
  → 50000 / 10
  ✓ 5000.0 units per time unit

Step 3: Calculate number of workers needed
  → 5000.0 / 125.0
  ✓ 40.0 workers

Step 4: Verify the answer
  → 40.0 × 125.0 × 10
  ✓ 50000.0 units (should equal 50000) ✓

────────────────────────────────────────────────────────────

Final Answer:
────────────────────────────────────────────────────────────
40

Confidence: High (1.00)
────────────────────────────────────────────────────────────
```

**No:**
- Tool instructions (LIST:, READ:, SEARCH:)
- Extra Q&A pairs (Q1:, Q2:, etc.)
- Wrong calculations
- File operation errors

#### Test 2: Simple Math
**Input:** `What is 15 × 23?`
**Expected:** Clean answer with calculation

#### Test 3: Non-Math Question
**Input:** `Who are you?`
**Expected:** Genesis identity response (should use LLM normally)

#### Test 4: Code Generation
**Input:** `Write a Python function to reverse a string`
**Expected:** Clean code output (should use LLM normally)

---

## Verification Commands

```bash
# Verify syntax
python3 -m py_compile genesis.py

# Check for remaining tool instruction strings
grep -n "LIST: /path" genesis.py
grep -n "READ: /path" genesis.py

# Run Genesis
python3 genesis.py
```

---

## Success Criteria

✅ Math problems return correct numerical answers
✅ No tool instructions appear in output
✅ No extra Q&A pairs generated
✅ No "⚠ File not found" errors for placeholder paths
✅ Reasoning trace shows calculation steps clearly
✅ Non-math queries work normally with LLM

---

## Files Modified

- `genesis.py` - Main fixes (5 changes)
  - Line 256-265: Removed tool instructions from prompt
  - Line 276-300: Added stop tokens
  - Line 894-911: Skip LLM when math answer ready
  - Line 915-929: Skip uncertainty for calculated answers
  - Line 934-936: Prevent response_source overwriting

---

## Implementation Notes

- **Backward Compatible:** Non-math queries continue to use LLM normally
- **Performance:** Math problems now faster (skip LLM inference)
- **Accuracy:** Deterministic math calculations (100% confidence)
- **User Experience:** Clean output without debug artifacts

---

## Rollback Instructions

If issues occur:

```bash
git checkout HEAD~1 -- genesis.py
python3 genesis.py
```

Or restore specific changes as needed.

---

## Related Issues

- Genesis v2.1.1 reasoning trace clarity improvements
- Math reasoner integration (math_reasoner.py)
- Uncertainty detection system
- Thinking trace display module

---

**Status:** ✅ Fixed and ready for testing
**Next Steps:** Test with sample math problems, monitor for regressions
