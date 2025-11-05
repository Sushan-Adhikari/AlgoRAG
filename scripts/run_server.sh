#!/bin/bash

# Run AlgoRAG Server

echo "======================================"
echo "Starting AlgoRAG Server"
echo "======================================"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "Project directory: $PROJECT_DIR"
echo ""

# Check if .env exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo "✓ Created .env file. Please edit it with your API keys if needed."
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/backend/venv" ]; then
    echo "Creating virtual environment..."
    cd "$PROJECT_DIR/backend"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✓ Virtual environment created and dependencies installed"
else
    source "$PROJECT_DIR/backend/venv/bin/activate"
fi

# Check if vector DB has data
cd "$PROJECT_DIR/backend"
python -c "
from rag.embeddings import EmbeddingClient
from rag.retriever import Retriever
import config

try:
    emb_client = EmbeddingClient(backend=config.EMBED_BACKEND)
    retriever = Retriever(
        embedding_client=emb_client,
        db_type=config.VECTOR_DB_TYPE,
        db_path=str(config.VECTOR_DB_DIR)
    )
    count = retriever.collection.count()
    print(f'\\nVector DB status: {count} documents indexed')
    if count == 0:
        print('⚠️  No documents in vector database!')
        print('   Run: bash scripts/ingest_sample.sh')
except Exception as e:
    print(f'⚠️  Could not check vector DB: {e}')
"

echo ""
echo "Starting server on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$PROJECT_DIR/backend"
uvicorn app:app --reload --host 0.0.0.0 --port 8000
