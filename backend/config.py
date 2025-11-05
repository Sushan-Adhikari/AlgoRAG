"""
Configuration module for AlgoRAG system.
Manages environment variables and system-wide settings.
"""
import os
from typing import Literal
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
VECTOR_DB_DIR = DATA_DIR / "vector_db"

# Ensure directories exist
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# Embedding backend configuration
# Supports: "local" (sentence-transformers), "gemini", "openai"
EMBED_BACKEND: Literal["local", "gemini", "openai"] = os.getenv("EMBED_BACKEND", "local")

# API Keys (optional, depending on backend)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Embedding model configurations
EMBEDDING_CONFIGS = {
    "local": {
        "model_name": "all-mpnet-base-v2",  # 768 dimensions, good quality
        "device": "cpu",  # Change to "cuda" if GPU available
    },
    "gemini": {
        "model_name": "models/text-embedding-004",
        "api_key": GEMINI_API_KEY,
    },
    "openai": {
        "model_name": "text-embedding-3-small",  # 1536 dimensions
        "api_key": OPENAI_API_KEY,
    }
}

# Vector database configuration
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chroma")  # or "qdrant"
COLLECTION_NAME = "algorag_knowledge"

# Retrieval configuration
TOP_K = int(os.getenv("TOP_K", "5"))  # Number of documents to retrieve
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))

# Generator configuration (LLM for answer generation)
GENERATOR_MODEL = os.getenv("GENERATOR_MODEL", "gemini-2.0-flash-exp")
GENERATOR_TEMPERATURE = float(os.getenv("GENERATOR_TEMPERATURE", "0.3"))
GENERATOR_MAX_TOKENS = int(os.getenv("GENERATOR_MAX_TOKENS", "2048"))

# Mathematical entity recognition
MATH_PATTERNS = [
    r"O\([^)]+\)",  # Big-O notation
    r"Ω\([^)]+\)",  # Omega notation
    r"Θ\([^)]+\)",  # Theta notation
    r"o\([^)]+\)",  # Little-o notation
    r"ω\([^)]+\)",  # Little-omega notation
    r"T\([^)]+\)",  # Time complexity notation
    r"S\([^)]+\)",  # Space complexity notation
]

# Pedagogical ranking weights
PEDAGOGICAL_WEIGHTS = {
    "topic_coverage": 0.3,
    "step_granularity": 0.4,
    "difficulty_match": 0.3,
}

# Topics for theoretical CS
TOPICS = [
    "asymptotic_analysis",
    "recurrence_relations",
    "dynamic_programming",
    "graph_algorithms",
    "greedy_algorithms",
    "divide_and_conquer",
    "np_completeness",
    "sorting_algorithms",
    "data_structures",
    "proof_techniques",
]

# Difficulty levels
DIFFICULTY_LEVELS = ["foundation", "conceptual", "application", "advanced"]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
