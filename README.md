# AlgoRAG: RAG for Theoretical Computer Science Education

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A specialized Retrieval-Augmented Generation (RAG) system for teaching and learning theoretical computer science, focusing on **algorithm analysis** and **complexity theory**.

## 🎯 Overview

AlgoRAG addresses key challenges in theoretical computer science education:

- **Personalized Explanations**: Adapts responses to different question formats and difficulty levels
- **Proof Construction**: Provides step-by-step proof guidance with mathematical rigor
- **Complexity Analysis**: Shows detailed complexity calculations and comparisons
- **Mathematical Entity Recognition**: Understands and normalizes complexity notations (O, Ω, Θ)
- **Pedagogical Ranking**: Prioritizes educational value over pure similarity

## 🏗️ Architecture

```
┌─────────────┐
│   Student   │
│   Query     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│          Preprocessing Layer                │
│  • Math entity extraction (O(n), Θ(n²))    │
│  • Query type detection (proof/analysis)    │
│  • Topic extraction                         │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│          Embedding Layer                    │
│  • Local: sentence-transformers (FREE)      │
│  • Cloud: Gemini/OpenAI (PAID)             │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│       Vector Database (ChromaDB/Qdrant)     │
│  • 847 lecture slides                       │
│  • 312 practice problems                    │
│  • 156 proof templates                      │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│       Pedagogical Re-ranking                │
│  • Topic coverage: 30%                      │
│  • Step granularity: 40%                    │
│  • Difficulty match: 30%                    │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│       Answer Generation (LLM)               │
│  • Gemini 2.0 Flash / GPT-4                 │
│  • Proof-aware prompting                    │
│  • Step-by-step explanations                │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Answer    │
│  + Sources  │
└─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+ (for frontend)
- pip and npm

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/algorag.git
cd algorag
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys (optional for local mode)
```

3. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Generate sample data**
```bash
cd ../scripts
python generate_sample_pdfs.py
```

5. **Ingest sample data**
```bash
bash ingest_sample.sh
```

6. **Start the backend server**
```bash
cd ../backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

7. **Install and start frontend** (separate terminal)
```bash
cd frontend
npm install
npm start
```

Visit `http://localhost:3000` to use the application!

## 📊 Usage Examples

### Example 1: Proof Query

**Query**: "Prove that QuickSort has O(n log n) average case time complexity"

**Response**:
```
Proof of QuickSort Average Case Complexity

Let T(n) be the expected time to sort n elements with QuickSort.

Step 1: Recurrence Relation
When we choose a random pivot, the probability that the pivot is the
k-th smallest element is 1/n for each k from 1 to n.

T(n) = (1/n) Σ[k=1 to n] [T(k-1) + T(n-k) + Θ(n)]

The Θ(n) term comes from the partition operation.

Step 2: Simplification
By symmetry: T(k-1) + T(n-k) appears twice for each k
T(n) = (2/n) Σ[k=0 to n-1] T(k) + Θ(n)

Step 3: Solving the Recurrence
We can prove by substitution that T(n) ≤ cn log n for appropriate c.

Base case: T(1) = Θ(1) ✓

Inductive step: Assume T(k) ≤ ck log k for k < n
... [detailed proof steps]

Therefore, T(n) = O(n log n) ∎
```

### Example 2: Complexity Analysis

**Query**: "What is the time complexity of binary search?"

**Response**:
```
Binary Search Time Complexity Analysis

Algorithm: Repeatedly divide search space in half

Recurrence Relation: T(n) = T(n/2) + Θ(1)

Using Master Theorem:
- a = 1 (one recursive call)
- b = 2 (divide by 2)
- f(n) = Θ(1) (constant work)

log_b(a) = log_2(1) = 0
f(n) = Θ(n^0) → Case 2 applies

Result: T(n) = Θ(log n)

Comparison with other search methods:
- Linear Search: O(n)
- Binary Search: O(log n) ← requires sorted array
- Hash Table: O(1) average, O(n) worst
```

## 🧪 Testing

### Run Test Harness
```bash
cd scripts
python test_harness.py
```

This will test:
1. ✅ Embedding generation (local/cloud)
2. ✅ Document ingestion
3. ✅ Retrieval and pedagogical re-ranking
4. ✅ Answer generation

### Run Unit Tests
```bash
cd backend
pytest
```

## 📁 Project Structure

```
algorag/
├── backend/
│   ├── app.py                 # FastAPI server
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Python dependencies
│   └── rag/
│       ├── embeddings.py      # Embedding backends
│       ├── retriever.py       # Vector DB + re-ranking
│       ├── generator.py       # LLM answer generation
│       ├── preprocessing.py   # Math entity extraction
│       └── ingest.py          # Document ingestion
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # React main component
│   │   └── App.css           # Styling
│   └── package.json
├── scripts/
│   ├── generate_sample_pdfs.py
│   ├── ingest_sample.sh
│   └── test_harness.py
├── data/
│   ├── knowledge_base/        # Source documents
│   └── vector_db/             # ChromaDB storage
├── docker-compose.yml
├── .env.example
└── README.md
```

## ⚙️ Configuration

### Embedding Backends

#### Local (FREE, Recommended)
```env
EMBED_BACKEND=local
```
Uses `sentence-transformers` (all-mpnet-base-v2, 768 dims)
- ✅ Free, works offline
- ✅ No API keys needed
- ✅ Good quality

#### Gemini (PAID, Free tier available)
```env
EMBED_BACKEND=gemini
GEMINI_API_KEY=your_key_here
```
Uses Gemini text-embedding-004 (768 dims)
- ~$0.00003 per 1K characters
- Free tier: 15 requests/minute

#### OpenAI (PAID)
```env
EMBED_BACKEND=openai
OPENAI_API_KEY=your_key_here
```
Uses text-embedding-3-small (1536 dims)
- ~$0.00002 per 1K tokens

### Vector Database

#### ChromaDB (Recommended)
```env
VECTOR_DB_TYPE=chroma
```
- ✅ Simple, local
- ✅ No setup required
- Good for development

#### Qdrant
```env
VECTOR_DB_TYPE=qdrant
```
- More features
- Better performance at scale

## 💰 Cost Breakdown

### FREE Configuration (Student Budget)
```env
EMBED_BACKEND=local           # $0
VECTOR_DB_TYPE=chroma          # $0
GENERATOR_MODEL=gemini-2.0-flash-exp  # Free tier available
```

**Estimated monthly cost**: $0 - $5 (depending on usage)

### Production Configuration
```env
EMBED_BACKEND=openai
VECTOR_DB_TYPE=qdrant
GENERATOR_MODEL=gpt-4
```

**Estimated monthly cost**: $50 - $200 (depending on volume)

## 📚 Research Context

This system implements the research proposal:
> "Retrieval-Augmented Generation for Theoretical Computer Science Education:
> A Comprehensive Evaluation Framework for Algorithm Analysis and Complexity Theory"

### Key Innovations

1. **Mathematical Entity Recognition**: Custom preprocessing for complexity notations
2. **Pedagogical Re-ranking**: Prioritizes educational value, not just similarity
3. **Proof-Aware Generation**: Specialized prompting for step-by-step proofs
4. **Multi-Backend Support**: Flexible embedding and LLM backends

### Evaluation Metrics

- Answer Accuracy: Target ≥85% on standard exam questions
- Relevance Score: ROUGE/BLEU against reference answers
- Student Comprehension: Pre/post intervention assessments
- Proof Completeness: All logical steps present

## 🛠️ Development

### Adding New Topics

1. Create documents in `data/knowledge_base/`
2. Run ingestion: `bash scripts/ingest_sample.sh`
3. Update `config.py` with new topic keywords

### Customizing Re-ranking

Edit `backend/rag/retriever.py`:
```python
self.weights = {
    "topic_coverage": 0.3,      # Adjust weights
    "step_granularity": 0.4,
    "difficulty_match": 0.3,
}
```

### Adding New Embeddings Backend

Implement in `backend/rag/embeddings.py`:
```python
def _init_custom(self):
    # Your embedding service initialization
    pass
```

## 🐳 Docker Deployment

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- **Textbooks**: CLRS, Sipser, Kleinberg & Tardos
- **Frameworks**: FastAPI, React, sentence-transformers
- **Vector DBs**: ChromaDB, Qdrant
- **LLMs**: Google Gemini, OpenAI GPT

## 📞 Contact

For questions or collaboration:
- GitHub Issues: [Create an issue](https://github.com/yourusername/algorag/issues)
- Email: your.email@example.com

---

**Built with ❤️ for theoretical computer science education**
