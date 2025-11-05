"""
Evaluation Framework for AlgoRAG Research

This module provides comprehensive evaluation tools for the research paper.
"""

from .metrics import EvaluationMetrics, quick_evaluate
from .experiment_runner import ExperimentRunner, Experiment
from .baseline_comparison import BaselineRAG, compare_systems

__all__ = [
    'EvaluationMetrics',
    'quick_evaluate',
    'ExperimentRunner',
    'Experiment',
    'BaselineRAG',
    'compare_systems'
]
