"""
Test harness for AlgoRAG system.
Tests the complete pipeline: ingest -> retrieve -> generate
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from rag.embeddings import EmbeddingClient
from rag.retriever import Retriever
from rag.generator import Generator
from rag.ingest import DocumentIngester
import config


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "="*70)
    print(title)
    print("="*70 + "\n")


def test_embeddings():
    """Test embedding generation."""
    print_section("TEST 1: Embedding Generation")

    client = EmbeddingClient(backend=config.EMBED_BACKEND)

    test_texts = [
        "What is the time complexity of quicksort?",
        "Prove that the halting problem is undecidable.",
    ]

    print(f"Backend: {client.backend}")
    print(f"Dimension: {client.dimension}")
    print(f"\nGenerating embeddings for {len(test_texts)} texts...")

    embeddings = client.embed_batch(test_texts)

    print(f"✓ Generated {len(embeddings)} embeddings")
    print(f"  Shape: {len(embeddings[0])} dimensions")

    return client


def test_ingestion(emb_client):
    """Test document ingestion."""
    print_section("TEST 2: Document Ingestion")

    retriever = Retriever(
        embedding_client=emb_client,
        db_type=config.VECTOR_DB_TYPE,
        db_path=str(config.VECTOR_DB_DIR)
    )

    ingester = DocumentIngester(retriever)

    # Create sample documents
    sample_docs = [
        {
            "content": """
            QuickSort Algorithm

            QuickSort is a divide-and-conquer sorting algorithm that works by selecting
            a 'pivot' element and partitioning the array around it.

            Time Complexity:
            - Best case: O(n log n) - when pivot divides array evenly
            - Average case: O(n log n) - random pivot selection
            - Worst case: O(n²) - when pivot is always min/max element

            Space Complexity: O(log n) for recursion stack

            Proof of Average Case Complexity:
            Let T(n) be the average time for n elements.
            T(n) = T(k) + T(n-k-1) + Θ(n)
            where k is the random position of the pivot.

            Averaging over all possible k:
            T(n) = (1/n)Σ[T(k) + T(n-k-1)] + Θ(n)
                 = (2/n)Σ T(k) + Θ(n)

            By the master theorem: T(n) = Θ(n log n)

            Implementation Tips:
            - Use median-of-three for pivot selection
            - Switch to insertion sort for small subarrays (n < 10)
            - Can be optimized to O(log n) space with tail recursion
            """,
            "metadata": {
                "topic": "sorting_algorithms",
                "difficulty_level": "conceptual",
                "source_textbook": "CLRS Chapter 7",
                "has_proof": True,
                "has_complexity_analysis": True,
            }
        },
        {
            "content": """
            Master Theorem for Divide-and-Conquer Recurrences

            For recurrences of the form: T(n) = aT(n/b) + f(n)
            where a ≥ 1, b > 1, and f(n) is asymptotically positive.

            Let c_crit = log_b(a)

            Case 1: f(n) = O(n^c) where c < c_crit
                    Then T(n) = Θ(n^c_crit)

            Case 2: f(n) = Θ(n^c_crit · log^k(n)) where k ≥ 0
                    Then T(n) = Θ(n^c_crit · log^(k+1)(n))

            Case 3: f(n) = Ω(n^c) where c > c_crit
                    AND af(n/b) ≤ κf(n) for some κ < 1 and large n
                    Then T(n) = Θ(f(n))

            Examples:

            1. T(n) = 2T(n/2) + n
               a=2, b=2, f(n)=n
               c_crit = log_2(2) = 1
               f(n) = n^1 → Case 2 with k=0
               T(n) = Θ(n log n)  ← QuickSort, MergeSort

            2. T(n) = 9T(n/3) + n
               a=9, b=3, f(n)=n
               c_crit = log_3(9) = 2
               f(n) = O(n^2) → Case 1
               T(n) = Θ(n²)

            3. T(n) = 3T(n/4) + n log n
               a=3, b=4, f(n)=n log n
               c_crit = log_4(3) ≈ 0.79
               f(n) = Ω(n^0.79) → Case 3
               T(n) = Θ(n log n)
            """,
            "metadata": {
                "topic": "recurrence_relations",
                "difficulty_level": "application",
                "source_textbook": "CLRS Chapter 4",
                "has_proof": False,
                "has_complexity_analysis": True,
            }
        },
        {
            "content": """
            Proof Technique: Mathematical Induction

            Mathematical induction is used to prove statements about natural numbers.

            Structure:
            1. Base Case: Prove P(n₀) is true
            2. Inductive Hypothesis: Assume P(k) is true for some k ≥ n₀
            3. Inductive Step: Prove P(k+1) is true using the hypothesis
            4. Conclusion: By induction, P(n) is true for all n ≥ n₀

            Example: Prove Σᵢ₌₁ⁿ i = n(n+1)/2

            Base case: n=1
            LHS = 1, RHS = 1(2)/2 = 1 ✓

            Inductive hypothesis: Assume Σᵢ₌₁ᵏ i = k(k+1)/2

            Inductive step: Prove for k+1
            Σᵢ₌₁ᵏ⁺¹ i = (Σᵢ₌₁ᵏ i) + (k+1)
                       = k(k+1)/2 + (k+1)        [by IH]
                       = [k(k+1) + 2(k+1)]/2
                       = [(k+1)(k+2)]/2
                       = (k+1)((k+1)+1)/2 ✓

            By induction, the formula holds for all n ≥ 1. QED

            Common Mistakes:
            - Forgetting the base case
            - Not using the inductive hypothesis in the step
            - Assuming what you're trying to prove (circular reasoning)
            """,
            "metadata": {
                "topic": "proof_techniques",
                "difficulty_level": "foundation",
                "source_textbook": "Rosen Discrete Math",
                "has_proof": True,
                "has_complexity_analysis": False,
            }
        }
    ]

    print(f"Ingesting {len(sample_docs)} sample documents...")

    chunks = ingester._chunk_documents(sample_docs)
    num_ingested = ingester._ingest_documents(chunks)

    print(f"✓ Ingested {num_ingested} chunks")
    print(f"  Total documents in DB: {retriever.collection.count()}")

    return retriever


def test_retrieval(retriever):
    """Test document retrieval and re-ranking."""
    print_section("TEST 3: Retrieval & Pedagogical Re-ranking")

    test_queries = [
        {
            "query": "What is the time complexity of quicksort in the average case?",
            "type": "complexity_analysis"
        },
        {
            "query": "Prove the sum formula using induction",
            "type": "proof"
        },
        {
            "query": "How do I solve recurrence relations?",
            "type": "algorithm"
        }
    ]

    for i, test in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {test['query']}")
        print(f"Type: {test['type']}")
        print("-" * 70)

        results = retriever.retrieve(
            query=test['query'],
            query_type=test['type'],
            top_k=3
        )

        print(f"Retrieved {len(results)} documents:\n")

        for j, doc in enumerate(results, 1):
            print(f"{j}. Similarity: {doc['similarity_score']:.3f}, "
                  f"Pedagogical: {doc['pedagogical_score']:.3f}")
            print(f"   Topic: {doc.get('metadata', {}).get('topic', 'N/A')}")
            print(f"   Level: {doc.get('metadata', {}).get('difficulty_level', 'N/A')}")
            print(f"   Content: {doc['content'][:100]}...")
            print()


def test_generation(retriever):
    """Test answer generation."""
    print_section("TEST 4: Answer Generation")

    generator = Generator(
        model_name=config.GENERATOR_MODEL,
        temperature=config.GENERATOR_TEMPERATURE
    )

    # Test with proof query
    query = "Prove that QuickSort has O(n log n) average case time complexity."

    print(f"Query: {query}\n")
    print("Retrieving relevant documents...")

    results = retriever.retrieve(
        query=query,
        query_type="proof",
        top_k=3
    )

    print(f"✓ Retrieved {len(results)} documents")
    print("\nGenerating answer...")

    response = generator.generate(
        query=query,
        retrieved_docs=results,
        query_type="proof"
    )

    print("\n" + "-"*70)
    print("GENERATED ANSWER:")
    print("-"*70)
    print(response["answer"])
    print("-"*70)
    print(f"\nSources used: {response['num_sources']}")


def test_complete_pipeline():
    """Test the complete RAG pipeline."""
    print_section("AlgoRAG Complete Pipeline Test")

    print("Configuration:")
    print(f"  Embedding Backend: {config.EMBED_BACKEND}")
    print(f"  Vector DB: {config.VECTOR_DB_TYPE}")
    print(f"  Generator Model: {config.GENERATOR_MODEL}")

    try:
        # Test 1: Embeddings
        emb_client = test_embeddings()

        # Test 2: Ingestion
        retriever = test_ingestion(emb_client)

        # Test 3: Retrieval
        test_retrieval(retriever)

        # Test 4: Generation (only if API keys available)
        if config.GEMINI_API_KEY or config.OPENAI_API_KEY:
            test_generation(retriever)
        else:
            print("\n⊘ Skipping generation test (no API keys)")

        print_section("✓ ALL TESTS PASSED")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_complete_pipeline()
