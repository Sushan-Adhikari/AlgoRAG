#!/usr/bin/env python3
"""
Results analysis and visualization script for AlgoRAG research paper.
Generates tables, charts, and statistical analysis for publication.
"""

import sys
import json
import numpy as np
from pathlib import Path
from typing import Dict, List
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResultsAnalyzer:
    """
    Analyzes evaluation results and generates publication-ready outputs.
    """

    def __init__(self, results_file: Path, output_dir: Path):
        """
        Initialize analyzer.

        Args:
            results_file: Path to detailed results JSON
            output_dir: Directory to save analysis outputs
        """
        self.results_file = results_file
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Loading results from: {results_file}")
        with open(results_file, 'r', encoding='utf-8') as f:
            self.results = json.load(f)

        # Filter successful results
        self.successful = [r for r in self.results if "error" not in r]
        logger.info(f"Loaded {len(self.successful)} successful evaluations")

    def generate_latex_table(self):
        """
        Generate LaTeX table of results for paper.
        """
        logger.info("Generating LaTeX table...")

        # Aggregate by topic
        by_topic = {}
        for result in self.successful:
            topic = result.get("topic", "unknown")
            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(result)

        # Generate table
        latex = []
        latex.append("\\begin{table}[h]")
        latex.append("\\centering")
        latex.append("\\caption{AlgoRAG Evaluation Results by Topic}")
        latex.append("\\label{tab:results}")
        latex.append("\\begin{tabular}{lcccccc}")
        latex.append("\\toprule")
        latex.append("Topic & Cases & BLEU & ROUGE-1 & ROUGE-L & BERTScore & Avg Time (s) \\\\")
        latex.append("\\midrule")

        for topic, topic_results in sorted(by_topic.items()):
            count = len(topic_results)

            # Compute averages
            def avg(metric):
                values = [r["metrics"].get(metric) for r in topic_results
                         if r["metrics"].get(metric) is not None]
                return np.mean(values) if values else 0

            bleu = avg("bleu")
            rouge1 = avg("rouge1_f")
            rougeL = avg("rougeL_f")
            bert = avg("bertscore_f1")
            time_avg = avg("response_time_seconds")

            # Format topic name
            topic_name = topic.replace("_", " ").title()

            latex.append(f"{topic_name} & {count} & "
                        f"{bleu:.3f} & {rouge1:.3f} & {rougeL:.3f} & "
                        f"{bert:.3f} & {time_avg:.2f} \\\\")

        # Overall row
        count = len(self.successful)
        bleu = np.mean([r["metrics"].get("bleu", 0) for r in self.successful])
        rouge1 = np.mean([r["metrics"].get("rouge1_f", 0) for r in self.successful])
        rougeL = np.mean([r["metrics"].get("rougeL_f", 0) for r in self.successful])
        bert_values = [r["metrics"].get("bertscore_f1") for r in self.successful
                      if r["metrics"].get("bertscore_f1") is not None]
        bert = np.mean(bert_values) if bert_values else 0
        time_avg = np.mean([r["metrics"].get("response_time_seconds", 0)
                           for r in self.successful])

        latex.append("\\midrule")
        latex.append(f"\\textbf{{Overall}} & \\textbf{{{count}}} & "
                    f"\\textbf{{{bleu:.3f}}} & \\textbf{{{rouge1:.3f}}} & "
                    f"\\textbf{{{rougeL:.3f}}} & \\textbf{{{bert:.3f}}} & "
                    f"\\textbf{{{time_avg:.2f}}} \\\\")

        latex.append("\\bottomrule")
        latex.append("\\end{tabular}")
        latex.append("\\end{table}")

        # Save
        output_file = self.output_dir / "results_table.tex"
        with open(output_file, 'w') as f:
            f.write('\n'.join(latex))

        logger.info(f"✓ Saved LaTeX table: {output_file}")
        return '\n'.join(latex)

    def generate_pedagogical_quality_table(self):
        """
        Generate table showing pedagogical quality metrics.
        """
        logger.info("Generating pedagogical quality table...")

        # Group by query type
        by_query_type = {}
        for result in self.successful:
            qtype = result.get("query_type", "general")
            if qtype not in by_query_type:
                by_query_type[qtype] = []
            by_query_type[qtype].append(result)

        latex = []
        latex.append("\\begin{table}[h]")
        latex.append("\\centering")
        latex.append("\\caption{Pedagogical Quality Metrics by Query Type}")
        latex.append("\\label{tab:pedagogical}")
        latex.append("\\begin{tabular}{lcccc}")
        latex.append("\\toprule")
        latex.append("Query Type & Cases & Step-by-Step & Math Notation & Examples \\\\")
        latex.append("\\midrule")

        for qtype, qtype_results in sorted(by_query_type.items()):
            count = len(qtype_results)

            # Compute averages (these are binary 0/1 values)
            step_by_step = np.mean([r["metrics"].get("has_step_by_step", 0)
                                   for r in qtype_results])
            math_notation = np.mean([r["metrics"].get("has_mathematical_notation", 0)
                                    for r in qtype_results])
            examples = np.mean([r["metrics"].get("has_examples", 0)
                               for r in qtype_results])

            # Format query type
            qtype_name = qtype.replace("_", " ").title()

            latex.append(f"{qtype_name} & {count} & "
                        f"{step_by_step*100:.1f}\\% & "
                        f"{math_notation*100:.1f}\\% & "
                        f"{examples*100:.1f}\\% \\\\")

        latex.append("\\bottomrule")
        latex.append("\\end{tabular}")
        latex.append("\\end{table}")

        # Save
        output_file = self.output_dir / "pedagogical_table.tex"
        with open(output_file, 'w') as f:
            f.write('\n'.join(latex))

        logger.info(f"✓ Saved pedagogical table: {output_file}")
        return '\n'.join(latex)

    def generate_statistics_summary(self):
        """
        Generate statistical summary for paper.
        """
        logger.info("Generating statistics summary...")

        # Extract all metrics
        bleu_scores = [r["metrics"].get("bleu", 0) for r in self.successful]
        rouge1_scores = [r["metrics"].get("rouge1_f", 0) for r in self.successful]
        rougeL_scores = [r["metrics"].get("rougeL_f", 0) for r in self.successful]
        similarity_scores = [r["metrics"].get("avg_similarity", 0)
                            for r in self.successful]
        response_times = [r["metrics"].get("response_time_seconds", 0)
                         for r in self.successful]

        summary = {
            "total_cases": len(self.results),
            "successful_cases": len(self.successful),
            "success_rate": len(self.successful) / len(self.results) * 100,
            "bleu": {
                "mean": np.mean(bleu_scores),
                "std": np.std(bleu_scores),
                "min": np.min(bleu_scores),
                "max": np.max(bleu_scores),
                "median": np.median(bleu_scores)
            },
            "rouge1_f": {
                "mean": np.mean(rouge1_scores),
                "std": np.std(rouge1_scores),
                "min": np.min(rouge1_scores),
                "max": np.max(rouge1_scores),
                "median": np.median(rouge1_scores)
            },
            "rougeL_f": {
                "mean": np.mean(rougeL_scores),
                "std": np.std(rougeL_scores),
                "min": np.min(rougeL_scores),
                "max": np.max(rougeL_scores),
                "median": np.median(rougeL_scores)
            },
            "retrieval_similarity": {
                "mean": np.mean(similarity_scores),
                "std": np.std(similarity_scores),
                "min": np.min(similarity_scores),
                "max": np.max(similarity_scores),
                "median": np.median(similarity_scores)
            },
            "response_time_seconds": {
                "mean": np.mean(response_times),
                "std": np.std(response_times),
                "min": np.min(response_times),
                "max": np.max(response_times),
                "median": np.median(response_times)
            }
        }

        # Save as JSON
        stats_file = self.output_dir / "statistics_summary.json"
        with open(stats_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"✓ Saved statistics: {stats_file}")

        # Also save as text for easy reading
        text_file = self.output_dir / "statistics_summary.txt"
        with open(text_file, 'w') as f:
            f.write("AlgoRAG Statistical Summary\n")
            f.write("="*80 + "\n\n")

            f.write(f"Total cases: {summary['total_cases']}\n")
            f.write(f"Successful: {summary['successful_cases']}\n")
            f.write(f"Success rate: {summary['success_rate']:.2f}%\n\n")

            for metric, stats in summary.items():
                if isinstance(stats, dict):
                    f.write(f"{metric}:\n")
                    for stat_name, value in stats.items():
                        f.write(f"  {stat_name}: {value:.4f}\n")
                    f.write("\n")

        logger.info(f"✓ Saved statistics text: {text_file}")

        return summary

    def generate_error_analysis(self):
        """
        Analyze failed cases.
        """
        logger.info("Generating error analysis...")

        failed = [r for r in self.results if "error" in r]

        if not failed:
            logger.info("No failed cases to analyze")
            return

        # Group by error type
        error_types = {}
        for result in failed:
            error = result.get("error", "Unknown")
            if error not in error_types:
                error_types[error] = []
            error_types[error].append(result)

        # Save analysis
        output_file = self.output_dir / "error_analysis.txt"
        with open(output_file, 'w') as f:
            f.write("Error Analysis\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total failed cases: {len(failed)}\n")
            f.write(f"Failure rate: {len(failed)/len(self.results)*100:.2f}%\n\n")

            f.write("Errors by type:\n")
            f.write("-"*80 + "\n")
            for error, cases in sorted(error_types.items(),
                                      key=lambda x: len(x[1]), reverse=True):
                f.write(f"\n{error}: {len(cases)} cases\n")
                for case in cases[:3]:  # Show first 3 examples
                    f.write(f"  - {case.get('question', 'N/A')[:100]}...\n")

        logger.info(f"✓ Saved error analysis: {output_file}")

    def generate_full_report(self):
        """
        Generate full analysis report.
        """
        logger.info("\n" + "="*80)
        logger.info("GENERATING FULL ANALYSIS REPORT")
        logger.info("="*80)

        # Generate all analyses
        self.generate_latex_table()
        self.generate_pedagogical_quality_table()
        stats = self.generate_statistics_summary()
        self.generate_error_analysis()

        # Generate comprehensive report
        report_file = self.output_dir / "full_report.txt"
        with open(report_file, 'w') as f:
            f.write("AlgoRAG Research Evaluation - Full Report\n")
            f.write("="*80 + "\n\n")

            f.write(f"Generated: {Path(self.results_file).name}\n")
            f.write(f"Total evaluations: {len(self.results)}\n")
            f.write(f"Successful: {len(self.successful)}\n")
            f.write(f"Failed: {len(self.results) - len(self.successful)}\n\n")

            f.write("Key Findings:\n")
            f.write("-"*80 + "\n")
            f.write(f"Average BLEU score: {stats['bleu']['mean']:.4f} "
                   f"(±{stats['bleu']['std']:.4f})\n")
            f.write(f"Average ROUGE-1 F1: {stats['rouge1_f']['mean']:.4f} "
                   f"(±{stats['rouge1_f']['std']:.4f})\n")
            f.write(f"Average ROUGE-L F1: {stats['rougeL_f']['mean']:.4f} "
                   f"(±{stats['rougeL_f']['std']:.4f})\n")
            f.write(f"Average retrieval similarity: {stats['retrieval_similarity']['mean']:.4f}\n")
            f.write(f"Average response time: {stats['response_time_seconds']['mean']:.2f}s\n\n")

            f.write("Files generated:\n")
            f.write("  - results_table.tex (for paper)\n")
            f.write("  - pedagogical_table.tex (for paper)\n")
            f.write("  - statistics_summary.json\n")
            f.write("  - statistics_summary.txt\n")
            f.write("  - error_analysis.txt\n")

        logger.info(f"✓ Saved full report: {report_file}")
        logger.info("\n✓ Analysis complete! All outputs saved to: " + str(self.output_dir))


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze AlgoRAG evaluation results for publication"
    )
    parser.add_argument(
        "--results-file",
        type=Path,
        required=True,
        help="Path to detailed results JSON file"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent / "analysis",
        help="Directory to save analysis outputs"
    )

    args = parser.parse_args()

    # Validate
    if not args.results_file.exists():
        logger.error(f"Results file not found: {args.results_file}")
        sys.exit(1)

    # Run analysis
    try:
        analyzer = ResultsAnalyzer(args.results_file, args.output_dir)
        analyzer.generate_full_report()

        logger.info("\n✓ SUCCESS: Analysis complete!")
        logger.info(f"All outputs saved to: {args.output_dir}")

    except Exception as e:
        logger.error(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
