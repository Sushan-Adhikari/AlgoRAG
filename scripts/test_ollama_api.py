#!/usr/bin/env python3
"""Test script to find the correct Ollama API endpoint."""

import requests
import json

OLLAMA_URL = "http://localhost:11434"

def test_endpoint(endpoint, payload):
    """Test an endpoint with given payload."""
    url = f"{OLLAMA_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print('='*60)

    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("✓ SUCCESS!")
            print(f"Response: {json.dumps(response.json(), indent=2)[:500]}")
            return True
        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Test various Ollama API endpoints."""

    # First, check if server is running
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        print(f"✓ Ollama server is running (version check: {response.status_code})")
        print(f"Available models: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"✗ Cannot connect to Ollama server: {e}")
        return

    # Test payloads
    model = "llama3.1:8b"

    # Test 1: /api/generate (old API style)
    test_endpoint("/api/generate", {
        "model": model,
        "prompt": "What is 2+2?",
        "stream": False
    })

    # Test 2: /api/chat (chat API style)
    test_endpoint("/api/chat", {
        "model": model,
        "messages": [
            {"role": "user", "content": "What is 2+2?"}
        ],
        "stream": False
    })

    # Test 3: /generate (without /api prefix)
    test_endpoint("/generate", {
        "model": model,
        "prompt": "What is 2+2?",
        "stream": False
    })

    # Test 4: /chat (without /api prefix)
    test_endpoint("/chat", {
        "model": model,
        "messages": [
            {"role": "user", "content": "What is 2+2?"}
        ],
        "stream": False
    })

    # Test 5: /v1/completions (OpenAI-compatible)
    test_endpoint("/v1/completions", {
        "model": model,
        "prompt": "What is 2+2?",
        "max_tokens": 50
    })

    # Test 6: /v1/chat/completions (OpenAI-compatible chat)
    test_endpoint("/v1/chat/completions", {
        "model": model,
        "messages": [
            {"role": "user", "content": "What is 2+2?"}
        ],
        "max_tokens": 50
    })

if __name__ == "__main__":
    main()
