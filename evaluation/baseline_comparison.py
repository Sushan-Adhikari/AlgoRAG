"""
Baseline RAG System for Comparison

Implements a standard RAG system WITHOUT:
- Mathematical entity preprocessing
- Pedagogical re-ranking
- Query-type awareness

This serves as the control group for A/B testing.
"""

import sys
import os
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.rag.embeddings import EmbeddingClient
from backend.rag.generator import Generator
from backend import config
import chromadb


class BaselineRAG:
    """
    Vanilla RAG system for baseline comparison.

    Features ONLY:
    - Basic embedding
    - Simple vector similarity retrieval
    - Standard generation (no query-type specialization)
    """

    def __init__(
        self,
        embed_backend: str = 'local',
        vector_db_path: str = None,
        collection_name: str = None
    ):
        """
        Initialize baseline RAG system.

        Args:
            embed_backend: Embedding backend ('local', 'gemini', 'openai')
            vector_db_path: Path to ChromaDB storage (defaults to config path)
            collection_name: Collection name (defaults to config name)
        """
        # Use config defaults if not provided
        if vector_db_path is None:
            vector_db_path = str(config.VECTOR_DB_DIR)
        if collection_name is None:
            collection_name = config.COLLECTION_NAME

        # Embedding client
        self.emb_client = EmbeddingClient(backend=embed_backend)

        # Vector database (simple ChromaDB without custom distance)
        self.chroma_client = chromadb.PersistentClient(path=vector_db_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # Generator (no special prompting)
        self.generator = Generator()

    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Basic retrieval using cosine similarity only.

        NO preprocessing, NO re-ranking.

        Args:
            query: User query
            top_k: Number of results

        Returns:
            List of retrieved documents
        """
        # Embed query (no preprocessing)
        query_embedding = self.emb_client.embed_text(query)

        # Simple retrieval
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )

        # Format results
        documents = []
        if results and results['ids']:
            for i in range(len(results['ids'][0])):
                doc = {
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'pedagogical_score': 0.0  # No pedagogical ranking
                }
                documents.append(doc)

        return documents

    def generate(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> str:
        """
        Generate answer using standard prompting.

        NO query-type specific instructions.

        Args:
            query: User query
            retrieved_docs: Retrieved context documents

        Returns:
            Generated answer
        """
        # Use generator but with generic query type (no proof/complexity specialization)
        result = self.generator.generate(
            query=query,
            retrieved_docs=retrieved_docs,
            query_type='general'
        )
        return result['answer']

    def query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Full RAG pipeline (baseline version).

        Args:
            query: User question
            top_k: Retrieval count

        Returns:
            Dictionary with answer and metadata
        """
        # Retrieve
        retrieved_docs = self.retrieve(query, top_k)

        # Generate
        answer = self.generate(query, retrieved_docs)

        return {
            'query': query,
            'answer': answer,
            'retrieved_docs': retrieved_docs,
            'retrieval_count': len(retrieved_docs)
        }


def compare_systems(
    algorag_system: Any,
    baseline_system: BaselineRAG,
    test_cases: List[Dict[str, Any]],
    evaluator: Any
) -> Dict[str, Any]:
    """
    Compare AlgoRAG vs Baseline on same test cases.

    Args:
        algorag_system: Full AlgoRAG system with preprocessing + reranking
        baseline_system: Baseline RAG system
        test_cases: Test questions with reference answers
        evaluator: EvaluationMetrics instance

    Returns:
        Comparison results
    """
    algorag_results = []
    baseline_results = []

    print("Running comparison: AlgoRAG vs Baseline\n")

    for i, case in enumerate(test_cases, 1):
        query = case['query']
        reference = case.get('reference_answer', '')
        metadata = case.get('metadata', {})

        print(f"[{i}/{len(test_cases)}] {query[:50]}...")

        # AlgoRAG
        try:
            # Assuming algorag_system has .query() method
            algo_response = algorag_system.query(
                query=query,
                query_type=metadata.get('query_type', 'general')
            )
            algo_answer = algo_response['answer']
            algo_docs = algo_response.get('retrieved_docs', [])

            algo_eval = evaluator.evaluate_answer(
                query=query,
                reference_answer=reference,
                generated_answer=algo_answer,
                retrieved_docs=algo_docs,
                metadata=metadata
            )
            algorag_results.append(algo_eval)

        except Exception as e:
            print(f"  AlgoRAG error: {e}")
            algorag_results.append({'error': str(e), 'overall_quality': 0.0})

        # Baseline
        try:
            base_response = baseline_system.query(query)
            base_answer = base_response['answer']
            base_docs = base_response['retrieved_docs']

            base_eval = evaluator.evaluate_answer(
                query=query,
                reference_answer=reference,
                generated_answer=base_answer,
                retrieved_docs=base_docs,
                metadata=metadata
            )
            baseline_results.append(base_eval)

        except Exception as e:
            print(f"  Baseline error: {e}")
            baseline_results.append({'error': str(e), 'overall_quality': 0.0})

    # Compute aggregate comparison
    import numpy as np

    def safe_mean(values):
        return round(np.mean([v for v in values if v > 0]), 4) if values else 0.0

    algo_qualities = [r.get('overall_quality', 0) for r in algorag_results]
    base_qualities = [r.get('overall_quality', 0) for r in baseline_results]

    algo_bleu = [r['bleu']['BLEU'] for r in algorag_results if 'bleu' in r]
    base_bleu = [r['bleu']['BLEU'] for r in baseline_results if 'bleu' in r]

    comparison = {
        'test_cases_count': len(test_cases),
        'algorag': {
            'mean_overall_quality': safe_mean(algo_qualities),
            'mean_bleu': safe_mean(algo_bleu),
            'results': algorag_results
        },
        'baseline': {
            'mean_overall_quality': safe_mean(base_qualities),
            'mean_bleu': safe_mean(base_bleu),
            'results': baseline_results
        },
        'improvement': {
            'overall_quality': safe_mean(algo_qualities) - safe_mean(base_qualities),
            'bleu': safe_mean(algo_bleu) - safe_mean(base_bleu)
        }
    }

    print(f"\n{'='*60}")
    print("COMPARISON RESULTS")
    print(f"{'='*60}")
    print(f"AlgoRAG Mean Quality:   {comparison['algorag']['mean_overall_quality']:.4f}")
    print(f"Baseline Mean Quality:  {comparison['baseline']['mean_overall_quality']:.4f}")
    print(f"Improvement:            {comparison['improvement']['overall_quality']:+.4f}")
    print(f"{'='*60}\n")

    return comparison


if __name__ == '__main__':
    # Test baseline system
    baseline = BaselineRAG(embed_backend='local')

    test_query = "What is the time complexity of binary search?"
    result = baseline.query(test_query)

    print(f"Query: {test_query}")
    print(f"Answer: {result['answer'][:200]}...")
    print(f"Retrieved: {result['retrieval_count']} documents")
