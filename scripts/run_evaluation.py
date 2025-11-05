#!/usr/bin/env python3
"""
Main Evaluation Script for AlgoRAG Research Paper

This script orchestrates the complete evaluation pipeline:
1. Load test cases
2. Run experiments (AlgoRAG vs Baseline)
3. Generate visualizations
4. Export results for publication

Usage:
    python run_evaluation.py --config evaluation_config.json
    python run_evaluation.py --quick-test  # Run on 5 test cases only
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from evaluation.metrics import EvaluationMetrics
from evaluation.experiment_runner import ExperimentRunner, Experiment
try:
    from evaluation.visualizations import ResearchVisualizer
    VISUALIZATIONS_AVAILABLE = True
except ImportError:
    VISUALIZATIONS_AVAILABLE = False
    print("WARNING: visualizations module not available")
from evaluation.baseline_comparison import BaselineRAG, compare_systems
from backend.rag.embeddings import EmbeddingClient
from backend.rag.retriever import Retriever
from backend.rag.generator import Generator


class AlgoRAGEvaluation:
    """
    Complete evaluation pipeline for research paper.
    """

    def __init__(self, config: dict):
        """
        Initialize evaluation pipeline.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_dir = Path(config.get('output_dir', './results'))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.output_dir / 'experiments').mkdir(exist_ok=True)
        (self.output_dir / 'visualizations').mkdir(exist_ok=True)
        (self.output_dir / 'exports').mkdir(exist_ok=True)

        self.evaluator = EvaluationMetrics()
        self.experiment_runner = ExperimentRunner(
            output_dir=str(self.output_dir / 'experiments'),
            verbose=True
        )
        if VISUALIZATIONS_AVAILABLE:
            self.visualizer = ResearchVisualizer(
                output_dir=str(self.output_dir / 'visualizations')
            )
        else:
            self.visualizer = None

        # Load test cases
        self.test_cases = self._load_test_cases()

        print(f"\n{'='*60}")
        print("AlgoRAG Research Evaluation Pipeline")
        print(f"{'='*60}")
        print(f"Output directory: {self.output_dir}")
        print(f"Test cases loaded: {len(self.test_cases)}")
        print(f"{'='*60}\n")

    def _load_test_cases(self) -> list:
        """Load test cases from configured source."""
        test_file = self.config.get('test_cases_file',
                                   '../evaluation/test_datasets/sample_test_cases.json')

        test_file_path = Path(__file__).parent / test_file

        if not test_file_path.exists():
            # Try absolute path
            test_file_path = Path(test_file)

        if not test_file_path.exists():
            print(f"WARNING: Test file not found: {test_file}")
            print("Creating minimal test set...")
            return self._create_minimal_test_set()

        with open(test_file_path, 'r') as f:
            test_cases = json.load(f)

        # Limit if quick test
        if self.config.get('quick_test', False):
            test_cases = test_cases[:5]
            print(f"Quick test mode: Using {len(test_cases)} cases")

        return test_cases

    def _create_minimal_test_set(self) -> list:
        """Create minimal test set if file not found."""
        return [
            {
                "query": "What is the time complexity of binary search?",
                "reference_answer": "Binary search has O(log n) time complexity.",
                "metadata": {"query_type": "complexity", "topic": "algorithms", "difficulty": "easy"}
            },
            {
                "query": "Prove that 2n^2 + 3n = O(n^2)",
                "reference_answer": "Choose c=5 and n0=1. Then 2n^2 + 3n <= 5n^2 for all n >= 1.",
                "metadata": {"query_type": "proof", "topic": "asymptotic_analysis", "difficulty": "medium"}
            }
        ]

    def run_algorag_experiment(self) -> dict:
        """Run AlgoRAG system experiment."""
        print("\n" + "="*60)
        print("EXPERIMENT 1: AlgoRAG (Full System)")
        print("="*60 + "\n")

        experiment = Experiment(
            experiment_id='algorag_full',
            name='AlgoRAG Full System',
            description='AlgoRAG with preprocessing + pedagogical reranking',
            embed_backend=self.config.get('embed_backend', 'local'),
            generator_model=self.config.get('generator_model', 'gemini-2.0-flash-exp'),
            top_k=self.config.get('top_k', 5),
            use_reranking=True
        )

        results = self.experiment_runner.run_experiment(
            experiment=experiment,
            test_cases=self.test_cases,
            save_results=True
        )

        return results

    def run_baseline_experiment(self) -> dict:
        """Run baseline RAG experiment."""
        print("\n" + "="*60)
        print("EXPERIMENT 2: Baseline RAG")
        print("="*60 + "\n")

        experiment = Experiment(
            experiment_id='baseline_rag',
            name='Baseline RAG (No Enhancements)',
            description='Standard RAG without AlgoRAG enhancements',
            embed_backend=self.config.get('embed_backend', 'local'),
            generator_model=self.config.get('generator_model', 'gemini-2.0-flash-exp'),
            top_k=self.config.get('top_k', 5),
            use_reranking=False  # Key difference
        )

        results = self.experiment_runner.run_experiment(
            experiment=experiment,
            test_cases=self.test_cases,
            save_results=True
        )

        return results

    def run_ab_comparison(self):
        """Run A/B test between AlgoRAG and Baseline."""
        print("\n" + "="*60)
        print("A/B COMPARISON: AlgoRAG vs Baseline")
        print("="*60 + "\n")

        exp_algo = Experiment(
            experiment_id='algorag_ab',
            name='AlgoRAG',
            description='Full system with all enhancements',
            embed_backend=self.config.get('embed_backend', 'local'),
            generator_model=self.config.get('generator_model', 'gemini-2.0-flash-exp'),
            use_reranking=True
        )

        exp_baseline = Experiment(
            experiment_id='baseline_ab',
            name='Baseline',
            description='Standard RAG',
            embed_backend=self.config.get('embed_backend', 'local'),
            generator_model=self.config.get('generator_model', 'gemini-2.0-flash-exp'),
            use_reranking=False
        )

        ab_results = self.experiment_runner.run_ab_test(
            experiment_a=exp_algo,
            experiment_b=exp_baseline,
            test_cases=self.test_cases,
            save_results=True
        )

        return ab_results

    def generate_visualizations(self, results: dict):
        """Generate all visualizations for a result set."""
        if not self.visualizer:
            print("\nSkipping visualizations (module not available)")
            return None

        print("\n" + "="*60)
        print("GENERATING VISUALIZATIONS")
        print("="*60 + "\n")

        charts = self.visualizer.generate_full_report(
            experiment_results=results,
            report_name=results['experiment']['experiment_id']
        )

        return charts

    def generate_ab_visualizations(self, ab_results: dict):
        """Generate A/B comparison visualizations."""
        if not self.visualizer:
            print("\nSkipping A/B visualizations (module not available)")
            return None

        print("\nGenerating A/B comparison chart...")

        chart_path = self.visualizer.plot_ab_comparison(
            ab_results=ab_results,
            output_filename='ab_comparison.png'
        )

        return chart_path

    def export_results(self, algorag_results: dict, baseline_results: dict, ab_results: dict):
        """Export results in publication-ready formats."""
        print("\n" + "="*60)
        print("EXPORTING RESULTS")
        print("="*60 + "\n")

        export_dir = self.output_dir / 'exports'

        # 1. Summary JSON
        summary = {
            'evaluation_date': datetime.now().isoformat(),
            'config': self.config,
            'test_cases_count': len(self.test_cases),
            'algorag': algorag_results['aggregate'],
            'baseline': baseline_results['aggregate'],
            'ab_comparison': ab_results['comparison'],
            'winner': ab_results['winner']
        }

        summary_file = export_dir / 'evaluation_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Summary exported: {summary_file}")

        # 2. CSV for statistical analysis
        self._export_csv(algorag_results, export_dir / 'algorag_results.csv')
        self._export_csv(baseline_results, export_dir / 'baseline_results.csv')

        # 3. LaTeX table
        self._export_latex_table(summary, export_dir / 'results_table.tex')

        # 4. Markdown report
        self._export_markdown_report(summary, ab_results, export_dir / 'evaluation_report.md')

        print(f"\nAll exports saved to: {export_dir}")

    def _export_csv(self, results: dict, filepath: Path):
        """Export individual results to CSV."""
        import csv

        with open(filepath, 'w', newline='') as f:
            fieldnames = [
                'query', 'overall_quality', 'bleu', 'rouge_f1',
                'pedagogical_score', 'topic', 'difficulty',
                'retrieval_ms', 'generation_ms'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in results['individual_results']:
                if 'error' in result:
                    continue

                writer.writerow({
                    'query': result['query'],
                    'overall_quality': result['overall_quality'],
                    'bleu': result['bleu']['BLEU'],
                    'rouge_f1': result['rouge']['ROUGE-L-F1'],
                    'pedagogical_score': result['pedagogical_quality']['overall_pedagogical_score'],
                    'topic': result['metadata'].get('topic', 'unknown'),
                    'difficulty': result['metadata'].get('difficulty', 'unknown'),
                    'retrieval_ms': result['timing']['retrieval_ms'],
                    'generation_ms': result['timing']['generation_ms']
                })

        print(f"✓ CSV exported: {filepath}")

    def _export_latex_table(self, summary: dict, filepath: Path):
        """Generate LaTeX table for paper."""
        latex = r"""
\begin{table}[h]
\centering
\caption{AlgoRAG vs Baseline RAG Performance Comparison}
\label{tab:results}
\begin{tabular}{lcc}
\toprule
\textbf{Metric} & \textbf{AlgoRAG} & \textbf{Baseline} \\
\midrule
Overall Quality & {algo_quality:.3f} & {base_quality:.3f} \\
BLEU-4 & {algo_bleu:.3f} & {base_bleu:.3f} \\
ROUGE-L F1 & {algo_rouge:.3f} & {base_rouge:.3f} \\
Pedagogical Score & {algo_ped:.3f} & {base_ped:.3f} \\
Avg Latency (ms) & {algo_time:.1f} & {base_time:.1f} \\
\midrule
\textbf{{Improvement}} & \multicolumn{{2}}{{c}}{{{improvement:+.3f}}} \\
\bottomrule
\end{tabular}
\end{table}
""".format(
            algo_quality=summary['algorag']['mean_overall_quality'],
            base_quality=summary['baseline']['mean_overall_quality'],
            algo_bleu=summary['algorag']['mean_bleu'],
            base_bleu=summary['baseline']['mean_bleu'],
            algo_rouge=summary['algorag']['mean_rouge_f1'],
            base_rouge=summary['baseline']['mean_rouge_f1'],
            algo_ped=summary['algorag']['mean_pedagogical_score'],
            base_ped=summary['baseline']['mean_pedagogical_score'],
            algo_time=summary['algorag']['avg_time_per_case_ms'],
            base_time=summary['baseline']['avg_time_per_case_ms'],
            improvement=summary['ab_comparison']['overall_quality_diff']
        )

        with open(filepath, 'w') as f:
            f.write(latex)

        print(f"✓ LaTeX table exported: {filepath}")

    def _export_markdown_report(self, summary: dict, ab_results: dict, filepath: Path):
        """Generate Markdown evaluation report."""
        report = f"""# AlgoRAG Evaluation Report

**Date:** {summary['evaluation_date']}

**Test Cases:** {summary['test_cases_count']}

---

## Results Summary

### AlgoRAG (Full System)

- **Overall Quality:** {summary['algorag']['mean_overall_quality']:.4f}
- **BLEU-4:** {summary['algorag']['mean_bleu']:.4f}
- **ROUGE-L F1:** {summary['algorag']['mean_rouge_f1']:.4f}
- **Pedagogical Score:** {summary['algorag']['mean_pedagogical_score']:.4f}
- **Average Latency:** {summary['algorag']['avg_time_per_case_ms']:.2f}ms

### Baseline RAG

- **Overall Quality:** {summary['baseline']['mean_overall_quality']:.4f}
- **BLEU-4:** {summary['baseline']['mean_bleu']:.4f}
- **ROUGE-L F1:** {summary['baseline']['mean_rouge_f1']:.4f}
- **Pedagogical Score:** {summary['baseline']['mean_pedagogical_score']:.4f}
- **Average Latency:** {summary['baseline']['avg_time_per_case_ms']:.2f}ms

---

## A/B Comparison

**Winner:** {ab_results['winner']}

### Improvements (AlgoRAG - Baseline)

- **Overall Quality:** {summary['ab_comparison']['overall_quality_diff']:+.4f}
- **BLEU:** {summary['ab_comparison']['bleu_diff']:+.4f}
- **ROUGE:** {summary['ab_comparison']['rouge_diff']:+.4f}
- **Pedagogical:** {summary['ab_comparison']['pedagogical_diff']:+.4f}
- **Speed:** {summary['ab_comparison']['speed_diff_ms']:+.2f}ms

---

## Conclusion

AlgoRAG demonstrates {'improvement' if summary['ab_comparison']['overall_quality_diff'] > 0 else 'no significant difference'} over baseline RAG
with a {abs(summary['ab_comparison']['overall_quality_diff']):.4f} difference in overall quality.

The pedagogical enhancements and mathematical preprocessing contribute to
{'better' if summary['ab_comparison']['pedagogical_diff'] > 0 else 'similar'} educational outcomes.
"""

        with open(filepath, 'w') as f:
            f.write(report)

        print(f"✓ Markdown report exported: {filepath}")

    def run_full_evaluation(self):
        """Run complete evaluation pipeline."""
        print("\n" + "="*80)
        print(" "*20 + "ALGORAG FULL EVALUATION PIPELINE")
        print("="*80 + "\n")

        # 1. Run AlgoRAG experiment
        algorag_results = self.run_algorag_experiment()

        # 2. Run Baseline experiment
        baseline_results = self.run_baseline_experiment()

        # 3. Run A/B comparison
        ab_results = self.run_ab_comparison()

        # 4. Generate visualizations
        print("\n" + "="*60)
        print("VISUALIZATION GENERATION")
        print("="*60)

        self.generate_visualizations(algorag_results)
        self.generate_visualizations(baseline_results)
        self.generate_ab_visualizations(ab_results)

        # 5. Export results
        self.export_results(algorag_results, baseline_results, ab_results)

        # 6. Final summary
        print("\n" + "="*80)
        print(" "*25 + "EVALUATION COMPLETE!")
        print("="*80)
        print(f"\nAll results saved to: {self.output_dir}")
        print(f"\n✓ Experiments: {self.output_dir / 'experiments'}")
        print(f"✓ Visualizations: {self.output_dir / 'visualizations'}")
        print(f"✓ Exports: {self.output_dir / 'exports'}")
        print("\n" + "="*80 + "\n")

        return {
            'algorag': algorag_results,
            'baseline': baseline_results,
            'ab_comparison': ab_results
        }


def main():
    parser = argparse.ArgumentParser(description='AlgoRAG Research Evaluation')
    parser.add_argument('--config', type=str, help='Path to configuration JSON file')
    parser.add_argument('--quick-test', action='store_true', help='Run on 5 test cases only')
    parser.add_argument('--output-dir', type=str, default='./evaluation_results',
                       help='Output directory for results')

    args = parser.parse_args()

    # Load or create config
    if args.config and Path(args.config).exists():
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = {
            'embed_backend': os.environ.get('EMBED_BACKEND', 'local'),
            'generator_model': os.environ.get('GENERATOR_MODEL', 'gemini-2.0-flash-exp'),
            'top_k': 5,
            'output_dir': args.output_dir,
            'quick_test': args.quick_test,
            'test_cases_file': '../evaluation/test_datasets/sample_test_cases.json'
        }

    # Run evaluation
    evaluation = AlgoRAGEvaluation(config)
    results = evaluation.run_full_evaluation()

    return results


if __name__ == '__main__':
    main()
