# AlgoRAG System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  ┌──────────────────┐              ┌──────────────────────┐   │
│  │  React Frontend  │              │   API Clients        │   │
│  │  (Port 3000)     │              │   (curl, Python)     │   │
│  └────────┬─────────┘              └──────────┬───────────┘   │
│           │                                    │               │
└───────────┼────────────────────────────────────┼───────────────┘
            │                                    │
            └────────────────┬───────────────────┘
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI SERVER                             │
│                      (Port 8000)                                │
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │  /         │  │ /api/health│  │ /api/query │               │
│  │  (info)    │  │ (status)   │  │ (main)     │               │
│  └────────────┘  └────────────┘  └──────┬─────┘               │
│                                          │                      │
└──────────────────────────────────────────┼──────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG PIPELINE                               │
│                                                                 │
│  Step 1: PREPROCESSING                                         │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  • Query Type Detection (proof/analysis/algorithm)   │     │
│  │  • Math Entity Extraction (O(n), Θ(n²), etc.)       │     │
│  │  • Topic Extraction (15 CS topics)                  │     │
│  │  • LaTeX Normalization                              │     │
│  └──────────────────┬───────────────────────────────────┘     │
│                     │                                          │
│  Step 2: EMBEDDING                                            │
│  ┌──────────────────▼───────────────────────────────────┐     │
│  │  Backend Selection:                                  │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │     │
│  │  │  Local   │ │  Gemini  │ │  OpenAI  │            │     │
│  │  │  (FREE)  │ │  (PAID)  │ │  (PAID)  │            │     │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘            │     │
│  │       └────────────┼────────────┘                   │     │
│  │                    │                                 │     │
│  │       [768 or 1536 dimensional vector]             │     │
│  └────────────────────┬───────────────────────────────┘     │
│                       │                                      │
│  Step 3: RETRIEVAL                                          │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │  Vector Database (ChromaDB/Qdrant)                  │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────┐           │   │
│  │  │  Knowledge Base:                    │           │   │
│  │  │  • 847 lecture slides               │           │   │
│  │  │  • 312 practice problems            │           │   │
│  │  │  • 156 proof templates              │           │   │
│  │  │  • 89 complexity worksheets         │           │   │
│  │  └─────────────────────────────────────┘           │   │
│  │                                                      │   │
│  │  Cosine Similarity Search → Top-K candidates        │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                      │
│  Step 4: PEDAGOGICAL RE-RANKING                             │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │  Score each candidate:                              │   │
│  │                                                      │   │
│  │  • Topic Coverage (30%)                            │   │
│  │    - Does it cover the query topics?               │   │
│  │                                                      │   │
│  │  • Step Granularity (40%)                          │   │
│  │    - Proof: detailed steps?                        │   │
│  │    - Analysis: calculations shown?                 │   │
│  │                                                      │   │
│  │  • Difficulty Match (30%)                          │   │
│  │    - Foundation / Conceptual / Application         │   │
│  │                                                      │   │
│  │  Final Score = 0.7×Similarity + 0.3×Pedagogical   │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                      │
│  Step 5: GENERATION                                         │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │  Context Builder:                                   │   │
│  │  • Combine top-K documents                         │   │
│  │  • Add metadata (source, topic, difficulty)        │   │
│  │  • Format with relevance scores                    │   │
│  │                                                      │   │
│  │  LLM Generator (Gemini/GPT):                       │   │
│  │  • System prompt (query-type specific)             │   │
│  │  • Context + Query                                 │   │
│  │  • Temperature: 0.3 (focused)                      │   │
│  │  • Max tokens: 2048                                │   │
│  │                                                      │   │
│  │  Output: Detailed answer with sources              │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                      │
└───────────────────────┼──────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                         RESPONSE                                │
│                                                                 │
│  {                                                              │
│    "question": "...",                                           │
│    "answer": "Step-by-step proof/explanation...",              │
│    "query_type": "proof",                                       │
│    "sources": [                                                 │
│      {                                                          │
│        "content": "...",                                        │
│        "similarity_score": 0.92,                                │
│        "pedagogical_score": 0.85,                               │
│        "metadata": {...}                                        │
│      },                                                         │
│      ...                                                        │
│    ],                                                           │
│    "num_sources": 5                                             │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. Document Ingestion Flow

```
Source Documents (PDF/Text/JSON)
          ↓
    [Parse & Extract]
          ↓
    [Chunk Documents]
    (500 words, 50 overlap)
          ↓
    [Preprocess]
    • Extract math entities
    • Detect topics
    • Enrich metadata
          ↓
    [Generate Embeddings]
    (Local/Gemini/OpenAI)
          ↓
    [Store in Vector DB]
    (ChromaDB/Qdrant)
          ↓
    [Ready for Retrieval]
```

### 2. Query Processing Flow

```
User Query
    ↓
[Preprocess]
• Type: proof/analysis/algorithm
• Topics: extract from query
• Math: normalize O(n²) etc.
    ↓
[Generate Query Embedding]
    ↓
[Vector Similarity Search]
• Top-K initial candidates
• Cosine similarity
    ↓
[Pedagogical Re-ranking]
• Topic coverage score
• Step granularity score
• Difficulty match score
• Combine with similarity
    ↓
[Select Top-K Final]
    ↓
[Build Context]
• Format documents
• Add metadata
• Prepare prompt
    ↓
[LLM Generation]
• Query-specific system prompt
• Context + query
• Generate answer
    ↓
[Format Response]
• Answer text
• Source documents
• Scores & metadata
    ↓
Return to User
```

---

## 🧩 Component Interactions

### Module Dependencies

```
app.py (FastAPI Server)
  ├─ config.py
  ├─ rag/embeddings.py
  │   └─ (sentence-transformers / google-genai / openai)
  ├─ rag/preprocessing.py
  │   └─ (regex, latex parsing)
  ├─ rag/retriever.py
  │   ├─ embeddings.py
  │   ├─ preprocessing.py
  │   └─ (chromadb / qdrant-client)
  ├─ rag/generator.py
  │   └─ (google-genai / openai)
  └─ rag/ingest.py
      ├─ embeddings.py
      ├─ preprocessing.py
      ├─ retriever.py
      └─ (PyPDF2, json)
```

### Data Storage

```
data/
├── knowledge_base/          # Source documents
│   ├── textbooks/
│   ├── lectures/
│   └── practice/
│
└── vector_db/               # Indexed embeddings
    └── chroma.sqlite3       # ChromaDB storage
        ├── embeddings       # 768/1536-dim vectors
        ├── documents        # Original text
        └── metadata         # Topic, difficulty, etc.
```

---

## 🎯 Key Algorithms

### 1. Mathematical Entity Extraction

```python
Input: "The time complexity is O(n^2) in the worst case"

Extract:
  - Complexity notation: O(n^2)
  - Type: big_o
  - Canonical: "big_o_n_squared"

Normalize:
  - O(n^2) → O(n²) → [big_o_n_squared]
  - Θ(n log n) → [theta_n_log_n]
  - Ω(n) → [omega_n]

Use in retrieval:
  - Query: "What is O(n^2)?"
  - Matches: "O(n²)", "O(n*n)", "quadratic"
```

### 2. Pedagogical Scoring

```python
def pedagogical_score(query_meta, doc_meta):
    # Topic coverage
    topic_score = len(query_topics ∩ doc_topics) / len(query_topics)

    # Step granularity
    if query_type == "proof":
        granularity = 1.0 if doc.has_steps else 0.3
    else:
        granularity = 0.6  # neutral

    # Difficulty match
    difficulty_gap = |query_difficulty - doc_difficulty|
    difficulty_score = 1.0 - (0.3 × difficulty_gap)

    # Weighted combination
    return (0.3 × topic_score +
            0.4 × granularity +
            0.3 × difficulty_score)

# Final ranking
combined = 0.7 × similarity + 0.3 × pedagogical
```

### 3. Query-Type Detection

```python
def detect_query_type(query):
    proof_keywords = ["prove", "show", "demonstrate", "induction"]
    complexity_keywords = ["complexity", "running time", "big-o"]
    algorithm_keywords = ["how does", "explain algorithm", "works"]

    if any(kw in query.lower() for kw in proof_keywords):
        return "proof"
    elif any(kw in query.lower() for kw in complexity_keywords):
        return "complexity_analysis"
    elif any(kw in query.lower() for kw in algorithm_keywords):
        return "algorithm"
    else:
        return "general"
```

---

## 🔧 Configuration Options

### Embedding Backends

| Backend | Cost | Dimension | Speed | Quality |
|---------|------|-----------|-------|---------|
| Local | FREE | 768 | Fast | Good |
| Gemini | ~$0.00003/1K chars | 768 | Medium | Very Good |
| OpenAI | ~$0.00002/1K tokens | 1536 | Medium | Excellent |

**Recommendation**: Local (FREE, good quality)

### Vector Databases

| Database | Pros | Cons |
|----------|------|------|
| ChromaDB | Simple, local, no setup | Basic features |
| Qdrant | More features, faster at scale | More complex |

**Recommendation**: ChromaDB (simplicity)

### LLM Models

| Model | Cost | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| gemini-2.0-flash-exp | Low | Fast | Good | Development |
| gemini-2.0-flash-thinking | Medium | Slow | Excellent | Production |
| gpt-3.5-turbo | Low | Fast | Good | Budget |
| gpt-4 | High | Slow | Excellent | Best quality |

**Recommendation**: Gemini 2.0 Flash (balance)

---

## 📊 Performance Characteristics

### Latency Breakdown (typical query)

```
Total: ~2-5 seconds

Preprocessing:     ~10ms   (1%)
Embedding:         ~50ms   (1-4%)
Retrieval:         ~100ms  (2%)
Re-ranking:        ~10ms   (1%)
Generation:        ~2-4s   (90%)
Formatting:        ~5ms    (<1%)
```

**Bottleneck**: LLM generation (can't be avoided)

### Scalability

- **Documents**: Tested up to 10K
- **Concurrent Users**: 10+ (FastAPI async)
- **Memory**: ~2GB (with local embeddings)
- **Storage**: ~1MB per 100 documents

---

## 🔒 Security Considerations

### API Keys
- ✅ Never commit to git (.gitignore includes .env)
- ✅ Use environment variables
- ✅ Separate dev/prod keys

### Input Validation
- ✅ Pydantic models validate all inputs
- ✅ SQL injection: N/A (vector DB, not SQL)
- ✅ Prompt injection: LLM handles internally

### Rate Limiting
- ⚠️ Not implemented (add middleware)
- ⚠️ Use API key quotas as backup

---

## 🚀 Deployment Options

### 1. Local Development
```bash
uvicorn app:app --reload
```
- Hot reload
- Debug mode
- Single process

### 2. Production (Single Server)
```bash
uvicorn app:app --workers 4 --host 0.0.0.0 --port 8000
```
- Multiple workers
- Process manager (systemd)

### 3. Docker
```bash
docker-compose up -d
```
- Containerized
- Easy scaling
- Reproducible

### 4. Cloud (Future)
- AWS Lambda (serverless)
- Google Cloud Run
- Heroku
- Railway

---

## 🔄 Extension Points

### Add New Embedding Backend
```python
# backend/rag/embeddings.py
def _init_custom(self):
    from your_library import YourEmbedder
    self.model = YourEmbedder()
    self.dimension = 768
```

### Add New Ranking Factor
```python
# backend/rag/retriever.py
def score_custom_factor(self, doc, query):
    # Your logic
    return custom_score

# Update weights
self.weights["custom_factor"] = 0.2
```

### Add New Query Type
```python
# backend/rag/preprocessing.py
def detect_query_type(self, query):
    # Add new type
    if "implement" in query:
        return "implementation"
```

---

## 📚 References

### Core Technologies
- **FastAPI**: https://fastapi.tiangolo.com/
- **ChromaDB**: https://www.trychroma.com/
- **sentence-transformers**: https://www.sbert.net/
- **Gemini API**: https://ai.google.dev/
- **OpenAI API**: https://platform.openai.com/

### Research Papers
- RAG (Lewis et al., 2020): https://arxiv.org/abs/2005.11401
- Dense Passage Retrieval: https://arxiv.org/abs/2004.04906
- BERT Embeddings: https://arxiv.org/abs/1810.04805

---

**Last Updated**: 2025-11-03
**Version**: 1.0.0
