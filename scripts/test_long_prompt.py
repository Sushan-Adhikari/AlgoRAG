#!/usr/bin/env python3
"""Test Ollama with actual RAG prompt length (~4500 chars)."""

import subprocess
import os
import sys
import time

def test_long_prompt():
    """Test with a prompt similar to actual RAG evaluation."""

    # Simulate a RAG-style prompt with context from retrieved documents
    system_instruction = """You are an expert in theoretical computer science and algorithm analysis.
Your role is to provide clear, pedagogically sound explanations of algorithms,
data structures, complexity analysis, and computational theory.

When answering:
1. Be precise and use proper mathematical notation
2. Provide step-by-step reasoning
3. Reference relevant theorems or techniques
4. Keep explanations concise but complete"""

    context = """
Retrieved Context Documents:

1. Big-O Notation Definition:
Big-O notation describes an upper bound on the growth rate of a function.
We say f(n) = O(g(n)) if there exist positive constants c and n₀ such that
0 ≤ f(n) ≤ c·g(n) for all n ≥ n₀.

This means f(n) grows no faster than g(n), up to a constant factor.

2. Proving Big-O:
To prove f(n) = O(g(n)), we need to:
- Find constants c > 0 and n₀ > 0
- Show that f(n) ≤ c·g(n) for all n ≥ n₀

Example: Prove 3n + 5 = O(n)
- For n ≥ 5, we have 3n + 5 ≤ 3n + n = 4n
- So with c = 4 and n₀ = 5, we have 3n + 5 ≤ 4n for all n ≥ 5
- Therefore 3n + 5 = O(n)

3. Common Growth Rates:
O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(n³) < O(2ⁿ) < O(n!)

4. Properties of Big-O:
- Transitivity: If f = O(g) and g = O(h), then f = O(h)
- Sum rule: If f₁ = O(g) and f₂ = O(g), then f₁ + f₂ = O(g)
- Product rule: If f = O(g) and h = O(k), then f·h = O(g·k)
- Constant factors: If f = O(g), then c·f = O(g) for any constant c > 0

5. Linear Functions:
Any function of the form f(n) = an + b where a, b are constants is O(n).
This is because for sufficiently large n, the linear term an dominates.
"""

    question = "\n\nQuestion: Prove that f(n) = 9n + 7 = O(n) using the formal definition."

    full_prompt = f"{system_instruction}\n\n{context}{question}"

    print("=" * 70)
    print("Testing Ollama with Long Prompt (Actual RAG Length)")
    print("=" * 70)
    print(f"\nPrompt length: {len(full_prompt)} chars")
    print("Expected time: 15-60 seconds (depending on hardware)")
    print("\nRunning...\n")

    # Set environment to avoid warnings
    env = os.environ.copy()
    env["TOKENIZERS_PARALLELISM"] = "false"

    start = time.time()

    try:
        process = subprocess.Popen(
            ["ollama", "run", "llama3.1:8b"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )

        # Add progress indicator
        print("Waiting for response", end="", flush=True)

        # Communicate with timeout
        try:
            stdout, stderr = process.communicate(input=full_prompt, timeout=180)
        except subprocess.TimeoutExpired:
            print("\n\n✗ TIMEOUT after 180 seconds!")
            process.kill()
            stdout, stderr = process.communicate()
            print("\nThis suggests:")
            print("1. Your hardware may be too slow for llama3.1:8b")
            print("2. Ollama might be hanging on this specific prompt")
            print("3. Try a smaller model: ollama pull llama3.2:3b")
            return False

        elapsed = time.time() - start
        print(f"\n\nCompleted in {elapsed:.1f} seconds")

        if process.returncode != 0:
            print(f"\n✗ FAILED with return code {process.returncode}")
            print(f"stderr: {stderr}")
            return False

        response = stdout.strip()

        if not response:
            print("\n✗ FAILED: Empty response")
            return False

        print(f"\n✓ SUCCESS!")
        print(f"Response length: {len(response)} chars")
        print(f"\nFirst 300 chars of response:")
        print("-" * 70)
        print(response[:300] + "...")
        print("-" * 70)

        # Timing guidance
        if elapsed < 30:
            print(f"\n✅ Great! Your hardware is fast enough for research evaluation.")
            print(f"Expected time for 179 questions: ~{int(179 * elapsed / 60)} minutes")
        elif elapsed < 60:
            print(f"\n✅ Good. Evaluation will be slower but manageable.")
            print(f"Expected time for 179 questions: ~{int(179 * elapsed / 60)} minutes")
        else:
            print(f"\n⚠️  Slow. Consider using a smaller model or cloud API.")
            print(f"Expected time for 179 questions: ~{int(179 * elapsed / 60)} minutes")

        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

def main():
    """Run the test."""
    print("\n🧪 Long Prompt Test (RAG Evaluation Simulation)\n")

    success = test_long_prompt()

    if success:
        print("\n" + "=" * 70)
        print("✅ Test passed! Ready for full evaluation")
        print("=" * 70)
        print("\nRun the evaluation:")
        print("  python3 scripts/run_research_evaluation.py \\")
        print("    --test-file evaluation/test_datasets/exam_questions/evaluation_dataset.json \\")
        print("    --llm-backend ollama \\")
        print("    --results-dir results")
    else:
        print("\n" + "=" * 70)
        print("❌ Test failed!")
        print("=" * 70)
        print("\nTroubleshooting:")
        print("1. Try a smaller model:")
        print("   ollama pull llama3.2:3b")
        print("   (Then update .env: OLLAMA_MODEL=llama3.2:3b)")
        print("\n2. Or use a cloud API (Gemini has free tier)")
        print("   GENERATOR_BACKEND=gemini")
        print("   GEMINI_API_KEY=your_key")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
