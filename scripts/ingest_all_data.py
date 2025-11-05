#!/usr/bin/env python3
"""
Comprehensive data ingestion script for AlgoRAG research project.
Ingests all PDFs and text files from the knowledge base into the vector database.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import logging
from rag.embeddings import EmbeddingClient
from rag.retriever import Retriever
from rag.ingest import DocumentIngester
from rag.preprocessing import MathPreprocessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ingest_all_data(
    knowledge_base_dir: Path,
    vector_db_path: Path,
    embedding_backend: str = "local",
    db_type: str = "chroma"
):
    """
    Ingest all data from knowledge base.

    Args:
        knowledge_base_dir: Path to knowledge base directory
        vector_db_path: Path to vector database
        embedding_backend: Embedding backend (local, gemini, openai)
        db_type: Vector DB type (chroma, qdrant)
    """
    logger.info("="*80)
    logger.info("AlgoRAG Data Ingestion - Research Project")
    logger.info("="*80)

    # Initialize components
    logger.info(f"Initializing with embedding backend: {embedding_backend}")
    emb_client = EmbeddingClient(backend=embedding_backend)

    logger.info(f"Initializing vector database: {db_type} at {vector_db_path}")
    retriever = Retriever(
        embedding_client=emb_client,
        db_type=db_type,
        db_path=str(vector_db_path)
    )

    preprocessor = MathPreprocessor()
    ingester = DocumentIngester(retriever, preprocessor)

    # Define data categories and their metadata
    data_categories = {
        "textbooks": {
            "path": knowledge_base_dir / "textbooks",
            "metadata": {
                "category": "textbook",
                "pedagogical_value": "high",
                "content_type": "comprehensive"
            }
        },
        "lecture_slides": {
            "path": knowledge_base_dir / "lecture_slides",
            "metadata": {
                "category": "lecture_slides",
                "pedagogical_value": "high",
                "content_type": "instructional"
            }
        },
        "practice_problems": {
            "path": knowledge_base_dir / "practice_problems",
            "metadata": {
                "category": "practice_problems",
                "pedagogical_value": "very_high",
                "content_type": "problems_solutions"
            }
        },
        "proofs": {
            "path": knowledge_base_dir / "proofs",
            "metadata": {
                "category": "proof_examples",
                "pedagogical_value": "very_high",
                "content_type": "proof_templates"
            }
        },
        "worksheets": {
            "path": knowledge_base_dir / "worksheets",
            "metadata": {
                "category": "complexity_analysis",
                "pedagogical_value": "high",
                "content_type": "worksheets"
            }
        }
    }

    # Ingest each category
    total_stats = {
        "total_files": 0,
        "total_chunks": 0,
        "failed": 0
    }

    for category_name, category_info in data_categories.items():
        category_path = category_info["path"]

        if not category_path.exists():
            logger.warning(f"Category directory not found: {category_path}")
            continue

        logger.info("\n" + "="*80)
        logger.info(f"Ingesting category: {category_name}")
        logger.info(f"Path: {category_path}")
        logger.info("="*80)

        # Get all files in category
        pdf_files = list(category_path.glob("*.pdf"))
        txt_files = list(category_path.glob("*.txt"))
        json_files = list(category_path.glob("*.json"))

        logger.info(f"Found {len(pdf_files)} PDFs, {len(txt_files)} TXT files, "
                   f"{len(json_files)} JSON files")

        # Ingest PDFs
        for pdf_file in pdf_files:
            try:
                logger.info(f"\nIngesting PDF: {pdf_file.name}")
                metadata = {
                    **category_info["metadata"],
                    "filename": pdf_file.name,
                    "category_name": category_name
                }
                chunks = ingester.ingest_pdf(pdf_file, metadata)
                total_stats["total_files"] += 1
                total_stats["total_chunks"] += chunks
                logger.info(f"✓ Ingested {chunks} chunks from {pdf_file.name}")
            except Exception as e:
                logger.error(f"✗ Failed to ingest {pdf_file.name}: {e}")
                total_stats["failed"] += 1

        # Ingest TXT files
        for txt_file in txt_files:
            try:
                logger.info(f"\nIngesting TXT: {txt_file.name}")
                metadata = {
                    **category_info["metadata"],
                    "filename": txt_file.name,
                    "category_name": category_name
                }
                chunks = ingester.ingest_text_file(txt_file, metadata)
                total_stats["total_files"] += 1
                total_stats["total_chunks"] += chunks
                logger.info(f"✓ Ingested {chunks} chunks from {txt_file.name}")
            except Exception as e:
                logger.error(f"✗ Failed to ingest {txt_file.name}: {e}")
                total_stats["failed"] += 1

        # Ingest JSON files
        for json_file in json_files:
            try:
                logger.info(f"\nIngesting JSON: {json_file.name}")
                chunks = ingester.ingest_json(json_file)
                total_stats["total_files"] += 1
                total_stats["total_chunks"] += chunks
                logger.info(f"✓ Ingested {chunks} chunks from {json_file.name}")
            except Exception as e:
                logger.error(f"✗ Failed to ingest {json_file.name}: {e}")
                total_stats["failed"] += 1

    # Final statistics
    logger.info("\n" + "="*80)
    logger.info("INGESTION COMPLETE")
    logger.info("="*80)
    logger.info(f"Total files processed: {total_stats['total_files']}")
    logger.info(f"Total chunks ingested: {total_stats['total_chunks']}")
    logger.info(f"Failed files: {total_stats['failed']}")

    # Verify database
    try:
        if db_type == "chroma":
            count = retriever.collection.count()
        else:
            count = total_stats['total_chunks']
        logger.info(f"\nVector database now contains: {count} documents")
    except Exception as e:
        logger.error(f"Could not verify database count: {e}")

    logger.info("\n✓ Data ingestion complete!")
    logger.info("The system is now ready for evaluation.")

    return total_stats


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Ingest all data for AlgoRAG research project"
    )
    parser.add_argument(
        "--knowledge-base",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "knowledge_base",
        help="Path to knowledge base directory"
    )
    parser.add_argument(
        "--vector-db",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "vector_db",
        help="Path to vector database"
    )
    parser.add_argument(
        "--embedding-backend",
        choices=["local", "gemini", "openai"],
        default="local",
        help="Embedding backend to use"
    )
    parser.add_argument(
        "--db-type",
        choices=["chroma", "qdrant"],
        default="chroma",
        help="Vector database type"
    )

    args = parser.parse_args()

    # Validate paths
    if not args.knowledge_base.exists():
        logger.error(f"Knowledge base directory not found: {args.knowledge_base}")
        sys.exit(1)

    # Create vector DB directory if needed
    args.vector_db.mkdir(parents=True, exist_ok=True)

    # Run ingestion
    try:
        stats = ingest_all_data(
            knowledge_base_dir=args.knowledge_base,
            vector_db_path=args.vector_db,
            embedding_backend=args.embedding_backend,
            db_type=args.db_type
        )

        logger.info(f"\n✓ SUCCESS: Ingested {stats['total_chunks']} chunks "
                   f"from {stats['total_files']} files")

        if stats['failed'] > 0:
            logger.warning(f"⚠ {stats['failed']} files failed to ingest")
            sys.exit(1)

    except Exception as e:
        logger.error(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
