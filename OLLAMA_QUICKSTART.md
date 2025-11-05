# Ollama Quick Start (5 Commands!)

**Run AlgoRAG with llama3.1:7b - 100% Free, No API Keys!**

---

## Prerequisites

You said you have:
- ✅ Ollama installed
- ✅ llama3.1:7b model ready
- ✅ AlgoRAG repository cloned

---

## 5 Commands to Get Started

### 1. Make sure Ollama is running

```bash
# In a terminal, start Ollama (if not already running)
ollama serve
```

**Keep this terminal open** or run it in the background.

---

### 2. Install Python dependencies

```bash
cd AlgoRAG/backend
pip install -r requirements.txt
```

⏱️ **Wait ~5 minutes for installation...**

---

### 3. Configure for Ollama

```bash
cd ..
cp .env.example .env
nano .env
```

**Change these lines:**
```env
EMBED_BACKEND=local
GENERATOR_BACKEND=ollama
OLLAMA_MODEL=llama3.1:7b

# Leave API keys blank
GEMINI_API_KEY=
OPENAI_API_KEY=
```

**Save:** Ctrl+X, then Y, then Enter

---

### 4. Ingest your data

```bash
python scripts/ingest_all_data.py
```

⏱️ **Wait ~10 minutes...**

Expected output:
```
✓ Ingested XXX chunks from 6 files
Vector database now contains: XXX documents
✓ Data ingestion complete!
```

---

### 5. Run evaluation

```bash
python scripts/run_research_evaluation.py \
  --test-file evaluation/test_datasets/sample_test_cases.json \
  --llm-backend ollama
```

⏱️ **Wait ~3 minutes for 16 test cases...**

Expected output:
```
[1/16] Processing test case...
✓ Completed in X.XX seconds
...
[16/16] Processing test case...

EVALUATION SUMMARY
Successful: 16

✓ Results saved to: results/detailed_results_TIMESTAMP.json
```

---

## 🎉 Done!

You now have:
- ✅ AlgoRAG running with Ollama
- ✅ Evaluation results ready
- ✅ $0 cost - everything local

---

## View Your Results

```bash
# Analyze results
python scripts/analyze_results.py \
  --results-file results/detailed_results_*.json

# View report
cat analysis/full_report.txt
```

---

## Next Steps

1. **Expand test dataset** (16 → 450+ test cases)
2. **Run full evaluation** on complete dataset
3. **Generate paper tables** from results

See `RESEARCH_GUIDE.md` for complete workflow.

---

## Troubleshooting

### "Ollama not running"
```bash
# Start Ollama
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

### "Model not found"
```bash
# Check installed models
ollama list

# Pull llama3.1:7b if missing
ollama pull llama3.1:7b
```

### Slow responses
Your model is running! llama3.1:7b takes 5-30 seconds per response depending on your hardware. This is normal for local LLMs.

---

## Model Alternatives

If llama3.1:7b is too slow, try a smaller model:

```bash
# Pull smaller model
ollama pull llama3.1:3b

# Update .env
nano .env
# Change: OLLAMA_MODEL=llama3.1:3b
```

---

## Full Documentation

- **Detailed Ollama guide:** `OLLAMA_SETUP.md`
- **Research workflow:** `RESEARCH_GUIDE.md`
- **Complete setup:** `SETUP_INSTRUCTIONS.md`

---

**Total Setup Time:** ~20 minutes
**Total Cost:** $0

Enjoy your free, private AlgoRAG system! 🚀
