#!/usr/bin/env python3
"""
Quick test of evaluation system - tests just 2 questions
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from evaluation.experiment_runner import ExperimentRunner, Experiment
from pathlib import Path
import json

# Load test cases
test_file = Path(__file__).parent.parent / 'evaluation' / 'test_datasets' / 'sample_test_cases.json'

with open(test_file) as f:
    all_cases = json.load(f)

# Use only first 2 test cases for quick test
test_cases = all_cases[:2]

print("\n" + "="*60)
print("AlgoRAG Quick Evaluation Test")
print("="*60)
print(f"Testing {len(test_cases)} cases")
print("="*60 + "\n")

# Create experiment
experiment = Experiment(
    experiment_id="quick_test",
    name="Quick Test",
    description="Quick test with 2 cases",
    embed_backend="local",
    generator_model="gemini-2.0-flash-exp",
    top_k=3
)

# Run experiment
runner = ExperimentRunner(output_dir='./eval_quick_test')
results = runner.run_experiment(experiment, test_cases)

print("\n" + "="*60)
print("RESULTS")
print("="*60)
print(f"Average Quality: {results['avg_overall_quality']:.2f}")
print(f"Average BLEU: {results['avg_bleu']:.2f}")
print(f"Average ROUGE-L: {results['avg_rouge_l']:.2f}")
print(f"Average Time: {results['avg_latency']:.2f}s")
print("="*60)
print("\n✅ Evaluation system is working!")
