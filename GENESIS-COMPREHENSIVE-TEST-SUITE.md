# Genesis Comprehensive Test Suite
## Novel Test Questions for All Functions

**Date:** November 6, 2025
**Purpose:** Test every Genesis capability with completely new queries
**Status:** Ready for execution

---

## 📋 Test Categories

### 1. Deterministic Math Engine
### 2. Temporal Awareness & Time-Sensitive Queries
### 3. Code Generation & Execution
### 4. File Operations
### 5. Multi-Step Reasoning
### 6. Context & Memory Persistence
### 7. Adaptive Learning & Feedback
### 8. Tone Detection & Control
### 9. External Research (WebSearch, Perplexity, Claude)
### 10. Retry & Error Recovery
### 11. Performance Monitoring
### 12. Natural Language Understanding

---

## 🧮 Category 1: Deterministic Math Engine

### Test 1.1: Rate Problem with Scaling
**Question:**
```
A pharmaceutical factory has 8 machines that can package 8,000 tablets
in 8 hours. The factory needs to package 50,000 tablets in 10 hours.
How many machines are required?
```

**Expected Behavior:**
- ✅ Should use MathReasoner
- ✅ Should show algebraic solving steps
- ✅ Should calculate: rate per machine, scaling, verification
- ✅ Final answer: 5 machines
- ✅ Confidence: High (0.99)
- ✅ Source: local_calculated

---

### Test 1.2: Complex Percentage with Multiple Operations
**Question:**
```
A stock portfolio worth $15,000 increases by 18% in Q1, then decreases
by 12% in Q2, and finally increases by 25% in Q3. What is the final
portfolio value and what is the total percentage change from the start?
```

**Expected Behavior:**
- ✅ Should calculate step-by-step
- ✅ Should show each quarter's calculation
- ✅ Should compute overall percentage change
- ✅ Final answer: $19,305 and +28.7% total
- ✅ Should verify calculation

---

### Test 1.3: Logic Puzzle with State Tracking
**Question:**
```
I have a bag with 100 marbles. I give away half to Anna, then I receive
20 more from Bob, then I lose 15 marbles, and finally I give 30% of what
remains to Carlos. How many marbles do I have left?
```

**Expected Behavior:**
- ✅ Should track state through each step
- ✅ Should show running total
- ✅ Final answer: 38.5 marbles (or 38 if rounding to whole)
- ✅ Should verify each operation

---

## 🕒 Category 2: Temporal Awareness & Time-Sensitive Queries

### Test 2.1: Current Event Detection
**Question:**
```
What are the current top 3 technological innovations being developed
in renewable energy as of November 2025?
```

**Expected Behavior:**
- ✅ Should detect temporal keywords: "current", "as of November 2025"
- ✅ Should recognize query is beyond knowledge cutoff (Dec 2023)
- ✅ Should display: [Time Context] Current system date/time: 2025-11-06...
- ✅ Should trigger WebSearch or Perplexity
- ✅ Should show: [Step 1/3] Trying Genesis WebSearch...
- ✅ Source: websearch or perplexity
- ✅ Should provide 2025 information with citations

---

### Test 2.2: "Right Now" Query
**Question:**
```
What is the current Bitcoin price right now and what caused the most
recent significant price movement?
```

**Expected Behavior:**
- ✅ Should detect "current" and "right now"
- ✅ Should mark as time_sensitive: True
- ✅ Should trigger live data sources immediately
- ✅ Should NOT use local LLM knowledge
- ✅ Should provide current price with source citation
- ✅ Source: websearch or perplexity

---

### Test 2.3: Recent Discovery Query
**Question:**
```
What is the most recently approved Alzheimer's drug by the FDA and
what makes its mechanism of action unique?
```

**Expected Behavior:**
- ✅ Should detect "most recently" and "approved"
- ✅ Should recognize medical/regulatory information needs current data
- ✅ Should trigger external sources
- ✅ Should provide 2024-2025 FDA approval data
- ✅ Should cite sources (FDA, medical journals)

---

## 💻 Category 3: Code Generation & Execution

### Test 3.1: Algorithm Implementation
**Question:**
```
Write a Python function that implements the Sieve of Eratosthenes
algorithm to find all prime numbers up to n. Include optimizations
and test it with n=100.
```

**Expected Behavior:**
- ✅ Should classify as code_generation
- ✅ Should generate pseudocode first
- ✅ Should write complete, runnable Python code
- ✅ Should include optimizations (skip evens, sqrt limit)
- ✅ Should test and show output for n=100
- ✅ Should execute code safely in sandbox
- ✅ Problem type: programming

---

### Test 3.2: Data Structure with Edge Cases
**Question:**
```
Create a Python class for a circular buffer with fixed size that
supports enqueue, dequeue, peek, and is_full operations. Handle
all edge cases and demonstrate with examples.
```

**Expected Behavior:**
- ✅ Should generate class structure
- ✅ Should handle wrap-around logic
- ✅ Should include edge case handling (empty, full, single element)
- ✅ Should provide usage examples
- ✅ Should execute and show output

---

### Test 3.3: Code Analysis and Debugging
**Question:**
```
Here's a Python function with a bug. Find the bug and explain why it fails:

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-1)

What's wrong and how would you fix it?
```

**Expected Behavior:**
- ✅ Should identify the bug (duplicate recursion call)
- ✅ Should explain why it's incorrect
- ✅ Should provide corrected version
- ✅ Should explain performance implications
- ✅ Should optionally suggest memoization

---

## 📁 Category 4: File Operations

### Test 4.1: File Read and Analysis
**Question:**
```
Read the file setup_genesis.sh and tell me what the main installation
steps are and how long the entire process would take.
```

**Expected Behavior:**
- ✅ Should use read_file() from tools
- ✅ Should parse and analyze contents
- ✅ Should identify key steps
- ✅ Should estimate time based on operations
- ✅ Should provide structured summary

---

### Test 4.2: File Search with Pattern
**Question:**
```
Find all Python files in the current directory that contain the word
"reasoning" and list their names with line numbers where it appears.
```

**Expected Behavior:**
- ✅ Should use find_files() or grep_files()
- ✅ Should search with pattern matching
- ✅ Should return file:line format
- ✅ Should handle case sensitivity appropriately

---

### Test 4.3: File Creation with Content
**Question:**
```
Create a new file called test_config.json with the following structure:
{
  "model": "CodeLlama-7B",
  "temperature": 0.7,
  "max_tokens": 2048,
  "features": ["reasoning", "memory", "feedback"]
}
```

**Expected Behavior:**
- ✅ Should use write_file()
- ✅ Should create valid JSON
- ✅ Should confirm creation with file size
- ✅ Should handle path creation if needed

---

## 🧠 Category 5: Multi-Step Reasoning

### Test 5.1: Complex Problem with Multiple Constraints
**Question:**
```
You have a 3-liter jug and a 5-liter jug. How can you measure exactly
4 liters of water? Explain your reasoning step by step.
```

**Expected Behavior:**
- ✅ Should detect problem type: logic puzzle
- ✅ Should generate reasoning trace with steps
- ✅ Should show state at each step
- ✅ Should provide clear solution path
- ✅ Should verify solution works

---

### Test 5.2: Comparative Analysis
**Question:**
```
Compare and contrast functional programming and object-oriented
programming. Which paradigm would be better for building a real-time
trading system and why?
```

**Expected Behavior:**
- ✅ Should use multi-step reasoning
- ✅ Should analyze both paradigms
- ✅ Should consider domain requirements (real-time, trading)
- ✅ Should provide reasoned recommendation
- ✅ Should cite tradeoffs

---

### Test 5.3: Causal Chain Analysis
**Question:**
```
If global temperatures rise by 3°C over the next 50 years, explain
the cascade of effects on: ocean currents → marine ecosystems →
fishing industries → food security. Use scientific reasoning.
```

**Expected Behavior:**
- ✅ Should generate reasoning chain
- ✅ Should connect each causal link
- ✅ Should show step-by-step progression
- ✅ Should cite domain knowledge or external sources
- ✅ May trigger external research for current data

---

## 💾 Category 6: Context & Memory Persistence

### Test 6.1: Session Memory Recall
**Question (Part 1):**
```
I'm currently working on a machine learning project that predicts
customer churn using logistic regression. The dataset has 10,000
samples with 15 features.
```

**Question (Part 2, same session):**
```
For my project, should I use cross-validation or a simple train-test
split, and why?
```

**Expected Behavior:**
- ✅ Part 1: Should acknowledge and store in session memory
- ✅ Part 2: Should reference "your project" from context
- ✅ Should use dataset details (10k samples, 15 features) in answer
- ✅ Should not ask for context that was already provided

---

### Test 6.2: Long-Term Memory Retrieval (Requires Restart)
**Question (Session 1):**
```
My preferred coding style is to use functional programming with
immutable data structures whenever possible.
```

**[Restart Genesis]**

**Question (Session 2):**
```
I'm about to start a new Python project. What coding style should I use?
```

**Expected Behavior:**
- ✅ Session 1: Should store as important (user preference)
- ✅ Session 2: Should load from long-term memory
- ✅ Should recall functional programming preference
- ✅ Should reference previous conversation
- ✅ #context command should show this in long-term memory

---

### Test 6.3: Context Window Management
**Question:**
```
Have 20+ back-and-forth exchanges on various topics, then ask:
"What was the first thing we discussed today?"
```

**Expected Behavior:**
- ✅ Should maintain session memory of recent interactions
- ✅ Should be able to recall early conversation
- ✅ Should not lose context despite many exchanges
- ✅ Should use session memory (20 item limit)

---

## 🎓 Category 7: Adaptive Learning & Feedback

### Test 7.1: Positive Refinement
**Question:**
```
What is the time complexity of quicksort?
```

**Follow-up:**
```
#correct - excellent explanation with best/worst case analysis
```

**Expected Behavior:**
- ✅ Should store feedback with note
- ✅ Should display: 📝 Positive refinement: ...
- ✅ Should update source confidence weights
- ✅ Should create learning event
- ✅ #feedback should show this in statistics

---

### Test 7.2: Error Correction with Note
**Question:**
```
Who won the 2024 Nobel Prize in Physics?
```

**Follow-up:**
```
#incorrect - this information is from 2024, should have checked live sources
```

**Expected Behavior:**
- ✅ Should recognize incorrect response
- ✅ Should store correction note
- ✅ Should display: 📌 Correction note: ...
- ✅ Should reduce confidence for source used
- ✅ Should suggest "try again"
- ✅ Should flag for temporal awareness improvement

---

### Test 7.3: Adaptive Source Selection
**Question (After 10+ feedbacks on WebSearch):**
```
What are the latest developments in quantum computing hardware?
```

**Expected Behavior:**
- ✅ Should use learned weights from feedback
- ✅ If WebSearch has high success rate, should prefer it
- ✅ Should show confidence based on learned weights
- ✅ #feedback should show updated confidence scores
- ✅ Should demonstrate learning from past feedback

---

## 🎨 Category 8: Tone Detection & Control

### Test 8.1: Automatic Technical Tone Detection
**Question:**
```
Explain the difference between async/await and promises in JavaScript,
including the event loop mechanics and microtask queue behavior.
```

**Expected Behavior:**
- ✅ Should detect technical tone from keywords
- ✅ Should show: 🔧 [Tone: Technical | Length: Standard]
- ✅ Should use precise terminology
- ✅ Should include code examples
- ✅ Should explain low-level details

---

### Test 8.2: Automatic Conversational Tone Detection
**Question:**
```
Can you tell me in simple terms what blockchain is? I've heard about
it but don't really understand the concept.
```

**Expected Behavior:**
- ✅ Should detect conversational tone ("simple terms", "tell me")
- ✅ Should show: 💬 [Tone: Conversational | Length: Standard]
- ✅ Should use analogies and examples
- ✅ Should avoid heavy jargon
- ✅ Should be friendly and accessible

---

### Test 8.3: Manual Tone Override
**Question:**
```
#tone concise
#verbosity short

Explain neural networks.
```

**Expected Behavior:**
- ✅ Should use concise tone (brief, to-the-point)
- ✅ Should use short verbosity (3-5 lines)
- ✅ Should show: ⚡ [Tone: Concise | Length: Brief]
- ✅ Should provide key points only
- ✅ Should respect user preference

---

### Test 8.4: Advisory Tone for Instructions
**Question:**
```
How do I set up a PostgreSQL database on Ubuntu and configure it for
production use?
```

**Expected Behavior:**
- ✅ Should detect advisory tone ("how do I")
- ✅ Should show: 📖 [Tone: Advisory | Length: Standard]
- ✅ Should provide step-by-step instructions
- ✅ Should include best practices
- ✅ Should be guidance-oriented

---

## 🌐 Category 9: External Research

### Test 9.1: WebSearch for Current Data
**Question:**
```
What are the current mortgage interest rates in the United States
and how have they changed over the past month?
```

**Expected Behavior:**
- ✅ Should detect time-sensitive query
- ✅ Should trigger WebSearch first
- ✅ Should show: [Step 1/3] Trying Genesis WebSearch...
- ✅ Should query multiple sources (DuckDuckGo, Wikipedia, etc.)
- ✅ Should provide current rates with citations
- ✅ Source: websearch

---

### Test 9.2: Perplexity for Synthesis
**Question:**
```
Synthesize the current scientific consensus on the effectiveness of
intermittent fasting for longevity, including recent 2024-2025 studies.
```

**Expected Behavior:**
- ✅ Should recognize need for synthesis + current data
- ✅ May try WebSearch first, then Perplexity if low confidence
- ✅ Should provide synthesized analysis
- ✅ Should cite recent studies
- ✅ Source: perplexity or websearch

---

### Test 9.3: Direct Source Control - WebSearch
**Question:**
```
search web: latest AI model releases November 2025
```

**Expected Behavior:**
- ✅ Should detect direct source command
- ✅ Should bypass normal fallback logic
- ✅ Should show: [Step 1/1] Using WebSearch (user-directed)...
- ✅ Should force WebSearch regardless of confidence
- ✅ Source: websearch (forced)

---

### Test 9.4: Direct Source Control - Claude
**Question:**
```
ask claude: write me a complete REST API in Python using FastAPI
with authentication, CRUD operations, and database integration.
```

**Expected Behavior:**
- ✅ Should detect "ask claude:" prefix
- ✅ Should route directly to Claude
- ✅ Should show: [Step 1/1] Using Claude (user-directed)...
- ✅ Should receive comprehensive code from Claude
- ✅ Source: claude (forced)

---

## ♻️ Category 10: Retry & Error Recovery

### Test 10.1: Natural Retry Command
**Question (First):**
```
What is 25% of 480?
```

**Feedback:**
```
#incorrect - didn't show the calculation steps
```

**Retry:**
```
try again
```

**Expected Behavior:**
- ✅ First response: Should answer
- ✅ After feedback: Should store error
- ✅ After "try again": Should retry with improvements
- ✅ Should show calculation steps in retry
- ✅ Should reference feedback note

---

### Test 10.2: Clarification Request
**Question:**
```
Explain polymorphism.
```

**Follow-up:**
```
Can you explain that more simply?
```

**Expected Behavior:**
- ✅ First response: Should explain polymorphism
- ✅ Second response: Should detect request for simplification
- ✅ Should provide simpler explanation with analogies
- ✅ Should reference previous answer

---

### Test 10.3: Error Handling with Retry
**Question:**
```
Read the file /nonexistent/path/file.txt
```

**Expected Behavior:**
- ✅ Should attempt file read
- ✅ Should catch error gracefully
- ✅ Should display: ⚠ File not found: /nonexistent/path/file.txt
- ✅ Should not crash
- ✅ Should record error in performance metrics

---

## 📊 Category 11: Performance Monitoring

### Test 11.1: View Performance Metrics
**Question:**
```
#performance
```

**Expected Behavior:**
- ✅ Should display full performance dashboard
- ✅ Should show: Total Queries, Response Sources, Speed, Feedback
- ✅ Should include fallback statistics
- ✅ Should show average response time
- ✅ Should show success rates

---

### Test 11.2: View Feedback Summary
**Question:**
```
#feedback
```

**Expected Behavior:**
- ✅ Should display feedback & learning summary
- ✅ Should show session statistics (correct/incorrect)
- ✅ Should show learning events count
- ✅ Should show adaptive source confidence with success rates
- ✅ Should show per-source performance (WebSearch, Perplexity, etc.)

---

### Test 11.3: View Context Summary
**Question:**
```
#context
```

**Expected Behavior:**
- ✅ Should display context & memory summary
- ✅ Should show session memory stats (items, queries, last topic)
- ✅ Should show long-term memory stats (total stored, date range)
- ✅ Should show user preferences
- ✅ Should include session ID

---

## 🗣️ Category 12: Natural Language Understanding

### Test 12.1: Ambiguity Resolution
**Question:**
```
The bank is steep and the bank is closed. What am I talking about?
```

**Expected Behavior:**
- ✅ Should recognize word ambiguity
- ✅ Should explain both meanings of "bank"
- ✅ Should demonstrate context awareness
- ✅ Should provide clear distinction

---

### Test 12.2: Metaphor and Analogy Understanding
**Question:**
```
"Don't put all your eggs in one basket" - explain this phrase and give
me a modern technology example of what happens when people ignore this advice.
```

**Expected Behavior:**
- ✅ Should understand metaphor
- ✅ Should explain meaning (diversification)
- ✅ Should provide relevant tech example
- ✅ Should connect abstract to concrete

---

### Test 12.3: Multi-Part Question
**Question:**
```
What is machine learning, how does it differ from traditional programming,
what are its main types, and which type would be best for predicting
housing prices?
```

**Expected Behavior:**
- ✅ Should parse 4 distinct questions
- ✅ Should answer each part systematically
- ✅ Should maintain coherence across parts
- ✅ Should provide recommendation with reasoning

---

## 🎯 Testing Instructions

### How to Run This Test Suite

1. **Preparation:**
   ```bash
   cd ~/Genesis
   git pull origin main
   python3 genesis.py
   ```

2. **Execute Tests Category by Category:**
   - Copy each question into Genesis
   - Observe behavior and responses
   - Verify against expected behavior
   - Mark ✅ or ❌ for each test

3. **Record Results:**
   - Create a file: `test-results-YYYYMMDD.md`
   - For each test, note:
     - Question asked
     - Response received
     - Expected behavior matched? ✅/❌
     - Source used
     - Confidence score
     - Any issues or unexpected behavior

4. **Special Tests Requiring Restart:**
   - Test 6.2 (Long-term memory)
   - Save session, restart Genesis, then ask follow-up

5. **Tests Requiring Feedback:**
   - Tests 7.1, 7.2, 7.3
   - Provide feedback after initial response
   - Check #feedback summary

---

## 📈 Success Criteria

**For Genesis to pass this comprehensive test:**

✅ **Math (Category 1):** 100% accuracy, shows steps, verification
✅ **Temporal (Category 2):** Detects time-sensitive, triggers live sources
✅ **Code (Category 3):** Generates correct, runnable code
✅ **Files (Category 4):** Performs operations correctly
✅ **Reasoning (Category 5):** Shows logical steps, arrives at correct answer
✅ **Context (Category 6):** Recalls from session and long-term memory
✅ **Feedback (Category 7):** Stores notes, updates weights, learns
✅ **Tone (Category 8):** Detects correctly, adjusts response style
✅ **External (Category 9):** Uses appropriate sources, cites data
✅ **Retry (Category 10):** Handles errors, improves on retry
✅ **Performance (Category 11):** Shows accurate metrics
✅ **NLU (Category 12):** Understands context, ambiguity, metaphors

**Target:** 95%+ tests passing across all categories

---

## 📝 Notes

- These questions are **completely novel** - Genesis has never seen them before
- They test **real-world use cases** not synthetic examples
- They cover **all documented capabilities** in README
- They require **integration of multiple systems** (temporal + learning + tone)
- They verify **end-to-end functionality** not just individual components

---

**Generated:** November 6, 2025
**Version:** Genesis v1.8
**Total Tests:** 39 comprehensive tests
**Coverage:** 100% of documented features
**Status:** Ready for execution ✅
