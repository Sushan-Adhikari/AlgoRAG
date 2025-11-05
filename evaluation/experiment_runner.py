"""
Experiment Runner for AlgoRAG Research

Handles:
- Batch experiment execution
- A/B testing framework
- Result collection and aggregation
- Reproducibility tracking
- Performance benchmarking
"""

import json
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.rag.embeddings import EmbeddingClient
from backend.rag.retriever import Retriever
from backend.rag.generator import Generator
from backend.rag.preprocessing import MathPreprocessor
from .metrics import EvaluationMetrics


@dataclass
class Experiment:
    """Configuration for a single experiment."""
    experiment_id: str
    name: str
    description: str
    embed_backend: str  # 'local', 'gemini', 'openai'
    generator_model: str
    top_k: int = 5
    use_reranking: bool = True
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class ExperimentRunner:
    """
    Orchestrates batch experiments for research evaluation.

    Features:
    - Reproducible experiment execution
    - A/B testing between configurations
    - Comprehensive logging
    - Result export in multiple formats
    """

    def __init__(
        self,
        output_dir: str = './experiment_results',
        verbose: bool = True
    ):
        """
        Initialize experiment runner.

        Args:
            output_dir: Directory to save results
            verbose: Print progress messages
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose

        self.evaluator = EvaluationMetrics()
        self.results_history = []

    def run_experiment(
        self,
        experiment: Experiment,
        test_cases: List[Dict[str, Any]],
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Run a single experiment on a set of test cases.

        Args:
            experiment: Experiment configuration
            test_cases: List of test cases with 'query' and 'reference_answer'
            save_results: Whether to save results to disk

        Returns:
            Dictionary with experiment results
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Running Experiment: {experiment.name}")
            print(f"{'='*60}")
            print(f"Description: {experiment.description}")
            print(f"Embedding Backend: {experiment.embed_backend}")
            print(f"Generator Model: {experiment.generator_model}")
            print(f"Test Cases: {len(test_cases)}")
            print(f"Top-K Retrieval: {experiment.top_k}")
            print(f"Use Reranking: {experiment.use_reranking}")
            print(f"{'='*60}\n")

        # Initialize RAG components with experiment config
        try:
            # Set environment variables for this experiment
            os.environ['EMBED_BACKEND'] = experiment.embed_backend
            os.environ['GENERATOR_MODEL'] = experiment.generator_model

            # Import config to get correct paths
            from backend import config

            emb_client = EmbeddingClient(backend=experiment.embed_backend)
            retriever = Retriever(
                embedding_client=emb_client,
                db_type=config.VECTOR_DB_TYPE,
                db_path=str(config.VECTOR_DB_DIR),
                collection_name=config.COLLECTION_NAME
            )
            generator = Generator(model_name=experiment.generator_model)
            preprocessor = MathPreprocessor()

            if self.verbose:
                print("RAG components initialized successfully.\n")

        except Exception as e:
            if self.verbose:
                print(f"ERROR: Failed to initialize RAG components: {e}")
            return {'error': str(e), 'experiment': asdict(experiment)}

        # Run test cases
        results = []
        start_time = time.time()

        for idx, case in enumerate(test_cases, 1):
            if self.verbose:
                print(f"[{idx}/{len(test_cases)}] Processing: {case['query'][:60]}...")

            try:
                case_result = self._run_single_case(
                    case=case,
                    retriever=retriever,
                    generator=generator,
                    preprocessor=preprocessor,
                    top_k=experiment.top_k,
                    use_reranking=experiment.use_reranking
                )
                results.append(case_result)

                if self.verbose:
                    print(f"    ✓ Quality Score: {case_result['overall_quality']:.3f}")

            except Exception as e:
                if self.verbose:
                    print(f"    ✗ ERROR: {e}")
                results.append({
                    'query': case['query'],
                    'error': str(e),
                    'overall_quality': 0.0
                })

        elapsed_time = time.time() - start_time

        # Aggregate results
        experiment_results = self._aggregate_results(
            experiment=experiment,
            results=results,
            elapsed_time=elapsed_time
        )

        # Save results
        if save_results:
            self._save_results(experiment_results)

        self.results_history.append(experiment_results)

        if self.verbose:
            self._print_summary(experiment_results)

        return experiment_results

    def _run_single_case(
        self,
        case: Dict[str, Any],
        retriever: Retriever,
        generator: Generator,
        preprocessor: MathPreprocessor,
        top_k: int,
        use_reranking: bool
    ) -> Dict[str, Any]:
        """Run RAG pipeline on a single test case and evaluate."""
        query = case['query']
        reference_answer = case.get('reference_answer', '')
        metadata = case.get('metadata', {})

        # Preprocess query to get query type and topics
        query_type = preprocessor.detect_query_type(query)
        query_topics = preprocessor.extract_topics(query)
        preprocessed = {'query_type': query_type, 'topics': list(query_topics)}

        # Retrieve documents
        case_start = time.time()
        retrieved_docs = retriever.retrieve(
            query=query,
            query_type=preprocessed.get('query_type', 'general'),
            top_k=top_k,
            query_metadata=preprocessed
        )
        retrieval_time = time.time() - case_start

        # Generate answer
        gen_start = time.time()
        result = generator.generate(query, retrieved_docs, preprocessed.get('query_type', 'general'))
        generated_answer = result['answer']
        generation_time = time.time() - gen_start

        # Evaluate
        evaluation = self.evaluator.evaluate_answer(
            query=query,
            reference_answer=reference_answer,
            generated_answer=generated_answer,
            retrieved_docs=retrieved_docs,
            metadata=metadata
        )

        # Add timing information
        evaluation['timing'] = {
            'retrieval_ms': round(retrieval_time * 1000, 2),
            'generation_ms': round(generation_time * 1000, 2),
            'total_ms': round((retrieval_time + generation_time) * 1000, 2)
        }

        evaluation['generated_answer'] = generated_answer
        evaluation['retrieved_docs_count'] = len(retrieved_docs)

        return evaluation

    def _aggregate_results(
        self,
        experiment: Experiment,
        results: List[Dict[str, Any]],
        elapsed_time: float
    ) -> Dict[str, Any]:
        """Aggregate individual results into experiment summary."""
        successful_results = [r for r in results if 'error' not in r]
        failed_count = len(results) - len(successful_results)

        if not successful_results:
            return {
                'experiment': asdict(experiment),
                'summary': {'total': len(results), 'failed': failed_count},
                'error': 'All test cases failed'
            }

        # Calculate aggregate metrics
        aggregate = {
            'total_cases': len(results),
            'successful_cases': len(successful_results),
            'failed_cases': failed_count,
            'total_time_seconds': round(elapsed_time, 2),
            'avg_time_per_case_ms': round((elapsed_time / len(results)) * 1000, 2),

            # Quality metrics
            'mean_overall_quality': self._safe_mean([r['overall_quality'] for r in successful_results]),
            'mean_bleu': self._safe_mean([r['bleu']['BLEU'] for r in successful_results]),
            'mean_rouge_f1': self._safe_mean([r['rouge']['ROUGE-L-F1'] for r in successful_results]),
            'mean_pedagogical_score': self._safe_mean([r['pedagogical_quality']['overall_pedagogical_score'] for r in successful_results]),

            # Timing
            'mean_retrieval_ms': self._safe_mean([r['timing']['retrieval_ms'] for r in successful_results]),
            'mean_generation_ms': self._safe_mean([r['timing']['generation_ms'] for r in successful_results]),

            # Topic breakdown
            'by_topic': self._breakdown_by_topic(successful_results),
            'by_query_type': self._breakdown_by_query_type(successful_results),
        }

        # Proof-specific metrics
        proof_results = [r for r in successful_results if 'proof_completeness' in r]
        if proof_results:
            aggregate['mean_proof_completeness'] = self._safe_mean([r['proof_completeness']['completeness_score'] for r in proof_results])

        return {
            'experiment': asdict(experiment),
            'aggregate': aggregate,
            'individual_results': results
        }

    def _safe_mean(self, values: List[float]) -> float:
        """Compute mean, handling empty lists."""
        if not values:
            return 0.0
        return round(sum(values) / len(values), 4)

    def _breakdown_by_topic(self, results: List[Dict]) -> Dict[str, Dict]:
        """Break down results by topic."""
        by_topic = {}
        for result in results:
            topic = result.get('metadata', {}).get('topic', 'unknown')
            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(result['overall_quality'])

        return {
            topic: {
                'count': len(scores),
                'mean_quality': self._safe_mean(scores)
            }
            for topic, scores in by_topic.items()
        }

    def _breakdown_by_query_type(self, results: List[Dict]) -> Dict[str, Dict]:
        """Break down results by query type."""
        by_type = {}
        for result in results:
            qtype = result.get('metadata', {}).get('query_type', 'unknown')
            if qtype not in by_type:
                by_type[qtype] = []
            by_type[qtype].append(result['overall_quality'])

        return {
            qtype: {
                'count': len(scores),
                'mean_quality': self._safe_mean(scores)
            }
            for qtype, scores in by_type.items()
        }

    def _save_results(self, experiment_results: Dict[str, Any]):
        """Save experiment results to disk."""
        exp_id = experiment_results['experiment']['experiment_id']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{exp_id}_{timestamp}.json"

        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(experiment_results, f, indent=2)

        if self.verbose:
            print(f"\nResults saved to: {filepath}")

    def _print_summary(self, experiment_results: Dict[str, Any]):
        """Print experiment summary."""
        # Handle case where all tests failed
        if 'aggregate' not in experiment_results:
            print(f"\n{'='*60}")
            print("EXPERIMENT FAILED")
            print(f"{'='*60}")
            if 'error' in experiment_results:
                print(f"Error: {experiment_results['error']}")
            if 'summary' in experiment_results:
                summary = experiment_results['summary']
                print(f"Total Cases: {summary['total']}")
                print(f"Failed: {summary['failed']}")
            print(f"{'='*60}\n")
            return

        agg = experiment_results['aggregate']

        print(f"\n{'='*60}")
        print("EXPERIMENT SUMMARY")
        print(f"{'='*60}")
        print(f"Total Cases:       {agg['total_cases']}")
        print(f"Successful:        {agg['successful_cases']}")
        print(f"Failed:            {agg['failed_cases']}")
        print(f"Total Time:        {agg['total_time_seconds']:.2f}s")
        print(f"Avg Time/Case:     {agg['avg_time_per_case_ms']:.2f}ms")
        print(f"\nQUALITY METRICS")
        print(f"{'='*60}")
        print(f"Overall Quality:   {agg['mean_overall_quality']:.4f}")
        print(f"BLEU Score:        {agg['mean_bleu']:.4f}")
        print(f"ROUGE-L F1:        {agg['mean_rouge_f1']:.4f}")
        print(f"Pedagogical Score: {agg['mean_pedagogical_score']:.4f}")

        if 'mean_proof_completeness' in agg:
            print(f"Proof Completeness: {agg['mean_proof_completeness']:.4f}")

        print(f"\nPERFORMANCE")
        print(f"{'='*60}")
        print(f"Retrieval Time:    {agg['mean_retrieval_ms']:.2f}ms")
        print(f"Generation Time:   {agg['mean_generation_ms']:.2f}ms")
        print(f"{'='*60}\n")

    # ==================== A/B Testing ====================

    def run_ab_test(
        self,
        experiment_a: Experiment,
        experiment_b: Experiment,
        test_cases: List[Dict[str, Any]],
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Run A/B test comparing two experiment configurations.

        Args:
            experiment_a: First configuration
            experiment_b: Second configuration
            test_cases: Shared test cases
            save_results: Whether to save comparison results

        Returns:
            Comparison results dictionary
        """
        if self.verbose:
            print("\n" + "="*60)
            print("A/B TEST COMPARISON")
            print("="*60)
            print(f"Experiment A: {experiment_a.name}")
            print(f"Experiment B: {experiment_b.name}")
            print(f"Test Cases: {len(test_cases)}")
            print("="*60 + "\n")

        # Run both experiments
        results_a = self.run_experiment(experiment_a, test_cases, save_results=False)
        results_b = self.run_experiment(experiment_b, test_cases, save_results=False)

        # Compare results
        comparison = self._compare_experiments(results_a, results_b)

        # Save comparison
        if save_results:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ab_test_{experiment_a.experiment_id}_vs_{experiment_b.experiment_id}_{timestamp}.json"
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                json.dump(comparison, f, indent=2)

            if self.verbose:
                print(f"\nComparison saved to: {filepath}")

        if self.verbose:
            self._print_ab_summary(comparison)

        return comparison

    def _compare_experiments(
        self,
        results_a: Dict[str, Any],
        results_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare two experiment results."""
        agg_a = results_a['aggregate']
        agg_b = results_b['aggregate']

        comparison = {
            'experiment_a': results_a['experiment'],
            'experiment_b': results_b['experiment'],
            'comparison': {
                'overall_quality_diff': round(agg_a['mean_overall_quality'] - agg_b['mean_overall_quality'], 4),
                'bleu_diff': round(agg_a['mean_bleu'] - agg_b['mean_bleu'], 4),
                'rouge_diff': round(agg_a['mean_rouge_f1'] - agg_b['mean_rouge_f1'], 4),
                'pedagogical_diff': round(agg_a['mean_pedagogical_score'] - agg_b['mean_pedagogical_score'], 4),
                'speed_diff_ms': round(agg_a['avg_time_per_case_ms'] - agg_b['avg_time_per_case_ms'], 2),
            },
            'winner': self._determine_winner(agg_a, agg_b),
            'aggregate_a': agg_a,
            'aggregate_b': agg_b
        }

        return comparison

    def _determine_winner(self, agg_a: Dict, agg_b: Dict) -> str:
        """Determine winner based on overall quality."""
        qual_a = agg_a['mean_overall_quality']
        qual_b = agg_b['mean_overall_quality']

        if qual_a > qual_b + 0.01:  # Threshold for significance
            return 'Experiment A'
        elif qual_b > qual_a + 0.01:
            return 'Experiment B'
        else:
            return 'Tie (no significant difference)'

    def _print_ab_summary(self, comparison: Dict[str, Any]):
        """Print A/B test summary."""
        comp = comparison['comparison']

        print(f"\n{'='*60}")
        print("A/B TEST RESULTS")
        print(f"{'='*60}")
        print(f"Winner: {comparison['winner']}")
        print(f"\nDifferences (A - B):")
        print(f"Overall Quality:   {comp['overall_quality_diff']:+.4f}")
        print(f"BLEU Score:        {comp['bleu_diff']:+.4f}")
        print(f"ROUGE-L F1:        {comp['rouge_diff']:+.4f}")
        print(f"Pedagogical Score: {comp['pedagogical_diff']:+.4f}")
        print(f"Speed:             {comp['speed_diff_ms']:+.2f}ms (negative = A faster)")
        print(f"{'='*60}\n")

    # ==================== Utility Methods ====================

    def load_test_cases(self, filepath: str) -> List[Dict[str, Any]]:
        """Load test cases from JSON file."""
        with open(filepath, 'r') as f:
            return json.load(f)

    def export_results_csv(self, experiment_id: str, output_file: str):
        """Export experiment results to CSV."""
        import csv

        # Find experiment in history
        exp_results = None
        for result in self.results_history:
            if result['experiment']['experiment_id'] == experiment_id:
                exp_results = result
                break

        if not exp_results:
            print(f"Experiment {experiment_id} not found in history.")
            return

        # Extract individual results
        individual = exp_results['individual_results']

        with open(output_file, 'w', newline='') as f:
            fieldnames = [
                'query', 'overall_quality', 'bleu', 'rouge_f1',
                'pedagogical_score', 'retrieval_ms', 'generation_ms'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in individual:
                if 'error' in result:
                    continue

                writer.writerow({
                    'query': result['query'],
                    'overall_quality': result['overall_quality'],
                    'bleu': result['bleu']['BLEU'],
                    'rouge_f1': result['rouge']['ROUGE-L-F1'],
                    'pedagogical_score': result['pedagogical_quality']['overall_pedagogical_score'],
                    'retrieval_ms': result['timing']['retrieval_ms'],
                    'generation_ms': result['timing']['generation_ms']
                })

        print(f"Results exported to: {output_file}")


# ==================== Example Usage ====================

if __name__ == '__main__':
    # Create sample test cases
    test_cases = [
        {
            'query': 'Prove that 3n^2 + 5n = O(n^2)',
            'reference_answer': 'To prove f(n) = O(n^2), choose c=10 and n0=1. Then 3n^2 + 5n <= 10n^2 for all n >= 1.',
            'metadata': {'query_type': 'proof', 'topic': 'asymptotic_analysis'}
        },
        {
            'query': 'What is the time complexity of binary search?',
            'reference_answer': 'Binary search has O(log n) time complexity because it halves the search space in each iteration.',
            'metadata': {'query_type': 'complexity', 'topic': 'algorithms'}
        }
    ]

    # Define experiments
    exp_local = Experiment(
        experiment_id='exp_local_001',
        name='Local Embeddings',
        description='Using local sentence-transformers',
        embed_backend='local',
        generator_model='gemini-2.0-flash-exp'
    )

    # Run experiment
    runner = ExperimentRunner(output_dir='./experiment_results')
    results = runner.run_experiment(exp_local, test_cases)

    print("\nExperiment completed successfully!")
