#!/usr/bin/env python3
"""
Extract Correct Metrics from AlgoRAG Detailed Results
======================================================
This script fixes the metrics extraction bug and generates correct statistics
for the research paper.

Author: Auto-generated for paper finalization
Date: 2026-01-03
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

def load_detailed_results(filepath: str) -> List[Dict]:
    """Load detailed results JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def calculate_overall_metrics(data: List[Dict]) -> Dict:
    """Calculate correct overall metrics from detailed results."""
    total_cases = len(data)
    successful_cases = sum(1 for case in data if case.get('success', False))

    # Initialize accumulators
    total_bleu = 0.0
    total_rouge1_f = 0.0
    total_rouge1_p = 0.0
    total_rouge1_r = 0.0
    total_rouge2_f = 0.0
    total_rouge2_p = 0.0
    total_rouge2_r = 0.0
    total_rougeL_f = 0.0
    total_rougeL_p = 0.0
    total_rougeL_r = 0.0
    total_semantic_similarity = 0.0
    total_pedagogical_quality = 0.0
    total_response_time = 0.0

    # Accumulate metrics
    for case in data:
        if case.get('success', False):
            metrics = case['metrics']
            total_bleu += metrics.get('bleu', 0.0)

            rouge = metrics.get('rouge', {})
            total_rouge1_f += rouge.get('rouge1_f', 0.0)
            total_rouge1_p += rouge.get('rouge1_p', 0.0)
            total_rouge1_r += rouge.get('rouge1_r', 0.0)
            total_rouge2_f += rouge.get('rouge2_f', 0.0)
            total_rouge2_p += rouge.get('rouge2_p', 0.0)
            total_rouge2_r += rouge.get('rouge2_r', 0.0)
            total_rougeL_f += rouge.get('rougeL_f', 0.0)
            total_rougeL_p += rouge.get('rougeL_p', 0.0)
            total_rougeL_r += rouge.get('rougeL_r', 0.0)

            total_semantic_similarity += metrics.get('semantic_similarity', 0.0)
            total_pedagogical_quality += metrics.get('pedagogical_quality', 0.0)
            total_response_time += metrics.get('total_time_ms', 0.0) / 1000.0  # Convert to seconds

    # Calculate averages
    n = successful_cases if successful_cases > 0 else 1

    return {
        'total_cases': total_cases,
        'successful_cases': successful_cases,
        'failed_cases': total_cases - successful_cases,
        'success_rate': successful_cases / total_cases if total_cases > 0 else 0.0,
        'aggregate_metrics': {
            'mean_bleu': total_bleu / n,
            'mean_rouge_1_f1': total_rouge1_f / n,
            'mean_rouge_1_precision': total_rouge1_p / n,
            'mean_rouge_1_recall': total_rouge1_r / n,
            'mean_rouge_2_f1': total_rouge2_f / n,
            'mean_rouge_2_precision': total_rouge2_p / n,
            'mean_rouge_2_recall': total_rouge2_r / n,
            'mean_rouge_l_f1': total_rougeL_f / n,
            'mean_rouge_l_precision': total_rougeL_p / n,
            'mean_rouge_l_recall': total_rougeL_r / n,
            'mean_semantic_similarity': total_semantic_similarity / n,
            'mean_pedagogical_quality': total_pedagogical_quality / n,
            'mean_response_time_s': total_response_time / n
        }
    }

def calculate_topic_metrics(data: List[Dict]) -> Dict:
    """Calculate metrics broken down by topic."""
    topic_data = defaultdict(lambda: {
        'cases': [],
        'count': 0,
        'bleu': [],
        'rouge1_f': [],
        'rouge2_f': [],
        'rougeL_f': [],
        'similarity': [],
        'pedagogical': [],
        'time': []
    })

    # Group by topic
    for case in data:
        if case.get('success', False):
            topic = case['metadata']['topic']
            metrics = case['metrics']

            topic_data[topic]['cases'].append(case['query'])
            topic_data[topic]['count'] += 1
            topic_data[topic]['bleu'].append(metrics.get('bleu', 0.0))
            topic_data[topic]['rouge1_f'].append(metrics['rouge'].get('rouge1_f', 0.0))
            topic_data[topic]['rouge2_f'].append(metrics['rouge'].get('rouge2_f', 0.0))
            topic_data[topic]['rougeL_f'].append(metrics['rouge'].get('rougeL_f', 0.0))
            topic_data[topic]['similarity'].append(metrics.get('semantic_similarity', 0.0))
            topic_data[topic]['pedagogical'].append(metrics.get('pedagogical_quality', 0.0))
            topic_data[topic]['time'].append(metrics.get('total_time_ms', 0.0) / 1000.0)

    # Calculate averages per topic
    topic_stats = {}
    for topic, data_dict in topic_data.items():
        n = data_dict['count']
        topic_stats[topic] = {
            'count': n,
            'avg_bleu': sum(data_dict['bleu']) / n if n > 0 else 0.0,
            'avg_rouge_1_f1': sum(data_dict['rouge1_f']) / n if n > 0 else 0.0,
            'avg_rouge_2_f1': sum(data_dict['rouge2_f']) / n if n > 0 else 0.0,
            'avg_rouge_l_f1': sum(data_dict['rougeL_f']) / n if n > 0 else 0.0,
            'avg_similarity': sum(data_dict['similarity']) / n if n > 0 else 0.0,
            'avg_pedagogical': sum(data_dict['pedagogical']) / n if n > 0 else 0.0,
            'avg_time_s': sum(data_dict['time']) / n if n > 0 else 0.0
        }

    return topic_stats

def generate_latex_tables(overall: Dict, topic_stats: Dict) -> str:
    """Generate LaTeX tables for the paper."""
    output = []
    output.append("="*70)
    output.append("CORRECTED LATEX TABLES FOR PAPER")
    output.append("="*70)
    output.append("")

    # Table 1: Overall Performance
    output.append("Table 1: Overall Performance Metrics")
    output.append("-" * 70)
    output.append("\\begin{table}[h]")
    output.append("\\centering")
    output.append("\\begin{tabular}{lr}")
    output.append("\\toprule")
    output.append("Metric & Value \\\\")
    output.append("\\midrule")

    agg = overall['aggregate_metrics']
    output.append(f"Success Rate & {overall['success_rate']*100:.1f}\\% \\\\")
    output.append(f"BLEU-4 & {agg['mean_bleu']:.4f} \\\\")
    output.append(f"ROUGE-1 F1 & {agg['mean_rouge_1_f1']:.4f} \\\\")
    output.append(f"ROUGE-2 F1 & {agg['mean_rouge_2_f1']:.4f} \\\\")
    output.append(f"ROUGE-L F1 & {agg['mean_rouge_l_f1']:.4f} \\\\")
    output.append(f"Semantic Similarity & {agg['mean_semantic_similarity']:.4f} \\\\")
    output.append(f"Pedagogical Quality & {agg['mean_pedagogical_quality']:.4f} \\\\")
    output.append(f"Avg Response Time (s) & {agg['mean_response_time_s']:.1f} \\\\")

    output.append("\\bottomrule")
    output.append("\\end{tabular}")
    output.append(f"\\caption{{Overall performance metrics for AlgoRAG system on {overall['total_cases']} questions}}")
    output.append("\\end{table}")
    output.append("")

    # Table 2: Performance by Topic
    output.append("Table 2: Performance by Topic")
    output.append("-" * 70)
    output.append("\\begin{table}[h]")
    output.append("\\centering")
    output.append("\\begin{tabular}{lrrrrr}")
    output.append("\\toprule")
    output.append("Topic & Cases & ROUGE-1 & ROUGE-L & Similarity & Ped. Quality \\\\")
    output.append("\\midrule")

    # Sort topics by name for consistency
    for topic in sorted(topic_stats.keys()):
        stats = topic_stats[topic]
        # Format topic name nicely
        topic_name = topic.replace('_', ' ').title()
        output.append(f"{topic_name} & {stats['count']} & "
                     f"{stats['avg_rouge_1_f1']:.4f} & "
                     f"{stats['avg_rouge_l_f1']:.4f} & "
                     f"{stats['avg_similarity']:.4f} & "
                     f"{stats['avg_pedagogical']:.4f} \\\\")

    output.append("\\bottomrule")
    output.append("\\end{tabular}")
    output.append("\\caption{Performance metrics by topic area}")
    output.append("\\end{table}")
    output.append("")

    return "\n".join(output)

def generate_summary_stats(overall: Dict, topic_stats: Dict) -> str:
    """Generate human-readable summary statistics."""
    output = []
    output.append("="*70)
    output.append("SUMMARY STATISTICS")
    output.append("="*70)
    output.append("")

    output.append(f"Total Questions: {overall['total_cases']}")
    output.append(f"Successful: {overall['successful_cases']} ({overall['success_rate']*100:.1f}%)")
    output.append(f"Failed: {overall['failed_cases']}")
    output.append("")

    agg = overall['aggregate_metrics']
    output.append("Average Metrics:")
    output.append(f"  BLEU-4: {agg['mean_bleu']:.4f}")
    output.append(f"  ROUGE-1 F1: {agg['mean_rouge_1_f1']:.4f}")
    output.append(f"  ROUGE-2 F1: {agg['mean_rouge_2_f1']:.4f}")
    output.append(f"  ROUGE-L F1: {agg['mean_rouge_l_f1']:.4f}")
    output.append(f"  Semantic Similarity: {agg['mean_semantic_similarity']:.4f}")
    output.append(f"  Pedagogical Quality: {agg['mean_pedagogical_quality']:.4f}")
    output.append(f"  Response Time: {agg['mean_response_time_s']:.2f}s")
    output.append("")

    output.append("Topic Breakdown:")
    for topic in sorted(topic_stats.keys()):
        stats = topic_stats[topic]
        topic_name = topic.replace('_', ' ').title()
        output.append(f"\n  {topic_name}:")
        output.append(f"    Cases: {stats['count']}")
        output.append(f"    ROUGE-1 F1: {stats['avg_rouge_1_f1']:.4f}")
        output.append(f"    ROUGE-L F1: {stats['avg_rouge_l_f1']:.4f}")
        output.append(f"    Similarity: {stats['avg_similarity']:.4f}")
        output.append(f"    Pedagogical: {stats['avg_pedagogical']:.4f}")

    return "\n".join(output)

def main():
    """Main execution function."""
    print("AlgoRAG Metrics Extraction Tool")
    print("=" * 70)
    print()

    # File paths
    input_file = "paper_results/detailed_results_20260103_141816.json"
    output_dir = Path("paper_results")

    if not Path(input_file).exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    print(f"Loading results from: {input_file}")
    data = load_detailed_results(input_file)
    print(f"Loaded {len(data)} cases")
    print()

    # Calculate metrics
    print("Calculating overall metrics...")
    overall_metrics = calculate_overall_metrics(data)

    print("Calculating topic-wise metrics...")
    topic_metrics = calculate_topic_metrics(data)

    # Generate outputs
    print("\nGenerating LaTeX tables...")
    latex_tables = generate_latex_tables(overall_metrics, topic_metrics)

    print("Generating summary statistics...")
    summary_stats = generate_summary_stats(overall_metrics, topic_metrics)

    # Save outputs
    latex_file = output_dir / "corrected_paper_tables.txt"
    summary_file = output_dir / "corrected_summary_stats.txt"
    json_file = output_dir / "corrected_aggregate_stats.json"

    with open(latex_file, 'w') as f:
        f.write(latex_tables)
    print(f"✓ LaTeX tables saved to: {latex_file}")

    with open(summary_file, 'w') as f:
        f.write(summary_stats)
    print(f"✓ Summary stats saved to: {summary_file}")

    with open(json_file, 'w') as f:
        json.dump({
            'overall': overall_metrics,
            'topic_breakdown': topic_metrics
        }, f, indent=2)
    print(f"✓ JSON stats saved to: {json_file}")

    print("\n" + "=" * 70)
    print("EXTRACTION COMPLETE!")
    print("=" * 70)
    print("\nPreview of corrected metrics:")
    print(summary_stats[:800] + "...")

if __name__ == "__main__":
    main()
