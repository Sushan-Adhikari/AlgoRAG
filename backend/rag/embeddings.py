"""
Embeddings module for AlgoRAG.
Supports multiple embedding backends: local (sentence-transformers), Gemini, OpenAI
"""
import os
import logging
from typing import List, Optional
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingClient:
    """
    Unified embedding client that supports multiple backends.
    Automatically falls back to local if remote services fail.
    """

    def __init__(self, backend: str = "local", config: dict = None):
        """
        Initialize embedding client.

        Args:
            backend: One of "local", "gemini", "openai"
            config: Configuration dictionary for the backend
        """
        self.backend = backend
        self.config = config or {}
        self.model = None
        self.dimension = None

        # Initialize the appropriate backend
        self._initialize_backend()

    def _initialize_backend(self):
        """Initialize the selected embedding backend with fallback."""
        try:
            if self.backend == "local":
                self._init_local()
            elif self.backend == "gemini":
                self._init_gemini()
            elif self.backend == "openai":
                self._init_openai()
            else:
                logger.warning(f"Unknown backend '{self.backend}', falling back to local")
                self._init_local()
        except Exception as e:
            logger.error(f"Failed to initialize {self.backend} backend: {e}")
            logger.info("Falling back to local embedding model")
            self._init_local()

    def _init_local(self):
        """Initialize local sentence-transformers model (FREE)."""
        try:
            from sentence_transformers import SentenceTransformer

            model_name = self.config.get("model_name", "all-mpnet-base-v2")
            device = self.config.get("device", "cpu")

            logger.info(f"Loading local model: {model_name} on {device}")
            self.model = SentenceTransformer(model_name, device=device)
            self.dimension = self.model.get_sentence_embedding_dimension()
            self.backend = "local"

            logger.info(f"✓ Local embedding model loaded (dimension: {self.dimension})")

        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

    def _init_gemini(self):
        """Initialize Gemini embedding model (PAID - with free tier)."""
        try:
            from google import genai

            api_key = self.config.get("api_key") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in config or environment")

            self.model = genai.Client(api_key=api_key)
            model_name = self.config.get("model_name", "models/text-embedding-004")
            self.model_name = model_name

            # Gemini text-embedding-004 has 768 dimensions
            self.dimension = 768
            self.backend = "gemini"

            logger.info(f"✓ Gemini embedding initialized (model: {model_name})")
            logger.warning("⚠️  Gemini API is a paid service (with free tier)")

        except ImportError:
            raise ImportError(
                "google-genai not installed. "
                "Install with: pip install google-genai"
            )

    def _init_openai(self):
        """Initialize OpenAI embedding model (PAID)."""
        try:
            from openai import OpenAI

            api_key = self.config.get("api_key") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in config or environment")

            self.model = OpenAI(api_key=api_key)
            model_name = self.config.get("model_name", "text-embedding-3-small")
            self.model_name = model_name

            # text-embedding-3-small has 1536 dimensions
            self.dimension = 1536
            self.backend = "openai"

            logger.info(f"✓ OpenAI embedding initialized (model: {model_name})")
            logger.warning("⚠️  OpenAI API is a paid service")

        except ImportError:
            raise ImportError(
                "openai not installed. "
                "Install with: pip install openai"
            )

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            Numpy array of embeddings
        """
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of numpy arrays (embeddings)
        """
        if not texts:
            return []

        try:
            if self.backend == "local":
                return self._embed_local(texts)
            elif self.backend == "gemini":
                return self._embed_gemini(texts)
            elif self.backend == "openai":
                return self._embed_openai(texts)
        except Exception as e:
            logger.error(f"Embedding failed with {self.backend}: {e}")
            logger.info("Attempting fallback to local model")

            # Fallback to local
            if self.backend != "local":
                self._init_local()
                return self._embed_local(texts)
            raise

    def _embed_local(self, texts: List[str]) -> List[np.ndarray]:
        """Embed using local sentence-transformers."""
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10
        )
        return [emb for emb in embeddings]

    def _embed_gemini(self, texts: List[str]) -> List[np.ndarray]:
        """Embed using Gemini API."""
        embeddings = []

        # Gemini supports batch embedding
        for text in texts:
            result = self.model.models.embed_content(
                model=self.model_name,
                content=text
            )
            embeddings.append(np.array(result.embeddings[0].values))

        return embeddings

    def _embed_openai(self, texts: List[str]) -> List[np.ndarray]:
        """Embed using OpenAI API."""
        response = self.model.embeddings.create(
            input=texts,
            model=self.model_name
        )

        embeddings = [
            np.array(item.embedding)
            for item in response.data
        ]

        return embeddings

    def get_info(self) -> dict:
        """Get information about the current embedding backend."""
        return {
            "backend": self.backend,
            "dimension": self.dimension,
            "config": self.config
        }


def test_embedding_backends():
    """Test function to verify all embedding backends."""
    test_texts = [
        "What is the time complexity of quicksort?",
        "Prove that the halting problem is undecidable.",
        "Explain the master theorem for recurrence relations."
    ]

    print("\n" + "="*60)
    print("Testing Embedding Backends")
    print("="*60)

    # Test local (always works)
    print("\n1. Testing LOCAL (sentence-transformers) - FREE")
    print("-" * 60)
    try:
        client = EmbeddingClient(backend="local")
        embeddings = client.embed_batch(test_texts)
        print(f"✓ Success: Generated {len(embeddings)} embeddings")
        print(f"  Dimension: {len(embeddings[0])}")
        print(f"  Info: {client.get_info()}")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test Gemini (if API key available)
    print("\n2. Testing GEMINI - PAID (with free tier)")
    print("-" * 60)
    if os.getenv("GEMINI_API_KEY"):
        try:
            client = EmbeddingClient(backend="gemini")
            embeddings = client.embed_batch(test_texts[:1])  # Test with 1 to save quota
            print(f"✓ Success: Generated {len(embeddings)} embeddings")
            print(f"  Dimension: {len(embeddings[0])}")
            print(f"  Cost: ~$0.00003 per 1000 chars (free tier: 15 RPM)")
        except Exception as e:
            print(f"✗ Failed: {e}")
    else:
        print("  ⊘ Skipped: GEMINI_API_KEY not found")

    # Test OpenAI (if API key available)
    print("\n3. Testing OPENAI - PAID")
    print("-" * 60)
    if os.getenv("OPENAI_API_KEY"):
        try:
            client = EmbeddingClient(backend="openai")
            embeddings = client.embed_batch(test_texts[:1])  # Test with 1 to save quota
            print(f"✓ Success: Generated {len(embeddings)} embeddings")
            print(f"  Dimension: {len(embeddings[0])}")
            print(f"  Cost: ~$0.00002 per 1000 tokens")
        except Exception as e:
            print(f"✗ Failed: {e}")
    else:
        print("  ⊘ Skipped: OPENAI_API_KEY not found")

    print("\n" + "="*60)
    print("RECOMMENDATION: Use 'local' backend (FREE, works offline)")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Run tests
    test_embedding_backends()
