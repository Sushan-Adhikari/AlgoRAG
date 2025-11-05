"""
AlgoRAG - RAG components for theoretical computer science education.
"""

from .embeddings import EmbeddingClient
from .retriever import Retriever, PedagogicalRanker
from .generator import Generator
from .preprocessing import MathPreprocessor
from .ingest import DocumentIngester

__all__ = [
    'EmbeddingClient',
    'Retriever',
    'PedagogicalRanker',
    'Generator',
    'MathPreprocessor',
    'DocumentIngester',
]

__version__ = '1.0.0'
