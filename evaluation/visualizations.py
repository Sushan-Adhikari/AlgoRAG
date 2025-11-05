"""
Visualization Tools for AlgoRAG Research Paper

Generates publication-ready charts and graphs:
- Performance comparison charts
- Quality metric distributions
- A/B test visualizations
- Topic-wise performance breakdown
- Timing analysis
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import List, Dict, Any, Optional
import seaborn as sns

# Set publication-quality defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

# Color palette for consistency
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#06A77D',
    'warning': '#F18F01',
    'error': '#C73E1D',
    'neutral': '#6C757D'
}


class ResearchVisualizer:
    """
    Generate publication-ready visualizations for research paper.

    All charts are designed for LaTeX/PDF inclusion.
    """

    def __init__(self, output_dir: str = './visualizations'):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set seaborn style for cleaner plots
        sns.set_style('whitegrid')

    # ==================== Quality Metrics Visualization ====================

    def plot_quality_metrics_comparison(
        self,
        experiment_results: Dict[str, Any],
        output_filename: str = 'quality_metrics.png'
    ):
        """
        Bar chart comparing different quality metrics.

        Shows BLEU, ROUGE, Pedagogical Score, and Overall Quality.
        """
        agg = experiment_results['aggregate']

        metrics = {
            'BLEU-4': agg['mean_bleu'],
            'ROUGE-L\nF1': agg['mean_rouge_f1'],
            'Pedagogical\nScore': agg['mean_pedagogical_score'],
            'Overall\nQuality': agg['mean_overall_quality']
        }

        fig, ax = plt.subplots(figsize=(8, 5))

        bars = ax.bar(
            range(len(metrics)),
            list(metrics.values()),
            color=[COLORS['primary'], COLORS['secondary'],
                   COLORS['success'], COLORS['warning']],
            alpha=0.8,
            edgecolor='black',
            linewidth=1.2
        )

        ax.set_xticks(range(len(metrics)))
        ax.set_xticklabels(list(metrics.keys()), rotation=0)
        ax.set_ylabel('Score')
        ax.set_ylim(0, 1.0)
        ax.set_title(f"Quality Metrics: {experiment_results['experiment']['name']}")
        ax.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold'
            )

        plt.tight_layout()
        filepath = self.output_dir / output_filename
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()

        print(f"✓ Quality metrics chart saved: {filepath}")
        return str(filepath)

    def plot_ab_comparison(
        self,
        ab_results: Dict[str, Any],
        output_filename: str = 'ab_comparison.png'
    ):
        """
        Side-by-side comparison of A/B test results.
        """
        agg_a = ab_results['aggregate_a']
        agg_b = ab_results['aggregate_b']

        metrics = ['mean_overall_quality', 'mean_bleu', 'mean_rouge_f1', 'mean_pedagogical_score']
        metric_labels = ['Overall\nQuality', 'BLEU-4', 'ROUGE-L\nF1', 'Pedagogical\nScore']

        values_a = [agg_a[m] for m in metrics]
        values_b = [agg_b[m] for m in metrics]

        x = np.arange(len(metrics))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))

        bars_a = ax.bar(x - width/2, values_a, width,
                       label=ab_results['experiment_a']['name'],
                       color=COLORS['primary'], alpha=0.8, edgecolor='black', linewidth=1)
        bars_b = ax.bar(x + width/2, values_b, width,
                       label=ab_results['experiment_b']['name'],
                       color=COLORS['secondary'], alpha=0.8, edgecolor='black', linewidth=1)

        ax.set_ylabel('Score')
        ax.set_ylim(0, 1.0)
        ax.set_title(f"A/B Test Comparison\nWinner: {ab_results['winner']}")
        ax.set_xticks(x)
        ax.set_xticklabels(metric_labels)
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for bars in [bars_a, bars_b]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        filepath = self.output_dir / output_filename
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()

        print(f"✓ A/B comparison chart saved: {filepath}")
        return str(filepath)

    # ==================== Performance Analysis ====================

    def plot_topic_performance(
        self,
        experiment_results: Dict[str, Any],
        output_filename: str = 'topic_performance.png'
    ):
        """
        Bar chart showing performance breakdown by topic.
        """
        by_topic = experiment_results['aggregate'].get('by_topic', {})

        if not by_topic:
            print("⚠ No topic breakdown available")
            return None

        topics = list(by_topic.keys())
        scores = [by_topic[t]['mean_quality'] for t in topics]
        counts = [by_topic[t]['count'] for t in topics]

        # Sort by score
        sorted_data = sorted(zip(topics, scores, counts), key=lambda x: x[1], reverse=True)
        topics, scores, counts = zip(*sorted_data)

        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.barh(range(len(topics)), scores,
                      color=COLORS['primary'], alpha=0.8,
                      edgecolor='black', linewidth=1)

        ax.set_yticks(range(len(topics)))
        ax.set_yticklabels([t.replace('_', ' ').title() for t in topics])
        ax.set_xlabel('Mean Quality Score')
        ax.set_xlim(0, 1.0)
        ax.set_title('Performance by Topic')
        ax.grid(axis='x', alpha=0.3)

        # Add value and count labels
        for i, (bar, score, count) in enumerate(zip(bars, scores, counts)):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f' {score:.3f} (n={count})',
                   ha='left', va='center', fontsize=9)

        plt.tight_layout()
        filepath = self.output_dir / output_filename
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()

        print(f"✓ Topic performance chart saved: {filepath}")
        return str(filepath)

    def plot_query_type_performance(
        self,
        experiment_results: Dict[str, Any],
        output_filename: str = 'query_type_performance.png'
    ):
        """
        Performance breakdown by query type (proof, complexity, etc.).
        """
        by_type = experiment_results['aggregate'].get('by_query_type', {})

        if not by_type:
            print("⚠ No query type breakdown available")
            return None

        types = list(by_type.keys())
        scores = [by_type[t]['mean_quality'] for t in types]
        counts = [by_type[t]['count'] for t in types]

        fig, ax = plt.subplots(figsize=(8, 5))

        colors_map = {
            'proof': COLORS['primary'],
            'complexity': COLORS['secondary'],
            'algorithm': COLORS['success'],
            'general': COLORS['warning']
        }
        bar_colors = [colors_map.get(t, COLORS['neutral']) for t in types]

        bars = ax.bar(range(len(types)), scores,
                     color=bar_colors, alpha=0.8,
                     edgecolor='black', linewidth=1.2)

        ax.set_xticks(range(len(types)))
        ax.set_xticklabels([t.replace('_', ' ').title() for t in types])
        ax.set_ylabel('Mean Quality Score')
        ax.set_ylim(0, 1.0)
        ax.set_title('Performance by Query Type')
        ax.grid(axis='y', alpha=0.3)

        # Add labels
        for bar, score, count in zip(bars, scores, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{score:.3f}\n(n={count})',
                   ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        filepath = self.output_dir / output_filename
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()

        print(f"✓ Query type performance chart saved: {filepath}")
        return str(filepath)

    # ==================== Timing Analysis ====================

    def plot_timing_breakdown(
        self,
        experiment_results: Dict[str, Any],
        output_filename: str = 'timing_breakdown.png'
    ):
        """
        Pie chart showing retrieval vs generation time.
        """
        agg = experiment_results['aggregate']

        retrieval_time = agg['mean_retrieval_ms']
        generation_time = agg['mean_generation_ms']

        fig, ax = plt.subplots(figsize=(7, 5))

        times = [retrieval_time, generation_time]
        labels = ['Retrieval', 'Generation']
        colors_list = [COLORS['primary'], COLORS['secondary']]

        wedges, texts, autotexts = ax.pie(
            times, labels=labels, colors=colors_list,
            autopct='%1.1f%%', startangle=90,
            textprops={'fontsize': 10},
            wedgeprops={'edgecolor': 'black', 'linewidth': 1.5}
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title(f'Average Query Time Breakdown\nTotal: {retrieval_time + generation_time:.1f}ms')

        plt.tight_layout()
        filepath = self.output_dir / output_filename
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()

        print(f"✓ Timing breakdown chart saved: {filepath}")
        return str(filepath)

    def plot_latency_distribution(
        self,
        experiment_results: Dict[str, Any],
        output_filename: str = 'latency_distribution.png'
    ):
        """
        Histogram of total query latency distribution.
        """
        individual = experiment_results['individual_results']

        # Filter out errors
        latencies = [
            r['timing']['total_ms'] for r in individual
            if 'error' not in r and 'timing' in r
        ]

        if not latencies:
            print("⚠ No latency data available")
            return None

        fig, ax = plt.subplots(figsize=(8, 5))

        n, bins, patches = ax.hist(
            latencies, bins=20, color=COLORS['primary'],
            alpha=0.7, edgecolor='black', linewidth=1.2
        )

        # Color bins by percentile
        median = np.median(latencies)
        for i, patch in enumerate(patches):
            if bins[i] < median:
                patch.set_facecolor(COLORS['success'])
            else:
                patch.set_facecolor(COLORS['warning'])

        ax.set_xlabel('Total Latency (ms)')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Query Latency Distribution\nMean: {np.mean(latencies):.1f}ms, Median: {median:.1f}ms')
        ax.grid(axis='y', alpha=0.3)

        # Add median line
        ax.axvline(median, color='red', linestyle='--', linewidth=2, label=f'Median: {median:.1f}ms')
        ax.legend()

        plt.tight_layout()
        filepath = self.output_dir / output_filename
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()

        print(f"✓ Latency distribution chart saved: {filepath}")
        return str(filepath)

    # ==================== Score Distributions ====================

    def plot_score_distributions(
        self,
        experiment_results: Dict[str, Any],
        output_filename: str = 'score_distributions.png'
    ):
        """
        Box plots showing distribution of different quality scores.
        """
        individual = experiment_results['individual_results']

        # Extract scores
        bleu_scores = [r['bleu']['BLEU'] for r in individual if 'error' not in r]
        rouge_scores = [r['rouge']['ROUGE-L-F1'] for r in individual if 'error' not in r]
        ped_scores = [r['pedagogical_quality']['overall_pedagogical_score'] for r in individual if 'error' not in r]
        overall_scores = [r['overall_quality'] for r in individual if 'error' not in r]

        fig, ax = plt.subplots(figsize=(9, 6))

        data = [bleu_scores, rouge_scores, ped_scores, overall_scores]
        labels = ['BLEU-4', 'ROUGE-L F1', 'Pedagogical', 'Overall']

        bp = ax.boxplot(
            data, labels=labels, patch_artist=True,
            boxprops=dict(facecolor=COLORS['primary'], alpha=0.7),
            medianprops=dict(color='red', linewidth=2),
            whiskerprops=dict(linewidth=1.5),
            capprops=dict(linewidth=1.5)
        )

        ax.set_ylabel('Score')
        ax.set_ylim(0, 1.0)
        ax.set_title('Distribution of Quality Metrics')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        filepath = self.output_dir / output_filename
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()

        print(f"✓ Score distributions chart saved: {filepath}")
        return str(filepath)

    # ==================== Multi-Experiment Comparison ====================

    def plot_multi_experiment_comparison(
        self,
        experiments: List[Dict[str, Any]],
        output_filename: str = 'multi_experiment_comparison.png'
    ):
        """
        Grouped bar chart comparing multiple experiments.

        Args:
            experiments: List of experiment results dictionaries
        """
        metrics = ['mean_overall_quality', 'mean_bleu', 'mean_rouge_f1', 'mean_pedagogical_score']
        metric_labels = ['Overall', 'BLEU-4', 'ROUGE-L', 'Pedagogical']

        n_metrics = len(metrics)
        n_experiments = len(experiments)

        fig, ax = plt.subplots(figsize=(12, 6))

        x = np.arange(n_metrics)
        width = 0.8 / n_experiments

        colors_list = [COLORS['primary'], COLORS['secondary'], COLORS['success'],
                      COLORS['warning'], COLORS['error'], COLORS['neutral']]

        for i, exp in enumerate(experiments):
            agg = exp['aggregate']
            values = [agg[m] for m in metrics]

            offset = (i - n_experiments/2 + 0.5) * width
            ax.bar(x + offset, values, width,
                  label=exp['experiment']['name'],
                  color=colors_list[i % len(colors_list)],
                  alpha=0.8, edgecolor='black', linewidth=1)

        ax.set_ylabel('Score')
        ax.set_ylim(0, 1.0)
        ax.set_title('Multi-Experiment Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(metric_labels)
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        filepath = self.output_dir / output_filename
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()

        print(f"✓ Multi-experiment comparison chart saved: {filepath}")
        return str(filepath)

    # ==================== Comprehensive Report ====================

    def generate_full_report(
        self,
        experiment_results: Dict[str, Any],
        report_name: str = 'experiment_report'
    ):
        """
        Generate all visualizations for a single experiment.

        Returns:
            Dictionary mapping chart type to filepath
        """
        print(f"\n{'='*60}")
        print(f"Generating Full Visualization Report: {report_name}")
        print(f"{'='*60}\n")

        charts = {}

        # Quality metrics
        charts['quality_metrics'] = self.plot_quality_metrics_comparison(
            experiment_results,
            f'{report_name}_quality_metrics.png'
        )

        # Topic performance
        charts['topic_performance'] = self.plot_topic_performance(
            experiment_results,
            f'{report_name}_topic_performance.png'
        )

        # Query type performance
        charts['query_type_performance'] = self.plot_query_type_performance(
            experiment_results,
            f'{report_name}_query_type_performance.png'
        )

        # Timing breakdown
        charts['timing_breakdown'] = self.plot_timing_breakdown(
            experiment_results,
            f'{report_name}_timing_breakdown.png'
        )

        # Latency distribution
        charts['latency_distribution'] = self.plot_latency_distribution(
            experiment_results,
            f'{report_name}_latency_distribution.png'
        )

        # Score distributions
        charts['score_distributions'] = self.plot_score_distributions(
            experiment_results,
            f'{report_name}_score_distributions.png'
        )

        print(f"\n{'='*60}")
        print(f"Report Generation Complete!")
        print(f"All charts saved to: {self.output_dir}")
        print(f"{'='*60}\n")

        return {k: v for k, v in charts.items() if v is not None}


# ==================== Convenience Functions ====================

def quick_visualize(experiment_results_json: str, output_dir: str = './visualizations'):
    """
    Quick visualization from experiment results JSON file.

    Args:
        experiment_results_json: Path to experiment results JSON
        output_dir: Where to save charts
    """
    with open(experiment_results_json, 'r') as f:
        results = json.load(f)

    viz = ResearchVisualizer(output_dir)
    return viz.generate_full_report(results)


if __name__ == '__main__':
    # Example usage
    print("AlgoRAG Research Visualizations")
    print("Usage: python visualizations.py <experiment_results.json>")

    import sys
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
        quick_visualize(results_file)
