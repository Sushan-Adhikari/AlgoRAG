"""
Retriever module for AlgoRAG.
Handles vector database operations and pedagogical re-ranking.
"""
import logging
from typing import List, Dict, Optional, Tuple
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PedagogicalRanker:
    """
    Re-ranks retrieval results based on pedagogical value.
    Considers topic coverage, step granularity, and difficulty matching.
    """

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize ranker with custom weights.

        Args:
            weights: Dictionary with keys:
                - topic_coverage: How well document covers query topics
                - step_granularity: Level of detail in explanations
                - difficulty_match: Match between query and document difficulty
        """
        self.weights = weights or {
            "topic_coverage": 0.3,
            "step_granularity": 0.4,
            "difficulty_match": 0.3,
        }

    def score_topic_coverage(self, query_topics: set, doc_topics: set) -> float:
        """
        Score how well document topics cover query topics.

        Args:
            query_topics: Set of topics extracted from query
            doc_topics: Set of topics in document

        Returns:
            Score from 0 to 1
        """
        if not query_topics:
            return 1.0

        overlap = len(query_topics & doc_topics)
        return overlap / len(query_topics)

    def score_step_granularity(self, doc_metadata: dict, query_type: str) -> float:
        """
        Score the level of detail in document based on query type.

        Args:
            doc_metadata: Document metadata
            query_type: Type of query (proof, analysis, etc.)

        Returns:
            Score from 0 to 1
        """
        # For proof queries, prioritize documents with step-by-step proofs
        if query_type == "proof":
            has_proof = doc_metadata.get("has_proof", False)
            step_count = doc_metadata.get("step_count", 0)

            if has_proof and step_count > 3:
                return 1.0
            elif has_proof:
                return 0.7
            else:
                return 0.3

        # For complexity analysis, prioritize detailed analysis
        elif query_type == "complexity_analysis":
            has_analysis = doc_metadata.get("has_complexity_analysis", False)
            return 1.0 if has_analysis else 0.5

        # Default: moderate granularity
        return 0.6

    def score_difficulty_match(
        self,
        query_difficulty: Optional[str],
        doc_difficulty: Optional[str]
    ) -> float:
        """
        Score how well document difficulty matches query difficulty.

        Args:
            query_difficulty: Estimated query difficulty level
            doc_difficulty: Document difficulty level

        Returns:
            Score from 0 to 1
        """
        difficulty_order = ["foundation", "conceptual", "application", "advanced"]

        if not query_difficulty or not doc_difficulty:
            return 0.5  # Neutral if difficulty unknown

        try:
            query_idx = difficulty_order.index(query_difficulty)
            doc_idx = difficulty_order.index(doc_difficulty)

            # Perfect match
            if query_idx == doc_idx:
                return 1.0

            # Close match (1 level difference)
            elif abs(query_idx - doc_idx) == 1:
                return 0.7

            # Moderate mismatch (2 levels)
            elif abs(query_idx - doc_idx) == 2:
                return 0.4

            # Large mismatch
            else:
                return 0.2

        except ValueError:
            return 0.5

    def compute_pedagogical_score(
        self,
        query_metadata: dict,
        doc_metadata: dict
    ) -> float:
        """
        Compute overall pedagogical score.

        Args:
            query_metadata: Metadata extracted from query
            doc_metadata: Document metadata

        Returns:
            Combined pedagogical score (0 to 1)
        """
        # Extract relevant features
        query_topics = set(query_metadata.get("topics", []))
        doc_topics = set(doc_metadata.get("topics", []))
        query_type = query_metadata.get("query_type", "general")
        query_difficulty = query_metadata.get("difficulty", None)
        doc_difficulty = doc_metadata.get("difficulty_level", None)

        # Compute individual scores
        topic_score = self.score_topic_coverage(query_topics, doc_topics)
        granularity_score = self.score_step_granularity(doc_metadata, query_type)
        difficulty_score = self.score_difficulty_match(query_difficulty, doc_difficulty)

        # Weighted combination
        total_score = (
            self.weights["topic_coverage"] * topic_score +
            self.weights["step_granularity"] * granularity_score +
            self.weights["difficulty_match"] * difficulty_score
        )

        return total_score

    def rerank(
        self,
        query_metadata: dict,
        documents: List[Dict],
        similarity_scores: List[float]
    ) -> List[Tuple[Dict, float, float]]:
        """
        Re-rank documents by combining similarity and pedagogical scores.

        Args:
            query_metadata: Metadata from query
            documents: List of retrieved documents
            similarity_scores: Cosine similarity scores

        Returns:
            List of (document, similarity_score, pedagogical_score) tuples,
            sorted by combined score
        """
        results = []

        for doc, sim_score in zip(documents, similarity_scores):
            doc_metadata = doc.get("metadata", {})
            ped_score = self.compute_pedagogical_score(query_metadata, doc_metadata)

            # Combined score: 70% similarity, 30% pedagogical
            combined_score = 0.7 * sim_score + 0.3 * ped_score

            results.append((doc, sim_score, ped_score, combined_score))

        # Sort by combined score (descending)
        results.sort(key=lambda x: x[3], reverse=True)

        return [(doc, sim, ped) for doc, sim, ped, _ in results]


class Retriever:
    """
    Vector database retriever with pedagogical re-ranking.
    Supports Chroma and Qdrant backends.
    """

    def __init__(
        self,
        embedding_client,
        db_type: str = "chroma",
        db_path: str = "./vector_db",
        collection_name: str = "algorag_knowledge"
    ):
        """
        Initialize retriever.

        Args:
            embedding_client: EmbeddingClient instance
            db_type: "chroma" or "qdrant"
            db_path: Path to vector database
            collection_name: Name of the collection
        """
        self.embedding_client = embedding_client
        self.db_type = db_type
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        self.ranker = PedagogicalRanker()

        # Initialize database
        self.db = None
        self.collection = None
        self._initialize_db()

    def _initialize_db(self):
        """Initialize vector database."""
        if self.db_type == "chroma":
            self._init_chroma()
        elif self.db_type == "qdrant":
            self._init_qdrant()
        else:
            raise ValueError(f"Unsupported db_type: {self.db_type}")

    def _init_chroma(self):
        """Initialize ChromaDB."""
        try:
            import chromadb
            from chromadb.config import Settings

            self.db_path.mkdir(parents=True, exist_ok=True)

            self.db = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)
            )

            # Get or create collection
            self.collection = self.db.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

            logger.info(f"✓ ChromaDB initialized at {self.db_path}")
            logger.info(f"  Collection: {self.collection_name}")
            logger.info(f"  Documents: {self.collection.count()}")

        except ImportError:
            raise ImportError(
                "chromadb not installed. Install with: pip install chromadb"
            )

    def _init_qdrant(self):
        """Initialize Qdrant (local mode)."""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            self.db_path.mkdir(parents=True, exist_ok=True)

            self.db = QdrantClient(path=str(self.db_path))

            # Create collection if it doesn't exist
            collections = self.db.get_collections().collections
            if self.collection_name not in [c.name for c in collections]:
                self.db.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_client.dimension,
                        distance=Distance.COSINE
                    )
                )

            self.collection = self.collection_name

            logger.info(f"✓ Qdrant initialized at {self.db_path}")
            logger.info(f"  Collection: {self.collection_name}")

        except ImportError:
            raise ImportError(
                "qdrant-client not installed. Install with: pip install qdrant-client"
            )

    def retrieve(
        self,
        query: str,
        query_type: str = "general",
        top_k: int = 5,
        query_metadata: dict = None
    ) -> List[Dict]:
        """
        Retrieve and re-rank documents.

        Args:
            query: Query text
            query_type: Type of query (proof, analysis, etc.)
            top_k: Number of documents to retrieve
            query_metadata: Optional metadata for re-ranking

        Returns:
            List of retrieved documents with scores
        """
        # Generate query embedding
        query_embedding = self.embedding_client.embed_text(query)

        # Retrieve from vector DB
        if self.db_type == "chroma":
            results = self._retrieve_chroma(query_embedding, top_k * 2)  # Get more for reranking
        else:
            results = self._retrieve_qdrant(query_embedding, top_k * 2)

        # Prepare query metadata if not provided
        if query_metadata is None:
            from .preprocessing import MathPreprocessor
            preprocessor = MathPreprocessor()
            query_metadata = {
                "query_type": preprocessor.detect_query_type(query),
                "topics": preprocessor.extract_topics(query),
            }

        # Re-rank with pedagogical scoring
        documents, similarities = results
        reranked = self.ranker.rerank(query_metadata, documents, similarities)

        # Return top_k after re-ranking
        return [
            {
                **doc,
                "similarity_score": sim,
                "pedagogical_score": ped,
            }
            for doc, sim, ped in reranked[:top_k]
        ]

    def _retrieve_chroma(
        self,
        query_embedding: np.ndarray,
        top_k: int
    ) -> Tuple[List[Dict], List[float]]:
        """Retrieve from ChromaDB."""
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )

        documents = []
        similarities = []

        if results["documents"]:
            for i, doc_text in enumerate(results["documents"][0]):
                doc = {
                    "content": doc_text,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "id": results["ids"][0][i]
                }
                documents.append(doc)

                # Chroma returns distances, convert to similarity
                distance = results["distances"][0][i]
                similarity = 1 - distance  # Cosine distance to similarity
                similarities.append(similarity)

        return documents, similarities

    def _retrieve_qdrant(
        self,
        query_embedding: np.ndarray,
        top_k: int
    ) -> Tuple[List[Dict], List[float]]:
        """Retrieve from Qdrant."""
        results = self.db.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=top_k
        )

        documents = []
        similarities = []

        for result in results:
            doc = {
                "content": result.payload.get("content", ""),
                "metadata": result.payload.get("metadata", {}),
                "id": result.id
            }
            documents.append(doc)
            similarities.append(result.score)

        return documents, similarities


if __name__ == "__main__":
    # Simple test
    from .embeddings import EmbeddingClient

    print("\n" + "="*60)
    print("Testing Retriever")
    print("="*60)

    # Initialize embedding client
    emb_client = EmbeddingClient(backend="local")

    # Initialize retriever
    retriever = Retriever(
        embedding_client=emb_client,
        db_type="chroma",
        db_path="./test_vector_db"
    )

    print(f"\n✓ Retriever initialized")
    print(f"  Database type: {retriever.db_type}")
    print(f"  Collection: {retriever.collection_name}")
    print(f"  Documents in DB: {retriever.collection.count()}")
