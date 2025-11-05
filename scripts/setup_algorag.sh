#!/bin/bash

# AlgoRAG Complete Setup Script
# This script sets up the entire AlgoRAG system from scratch

set -e  # Exit on error

echo "======================================"
echo "AlgoRAG Complete Setup"
echo "======================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Step 1: Check Python version
echo "Step 1/7: Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    print_step "Python $python_version (>= 3.9 required)"
else
    echo "Error: Python 3.9+ required, found $python_version"
    exit 1
fi

# Step 2: Create virtual environment
echo ""
echo "Step 2/7: Setting up virtual environment..."
cd "$PROJECT_DIR/backend"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_step "Created virtual environment"
else
    print_warning "Virtual environment already exists, skipping"
fi

source venv/bin/activate

# Step 3: Install Python dependencies
echo ""
echo "Step 3/7: Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
print_step "Installed Python packages"

# Step 4: Create .env file
echo ""
echo "Step 4/7: Setting up environment configuration..."
cd "$PROJECT_DIR"

if [ ! -f ".env" ]; then
    cp .env.example .env
    print_step "Created .env file"
    print_warning "IMPORTANT: Edit .env and add your API keys if using cloud backends"
else
    print_warning ".env already exists, skipping"
fi

# Step 5: Generate sample PDFs
echo ""
echo "Step 5/7: Generating sample exam questions..."
cd "$SCRIPT_DIR"

if [ ! -d "sample_pdfs" ] || [ -z "$(ls -A sample_pdfs 2>/dev/null)" ]; then
    python generate_sample_pdfs.py
    print_step "Generated sample PDF datasets"
else
    print_warning "Sample PDFs already exist, skipping"
fi

# Step 6: Ingest sample data
echo ""
echo "Step 6/7: Ingesting sample data into vector database..."

# Check if vector DB has data
cd "$PROJECT_DIR/backend"
source venv/bin/activate

existing_docs=$(python -c "
try:
    from rag.embeddings import EmbeddingClient
    from rag.retriever import Retriever
    import config
    emb_client = EmbeddingClient(backend=config.EMBED_BACKEND)
    retriever = Retriever(
        embedding_client=emb_client,
        db_type=config.VECTOR_DB_TYPE,
        db_path=str(config.VECTOR_DB_DIR)
    )
    print(retriever.collection.count())
except:
    print('0')
" 2>/dev/null)

if [ "$existing_docs" -eq "0" ] || [ -z "$existing_docs" ]; then
    cd "$SCRIPT_DIR"
    bash ingest_sample.sh
    print_step "Ingested sample documents"
else
    print_warning "Vector database already has $existing_docs documents, skipping ingestion"
fi

# Step 7: Install frontend dependencies (optional)
echo ""
echo "Step 7/7: Setting up frontend (optional)..."

if command -v npm &> /dev/null; then
    cd "$PROJECT_DIR/frontend"
    if [ ! -d "node_modules" ]; then
        npm install
        print_step "Installed Node.js dependencies"
    else
        print_warning "node_modules already exists, skipping"
    fi
else
    print_warning "npm not found - skipping frontend setup"
    print_warning "Install Node.js to use the web interface"
fi

# Summary
echo ""
echo "======================================"
echo "Setup Complete! ✅"
echo "======================================"
echo ""
echo "What's been set up:"
echo "  ✓ Python virtual environment"
echo "  ✓ Backend dependencies installed"
echo "  ✓ Environment configuration (.env)"
echo "  ✓ Sample exam questions generated"
echo "  ✓ Vector database populated"
if command -v npm &> /dev/null && [ -d "$PROJECT_DIR/frontend/node_modules" ]; then
    echo "  ✓ Frontend dependencies installed"
fi
echo ""
echo "Next steps:"
echo ""
echo "1. (Optional) Edit .env with your API keys:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2. Start the backend server:"
echo "   cd $PROJECT_DIR/backend"
echo "   source venv/bin/activate"
echo "   uvicorn app:app --reload"
echo ""
echo "   Or use the helper script:"
echo "   bash $SCRIPT_DIR/run_server.sh"
echo ""
if command -v npm &> /dev/null; then
    echo "3. (Optional) Start the frontend (in a new terminal):"
    echo "   cd $PROJECT_DIR/frontend"
    echo "   npm start"
    echo ""
fi
echo "4. Test the system:"
echo "   python $SCRIPT_DIR/test_harness.py"
echo ""
echo "5. Visit the API docs:"
echo "   http://localhost:8000/docs"
echo ""
echo "======================================"
echo "Happy researching! 🎓"
echo "======================================"
