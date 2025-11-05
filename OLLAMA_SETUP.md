# Using Ollama with AlgoRAG (100% Free, Local Setup)

**Complete guide for running AlgoRAG with Ollama (llama3.1:7b) - No API keys needed!**

---

## Why Ollama?

✅ **Completely FREE** - No API costs
✅ **Runs locally** - No internet required (after model download)
✅ **Private** - Your data never leaves your machine
✅ **Fast** - Low latency, no API rate limits
✅ **Multiple models** - llama3.1, mistral, gemma, and more

---

## Prerequisites

- **RAM:** 8GB minimum (16GB recommended for llama3.1:7b)
- **Storage:** ~4-8GB for model files
- **OS:** Linux, macOS, or Windows

---

## Step 1: Install Ollama (5 minutes)

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### macOS
```bash
# Download from: https://ollama.com/download
# Or use Homebrew:
brew install ollama
```

### Windows
Download installer from: https://ollama.com/download

---

## Step 2: Start Ollama Service (1 minute)

```bash
# Start Ollama server (runs in background)
ollama serve
```

**Leave this terminal open** or run it in the background.

To check if Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

You should see a JSON response with available models.

---

## Step 3: Pull llama3.1:7b Model (5-10 minutes)

Open a **new terminal** and run:

```bash
# Pull llama3.1 7B model (recommended, ~4.7GB)
ollama pull llama3.1:7b
```

**Alternative models you can use:**
```bash
# Smaller, faster (good for testing)
ollama pull llama3.1:3b     # ~2GB

# Larger, better quality
ollama pull llama3.1:70b    # ~40GB (requires 64GB+ RAM)

# Other good options
ollama pull mistral:7b      # ~4.1GB
ollama pull gemma2:9b       # ~5.4GB
```

**Wait for download to complete...**

Verify the model is installed:
```bash
ollama list
```

You should see `llama3.1:7b` in the list.

---

## Step 4: Test Ollama (1 minute)

Test that Ollama works with a simple query:

```bash
ollama run llama3.1:7b "What is the time complexity of binary search?"
```

You should get a response about O(log n).

Press `Ctrl+D` or type `/bye` to exit the chat.

---

## Step 5: Configure AlgoRAG for Ollama (2 minutes)

```bash
cd AlgoRAG

# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or vim, code, etc.
```

**Set these values in .env:**
```env
# Use local embeddings (free)
EMBED_BACKEND=local

# Use Ollama for generation
GENERATOR_BACKEND=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:7b

# Leave API keys blank (not needed)
GEMINI_API_KEY=
OPENAI_API_KEY=
```

**Save and exit** (Ctrl+X, then Y, then Enter in nano)

---

## Step 6: Install Python Dependencies (5 minutes)

```bash
cd backend
pip install -r requirements.txt
```

---

## Step 7: Validate Setup (1 minute)

```bash
cd ..
python scripts/validate_setup.py
```

**Expected output:**
- ✅ Python 3.8+
- ✅ Dependencies installed
- ✅ Data files present
- ✅ Environment variables configured (no API keys needed!)
- ⚠️ Vector database not found (normal - we'll create it next)

---

## Step 8: Ingest Data (10-15 minutes)

```bash
python scripts/ingest_all_data.py
```

**What this does:**
- Processes PDFs and text files
- Generates embeddings locally (no API calls!)
- Stores in vector database

**Expected output:**
```
✓ Ingested XXX chunks from 6 files
Vector database now contains: XXX documents
✓ Data ingestion complete!
```

---

## Step 9: Run Evaluation with Ollama (3-5 minutes)

```bash
python scripts/run_research_evaluation.py \
  --test-file evaluation/test_datasets/sample_test_cases.json \
  --llm-backend ollama
```

**What happens:**
- Evaluates 16 test questions
- Uses Ollama (llama3.1:7b) to generate answers
- All processing happens locally on your machine
- No internet required (except initial setup)

**Expected output:**
```
[1/16] Processing test case...
✓ Completed in X.XX seconds
...
[16/16] Processing test case...

EVALUATION SUMMARY
==================
Total test cases: 16
Successful: 16

Overall Metrics:
BLEU: 0.XXXX
ROUGE-1 F1: 0.XXXX
...

✓ Results saved to: results/detailed_results_TIMESTAMP.json
```

---

## Step 10: Analyze Results (1 minute)

```bash
python scripts/analyze_results.py \
  --results-file results/detailed_results_*.json \
  --output-dir analysis
```

**Generated files:**
- `analysis/results_table.tex` - LaTeX table for your paper
- `analysis/pedagogical_table.tex` - Pedagogical metrics
- `analysis/statistics_summary.json` - Complete stats
- `analysis/full_report.txt` - Human-readable report

---

## 🎉 Success! You're Running AlgoRAG with Ollama

Your system is now:
- ✅ Running 100% locally
- ✅ No API costs
- ✅ No internet required (after setup)
- ✅ Private and secure
- ✅ Ready for research evaluation

---

## Using Different Ollama Models

To use a different model, update `.env`:

```env
# For faster responses (smaller model)
OLLAMA_MODEL=llama3.1:3b

# For better quality (if you have RAM)
OLLAMA_MODEL=llama3.1:70b

# Alternative models
OLLAMA_MODEL=mistral:7b
OLLAMA_MODEL=gemma2:9b
```

Then re-run your evaluation:
```bash
python scripts/run_research_evaluation.py \
  --test-file evaluation/test_datasets/sample_test_cases.json \
  --llm-backend ollama
```

---

## Troubleshooting

### Issue: "Ollama not running"

**Check if Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

**If not running, start it:**
```bash
ollama serve
```

### Issue: "Model not found"

**List installed models:**
```bash
ollama list
```

**Pull the model if missing:**
```bash
ollama pull llama3.1:7b
```

### Issue: "Connection timeout"

**Increase timeout in .env (if model is slow):**
```env
OLLAMA_TIMEOUT=300  # 5 minutes
```

### Issue: Slow response times

**Options:**
1. Use a smaller model: `llama3.1:3b`
2. Reduce max tokens in `.env`:
   ```env
   GENERATOR_MAX_TOKENS=1024
   ```
3. Use GPU acceleration (if available)

### Issue: Out of memory

**Solutions:**
1. Use smaller model: `ollama pull llama3.1:3b`
2. Close other applications
3. Increase swap space (Linux)

---

## Performance Comparison

| Model | Size | RAM Required | Speed | Quality |
|-------|------|--------------|-------|---------|
| llama3.1:3b | 2GB | 8GB | Fast | Good |
| **llama3.1:7b** | 4.7GB | 16GB | Medium | **Excellent** |
| llama3.1:70b | 40GB | 64GB+ | Slow | Best |
| mistral:7b | 4.1GB | 16GB | Fast | Excellent |
| gemma2:9b | 5.4GB | 16GB | Medium | Excellent |

**Recommended:** llama3.1:7b (best balance of quality and speed)

---

## Advanced: Using Custom Ollama Models

If you have a custom Ollama model:

```bash
# Create custom model
ollama create mymodel -f Modelfile

# Use in AlgoRAG
# Update .env:
OLLAMA_MODEL=mymodel
```

---

## Comparing Ollama vs Cloud LLMs

| Feature | Ollama | Gemini | OpenAI |
|---------|--------|--------|--------|
| **Cost** | $0 | Free tier + paid | Paid only |
| **Privacy** | 100% local | Cloud | Cloud |
| **Speed** | Fast (local) | Fast | Fast |
| **Quality** | Excellent | Excellent | Best |
| **Internet** | Not needed* | Required | Required |
| **Setup** | Easy | Very easy | Very easy |

\* Internet only needed for initial model download

---

## Next Steps

Now that you have AlgoRAG running with Ollama:

1. **Expand test dataset** (16 → 450+ test cases)
2. **Run full evaluation** on complete dataset
3. **Generate paper tables** and statistics
4. **Optional:** Compare Ollama vs cloud LLMs (ablation study)

See `RESEARCH_GUIDE.md` for full research workflow.

---

## Cost Comparison

**Your setup (Ollama + local embeddings):**
- Setup cost: $0
- Monthly cost: $0
- Electricity: ~$0.50/month (running model locally)
- **Total: $0.50/month**

**Cloud setup (Gemini):**
- Setup cost: $0
- Monthly cost: $5-10
- **Total: $5-10/month**

**Cloud setup (OpenAI GPT-4):**
- Setup cost: $0
- Monthly cost: $50-100
- **Total: $50-100/month**

**For a complete research project (6-8 weeks):**
- Ollama: **~$1 total**
- Gemini: **~$10-20 total**
- OpenAI GPT-4: **~$100-200 total**

---

## Frequently Asked Questions

### Q: Can I use Ollama and cloud LLMs together?

Yes! You can easily switch between them:

```bash
# Use Ollama
python scripts/run_research_evaluation.py --llm-backend ollama

# Use Gemini
python scripts/run_research_evaluation.py --llm-backend gemini

# Compare results
python scripts/analyze_results.py --results-file results/detailed_results_ollama_*.json
python scripts/analyze_results.py --results-file results/detailed_results_gemini_*.json
```

### Q: Which model is best for my research?

For academic research, we recommend:
- **Primary:** llama3.1:7b (Ollama) - Good quality, reproducible
- **Comparison:** Gemini or GPT-4 - For ablation study

### Q: Will Ollama results be as good as GPT-4?

llama3.1:7b produces excellent results for theoretical CS questions. For your research:
- Quality is comparable for most questions
- May be slightly less polished in phrasing
- **Advantage:** Reproducible, free, private

### Q: Can I run this on a laptop?

Yes! Requirements:
- **Minimum:** 8GB RAM, run llama3.1:3b
- **Recommended:** 16GB RAM, run llama3.1:7b
- **Optimal:** 32GB+ RAM, run larger models

---

## Quick Command Reference

```bash
# Ollama commands
ollama serve                    # Start Ollama
ollama pull llama3.1:7b        # Download model
ollama list                     # List installed models
ollama run llama3.1:7b         # Test model interactively
ollama rm llama3.1:7b          # Remove model

# AlgoRAG with Ollama
python scripts/validate_setup.py
python scripts/ingest_all_data.py
python scripts/run_research_evaluation.py --llm-backend ollama
python scripts/analyze_results.py --results-file results/detailed_results_*.json
```

---

## Resources

- **Ollama website:** https://ollama.com
- **Ollama models:** https://ollama.com/library
- **Llama 3.1 info:** https://ollama.com/library/llama3.1
- **AlgoRAG docs:** See `RESEARCH_GUIDE.md`

---

**You're all set! Enjoy running AlgoRAG completely free with Ollama! 🚀**
