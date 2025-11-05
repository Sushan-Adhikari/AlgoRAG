#!/bin/bash
# Diagnose Ollama API issues

echo "==================================="
echo "Ollama API Diagnostic Script"
echo "==================================="

OLLAMA_URL="http://localhost:11434"

# Test 1: Check if server is running
echo -e "\n1. Testing server connectivity..."
if curl -s "${OLLAMA_URL}/api/tags" > /dev/null 2>&1; then
    echo "✓ Server is reachable"
else
    echo "✗ Cannot connect to server"
    exit 1
fi

# Test 2: Check version
echo -e "\n2. Checking Ollama version..."
curl -s "${OLLAMA_URL}/api/version" 2>&1 | head -20

# Test 3: List available models
echo -e "\n3. Listing available models..."
curl -s "${OLLAMA_URL}/api/tags" 2>&1 | head -20

# Test 4: Try /api/generate with minimal payload
echo -e "\n4. Testing /api/generate endpoint..."
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${OLLAMA_URL}/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "prompt": "Say hello",
    "stream": false
  }' 2>&1)

http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d':' -f2)
body=$(echo "$response" | grep -v "HTTP_CODE:")

echo "HTTP Status: $http_code"
if [ "$http_code" = "200" ]; then
    echo "✓ /api/generate works!"
    echo "Response: $body" | head -10
else
    echo "✗ /api/generate failed"
    echo "Response: $body" | head -10
fi

# Test 5: Try /api/chat
echo -e "\n5. Testing /api/chat endpoint..."
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${OLLAMA_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Say hello"}],
    "stream": false
  }' 2>&1)

http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d':' -f2)
body=$(echo "$response" | grep -v "HTTP_CODE:")

echo "HTTP Status: $http_code"
if [ "$http_code" = "200" ]; then
    echo "✓ /api/chat works!"
    echo "Response: $body" | head -10
else
    echo "✗ /api/chat failed"
    echo "Response: $body" | head -10
fi

# Test 6: Check if model is loaded
echo -e "\n6. Checking running models..."
curl -s "${OLLAMA_URL}/api/ps" 2>&1 | head -20

echo -e "\n==================================="
echo "Diagnostic complete"
echo "==================================="
