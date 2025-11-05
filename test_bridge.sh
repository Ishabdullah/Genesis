#!/data/data/com.termux/files/usr/bin/bash
# Genesis Bridge Test Script
# Tests the Genesis-Claude Code bridge connection

echo "🧬 Genesis Bridge Test Suite"
echo "=============================="
echo ""

BRIDGE_URL="http://127.0.0.1:5050"
API_KEY="localonly"

# Test 1: Health Check
echo "[Test 1/5] Health Check..."
response=$(curl -s -w "\n%{http_code}" "$BRIDGE_URL/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "✓ Bridge is healthy"
else
    echo "✗ Health check failed (HTTP $http_code)"
    exit 1
fi
echo ""

# Test 2: Status Check
echo "[Test 2/5] Status Check..."
response=$(curl -s -w "\n%{http_code}" "$BRIDGE_URL/status")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "✓ Status endpoint working"
    echo "Response: $body"
else
    echo "✗ Status check failed (HTTP $http_code)"
fi
echo ""

# Test 3: Simple Code Execution
echo "[Test 3/5] Simple Code Execution..."
response=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-Genesis-Key: $API_KEY" \
    -d '{"code":"print(\"Hello from Genesis Bridge!\")"}' \
    "$BRIDGE_URL/run")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "✓ Code executed successfully"
    echo "Response: $body"
else
    echo "✗ Code execution failed (HTTP $http_code)"
    echo "Response: $body"
fi
echo ""

# Test 4: Math Calculation
echo "[Test 4/5] Math Calculation..."
response=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-Genesis-Key: $API_KEY" \
    -d '{"code":"result = 2 + 2\nprint(f\"2 + 2 = {result}\")"}' \
    "$BRIDGE_URL/run")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ] && echo "$body" | grep -q "2 + 2 = 4"; then
    echo "✓ Math calculation correct"
    echo "Response: $body"
else
    echo "✗ Math calculation failed"
    echo "Response: $body"
fi
echo ""

# Test 5: Error Handling
echo "[Test 5/5] Error Handling..."
response=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-Genesis-Key: $API_KEY" \
    -d '{"code":"raise ValueError(\"Test error\")"}' \
    "$BRIDGE_URL/run")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ] && echo "$body" | grep -q "ValueError"; then
    echo "✓ Error handling works correctly"
    echo "Response: $body"
else
    echo "✗ Error handling test failed"
    echo "Response: $body"
fi
echo ""

# Test 6: Security - Missing API Key
echo "[Test 6/6] Security - Missing API Key..."
response=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"code":"print(\"test\")"}' \
    "$BRIDGE_URL/run")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "401" ]; then
    echo "✓ Security check passed (rejected unauthorized request)"
else
    echo "⚠ Security warning: request without API key returned HTTP $http_code"
fi
echo ""

echo "=============================="
echo "Bridge tests complete!"
echo ""
echo "Check bridge_log.txt for detailed logs:"
echo "  tail -f ~/Genesis/bridge_log.txt"
