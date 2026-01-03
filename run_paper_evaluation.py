#!/usr/bin/env python3
"""
MAIN EVALUATION SCRIPT FOR ALGORAG RESEARCH PAPER
==================================================
Run this single file to generate ALL results for the paper.

Usage:
    python run_paper_evaluation.py

For Colab/Lightning.ai:
    1. Upload this folder
    2. Install: pip install -r requirements_eval.txt
    3. Set GEMINI_API_KEY environment variable
    4. Run: python run_paper_evaluation.py

Outputs:
    - paper_results/detailed_results.json (all question results)
    - paper_results/aggregate_stats.json (summary statistics)
    - paper_results/topic_breakdown.json (per-topic analysis)
    - paper_results/paper_tables.txt (LaTeX tables for paper)
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# Set environment before imports to avoid warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Add paths
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR / "backend"))
sys.path.insert(0, str(ROOT_DIR / "evaluation"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evaluation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def setup_environment():
    """Setup and validate environment."""
    logger.info("=" * 70)
    logger.info("ALGORAG PAPER EVALUATION - SETUP")
    logger.info("=" * 70)

    # Check for API key
    has_key = (os.getenv("GEMINI_API_KEY") or
               os.getenv("OPENAI_API_KEY") or
               os.getenv("DEEPSEEK_API_KEY"))

    if not has_key:
        logger.warning("No API key found. Set one of:")
        logger.warning("  GEMINI_API_KEY (recommended for Colab)")
        logger.warning("  DEEPSEEK_API_KEY (cheapest: $0.28/1M tokens)")
        logger.warning("  OPENAI_API_KEY")

    # Create output directory
    output_dir = ROOT_DIR / "paper_results"
    output_dir.mkdir(exist_ok=True)
    logger.info(f"Output directory: {output_dir}")

    return output_dir


def load_test_dataset(num_questions=None):
    """Load evaluation dataset."""
    dataset_path = ROOT_DIR / "evaluation" / "test_datasets" / "exam_questions" / "evaluation_dataset.json"

    logger.info(f"Loading dataset: {dataset_path}")
    with open(dataset_path, 'r') as f:
        questions = json.load(f)

    if num_questions:
        questions = questions[:num_questions]

    logger.info(f"Loaded {len(questions)} questions")
    return questions


def evaluate_single_question(question_data, retriever, generator, preprocessor, metrics):
    """Evaluate a single question."""
    query = question_data['query']
    reference = question_data['reference_answer']
    metadata = question_data.get('metadata', {})

    start_time = time.time()

    try:
        # Preprocess query
        query_features = preprocessor.extract_query_features(query)

        # Retrieve relevant documents
        retrieval_start = time.time()
        retrieved_docs = retriever.retrieve(
            query=query,
            query_metadata=query_features,
            top_k=5
        )
        retrieval_time = (time.time() - retrieval_start) * 1000

        # Generate answer
        gen_start = time.time()
        generation_result = generator.generate(
            query=query,
            retrieved_docs=retrieved_docs,
            query_type=query_features.get('query_type', 'general')
        )
        generation_time = (time.time() - gen_start) * 1000
        
        # Extract actual answer text
        answer_text = generation_result.get("answer", "")

        # Compute metrics
        from metrics import (
            compute_bleu_score,
            compute_rouge_scores,
            compute_pedagogical_quality
        )

        bleu = compute_bleu_score(reference, answer_text)
        rouge = compute_rouge_scores(reference, answer_text)
        ped_quality = compute_pedagogical_quality(query, answer_text, retrieved_docs)
        ped_score = ped_quality.get('overall_pedagogical_score', 0.5)

        # Compute semantic similarity (simple word overlap for now)
        ref_words = set(reference.lower().split())
        ans_words = set(answer_text.lower().split())
        overlap = len(ref_words & ans_words)
        similarity = overlap / max(len(ref_words), len(ans_words)) if ref_words or ans_words else 0

        total_time = (time.time() - start_time) * 1000

        return {
            "query": query,
            "reference_answer": reference,
            "generated_answer": answer_text,
            "metadata": metadata,
            "metrics": {
                "bleu": bleu,
                "rouge": rouge,
                "pedagogical_quality": ped_score,
                "pedagogical_details": ped_quality,
                "semantic_similarity": similarity,
                "retrieval_time_ms": retrieval_time,
                "generation_time_ms": generation_time,
                "total_time_ms": total_time
            },
            "retrieved_sources": len(retrieved_docs),
            "success": True
        }

    except Exception as e:
        logger.error(f"Error evaluating question: {str(e)}")
        return {
            "query": query,
            "reference_answer": reference,
            "generated_answer": "",
            "metadata": metadata,
            "error": str(e),
            "success": False
        }


def compute_aggregate_statistics(results):
    """Compute aggregate statistics for the paper."""
    successful = [r for r in results if r.get('success', False)]
    total = len(results)

    if not successful:
        return {
            "error": "No successful evaluations",
            "total_cases": total,
            "successful_cases": 0
        }

    # Overall statistics
    success_rate = len(successful) / total

    # Average metrics
    avg_bleu = sum(r['metrics']['bleu'] for r in successful) / len(successful)
    avg_rouge_1 = sum(r['metrics']['rouge'].get('rouge-1', {}).get('f', 0) for r in successful) / len(successful)
    avg_rouge_l = sum(r['metrics']['rouge'].get('rouge-l', {}).get('f', 0) for r in successful) / len(successful)
    avg_similarity = sum(r['metrics']['semantic_similarity'] for r in successful) / len(successful)
    avg_ped_quality = sum(r['metrics']['pedagogical_quality'] for r in successful) / len(successful)
    avg_time = sum(r['metrics']['total_time_ms'] for r in successful) / len(successful)

    # Topic breakdown
    topic_stats = {}
    for result in successful:
        topic = result['metadata'].get('topic', 'unknown')
        if topic not in topic_stats:
            topic_stats[topic] = []
        topic_stats[topic].append(result)

    topic_breakdown = {}
    for topic, topic_results in topic_stats.items():
        topic_breakdown[topic] = {
            "count": len(topic_results),
            "avg_bleu": sum(r['metrics']['bleu'] for r in topic_results) / len(topic_results),
            "avg_rouge_1": sum(r['metrics']['rouge'].get('rouge-1', {}).get('f', 0) for r in topic_results) / len(topic_results),
            "avg_rouge_l": sum(r['metrics']['rouge'].get('rouge-l', {}).get('f', 0) for r in topic_results) / len(topic_results),
            "avg_similarity": sum(r['metrics']['semantic_similarity'] for r in topic_results) / len(topic_results),
            "avg_time_s": sum(r['metrics']['total_time_ms'] for r in topic_results) / len(topic_results) / 1000
        }

    return {
        "total_cases": total,
        "successful_cases": len(successful),
        "failed_cases": total - len(successful),
        "success_rate": success_rate,
        "aggregate_metrics": {
            "mean_bleu": avg_bleu,
            "mean_rouge_1_f1": avg_rouge_1,
            "mean_rouge_l_f1": avg_rouge_l,
            "mean_semantic_similarity": avg_similarity,
            "mean_pedagogical_quality": avg_ped_quality,
            "mean_response_time_s": avg_time / 1000
        },
        "topic_breakdown": topic_breakdown
    }


def generate_paper_tables(aggregate_stats, output_file):
    """Generate LaTeX tables for the paper."""
    with open(output_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("LATEX TABLES FOR PAPER\n")
        f.write("=" * 70 + "\n\n")

        # Check if there are successful evaluations
        if 'aggregate_metrics' not in aggregate_stats:
            f.write("ERROR: No successful evaluations to generate tables.\n")
            f.write(f"Total cases: {aggregate_stats.get('total_cases', 0)}\n")
            f.write(f"Successful cases: {aggregate_stats.get('successful_cases', 0)}\n")
            if 'error' in aggregate_stats:
                f.write(f"Error: {aggregate_stats['error']}\n")
            return

        # Table 1: Overall Performance
        f.write("Table 1: Overall Performance Metrics\n")
        f.write("-" * 70 + "\n")
        f.write("\\begin{table}[h]\n")
        f.write("\\centering\n")
        f.write("\\begin{tabular}{lr}\n")
        f.write("\\toprule\n")
        f.write("Metric & Value \\\\\n")
        f.write("\\midrule\n")

        metrics = aggregate_stats['aggregate_metrics']
        f.write(f"Success Rate & {aggregate_stats['success_rate']*100:.1f}\\% \\\\\n")
        f.write(f"BLEU & {metrics['mean_bleu']:.4f} \\\\\n")
        f.write(f"ROUGE-1 F1 & {metrics['mean_rouge_1_f1']:.4f} \\\\\n")
        f.write(f"ROUGE-L F1 & {metrics['mean_rouge_l_f1']:.4f} \\\\\n")
        f.write(f"Semantic Similarity & {metrics['mean_semantic_similarity']:.4f} \\\\\n")
        f.write(f"Pedagogical Quality & {metrics['mean_pedagogical_quality']:.4f} \\\\\n")
        f.write(f"Avg Response Time (s) & {metrics['mean_response_time_s']:.1f} \\\\\n")
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\caption{Overall performance metrics for AlgoRAG system}\n")
        f.write("\\end{table}\n\n")

        # Table 2: Topic-wise Performance
        f.write("Table 2: Performance by Topic\n")
        f.write("-" * 70 + "\n")
        f.write("\\begin{table}[h]\n")
        f.write("\\centering\n")
        f.write("\\begin{tabular}{lrrrr}\n")
        f.write("\\toprule\n")
        f.write("Topic & Cases & ROUGE-1 & ROUGE-L & Similarity \\\\\n")
        f.write("\\midrule\n")

        for topic, stats in aggregate_stats['topic_breakdown'].items():
            topic_name = topic.replace('_', ' ').title()
            f.write(f"{topic_name} & {stats['count']} & ")
            f.write(f"{stats['avg_rouge_1']:.4f} & ")
            f.write(f"{stats['avg_rouge_l']:.4f} & ")
            f.write(f"{stats['avg_similarity']:.4f} \\\\\n")

        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\caption{Performance metrics by topic area}\n")
        f.write("\\end{table}\n\n")

    logger.info(f"Paper tables generated: {output_file}")


def main():
    """Main evaluation function."""
    print("\n" + "=" * 70)
    print("ALGORAG RESEARCH PAPER - COMPLETE EVALUATION")
    print("=" * 70 + "\n")

    # Setup
    output_dir = setup_environment()

    # Configuration - Auto-detect backend from API keys
    NUM_QUESTIONS = int(os.getenv("NUM_QUESTIONS", "179"))  # All questions by default

    # Auto-detect which API to use based on available keys
    if os.getenv("DEEPSEEK_API_KEY"):
        GENERATOR_BACKEND = os.getenv("GENERATOR_BACKEND", "deepseek")
    elif os.getenv("GEMINI_API_KEY"):
        GENERATOR_BACKEND = os.getenv("GENERATOR_BACKEND", "gemini")
    elif os.getenv("OPENAI_API_KEY"):
        GENERATOR_BACKEND = os.getenv("GENERATOR_BACKEND", "openai")
    else:
        GENERATOR_BACKEND = "gemini"  # Default

    logger.info(f"Configuration:")
    logger.info(f"  - Number of questions: {NUM_QUESTIONS}")
    logger.info(f"  - Generator backend: {GENERATOR_BACKEND}")

    # Load dataset
    questions = load_test_dataset(NUM_QUESTIONS)

    # Initialize components
    logger.info("\nInitializing AlgoRAG components...")

    from rag.embeddings import EmbeddingClient
    from rag.retriever import Retriever
    from rag.generator import AnswerGenerator
    from rag.preprocessing import MathPreprocessor
    import evaluation.metrics as metrics

    # Use local embeddings (works without API key)
    emb_client = EmbeddingClient(backend="local")

    # Initialize retriever
    vector_db_path = ROOT_DIR / "data" / "vector_db"
    retriever = Retriever(
        embedding_client=emb_client,
        db_type="chroma",
        db_path=str(vector_db_path)
    )

    # Initialize generator (requires API key)
    generator = AnswerGenerator(backend=GENERATOR_BACKEND)

    # Initialize preprocessor
    preprocessor = MathPreprocessor()

    logger.info("Components initialized successfully!\n")

    # Run evaluation
    logger.info(f"Starting evaluation on {len(questions)} questions...")
    logger.info("This may take several hours depending on the number of questions.\n")

    results = []
    
    # Checkpoint file path
    checkpoint_file = output_dir / "checkpoint_results.json"
    
    # Load checkpoint if exists
    if checkpoint_file.exists():
        try:
            with open(checkpoint_file, 'r') as f:
                results = json.load(f)
            logger.info(f"🔄 Resuming from checkpoint: Loaded {len(results)} evaluated questions.")
        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {e}")

    # Track evaluated queries to skip duplicates
    evaluated_queries = {r['query'] for r in results}

    start_time = time.time()

    for i, question_data in enumerate(questions, 1):
        # Skip if already evaluated
        if question_data['query'] in evaluated_queries:
            continue

        logger.info(f"[{i}/{len(questions)}] Evaluating: {question_data['query'][:60]}...")

        result = evaluate_single_question(
            question_data, retriever, generator, preprocessor, metrics
        )
        results.append(result)
        
        # Save checkpoint every 5 questions
        if len(results) % 5 == 0:
            with open(checkpoint_file, 'w') as f:
                json.dump(results, f, indent=2)

        if i % 10 == 0:
            elapsed = time.time() - start_time
            # Avoid division by zero if resuming
            processed_count = i - len(evaluated_queries)
            if processed_count > 0:
                avg_time = elapsed / processed_count
                remaining = (len(questions) - i) * avg_time
                logger.info(f"Progress: {i}/{len(questions)} ({i/len(questions)*100:.1f}%)")
                logger.info(f"Estimated time remaining: {remaining/3600:.1f} hours\n")

    total_time = time.time() - start_time
    logger.info(f"\nEvaluation completed in {total_time/3600:.2f} hours")

    # Compute statistics
    logger.info("\nComputing aggregate statistics...")
    aggregate_stats = compute_aggregate_statistics(results)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    detailed_file = output_dir / f"detailed_results_{timestamp}.json"
    with open(detailed_file, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Detailed results saved: {detailed_file}")

    aggregate_file = output_dir / f"aggregate_stats_{timestamp}.json"
    with open(aggregate_file, 'w') as f:
        json.dump(aggregate_stats, f, indent=2)
    logger.info(f"Aggregate statistics saved: {aggregate_file}")

    # Generate paper tables
    tables_file = output_dir / f"paper_tables_{timestamp}.txt"
    generate_paper_tables(aggregate_stats, tables_file)

    # Print summary
    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total cases: {aggregate_stats.get('total_cases', 0)}")
    print(f"Successful: {aggregate_stats.get('successful_cases', 0)} ({aggregate_stats.get('success_rate', 0)*100:.1f}%)")
    print(f"Failed: {aggregate_stats.get('failed_cases', 0)}")
    
    # Only print detailed metrics if we have successful evaluations
    if 'aggregate_metrics' in aggregate_stats:
        print(f"\nKey Metrics:")
        metrics = aggregate_stats['aggregate_metrics']
        print(f"  BLEU: {metrics['mean_bleu']:.4f}")
        print(f"  ROUGE-1 F1: {metrics['mean_rouge_1_f1']:.4f}")
        print(f"  ROUGE-L F1: {metrics['mean_rouge_l_f1']:.4f}")
        print(f"  Semantic Similarity: {metrics['mean_semantic_similarity']:.4f}")
        print(f"  Pedagogical Quality: {metrics['mean_pedagogical_quality']:.4f}")
        print(f"  Avg Response Time: {metrics['mean_response_time_s']:.1f}s")
    else:
        print("\n⚠️ No successful evaluations - check error details in results files")
    print("\n" + "=" * 70)
    print("All results saved to: paper_results/")
    print("Use these files to update your research paper!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
