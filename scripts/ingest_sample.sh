#!/bin/bash

# Ingest sample PDFs into AlgoRAG vector database

echo "======================================"
echo "AlgoRAG Sample Data Ingestion"
echo "======================================"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "Project directory: $PROJECT_DIR"
echo "Sample PDFs directory: $SCRIPT_DIR/sample_pdfs"
echo ""

# Check if sample PDFs exist
if [ ! -d "$SCRIPT_DIR/sample_pdfs" ]; then
    echo "Sample PDFs not found. Generating..."
    cd "$SCRIPT_DIR"
    python generate_sample_pdfs.py
fi

# Run ingest script
echo ""
echo "Starting ingestion..."
cd "$PROJECT_DIR/backend"

python -c "
import sys
sys.path.insert(0, '.')

from pathlib import Path
from rag.embeddings import EmbeddingClient
from rag.retriever import Retriever
from rag.ingest import DocumentIngester
import config

print('\\nInitializing components...')
emb_client = EmbeddingClient(backend=config.EMBED_BACKEND)
retriever = Retriever(
    embedding_client=emb_client,
    db_type=config.VECTOR_DB_TYPE,
    db_path=str(config.VECTOR_DB_DIR)
)
ingester = DocumentIngester(retriever)

print('\\nIngesting sample PDFs...')
sample_dir = Path('$SCRIPT_DIR/sample_pdfs')
stats = ingester.ingest_directory(sample_dir, file_types=['.pdf'])

print('\\n' + '='*60)
print('Ingestion Complete')
print('='*60)
print(f'Files processed: {stats[\"total_files\"]}')
print(f'Chunks created: {stats[\"total_chunks\"]}')
print(f'Failed: {stats[\"failed\"]}')
print(f'Total documents in DB: {retriever.collection.count()}')
print('='*60)
"

echo ""
echo "✓ Ingestion complete!"
