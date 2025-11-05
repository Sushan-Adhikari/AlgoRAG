# AlgoRAG Document Ingestion Guide

Complete guide for ingesting educational materials into the AlgoRAG system for research evaluation.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Ingesting Your Own Documents](#ingesting-your-own-documents)
4. [Verification](#verification)
5. [Advanced Usage](#advanced-usage)
6. [Troubleshooting](#troubleshooting)

---

## Overview

AlgoRAG's knowledge base is built by ingesting PDF documents, text files, and JSON files containing:
- Algorithm textbooks (CLRS, Sedgewick, etc.)
- Lecture slides and notes
- Practice problems with solutions
- Proof examples and templates
- Complexity analysis worksheets

The ingestion pipeline:
1. **Extracts** text from PDFs/documents
2. **Chunks** content into manageable pieces (with overlap)
3. **Enriches** chunks with metadata (topic, difficulty, source)
4. **Embeds** chunks using your chosen embedding backend
5. **Stores** embeddings in ChromaDB vector database

---

## Quick Start

### Using the Provided Sample Documents

The project includes 16 sample documents covering major topics. To ingest them:

```bash
cd /Users/sushan/Desktop/Papers/RAG_Algorithms_and_Complexity/algorag

# Run the ingestion script
bash scripts/ingest_sample.sh
```

**What happens:**
- Scans `scripts/sample_pdfs/` directory
- Processes all PDF files
- Creates embeddings (using backend from `.env`)
- Stores in `data/vector_db/`

**Expected output:**
```
================================================================================
AlgoRAG Knowledge Base Ingestion
================================================================================
Embedding Backend: local
Vector DB Path: /Users/sushan/Desktop/Papers/RAG_Algorithms_and_Complexity/algorag/data/vector_db

Processing documents from: /Users/sushan/Desktop/Papers/RAG_Algorithms_and_Complexity/algorag/scripts/sample_pdfs

✓ Processed: asymptotic_analysis_problems.pdf (15 chunks)
✓ Processed: dynamic_programming_examples.pdf (23 chunks)
...

================================================================================
Ingestion Complete!
Total documents: 16
Total chunks: 342
Embedding dimension: 768
================================================================================
```

---

## Ingesting Your Own Documents

### Step 1: Prepare Your Documents

**Supported formats:**
- PDF (`.pdf`) - textbooks, papers, lecture slides
- Text (`.txt`) - plain text notes
- Markdown (`.md`) - formatted notes
- JSON (`.json`) - structured Q&A pairs

**Recommended structure:**
```
data/knowledge_base/
├── textbooks/
│   ├── CLRS_Chapter3_AsymptoticNotation.pdf
│   ├── CLRS_Chapter4_Recurrences.pdf
│   └── Sedgewick_Algorithms.pdf
├── lecture_slides/
│   ├── Week1_BigO_Notation.pdf
│   ├── Week2_MasterTheorem.pdf
│   └── Week3_DynamicProgramming.pdf
├── practice_problems/
│   ├── Asymptotic_Analysis_Problems.pdf
│   └── DP_Practice_Solutions.pdf
└── proof_templates/
    ├── BigO_Proof_Template.txt
    └── Induction_Proof_Examples.txt
```

### Step 2: Organize by Topic (Optional but Recommended)

For better metadata tagging, organize by topic:

```bash
mkdir -p data/knowledge_base/asymptotic_analysis
mkdir -p data/knowledge_base/dynamic_programming
mkdir -p data/knowledge_base/graph_algorithms
mkdir -p data/knowledge_base/np_completeness
mkdir -p data/knowledge_base/recurrence_relations
```

Then place relevant documents in each folder.

### Step 3: Run Ingestion

**Option A: Ingest a single directory**

```bash
cd backend
python -c "
from rag.ingest import DocumentIngestion
import os

# Set your embedding backend
os.environ['EMBED_BACKEND'] = 'local'  # or 'gemini' or 'openai'

ingester = DocumentIngestion(
    vector_db_path='../data/vector_db',
    collection_name='algorag_knowledge'
)

# Ingest all files from a directory
ingester.ingest_directory(
    directory_path='/path/to/your/documents',
    topic='asymptotic_analysis',  # optional
    difficulty='medium'  # optional
)

print('Ingestion complete!')
"
```

**Option B: Ingest a single file**

```bash
cd backend
python -c "
from rag.ingest import DocumentIngestion
import os

os.environ['EMBED_BACKEND'] = 'local'

ingester = DocumentIngestion(
    vector_db_path='../data/vector_db',
    collection_name='algorag_knowledge'
)

# Ingest single file with metadata
ingester.ingest_file(
    file_path='/path/to/CLRS_Chapter3.pdf',
    metadata={
        'topic': 'asymptotic_analysis',
        'difficulty': 'medium',
        'source': 'CLRS',
        'chapter': 3
    }
)

print('File ingested successfully!')
"
```

**Option C: Batch ingest with custom script**

Create `ingest_custom.py`:

```python
#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from rag.ingest import DocumentIngestion

# Configure
os.environ['EMBED_BACKEND'] = 'local'  # Change as needed

ingester = DocumentIngestion(
    vector_db_path='../data/vector_db',
    collection_name='algorag_knowledge'
)

# Define your document sets
document_sets = [
    {
        'path': 'data/knowledge_base/textbooks',
        'metadata': {'source': 'textbook', 'difficulty': 'medium'}
    },
    {
        'path': 'data/knowledge_base/lecture_slides',
        'metadata': {'source': 'lecture', 'difficulty': 'easy'}
    },
    {
        'path': 'data/knowledge_base/practice_problems',
        'metadata': {'source': 'practice', 'difficulty': 'hard'}
    },
]

# Ingest each set
for doc_set in document_sets:
    print(f"\nIngesting: {doc_set['path']}")
    ingester.ingest_directory(
        directory_path=doc_set['path'],
        **doc_set['metadata']
    )
    print("✓ Complete")

print("\n" + "="*60)
print("All documents ingested successfully!")
print("="*60)
```

Run it:
```bash
python ingest_custom.py
```

### Step 4: Metadata Best Practices

Metadata improves retrieval quality. Use these fields:

```python
metadata = {
    'topic': 'asymptotic_analysis',  # Main topic
    'difficulty': 'medium',  # easy, medium, hard
    'source': 'CLRS',  # Textbook/source name
    'chapter': 3,  # Chapter number
    'page_start': 43,  # Starting page
    'page_end': 58,  # Ending page
    'keywords': ['Big-O', 'complexity', 'proof'],  # Key terms
    'question_type': 'proof',  # proof, algorithm, complexity
}
```

---

## Verification

### Check Document Count

```bash
cd backend
python -c "
from rag.retriever import Retriever
from rag.embeddings import EmbeddingClient

emb_client = EmbeddingClient()
retriever = Retriever(emb_client)

count = retriever.collection.count()
print(f'Total documents in vector DB: {count}')
"
```

### Test Retrieval

```bash
cd backend
python -c "
from rag.retriever import Retriever
from rag.embeddings import EmbeddingClient

emb_client = EmbeddingClient()
retriever = Retriever(emb_client)

# Test query
results = retriever.retrieve(
    query='What is Big-O notation?',
    query_type='conceptual',
    top_k=3
)

print(f'Retrieved {len(results)} documents:')
for i, doc in enumerate(results, 1):
    print(f'{i}. Similarity: {doc[\"similarity\"]:.3f}')
    print(f'   Content: {doc[\"content\"][:100]}...')
    print()
"
```

### View Sample Documents

```bash
cd backend
python -c "
from rag.retriever import Retriever
from rag.embeddings import EmbeddingClient
import json

emb_client = EmbeddingClient()
retriever = Retriever(emb_client)

# Get first 5 documents
results = retriever.collection.get(limit=5)

for i, (doc_id, content, metadata) in enumerate(zip(
    results['ids'],
    results['documents'],
    results['metadatas']
), 1):
    print(f'{i}. ID: {doc_id}')
    print(f'   Metadata: {json.dumps(metadata, indent=2)}')
    print(f'   Content preview: {content[:150]}...')
    print()
"
```

---

## Advanced Usage

### Re-ingesting / Updating Documents

**Clear existing collection and re-ingest:**

```bash
cd backend
python -c "
from rag.ingest import DocumentIngestion
import chromadb

# Delete existing collection
client = chromadb.PersistentClient(path='../data/vector_db')
try:
    client.delete_collection('algorag_knowledge')
    print('Collection deleted')
except:
    print('Collection does not exist')

# Re-ingest
ingester = DocumentIngestion(
    vector_db_path='../data/vector_db',
    collection_name='algorag_knowledge'
)

ingester.ingest_directory('../scripts/sample_pdfs')
print('Re-ingestion complete!')
"
```

### Custom Chunking Parameters

```python
from rag.ingest import DocumentIngestion

ingester = DocumentIngestion(
    vector_db_path='../data/vector_db',
    collection_name='algorag_knowledge',
    chunk_size=1000,  # Tokens per chunk (default: 500)
    chunk_overlap=200  # Overlap between chunks (default: 100)
)
```

Larger chunks preserve more context but reduce granularity.
Smaller chunks improve retrieval precision but may lose context.

### Batch Processing with Progress

```python
from rag.ingest import DocumentIngestion
from pathlib import Path
from tqdm import tqdm

ingester = DocumentIngestion(
    vector_db_path='../data/vector_db',
    collection_name='algorag_knowledge'
)

files = list(Path('data/knowledge_base').rglob('*.pdf'))

for file in tqdm(files, desc='Ingesting'):
    ingester.ingest_file(str(file))
```

### Filtering by Metadata During Retrieval

```python
from rag.retriever import Retriever
from rag.embeddings import EmbeddingClient

emb_client = EmbeddingClient()
retriever = Retriever(emb_client)

# Only retrieve from CLRS textbook
results = retriever.collection.query(
    query_embeddings=[emb_client.embed_query('Big-O notation')],
    n_results=5,
    where={'source': 'CLRS'}  # Metadata filter
)
```

---

## Troubleshooting

### Issue: "No module named 'backend'"

**Solution:** Ensure you're running from the correct directory or add to path:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
```

### Issue: "ChromaDB collection not found"

**Solution:** The collection is created automatically on first ingestion. If it's missing:

```python
from rag.ingest import DocumentIngestion

ingester = DocumentIngestion(
    vector_db_path='../data/vector_db',
    collection_name='algorag_knowledge'
)
# Collection is now created
```

### Issue: PDF extraction fails

**Cause:** Some PDFs have image-based text (scanned documents).

**Solution:** Use OCR preprocessing:

```bash
# Install Tesseract OCR
# macOS:
brew install tesseract

# Then install pytesseract
pip install pytesseract pdf2image
```

Modify ingest to use OCR for scanned PDFs.

### Issue: Embedding generation is slow

**Solutions:**

1. **Use local embeddings** (fastest for small datasets):
   ```bash
   # In .env
   EMBED_BACKEND=local
   ```

2. **Batch processing**: The ingester already batches, but you can adjust:
   ```python
   ingester.ingest_directory(directory_path, batch_size=32)
   ```

3. **Use GPU acceleration** (if available):
   ```python
   # In backend/rag/embeddings.py, modify SentenceTransformer init:
   self.model = SentenceTransformer(model_name, device='cuda')
   ```

### Issue: Running out of disk space

**Solution:** ChromaDB vector storage can grow large. Monitor:

```bash
du -sh data/vector_db/
```

If too large, consider:
- Increasing chunk size (fewer, larger chunks)
- Removing duplicate or low-quality documents
- Using dimension reduction (requires code changes)

### Issue: Retrieval returns irrelevant documents

**Diagnose:**

```python
# Check embedding quality
from rag.embeddings import EmbeddingClient

client = EmbeddingClient()
query_emb = client.embed_query("What is Big-O?")
print(f"Embedding dimension: {len(query_emb)}")
print(f"Sample values: {query_emb[:10]}")
```

**Solutions:**
1. Verify documents are actually ingested (check count)
2. Try different embedding backend (Gemini often better for math)
3. Increase `top_k` in retrieval
4. Add metadata filters to narrow search

---

## Summary

**Standard workflow:**

```bash
# 1. Prepare documents
mkdir -p data/knowledge_base/my_topic
# Copy PDFs to data/knowledge_base/my_topic/

# 2. Configure embedding backend in .env
echo "EMBED_BACKEND=local" >> .env

# 3. Ingest
cd backend
python -c "
from rag.ingest import DocumentIngestion
ingester = DocumentIngestion(vector_db_path='../data/vector_db')
ingester.ingest_directory('../data/knowledge_base/my_topic')
"

# 4. Verify
python -c "
from rag.retriever import Retriever
from rag.embeddings import EmbeddingClient
retriever = Retriever(EmbeddingClient())
print(f'Total docs: {retriever.collection.count()}')
"

# 5. Test query
cd ..
# Start backend: bash scripts/run_server.sh
# Start frontend: cd frontend && npm start
# Visit http://localhost:3000
```

---

## For Research Paper Evaluation

When preparing your dataset for the research paper:

1. **Organize by source type:**
   - `textbooks/` - 3-5 major textbooks (CLRS, Sipser, etc.)
   - `lectures/` - 15+ lecture slide decks
   - `problems/` - 300+ practice problems with solutions
   - `proofs/` - 150+ proof examples

2. **Track ingestion statistics:**
   ```python
   # Log to file for paper
   with open('ingestion_stats.txt', 'w') as f:
       f.write(f"Total documents: {count}\n")
       f.write(f"Total chunks: {chunk_count}\n")
       f.write(f"Average chunks per doc: {chunk_count/count}\n")
   ```

3. **Maintain metadata for analysis:**
   - Record source, topic, difficulty for each document
   - Use consistent taxonomy (15 topics as defined in abstract)

4. **Version control:**
   - Keep ingestion scripts in git
   - Document exact PDF sources and versions
   - Ensure reproducibility

---

**For questions or issues, see the main README.md or open an issue.**
