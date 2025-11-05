#!/usr/bin/env python3
"""
Research evaluation script for AlgoRAG paper.
Runs comprehensive experiments and generates results for publication.
"""

import sys
import os
from pathlib import Path
import json
import time
from datetime import datetime
from typing import Dict, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import logging
from rag.embeddings import EmbeddingClient
from rag.retriever import Retriever
from rag.generator import AnswerGenerator
from rag.preprocessing import MathPreprocessor

# Import evaluation metrics
sys.path.insert(0, str(Path(__file__).parent.parent / "evaluation"))
from metrics import (
    compute_bleu_score,
    compute_rouge_scores,
    compute_bertscore,
    compute_pedagogical_quality
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResearchEvaluationRunner:
    """
    Runs comprehensive research evaluation for AlgoRAG paper.
    """

    def __init__(
        self,
        vector_db_path: Path,
        results_dir: Path,
        embedding_backend: str = "local",
        llm_backend: str = "gemini",
        db_type: str = "chroma"
    ):
        """
        Initialize evaluation runner.

        Args:
            vector_db_path: Path to vector database
            results_dir: Directory to save results
            embedding_backend: Embedding backend
            llm_backend: LLM backend for answer generation
            db_type: Vector database type
        """
        self.vector_db_path = vector_db_path
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        logger.info("Initializing AlgoRAG components...")
        self.emb_client = EmbeddingClient(backend=embedding_backend)
        self.retriever = Retriever(
            embedding_client=self.emb_client,
            db_type=db_type,
            db_path=str(vector_db_path)
        )
        self.generator = AnswerGenerator(backend=llm_backend)
        self.preprocessor = MathPreprocessor()

        logger.info("✓ Components initialized")

    def load_test_dataset(self, test_file: Path) -> List[Dict]:
        """
        Load test dataset.

        Args:
            test_file: Path to test dataset JSON file

        Returns:
            List of test cases
        """
        logger.info(f"Loading test dataset: {test_file}")

        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle both list and dict formats
        if isinstance(data, dict) and "test_cases" in data:
            test_cases = data["test_cases"]
        elif isinstance(data, list):
            test_cases = data
        else:
            raise ValueError("Invalid test dataset format")

        logger.info(f"✓ Loaded {len(test_cases)} test cases")
        return test_cases

    def run_single_evaluation(self, test_case: Dict) -> Dict:
        """
        Run evaluation on a single test case.

        Args:
            test_case: Test case dictionary

        Returns:
            Evaluation results
        """
        # Handle both formats: "question" or "query"
        question = test_case.get("question") or test_case.get("query", "")

        # Handle both formats: "expected_answer" or "reference_answer"
        expected_answer = test_case.get("expected_answer") or test_case.get("reference_answer", "")

        # Get topic from either root level or metadata
        metadata = test_case.get("metadata", {})
        topic = test_case.get("topic") or metadata.get("topic", "unknown")

        # Get query_type from either root level or metadata
        query_type = test_case.get("query_type") or metadata.get("query_type", "general")

        logger.info(f"\nEvaluating: {question[:100]}...")

        start_time = time.time()

        # Retrieve relevant documents
        retrieved_docs = self.retriever.retrieve(question, top_k=5)

        # Generate answer
        answer = self.generator.generate_answer(
            query=question,
            retrieved_docs=retrieved_docs,
            query_type=query_type
        )

        elapsed_time = time.time() - start_time

        # Compute metrics
        metrics = {}

        if expected_answer:
            # BLEU score
            metrics["bleu"] = compute_bleu_score(answer, expected_answer)

            # ROUGE scores
            rouge_scores = compute_rouge_scores(answer, expected_answer)
            metrics.update(rouge_scores)

            # BERTScore (if available)
            try:
                bertscore = compute_bertscore([answer], [expected_answer])
                metrics["bertscore_f1"] = bertscore["f1"][0]
            except Exception as e:
                logger.warning(f"BERTScore computation failed: {e}")
                metrics["bertscore_f1"] = None

        # Pedagogical quality
        ped_quality = compute_pedagogical_quality(
            question=question,
            answer=answer,
            retrieved_docs=retrieved_docs
        )
        metrics.update(ped_quality)

        # Retrieval metrics
        metrics["num_retrieved"] = len(retrieved_docs)
        metrics["avg_similarity"] = sum(
            d.get("similarity_score", 0) for d in retrieved_docs
        ) / len(retrieved_docs) if retrieved_docs else 0
        metrics["avg_pedagogical_score"] = sum(
            d.get("pedagogical_score", 0) for d in retrieved_docs
        ) / len(retrieved_docs) if retrieved_docs else 0

        # Response time
        metrics["response_time_seconds"] = elapsed_time

        result = {
            "question": question,
            "expected_answer": expected_answer,
            "generated_answer": answer,
            "topic": topic,
            "query_type": query_type,
            "difficulty": metadata.get("difficulty", "unknown"),
            "retrieved_docs": [
                {
                    "content": doc["content"][:200],
                    "similarity_score": doc.get("similarity_score"),
                    "pedagogical_score": doc.get("pedagogical_score")
                }
                for doc in retrieved_docs
            ],
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }

        return result

    def run_full_evaluation(self, test_file: Path) -> Dict:
        """
        Run full evaluation on test dataset.

        Args:
            test_file: Path to test dataset

        Returns:
            Aggregated evaluation results
        """
        logger.info("="*80)
        logger.info("RUNNING FULL RESEARCH EVALUATION")
        logger.info("="*80)

        # Load test cases
        test_cases = self.load_test_dataset(test_file)

        # Run evaluation on each test case
        results = []
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n[{i}/{len(test_cases)}] Processing test case...")

            try:
                result = self.run_single_evaluation(test_case)
                results.append(result)
                logger.info(f"✓ Completed in {result['metrics']['response_time_seconds']:.2f}s")

            except Exception as e:
                logger.error(f"✗ Failed: {e}")
                results.append({
                    "question": test_case["question"],
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })

        # Aggregate metrics
        aggregated = self._aggregate_results(results)

        # Save results
        self._save_results(results, aggregated)

        # Print summary
        self._print_summary(aggregated)

        return aggregated

    def _aggregate_results(self, results: List[Dict]) -> Dict:
        """
        Aggregate results across all test cases.

        Args:
            results: List of individual results

        Returns:
            Aggregated metrics
        """
        logger.info("\nAggregating results...")

        # Filter successful results
        successful = [r for r in results if "error" not in r]

        if not successful:
            logger.error("No successful evaluations!")
            return {"error": "No successful evaluations"}

        # Aggregate by topic
        by_topic = {}
        for result in successful:
            topic = result.get("topic", "unknown")
            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(result)

        # Compute averages
        def avg_metric(results_list, metric_name):
            values = [
                r["metrics"].get(metric_name)
                for r in results_list
                if r["metrics"].get(metric_name) is not None
            ]
            return sum(values) / len(values) if values else None

        aggregated = {
            "total_test_cases": len(results),
            "successful": len(successful),
            "failed": len(results) - len(successful),
            "overall_metrics": {
                "bleu": avg_metric(successful, "bleu"),
                "rouge1_f": avg_metric(successful, "rouge1_f"),
                "rouge2_f": avg_metric(successful, "rouge2_f"),
                "rougeL_f": avg_metric(successful, "rougeL_f"),
                "bertscore_f1": avg_metric(successful, "bertscore_f1"),
                "has_step_by_step": avg_metric(successful, "has_step_by_step"),
                "has_mathematical_notation": avg_metric(successful, "has_mathematical_notation"),
                "has_examples": avg_metric(successful, "has_examples"),
                "avg_similarity": avg_metric(successful, "avg_similarity"),
                "avg_pedagogical_score": avg_metric(successful, "avg_pedagogical_score"),
                "avg_response_time": avg_metric(successful, "response_time_seconds"),
            },
            "by_topic": {}
        }

        # Aggregate by topic
        for topic, topic_results in by_topic.items():
            aggregated["by_topic"][topic] = {
                "count": len(topic_results),
                "bleu": avg_metric(topic_results, "bleu"),
                "rouge1_f": avg_metric(topic_results, "rouge1_f"),
                "rougeL_f": avg_metric(topic_results, "rougeL_f"),
                "avg_similarity": avg_metric(topic_results, "avg_similarity"),
                "avg_response_time": avg_metric(topic_results, "response_time_seconds"),
            }

        return aggregated

    def _save_results(self, results: List[Dict], aggregated: Dict):
        """
        Save results to files.

        Args:
            results: Individual results
            aggregated: Aggregated results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results
        detailed_file = self.results_dir / f"detailed_results_{timestamp}.json"
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Saved detailed results: {detailed_file}")

        # Save aggregated results
        aggregated_file = self.results_dir / f"aggregated_results_{timestamp}.json"
        with open(aggregated_file, 'w', encoding='utf-8') as f:
            json.dump(aggregated, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Saved aggregated results: {aggregated_file}")

        # Save summary for paper
        summary_file = self.results_dir / f"paper_summary_{timestamp}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("AlgoRAG Research Evaluation Results\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total test cases: {aggregated['total_test_cases']}\n")
            f.write(f"Successful: {aggregated['successful']}\n")
            f.write(f"Failed: {aggregated['failed']}\n\n")

            f.write("Overall Metrics:\n")
            f.write("-"*80 + "\n")
            for metric, value in aggregated['overall_metrics'].items():
                if value is not None:
                    f.write(f"{metric}: {value:.4f}\n")

            f.write("\n\nBy Topic:\n")
            f.write("-"*80 + "\n")
            for topic, metrics in aggregated['by_topic'].items():
                f.write(f"\n{topic} ({metrics['count']} cases):\n")
                for metric, value in metrics.items():
                    if metric != 'count' and value is not None:
                        f.write(f"  {metric}: {value:.4f}\n")

        logger.info(f"✓ Saved paper summary: {summary_file}")

    def _print_summary(self, aggregated: Dict):
        """
        Print summary of results.

        Args:
            aggregated: Aggregated results
        """
        logger.info("\n" + "="*80)
        logger.info("EVALUATION SUMMARY")
        logger.info("="*80)

        logger.info(f"\nTotal test cases: {aggregated['total_test_cases']}")
        logger.info(f"Successful: {aggregated['successful']}")
        logger.info(f"Failed: {aggregated['failed']}")

        logger.info("\nOverall Metrics:")
        logger.info("-"*80)
        for metric, value in aggregated['overall_metrics'].items():
            if value is not None:
                logger.info(f"{metric:30s}: {value:.4f}")

        logger.info("\n✓ Evaluation complete!")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run research evaluation for AlgoRAG"
    )
    parser.add_argument(
        "--test-file",
        type=Path,
        required=True,
        help="Path to test dataset JSON file"
    )
    parser.add_argument(
        "--vector-db",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "vector_db",
        help="Path to vector database"
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path(__file__).parent.parent / "results",
        help="Directory to save results"
    )
    parser.add_argument(
        "--embedding-backend",
        choices=["local", "gemini", "openai"],
        default="local",
        help="Embedding backend"
    )
    parser.add_argument(
        "--llm-backend",
        choices=["gemini", "openai", "ollama"],
        default="gemini",
        help="LLM backend"
    )
    parser.add_argument(
        "--db-type",
        choices=["chroma", "qdrant"],
        default="chroma",
        help="Vector database type"
    )

    args = parser.parse_args()

    # Validate
    if not args.test_file.exists():
        logger.error(f"Test file not found: {args.test_file}")
        sys.exit(1)

    if not args.vector_db.exists():
        logger.error(f"Vector database not found: {args.vector_db}")
        logger.error("Please run ingestion first!")
        sys.exit(1)

    # Run evaluation
    try:
        runner = ResearchEvaluationRunner(
            vector_db_path=args.vector_db,
            results_dir=args.results_dir,
            embedding_backend=args.embedding_backend,
            llm_backend=args.llm_backend,
            db_type=args.db_type
        )

        aggregated = runner.run_full_evaluation(args.test_file)

        logger.info(f"\n✓ SUCCESS: Evaluation complete!")
        logger.info(f"Results saved to: {args.results_dir}")

    except Exception as e:
        logger.error(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
