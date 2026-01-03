#!/usr/bin/env python3
"""Quick test to verify Ollama is working properly."""

import subprocess
import sys
import time

def test_ollama_simple():
    """Test simple Ollama command."""
    print("=" * 60)
    print("Testing Ollama with simple prompt")
    print("=" * 60)

    prompt = "What is 2+2? Answer in one sentence."

    print(f"\nPrompt: {prompt}")
    print(f"Model: llama3.1:8b")
    print("\nRunning... (should take 5-15 seconds)\n")

    start = time.time()

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.1:8b"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=30
        )

        elapsed = time.time() - start

        if result.returncode != 0:
            print(f"✗ FAILED with return code {result.returncode}")
            print(f"stderr: {result.stderr}")
            return False

        response = result.stdout.strip()
        print(f"✓ SUCCESS in {elapsed:.1f}s")
        print(f"\nResponse: {response}\n")
        return True

    except subprocess.TimeoutExpired:
        print("✗ TIMEOUT after 30 seconds")
        print("\nThis suggests Ollama is hanging or very slow.")
        print("Try running this manually:")
        print('  echo "What is 2+2?" | ollama run llama3.1:8b')
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def test_ollama_with_context():
    """Test Ollama with longer prompt (similar to RAG context)."""
    print("\n" + "=" * 60)
    print("Testing Ollama with longer prompt (RAG-like)")
    print("=" * 60)

    context = """
    Context from retrieved documents:

    Binary search is an efficient algorithm for finding a target value within a sorted array.
    It works by repeatedly dividing the search interval in half.

    Time Complexity: O(log n)
    Space Complexity: O(1)

    The algorithm compares the target value to the middle element. If they are equal,
    the position is returned. If the target is less than the middle element, the search
    continues in the lower half. Otherwise, it continues in the upper half.
    """

    prompt = f"{context}\n\nQuestion: What is the time complexity of binary search? Answer briefly."

    print(f"\nPrompt length: {len(prompt)} chars")
    print("Running... (should take 5-20 seconds)\n")

    start = time.time()

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.1:8b"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60
        )

        elapsed = time.time() - start

        if result.returncode != 0:
            print(f"✗ FAILED with return code {result.returncode}")
            print(f"stderr: {result.stderr}")
            return False

        response = result.stdout.strip()
        print(f"✓ SUCCESS in {elapsed:.1f}s")
        print(f"\nResponse: {response[:200]}...\n")
        return True

    except subprocess.TimeoutExpired:
        print("✗ TIMEOUT after 60 seconds")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    """Run tests."""
    print("\n🧪 Ollama Quick Test\n")

    # Check if ollama is in PATH
    try:
        result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
        if result.returncode != 0:
            print("✗ ERROR: 'ollama' command not found")
            print("Make sure Ollama is installed and in your PATH")
            sys.exit(1)
        print(f"✓ Ollama found: {result.stdout.strip()}\n")
    except Exception as e:
        print(f"✗ ERROR checking for ollama: {e}")
        sys.exit(1)

    # Test 1: Simple prompt
    success1 = test_ollama_simple()

    if not success1:
        print("\n❌ Basic test failed. Fix this before running full evaluation.")
        sys.exit(1)

    # Test 2: Longer prompt
    success2 = test_ollama_with_context()

    if not success2:
        print("\n⚠️  Long prompt test failed. Full evaluation may be slow or fail.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ All tests passed! Ollama is working correctly.")
    print("=" * 60)
    print("\nYou can now run the full evaluation:")
    print("  python scripts/run_research_evaluation.py \\")
    print("    --test-file evaluation/test_datasets/exam_questions/evaluation_dataset.json \\")
    print("    --llm-backend ollama \\")
    print("    --results-dir results")
    print()

if __name__ == "__main__":
    main()
