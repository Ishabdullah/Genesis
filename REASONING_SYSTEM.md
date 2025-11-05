# 🧬 Genesis Reasoning System

## Overview

Genesis now includes a **comprehensive reasoning system** that displays multi-step thinking, generates pseudocode for programming problems, and validates logical consistency before presenting answers.

---

## ✅ Features

### 1. Multi-Step Reasoning

**Visible Thinking Process:**
- Genesis shows its reasoning steps before giving answers
- Each step is displayed sequentially with descriptions
- Calculations and intermediate results are shown
- Helps users understand the logic behind answers

**Problem Types Detected:**
- **Math Word Problems** - Multi-step calculations
- **Logic Problems** - Premise-conclusion chains
- **Programming** - Algorithm design
- **System Design** - Architecture planning
- **General** - Default reasoning framework

---

### 2. Pseudocode Generation

**For Programming Problems:**
- Automatically detects programming/algorithm queries
- Generates structured pseudocode before actual code
- Shows algorithmic thinking
- Helps understand approach before implementation

**Pseudocode Format:**
```
PSEUDOCODE:
──────────────────
FUNCTION name(parameters):
  // Step 1: Initialize
  // Step 2: Process
  // Step 3: Return result
END FUNCTION
```

---

### 3. Thinking Trace Display

**Live Step-by-Step Display:**
```
[Thinking...]
────────────────────────────────────────────────────────────

Step 1: Identify the given information
  → Extract numbers and relationships from the problem

Step 2: Determine what needs to be calculated
  → Identify the target variable or question

Step 3: Set up the mathematical relationship
  → Establish formula or equation

Step 4: Perform the calculation
  → Apply the formula with given values

Step 5: Verify the answer
  → Check if the result makes logical sense

────────────────────────────────────────────────────────────

Final Answer:
────────────────────────────────────────────────────────────
[Genesis's answer here]

Confidence: High (0.85)
────────────────────────────────────────────────────────────
```

---

### 4. Reasoning Validation

**Automatic Validation:**
- Checks reasoning chain for consistency
- Verifies sufficient steps were taken
- Flags missing calculations for math problems
- Warns if answer seems incomplete

**Validation Warnings:**
```
⚠ Reasoning Validation Warnings:
  1. Reasoning may be too brief - consider more detailed steps
  2. Math problem but no explicit calculations shown
```

---

## 📊 Problem Type Detection

### Math Word Problems
**Triggers:** if, how many, calculate, total, rate, per
**Reasoning Steps:**
1. Identify given information
2. Determine what to calculate
3. Set up relationship/formula
4. Perform calculation
5. Verify answer

**Example:**
```
User: If 3 cats catch 3 mice in 3 minutes, how many cats
      do you need to catch 100 mice in 100 minutes?

[Thinking...]
Step 1: Identify the given information
  → 3 cats catch 3 mice in 3 minutes
  → Need to catch 100 mice in 100 minutes

Step 2: Determine what needs to be calculated
  → Number of cats required

Step 3: Set up the mathematical relationship
  → Rate = mice per cat per time
  → 3 cats → 3 mice in 3 min = 1 mouse/cat/3min

Step 4: Perform the calculation
  → In 100 minutes: each cat catches 100/3 ≈ 33.3 mice
  → To catch 100 mice: 100 / 33.3 = 3 cats

Step 5: Verify the answer
  → 3 cats × 33.3 mice/cat ≈ 100 mice ✓

Final Answer:
3 cats are needed.
```

---

### Logic Problems
**Triggers:** implies, if...then, therefore, because
**Reasoning Steps:**
1. Identify premises
2. Identify conclusion
3. Check logical connections
4. Apply logical rules
5. State conclusion with justification

**Example:**
```
User: If A implies B and B implies C, does A imply C?

[Thinking...]
Step 1: Identify the premises (given statements)
  → Premise 1: A → B
  → Premise 2: B → C

Step 2: Identify what needs to be proven/concluded
  → Does A → C?

Step 3: Check logical connections between premises
  → Chain: A → B → C

Step 4: Apply logical rules (transitivity, modus ponens, etc.)
  → By transitive property of implication

Step 5: State the conclusion with justification
  → Yes, A → C by transitivity

Final Answer:
Yes, A implies C. This follows from the transitive property
of logical implication: if A→B and B→C, then A→C.
```

---

### Programming Problems
**Triggers:** write, function, code, implement, algorithm
**Reasoning Steps:**
1. Identify input types/constraints
2. Determine required operations
3. Design algorithm (with pseudocode)
4. Consider edge cases
5. Implement solution

**Example:**
```
User: Write a Python function that returns the sum of even
      numbers in a list.

[Thinking...]
Step 1: Identify input types and constraints
  → Input: list of numbers
  → Constraint: sum only even numbers

Step 2: Determine required operations
  → Filter even numbers (n % 2 == 0)
  → Sum filtered numbers

Step 3: Design the algorithm
  → (Pseudocode shown below)

Step 4: Consider edge cases
  → Empty list → return 0
  → No even numbers → return 0
  → All even → sum all

Step 5: Implement the solution
  → (Code shown below)

────────────────────────────────────────────────────────────

[Pseudocode]
────────────────────────────────────────────────────────────
PSEUDOCODE:
──────────────────
FUNCTION sum_filtered(list):
  SET total = 0
  FOR each element IN list:
    IF element meets condition:
      ADD element TO total
  RETURN total
END FUNCTION
────────────────────────────────────────────────────────────

Final Answer:
────────────────────────────────────────────────────────────
def sum_even_numbers(lst):
    return sum(x for x in lst if x % 2 == 0)
```

---

### Design Problems
**Triggers:** design, architect, structure, system, plan
**Reasoning Steps:**
1. Understand requirements
2. Identify key components
3. Define relationships/interfaces
4. Consider constraints/trade-offs
5. Produce design specification

---

## 🎨 Visual Display

### Color Coding

**Thinking Section:**
- Cyan: [Thinking...] header
- Yellow: Step numbers
- Blue: Calculations/logic (→)
- Green: Results (✓)
- Dim: Separators

**Pseudocode:**
- Magenta: [Pseudocode] header
- Cyan: FUNCTION, END statements
- Yellow: IF, FOR, WHILE loops
- Green: RETURN statements
- Dim: Comments (//)

**Final Answer:**
- Green Bold: "Final Answer:"
- Confidence indicator with color:
  - Green: High (≥ 0.9)
  - Yellow: Medium/Low (< 0.9)

---

## 🔧 Technical Implementation

### Core Modules

**reasoning.py (450+ lines):**
- `ReasoningEngine` class
- Problem type detection
- Multi-step reasoning generation
- Pseudocode generation
- Reasoning validation

**thinking_trace.py (200+ lines):**
- `ThinkingTrace` class
- Live display of reasoning steps
- Formatted pseudocode output
- Final answer presentation
- Validation warnings display

**Integration in genesis.py:**
- Reasoning before LLM call
- Pseudocode for programming problems
- Validation before answer display
- Reasoning trace stored in memory

---

## 📈 Reasoning Flow

```
User Query
    ↓
Detect Problem Type
    ↓
Generate Reasoning Steps
    ↓
Display [Thinking...] Trace
    ↓
Show Pseudocode (if programming)
    ↓
Call LLM for Answer
    ↓
Validate Reasoning Chain
    ↓
Display Warnings (if any)
    ↓
Present Final Answer
    ↓
Store in Learning Memory
```

---

## 💾 Memory Integration

**Reasoning Traces Stored:**
```json
{
  "user_input": "If 3 cats catch 3 mice...",
  "assistant_response": "3 cats are needed",
  "metadata": {
    "problem_type": "math_word_problem",
    "reasoning_steps": [
      {"step": 1, "description": "Identify given info"},
      {"step": 2, "description": "Determine calculation"},
      {"step": 3, "description": "Set up relationship"},
      {"step": 4, "description": "Perform calculation"},
      {"step": 5, "description": "Verify answer"}
    ],
    "reasoning_valid": true,
    "confidence_score": 0.85
  }
}
```

**Benefits:**
- Review past reasoning processes
- Learn from feedback on reasoning quality
- Track which problem types are handled well
- Improve reasoning over time

---

## 🎯 Usage Examples

### Example 1: Math Problem

**Input:**
```
Genesis> What is 15% of 200 plus 10?
```

**Output:**
```
[Thinking...]
────────────────────────────────────────────────────────────

Step 1: Identify the given information
  → Calculate 15% of 200, then add 10

Step 2: Determine what needs to be calculated
  → Two operations: percentage, then addition

Step 3: Set up the mathematical relationship
  → (200 × 0.15) + 10

Step 4: Perform the calculation
  → 30 + 10 = 40

Step 5: Verify the answer
  → 15% of 200 = 30 ✓, 30 + 10 = 40 ✓

────────────────────────────────────────────────────────────

Final Answer:
────────────────────────────────────────────────────────────
40

Confidence: High (0.95)
────────────────────────────────────────────────────────────
```

---

### Example 2: Programming Problem

**Input:**
```
Genesis> Write a function to check if a string is a palindrome.
```

**Output:**
```
[Thinking...]
────────────────────────────────────────────────────────────

Step 1: Identify input types and constraints
  → Input: string
  → Output: boolean (True/False)

Step 2: Determine required operations
  → Compare string with its reverse

Step 3: Design the algorithm
  → (See pseudocode below)

Step 4: Consider edge cases
  → Empty string → True (trivially palindrome)
  → Single character → True
  → Case sensitivity → normalize to lowercase

Step 5: Implement the solution
  → (See code below)

────────────────────────────────────────────────────────────

[Pseudocode]
────────────────────────────────────────────────────────────
FUNCTION is_palindrome(string):
  NORMALIZE string to lowercase
  REVERSE the string
  COMPARE original with reversed
  RETURN result (True/False)
END FUNCTION
────────────────────────────────────────────────────────────

Final Answer:
────────────────────────────────────────────────────────────
def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]

Confidence: High (0.92)
────────────────────────────────────────────────────────────
```

---

## ⚡ Performance Impact

**Reasoning Generation:**
- Time: < 50ms (instant)
- Memory: Minimal (~1KB per trace)
- Display: ~1-2 seconds (with animation)

**Overall Impact:**
- Startup: No change
- Response time: +1-2s (display overhead)
- User value: Significantly improved transparency

---

## 🔍 Validation System

### What Gets Validated:

1. **Step Count** - At least 3 steps for complex problems
2. **Calculations** - Math problems should show explicit calculations
3. **Completeness** - Final answer not empty
4. **Logical Flow** - Steps connect logically

### Validation Output:

**Valid Reasoning:**
```
✓ No warnings - reasoning appears sound
```

**With Warnings:**
```
⚠ Reasoning Validation Warnings:
  1. Reasoning may be too brief - consider more detailed steps
  2. Math problem but no explicit calculations shown
```

---

## 📚 Commands

**No new commands needed** - reasoning system activates automatically for:
- Any query that goes to LLM
- Automatically detects problem type
- Shows appropriate reasoning framework
- Generates pseudocode when relevant

**Existing Commands Still Work:**
- `#correct` - Marks reasoning as good
- `#incorrect` - Flags reasoning issues
- `#performance` - Includes reasoning metrics
- `#memory` - Shows stored reasoning traces

---

## 🎓 Educational Value

### For Users:

**Learn Through Reasoning:**
- See how problems are broken down
- Understand logical thinking process
- Follow calculations step-by-step
- Learn algorithm design patterns

**Build Confidence:**
- Transparent process = trust
- Can verify reasoning logic
- Catch errors before accepting answers
- Understand "why" not just "what"

---

## 🚀 Future Enhancements

**Potential Improvements:**
1. Interactive reasoning (ask Genesis to explain steps)
2. Alternative reasoning paths
3. Reasoning comparison (multiple approaches)
4. User-guided reasoning (override steps)
5. Reasoning templates for common problems
6. Export reasoning as flowcharts
7. Reasoning quality scoring
8. Learning from reasoning feedback

---

## ✅ Testing

### Run Reasoning Test Suite:
```bash
cd ~/Genesis
./test_reasoning.sh
```

**Tests:**
1. Multi-step math problem (cats & mice)
2. Logical reasoning (transitivity)
3. Programming with pseudocode
4. System design problem
5. Algorithm design

**Expected Output:**
- [Thinking...] section visible
- 5 reasoning steps shown
- Pseudocode for programming problems
- Final Answer clearly separated
- Confidence score displayed
- No validation warnings

---

## 🎯 Summary

Genesis reasoning system provides:

✅ **Multi-Step Reasoning** - Break down complex problems
✅ **Pseudocode Generation** - Show algorithmic thinking
✅ **Visible Thinking** - Transparent problem-solving process
✅ **Validation** - Check reasoning consistency
✅ **Memory Integration** - Store reasoning for learning
✅ **Automatic Detection** - No user configuration needed
✅ **Color-Coded Display** - Easy to follow visually

**Result:** Users understand not just what Genesis answers, but **why** and **how** it arrived at that answer.

---

**Status:** ✅ Production Ready
**Modules:** reasoning.py, thinking_trace.py
**Integration:** genesis.py
**Test Suite:** test_reasoning.sh
**Documentation:** This file

🧬 **Genesis: Now with transparent, step-by-step reasoning!**
