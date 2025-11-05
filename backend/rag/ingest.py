"""
Ingest module for AlgoRAG.
Handles document ingestion, preprocessing, and indexing into vector database.
"""
import logging
import json
from pathlib import Path
from typing import List, Dict, Optional
import PyPDF2
from tqdm import tqdm

from .preprocessing import MathPreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentIngester:
    """
    Ingests documents from various sources into the vector database.
    Supports: PDF, text files, JSON
    """

    def __init__(self, retriever, preprocessor: Optional[MathPreprocessor] = None):
        """
        Initialize ingester.

        Args:
            retriever: Retriever instance with vector DB
            preprocessor: MathPreprocessor instance
        """
        self.retriever = retriever
        self.preprocessor = preprocessor or MathPreprocessor()
        self.embedding_client = retriever.embedding_client

    def ingest_pdf(self, pdf_path: Path, metadata: dict = None) -> int:
        """
        Ingest a PDF file.

        Args:
            pdf_path: Path to PDF file
            metadata: Optional metadata to attach

        Returns:
            Number of chunks ingested
        """
        logger.info(f"Ingesting PDF: {pdf_path}")

        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)

                documents = []
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()

                    if text.strip():
                        doc = {
                            "content": text,
                            "metadata": {
                                **(metadata or {}),
                                "source_file": str(pdf_path),
                                "page_number": page_num + 1,
                                "total_pages": num_pages,
                            }
                        }
                        documents.append(doc)

                # Chunk and ingest
                chunks = self._chunk_documents(documents)
                return self._ingest_documents(chunks)

        except Exception as e:
            logger.error(f"Failed to ingest PDF {pdf_path}: {e}")
            return 0

    def ingest_text_file(self, text_path: Path, metadata: dict = None) -> int:
        """
        Ingest a text file.

        Args:
            text_path: Path to text file
            metadata: Optional metadata

        Returns:
            Number of chunks ingested
        """
        logger.info(f"Ingesting text file: {text_path}")

        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()

            doc = {
                "content": content,
                "metadata": {
                    **(metadata or {}),
                    "source_file": str(text_path),
                }
            }

            chunks = self._chunk_documents([doc])
            return self._ingest_documents(chunks)

        except Exception as e:
            logger.error(f"Failed to ingest text file {text_path}: {e}")
            return 0

    def ingest_json(self, json_path: Path) -> int:
        """
        Ingest from JSON file.

        Expected format:
        [
            {
                "content": "text content",
                "metadata": {
                    "topic": "...",
                    "difficulty_level": "...",
                    ...
                }
            },
            ...
        ]

        Args:
            json_path: Path to JSON file

        Returns:
            Number of documents ingested
        """
        logger.info(f"Ingesting JSON: {json_path}")

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)

            if not isinstance(documents, list):
                documents = [documents]

            chunks = self._chunk_documents(documents)
            return self._ingest_documents(chunks)

        except Exception as e:
            logger.error(f"Failed to ingest JSON {json_path}: {e}")
            return 0

    def ingest_directory(
        self,
        directory: Path,
        file_types: List[str] = None,
        recursive: bool = True
    ) -> Dict[str, int]:
        """
        Ingest all files from a directory.

        Args:
            directory: Path to directory
            file_types: List of file extensions (e.g., ['.pdf', '.txt'])
            recursive: Whether to search recursively

        Returns:
            Dictionary with statistics
        """
        file_types = file_types or ['.pdf', '.txt', '.json']
        stats = {"total_files": 0, "total_chunks": 0, "failed": 0}

        pattern = "**/*" if recursive else "*"
        files = []

        for ext in file_types:
            files.extend(directory.glob(f"{pattern}{ext}"))

        logger.info(f"Found {len(files)} files in {directory}")

        for file_path in tqdm(files, desc="Ingesting files"):
            stats["total_files"] += 1

            try:
                if file_path.suffix == '.pdf':
                    chunks = self.ingest_pdf(file_path)
                elif file_path.suffix == '.txt':
                    chunks = self.ingest_text_file(file_path)
                elif file_path.suffix == '.json':
                    chunks = self.ingest_json(file_path)
                else:
                    continue

                stats["total_chunks"] += chunks

            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")
                stats["failed"] += 1

        return stats

    def _chunk_documents(
        self,
        documents: List[Dict],
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[Dict]:
        """
        Chunk documents into smaller pieces.

        Args:
            documents: List of documents
            chunk_size: Target chunk size in words
            overlap: Overlap between chunks in words

        Returns:
            List of chunked documents
        """
        chunks = []

        for doc in documents:
            content = doc["content"]
            words = content.split()

            # If document is small enough, don't chunk
            if len(words) <= chunk_size:
                # Enrich with preprocessing
                enriched = self.preprocessor.enrich_document(doc)
                chunks.append(enriched)
                continue

            # Create overlapping chunks
            for i in range(0, len(words), chunk_size - overlap):
                chunk_words = words[i:i + chunk_size]
                chunk_text = " ".join(chunk_words)

                chunk_doc = {
                    "content": chunk_text,
                    "metadata": {
                        **doc.get("metadata", {}),
                        "chunk_index": len(chunks),
                        "is_chunk": True,
                    }
                }

                # Enrich with preprocessing
                enriched = self.preprocessor.enrich_document(chunk_doc)
                chunks.append(enriched)

        return chunks

    def _ingest_documents(self, documents: List[Dict]) -> int:
        """
        Ingest preprocessed documents into vector database.

        Args:
            documents: List of preprocessed documents

        Returns:
            Number of documents ingested
        """
        if not documents:
            return 0

        # Extract texts for embedding
        texts = [doc.get("preprocessed", doc["content"]) for doc in documents]

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedding_client.embed_batch(texts)

        # Ingest into vector DB
        logger.info("Storing in vector database...")

        if self.retriever.db_type == "chroma":
            self._ingest_chroma(documents, embeddings)
        elif self.retriever.db_type == "qdrant":
            self._ingest_qdrant(documents, embeddings)

        logger.info(f"✓ Ingested {len(documents)} documents")
        return len(documents)

    def _ingest_chroma(self, documents: List[Dict], embeddings: List):
        """Ingest into ChromaDB."""
        ids = [f"doc_{i}_{hash(doc['content'])}" for i, doc in enumerate(documents)]
        docs = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        # Convert metadata values to strings (Chroma requirement)
        for metadata in metadatas:
            for key, value in metadata.items():
                if isinstance(value, (list, dict)):
                    metadata[key] = json.dumps(value)
                elif not isinstance(value, (str, int, float, bool)):
                    metadata[key] = str(value)

        self.retriever.collection.add(
            ids=ids,
            documents=docs,
            embeddings=[emb.tolist() for emb in embeddings],
            metadatas=metadatas
        )

    def _ingest_qdrant(self, documents: List[Dict], embeddings: List):
        """Ingest into Qdrant."""
        from qdrant_client.models import PointStruct

        points = []
        for i, (doc, emb) in enumerate(zip(documents, embeddings)):
            point = PointStruct(
                id=i,
                vector=emb.tolist(),
                payload={
                    "content": doc["content"],
                    "metadata": doc.get("metadata", {})
                }
            )
            points.append(point)

        self.retriever.db.upsert(
            collection_name=self.retriever.collection_name,
            points=points
        )


def test_ingestion():
    """Test document ingestion."""
    from .embeddings import EmbeddingClient
    from .retriever import Retriever

    print("\n" + "="*60)
    print("Testing Document Ingestion")
    print("="*60)

    # Initialize components
    emb_client = EmbeddingClient(backend="local")
    retriever = Retriever(
        embedding_client=emb_client,
        db_type="chroma",
        db_path="./test_vector_db"
    )
    ingester = DocumentIngester(retriever)

    # Create sample document
    sample_doc = {
        "content": """
        QuickSort Algorithm Analysis

        QuickSort is a divide-and-conquer sorting algorithm.

        Time Complexity:
        - Best case: O(n log n)
        - Average case: O(n log n)
        - Worst case: O(n^2)

        The worst case occurs when the pivot is always the smallest or largest element.

        Proof (Average Case):
        Let T(n) be the average time to sort n elements.
        T(n) = T(k) + T(n-k-1) + O(n)
        where k is the position of the pivot.

        Using the master theorem, we can show T(n) = O(n log n).
        """,
        "metadata": {
            "topic": "sorting_algorithms",
            "difficulty_level": "conceptual",
            "source_textbook": "CLRS",
        }
    }

    # Ingest
    chunks = ingester._chunk_documents([sample_doc])
    num_ingested = ingester._ingest_documents(chunks)

    print(f"\n✓ Ingested {num_ingested} chunks")
    print(f"  Total documents in DB: {retriever.collection.count()}")

    # Test retrieval
    print("\nTesting retrieval...")
    query = "What is the time complexity of quicksort?"
    results = retriever.retrieve(query, top_k=3)

    print(f"\nQuery: {query}")
    print(f"Retrieved {len(results)} documents:")

    for i, doc in enumerate(results, 1):
        print(f"\n{i}. Similarity: {doc['similarity_score']:.3f}, "
              f"Pedagogical: {doc['pedagogical_score']:.3f}")
        print(f"   {doc['content'][:150]}...")


if __name__ == "__main__":
    test_ingestion()
