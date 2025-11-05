### AlgoRAG Evaluation Framework

Complete evaluation toolkit for the research paper: **"Retrieval-Augmented Generation for Theoretical Computer Science Education: A Comprehensive Evaluation Framework for Algorithm Analysis and Complexity Theory"**

---

## Overview

This module provides:
- **Automated quality metrics** (BLEU, ROUGE, pedagogical scoring)
- **Experiment orchestration** (batch testing, A/B comparisons)
- **Publication-ready visualizations** (charts, graphs, tables)
- **User study framework** (pre/post assessments, surveys)
- **Baseline comparison** (AlgoRAG vs vanilla RAG)
- **Result export** (CSV, JSON, LaTeX, Markdown)

---

## Module Structure

```
evaluation/
├── metrics.py              # BLEU, ROUGE, pedagogical quality metrics
├── experiment_runner.py    # Batch experiments, A/B testing
├── visualizations.py       # Publication-quality charts
├── baseline_comparison.py  # Vanilla RAG for comparison
├── user_study.py          # Pre/post assessments, surveys
├── test_datasets/
│   └── sample_test_cases.json  # 15 test questions with reference answers
├── requirements.txt        # Evaluation-specific dependencies
└── README.md              # This file
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Installs:**
- numpy, scipy (numerical computing)
- matplotlib, seaborn (visualization)
- pandas (data manipulation)
- scikit-learn (metrics)

### 2. Run Evaluation

```bash
cd ../scripts
python run_evaluation.py --quick-test
```

This runs a complete evaluation pipeline on 5 test cases.

---

## Module Reference

### `metrics.py` - Evaluation Metrics

Implements all quality metrics for the research paper.

**Example usage:**

```python
from evaluation.metrics import EvaluationMetrics

evaluator = EvaluationMetrics()

# Evaluate a single answer
result = evaluator.evaluate_answer(
    query="Prove that 2n^2 + 3n = O(n^2)",
    reference_answer="Choose c=5, n0=1. Then 2n^2+3n <= 5n^2 for n>=1. QED.",
    generated_answer="To prove, we need c>0 and n0>0...",
    retrieved_docs=[...],
    metadata={'query_type': 'proof', 'topic': 'asymptotic_analysis'}
)

print(result['bleu']['BLEU'])  # 0.7234
print(result['rouge']['ROUGE-L-F1'])  # 0.8012
print(result['pedagogical_quality']['overall_pedagogical_score'])  # 0.8891
print(result['overall_quality'])  # 0.8523
```

**Available metrics:**

1. **BLEU (Bilingual Evaluation Understudy)**
   - `compute_bleu(reference, candidate)` → BLEU-1 through BLEU-4
   - Measures n-gram precision with brevity penalty
   - Standard in machine translation, adapted for QA

2. **ROUGE-L (Longest Common Subsequence)**
   - `compute_rouge_l(reference, candidate)` → Precision, Recall, F1
   - Recall-oriented metric for content coverage

3. **Pedagogical Quality**
   - `compute_pedagogical_quality(answer, metadata)` → Multiple subscores
   - Measures: step granularity, explanation depth, examples, proof structure, math notation
   - Weighted composite score

4. **Proof Completeness**
   - `compute_proof_completeness(proof_text)` → Completeness score
   - Checks: statement, steps, conclusion, notation, logical flow

5. **Relevance**
   - `compute_relevance(query, answer, retrieved_docs)` → Relevance metrics
   - Query term coverage, source quality

**Batch evaluation:**

```python
# Evaluate multiple test cases
test_cases = [
    {
        'query': "...",
        'reference_answer': "...",
        'generated_answer': "...",
        'retrieved_docs': [...],
        'metadata': {...}
    },
    # ... more cases
]

batch_results = evaluator.evaluate_batch(test_cases)
print(batch_results['aggregate']['mean_bleu'])  # 0.7234
```

---

### `experiment_runner.py` - Experiment Orchestration

Manages batch experiments and A/B testing.

**Example usage:**

```python
from evaluation.experiment_runner import ExperimentRunner, Experiment

# Define experiment
experiment = Experiment(
    experiment_id='exp_001',
    name='AlgoRAG with Local Embeddings',
    description='Full system using local embeddings',
    embed_backend='local',
    generator_model='gemini-2.0-flash-exp',
    top_k=5,
    use_reranking=True
)

# Run experiment
runner = ExperimentRunner(output_dir='./results')
results = runner.run_experiment(experiment, test_cases)

# Results include:
# - Aggregate statistics (mean BLEU, ROUGE, etc.)
# - Individual case results
# - Timing information
# - Topic/query-type breakdowns
```

**A/B testing:**

```python
exp_a = Experiment(experiment_id='algorag', name='AlgoRAG', ...)
exp_b = Experiment(experiment_id='baseline', name='Baseline', ...)

ab_results = runner.run_ab_test(exp_a, exp_b, test_cases)

print(ab_results['winner'])  # "Experiment A"
print(ab_results['comparison']['overall_quality_diff'])  # +0.118
```

**CSV export:**

```python
runner.export_results_csv('exp_001', 'results.csv')
```

---

### `visualizations.py` - Publication-Quality Charts

Generates charts for research paper (300 DPI, publication-ready).

**Example usage:**

```python
from evaluation.visualizations import ResearchVisualizer

viz = ResearchVisualizer(output_dir='./charts')

# Generate all charts for an experiment
charts = viz.generate_full_report(experiment_results, report_name='algorag_exp1')

# Individual charts:
viz.plot_quality_metrics_comparison(results, 'quality.png')
viz.plot_ab_comparison(ab_results, 'comparison.png')
viz.plot_topic_performance(results, 'topics.png')
viz.plot_timing_breakdown(results, 'timing.png')
viz.plot_latency_distribution(results, 'latency.png')
```

**Available visualizations:**

- Quality metrics bar chart (BLEU, ROUGE, Pedagogical, Overall)
- A/B comparison (side-by-side bars)
- Topic performance (horizontal bars)
- Query type performance (colored bars)
- Timing breakdown (pie chart)
- Latency distribution (histogram)
- Score distributions (box plots)
- Multi-experiment comparison (grouped bars)

All charts:
- 300 DPI for publication
- Serif fonts, clean styling
- Suitable for LaTeX/PDF inclusion

---

### `baseline_comparison.py` - Baseline RAG System

Standard RAG without AlgoRAG enhancements (control group).

**Differences from AlgoRAG:**

| Feature | AlgoRAG | Baseline |
|---------|---------|----------|
| Mathematical preprocessing | ✓ | ✗ |
| Pedagogical re-ranking | ✓ | ✗ |
| Query-type awareness | ✓ | ✗ |
| Proof-specific prompting | ✓ | ✗ |

**Example usage:**

```python
from evaluation.baseline_comparison import BaselineRAG, compare_systems

baseline = BaselineRAG(embed_backend='local')

# Query baseline system
result = baseline.query("What is Big-O notation?")
print(result['answer'])

# Compare AlgoRAG vs Baseline
from evaluation.metrics import EvaluationMetrics

comparison = compare_systems(
    algorag_system=algorag,
    baseline_system=baseline,
    test_cases=test_cases,
    evaluator=EvaluationMetrics()
)

print(comparison['improvement']['overall_quality'])  # +0.118
```

---

### `user_study.py` - User Study Framework

Pre/post assessments and surveys for measuring learning outcomes.

**Example usage:**

```python
from evaluation.user_study import UserStudy

study = UserStudy(study_id='spring_2025')

# Create assessments
pre_questions = study.create_pre_assessment()  # 8 questions
post_questions = study.create_post_assessment()  # 8 parallel questions
survey = study.create_satisfaction_survey()  # Likert scale + open-ended

# Register participants
study.register_participant('student_001', demographics={'year': 'junior'})

# Collect responses
study.collect_pre_response('student_001', 'pre_1', 'answer', time_spent_seconds=120)
# ... intervention (student uses AlgoRAG) ...
study.collect_post_response('student_001', 'post_1', 'answer', time_spent_seconds=90)

# Analyze
analysis = study.analyze_results()
print(analysis['mean_normalized_gain'])  # 0.65

# Export
study.export_to_csv('user_study_results.csv')
```

**Pre/Post assessment topics:**
- Asymptotic analysis (Big-O proofs)
- Recurrence relations (Master Theorem)
- Dynamic programming (optimal substructure)
- Graph algorithms (complexity)
- NP-completeness (definitions, proofs)

**Survey questions (Likert 1-5):**
- AlgoRAG helped me understand concepts
- Explanations were clear
- Proofs were helpful
- I would use AlgoRAG again
- Better than textbooks
- Notation was accurate
- Response time was adequate

---

## Test Datasets

### `test_datasets/sample_test_cases.json`

Contains 15 test questions with reference answers:

```json
[
  {
    "query": "Prove that 3n^2 + 5n + 2 = O(n^2)",
    "reference_answer": "To prove f(n) = O(n^2)...",
    "metadata": {
      "query_type": "proof",
      "topic": "asymptotic_analysis",
      "difficulty": "medium",
      "source": "CLRS Chapter 3"
    }
  },
  ...
]
```

**Coverage:**
- Asymptotic analysis (proofs, comparisons)
- Algorithm complexity (binary search, QuickSort, etc.)
- Recurrence relations (Master Theorem)
- Dynamic programming (0/1 Knapsack, LCS)
- Graph algorithms (BFS, DFS, Dijkstra, Floyd-Warshall)
- NP-completeness (P vs NP, reductions)

**For research paper:**
Expand to 450+ questions covering all 15 topics.

---

## Complete Evaluation Pipeline

See `../scripts/run_evaluation.py` for the orchestration script.

**Pipeline steps:**

1. **Load test cases** from JSON
2. **Run AlgoRAG experiment** (full system)
3. **Run Baseline experiment** (vanilla RAG)
4. **A/B comparison** between systems
5. **Generate visualizations** (all charts)
6. **Export results**:
   - JSON summaries
   - CSV data files
   - LaTeX tables
   - Markdown reports

**Usage:**

```bash
cd ../scripts
python run_evaluation.py --config ../evaluation_config.json
```

**Output structure:**

```
evaluation_results/
├── experiments/
│   ├── algorag_full_20250103_143022.json
│   ├── baseline_rag_20250103_143545.json
│   └── ab_test_algorag_vs_baseline_20250103_144012.json
├── visualizations/
│   ├── algorag_full_quality_metrics.png
│   ├── algorag_full_topic_performance.png
│   ├── algorag_full_timing_breakdown.png
│   ├── baseline_rag_quality_metrics.png
│   └── ab_comparison.png
└── exports/
    ├── evaluation_summary.json
    ├── algorag_results.csv
    ├── baseline_results.csv
    ├── results_table.tex
    └── evaluation_report.md
```

---

## Metrics Reference

### Overall Quality Score

Composite metric combining:
- **30%** BLEU-4 (n-gram precision)
- **20%** ROUGE-L F1 (recall)
- **30%** Pedagogical score (educational quality)
- **20%** Source similarity (retrieval quality)

**Range:** 0.0 to 1.0 (higher is better)

**Target for research paper:** ≥0.85 on standard exam questions

### Pedagogical Score Components

- **30%** Step granularity (number of enumerated steps)
- **30%** Explanation depth (presence of reasoning keywords)
- **15%** Example inclusion (has examples)
- **25%** Mathematical notation richness

For proofs, also includes:
- Proof structure score (statement, steps, conclusion)

### Proof Completeness

- Has clear statement of what's being proved
- Contains logical steps
- Has conclusion (QED, ∴, etc.)
- Uses proper mathematical notation
- Demonstrates logical flow

**Range:** 0.0 to 1.0

---

## Statistical Analysis

After running experiments, use the exported CSVs for statistical testing:

**Python example:**

```python
import pandas as pd
from scipy import stats

algo = pd.read_csv('evaluation_results/exports/algorag_results.csv')
base = pd.read_csv('evaluation_results/exports/baseline_results.csv')

# Paired t-test
t_stat, p_value = stats.ttest_rel(algo['overall_quality'], base['overall_quality'])
print(f"P-value: {p_value:.4f}")

# Effect size
mean_diff = algo['overall_quality'].mean() - base['overall_quality'].mean()
print(f"Mean difference: {mean_diff:.4f}")
```

**R example:**

```R
library(tidyverse)

algo <- read_csv("evaluation_results/exports/algorag_results.csv")
base <- read_csv("evaluation_results/exports/baseline_results.csv")

# T-test
t.test(algo$overall_quality, base$overall_quality, paired = TRUE)

# Effect size
library(effsize)
cohen.d(algo$overall_quality, base$overall_quality)
```

---

## Citation

If you use this evaluation framework, please cite:

```bibtex
@article{algorag2025,
  title={Retrieval-Augmented Generation for Theoretical Computer Science Education:
         A Comprehensive Evaluation Framework for Algorithm Analysis and Complexity Theory},
  author={Your Name},
  journal={Your Journal},
  year={2025}
}
```

---

## License

See main project LICENSE file.

---

## Contributing

For research collaboration or improvements:
1. Fork the repository
2. Create feature branch
3. Add tests for new metrics
4. Submit pull request

---

**Questions?** See `../RESEARCH_GUIDE.md` for detailed usage instructions.
