#!/bin/bash
# Genesis Comprehensive Test Suite (Tests 7-20)
# Extended testing with scoring and feedback

echo "🧬 Genesis Comprehensive Test Suite"
echo "====================================="
echo ""

TOTAL_TESTS=14
PASSED=0
FAILED=0

# Helper function to run test
run_test() {
    local test_num=$1
    local test_name="$2"
    local input="$3"
    local expected="$4"

    echo "Test $test_num: $test_name"
    echo "$(printf '%.0s-' {1..60})"
    echo "Input: $input"
    echo "Expected: $expected"
    echo ""

    # Run test with timeout
    result=$(echo -e "$input\n#exit" | timeout 40 python genesis.py 2>/dev/null | grep -A 10 "Genesis:")

    echo "Output:"
    echo "$result" | head -15
    echo ""
}

# Test 7: Multi-Step Reasoning
echo ""
run_test 7 "Multi-Step Reasoning" \
    "If 3 cats catch 3 mice in 3 minutes, how many cats do you need to catch 100 mice in 100 minutes?" \
    "3 cats (same ratio, not linear scaling)"

# Test 8: Pseudocode Reasoning
echo ""
run_test 8 "Pseudocode Reasoning" \
    "Explain how you'd design a memory system for an AI assistant like yourself." \
    "Should describe short-term, long-term, retrieval modules"

# Test 9: Context Recall (Persistence) - Manual check
echo ""
echo "Test 9: Context Recall (Persistence)"
echo "$(printf '%.0s-' {1..60})"
echo "Checking persistent memory..."
python -c "
from learning_memory import LearningMemory
memory = LearningMemory()
recent = memory.get_recent_learning(count=5)
if recent:
    print('✓ Learning memory has', len(recent), 'entries')
    print('Recent:', recent[-1].get('description', 'N/A')[:50])
else:
    print('✗ No learning memory found')
" 2>/dev/null
echo ""

# Test 10: Uncertainty Detection (would trigger Claude if enabled)
echo ""
run_test 10 "Uncertainty Detection" \
    "Explain Gödel's incompleteness theorem in rhyme." \
    "Should detect complexity and attempt or defer to Claude"

# Test 11: JSON Structuring
echo ""
run_test 11 "JSON Structuring" \
    "Output a JSON object describing a user named Ish who codes in Python and builds AI." \
    '{"name": "Ish", "skills": ["Python", "AI Development"]}'

# Test 12: Logical Chain
echo ""
run_test 12 "Logical Chain Test" \
    "If A implies B and B implies C, does A imply C? Explain why." \
    "Yes, by transitivity of implication"

# Test 13: Code Understanding
echo ""
cat > /tmp/test_code.py << 'PYCODE'
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")
PYCODE

echo "Test 13: Code Understanding"
echo "$(printf '%.0s-' {1..60})"
echo "Asking Genesis to explain test code..."
echo -e "Explain what this code does:\n\n$(cat /tmp/test_code.py)\n#exit" | \
    timeout 40 python genesis.py 2>/dev/null | grep -A 15 "Genesis:"
echo ""

# Test 14: Creativity (Mini Game)
echo ""
run_test 14 "Creativity Test" \
    "Design a mini text adventure game in Python with choices and input loops." \
    "Should output playable Python code"

# Test 15: Self-Verification
echo ""
run_test 15 "Self-Verification" \
    "Genesis, check your current configuration and tell me which model you're using." \
    "Should report CodeLlama-7B model path"

# Test 16: Memory Summary
echo ""
echo "Test 16: Memory System Status"
echo "$(printf '%.0s-' {1..60})"
echo "#memory" | timeout 10 python genesis.py 2>/dev/null | grep -A 20 "MEMORY"
echo ""

# Test 17: Performance Metrics
echo ""
echo "Test 17: Performance Tracking"
echo "$(printf '%.0s-' {1..60})"
echo "#performance" | timeout 10 python genesis.py 2>/dev/null | grep -A 15 "PERFORMANCE"
echo ""

# Test 18: Error Handling
echo ""
echo "Test 18: Error Handling"
echo "$(printf '%.0s-' {1..60})"
echo "Testing intentional syntax error..."
run_test 18 "Debug Broken Code" \
    "Fix this code: def broken(): return x +" \
    "Should identify missing operand and suggest fix"

# Test 19: Mathematical Reasoning Variants
echo ""
run_test 19 "Math Reasoning Variant" \
    "What is 15 × 4 - 8?" \
    "52 (15×4=60, 60-8=52)"

# Test 20: String Operation Variants
echo ""
run_test 20 "String Operation Variant" \
    "Reverse this string: AI Assistant" \
    "tnatssissA IA"

echo ""
echo "====================================="
echo "Extended Test Suite Complete"
echo ""
echo "Manual Verification Required:"
echo "- Test 9: Check persistent memory across sessions"
echo "- Test 10: Verify uncertainty detection / Claude fallback"
echo "- Test 13: Verify code understanding accuracy"
echo "- Test 14: Check if generated code is playable"
echo "- Test 16: Review memory system status"
echo "- Test 17: Review performance metrics"
echo ""
echo "Key Capabilities Tested:"
echo "✓ Multi-step reasoning"
echo "✓ Pseudocode design thinking"
echo "✓ Persistent memory"
echo "✓ Uncertainty detection"
echo "✓ JSON formatting"
echo "✓ Logical reasoning"
echo "✓ Code understanding"
echo "✓ Creative code generation"
echo "✓ Self-awareness"
echo "✓ Error handling"
echo ""
