# AlgoRAG Quick Start Guide

## 🚀 One-Command Setup

```bash
cd /Users/sushan/Desktop/Papers/RAG_Algorithms_and_Complexity/algorag
bash scripts/setup_algorag.sh
```

This single command will:
- ✅ Check Python version (3.9+)
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Generate sample exam questions
- ✅ Ingest data into vector database
- ✅ Set up configuration files

**Takes ~5-10 minutes** (depending on internet speed)

---

## 🎯 Essential Commands

### Start the Backend Server
```bash
cd backend
source venv/bin/activate
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
**Or use helper script:**
```bash
bash scripts/run_server.sh
```

Access:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

### Start the Frontend (Optional)
```bash
cd frontend
npm start
```
Opens browser at `http://localhost:3000`

### Run Tests
```bash
python scripts/test_harness.py
```

---

## 📝 Example Queries

### Via API (curl)
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Prove that QuickSort has O(n log n) average case complexity",
    "query_type": "proof"
  }'
```

### Via Frontend
1. Open `http://localhost:3000`
2. Enter question: "What is the time complexity of binary search?"
3. Select query type or use auto-detect
4. Click "Ask AlgoRAG"

### Via Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/query",
    json={
        "question": "Explain dynamic programming",
        "top_k": 5
    }
)

result = response.json()
print(result["answer"])
```

---

## ⚙️ Configuration

### FREE Setup (No API Keys)
Edit `.env`:
```env
EMBED_BACKEND=local
VECTOR_DB_TYPE=chroma
GENERATOR_MODEL=gemini-2.0-flash-exp  # Will need API key
```

### With Gemini API
Edit `.env`:
```env
EMBED_BACKEND=local      # Keep local to save costs
GEMINI_API_KEY=your_key_here
GENERATOR_MODEL=gemini-2.0-flash-exp
```

Get free API key: https://ai.google.dev/

### With OpenAI API
Edit `.env`:
```env
EMBED_BACKEND=local
OPENAI_API_KEY=your_key_here
GENERATOR_MODEL=gpt-3.5-turbo
```

---

## 🧪 Test the System

### Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "embedding_backend": "local",
  "embedding_dimension": 768,
  "vector_db_type": "chroma",
  "documents_indexed": 15
}
```

### Sample Queries

#### Query 1: Proof
```
Prove that 3n² + 5n + 2 = O(n²)
```

#### Query 2: Complexity
```
What is the time complexity of MergeSort?
```

#### Query 3: Algorithm
```
How does Dijkstra's algorithm work?
```

---

## 📂 Project Structure

```
algorag/
├── backend/          # FastAPI server + RAG pipeline
├── frontend/         # React web app
├── scripts/          # Setup, ingestion, testing
├── data/
│   ├── knowledge_base/   # Your documents (PDFs, texts)
│   └── vector_db/        # ChromaDB storage
└── .env              # Configuration (create from .env.example)
```

---

## 🔧 Common Tasks

### Add New Documents
1. Place PDFs in `data/knowledge_base/`
2. Run: `bash scripts/ingest_sample.sh`

### Change Embedding Model
Edit `.env`:
```env
EMBED_BACKEND=gemini  # or openai
```
Restart server.

### Update Dependencies
```bash
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Clear Vector Database
```bash
rm -rf data/vector_db/*
bash scripts/ingest_sample.sh
```

---

## 🐛 Troubleshooting

### "Module not found" error
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "No documents indexed" warning
```bash
bash scripts/ingest_sample.sh
```

### Port 8000 already in use
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app:app --port 8001
```

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

---

## 📊 Performance Tips

### Faster Queries
- Use `local` embedding backend (no API latency)
- Reduce `TOP_K` in `.env` (default: 5)
- Enable caching (future feature)

### Better Answers
- Use `gemini-2.0-flash-thinking-exp` model (slower but better)
- Increase `TOP_K` for more context
- Add more documents to knowledge base

### Lower Costs
- Use `local` embeddings (FREE)
- Use Gemini instead of OpenAI (cheaper)
- Reduce `GENERATOR_MAX_TOKENS`

---

## 🎓 Example Workflow

### 1. Research Use Case
```bash
# Generate dataset
python scripts/generate_sample_pdfs.py

# Ingest
bash scripts/ingest_sample.sh

# Test
python scripts/test_harness.py

# Evaluate
# (Create your evaluation script)
```

### 2. Student Use Case
```bash
# Start server
bash scripts/run_server.sh

# Start frontend
cd frontend && npm start

# Students visit http://localhost:3000
```

### 3. Development Use Case
```bash
# Make changes to backend/rag/*.py
# Server auto-reloads (--reload flag)

# Test changes
python scripts/test_harness.py

# View API docs
# Visit http://localhost:8000/docs
```

---

## 🔗 Useful Links

- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Main README**: [README.md](README.md)
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## 💡 Pro Tips

1. **Use the API docs**: Visit `/docs` for interactive API testing
2. **Check logs**: Server prints detailed logs (query type, retrieval stats)
3. **Customize prompts**: Edit `backend/rag/generator.py` for better answers
4. **Adjust re-ranking**: Edit `backend/rag/retriever.py` weights
5. **Monitor costs**: Use local embeddings, track API usage

---

## ✅ Checklist

- [ ] Ran `bash scripts/setup_algorag.sh`
- [ ] Created `.env` file (from `.env.example`)
- [ ] Added API key (if using cloud services)
- [ ] Started backend server
- [ ] Tested with `curl` or frontend
- [ ] Ran test harness
- [ ] Read full documentation

---

**You're all set! Start asking algorithm questions!** 🎓

For detailed documentation, see [README.md](README.md)
