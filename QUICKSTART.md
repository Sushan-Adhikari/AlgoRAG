# AlgoRAG Quick Start Guide

**Get your system running in 6 steps!**

---

## Step 1: Install Python Dependencies (5 minutes)

```bash
cd AlgoRAG/backend
pip install -r requirements.txt
```

**What this installs:**
- PyTorch, sentence-transformers (for embeddings)
- ChromaDB (vector database)
- FastAPI, uvicorn (web server)
- PyPDF2 (PDF processing)
- NLTK, rouge_score (evaluation metrics)
- Google Gemini & OpenAI clients

**Wait for installation to complete...**

---

## Step 2: Configure API Keys (2 minutes)

```bash
cd ..  # Go back to AlgoRAG root
cp .env.example .env
nano .env  # or use: vim .env, code .env, etc.
```

**Add your API key** (you need at least ONE):

```env
# Option 1: Gemini (Recommended - Free tier available)
GEMINI_API_KEY=your_gemini_api_key_here

# Option 2: OpenAI (Paid)
OPENAI_API_KEY=your_openai_api_key_here
```

**Get API keys:**
- Gemini: https://makersuite.google.com/app/apikey (Free tier: 15 req/min)
- OpenAI: https://platform.openai.com/api-keys (Paid)

**Save and exit** the editor.

---

## Step 3: Validate Your Setup (1 minute)

```bash
python scripts/validate_setup.py
```

**Expected output:**
- ✅ Python 3.8+
- ✅ Dependencies installed
- ✅ Data files present (6 files)
- ✅ API keys configured
- ✅ Scripts ready
- ⚠️ Vector database not found (normal - we'll create it next)
- ⚠️ Only 16 test cases (need 450+ for full research)

**If you see errors**, fix them before proceeding!

---

## Step 4: Ingest Your Data (5-15 minutes)

```bash
python scripts/ingest_all_data.py
```

**What this does:**
- Processes your PDFs: cormen.pdf (12.5 MB), DGW2.pdf (1.8 MB), merged.pdf (8.1 MB)
- Processes your TXT files: questions, proofs, worksheets
- Extracts mathematical entities (O(n), Θ(n²), etc.)
- Generates embeddings
- Stores in vector database

**Expected output:**
```
✓ Ingested XXX chunks from textbooks/cormen.pdf
✓ Ingested XXX chunks from textbooks/DGW2.pdf
✓ Ingested XXX chunks from lecture_slides/merged.pdf
✓ Ingested XXX chunks from practice_problems/questions.txt
✓ Ingested XXX chunks from proofs/proofs.txt
✓ Ingested XXX chunks from worksheets/worksheets.txt

INGESTION COMPLETE
Total files processed: 6
Total chunks ingested: XXX
Vector database now contains: XXX documents

✓ Data ingestion complete!
```

**Duration:** 5-15 minutes depending on your setup (local embeddings = slower, API = faster)

---

## Step 5: Run Sample Evaluation (2-3 minutes)

```bash
python scripts/run_research_evaluation.py \
  --test-file evaluation/test_datasets/sample_test_cases.json \
  --llm-backend gemini
```

**If using OpenAI instead:**
```bash
python scripts/run_research_evaluation.py \
  --test-file evaluation/test_datasets/sample_test_cases.json \
  --llm-backend openai
```

**What this does:**
- Evaluates your system on 16 sample test cases
- Generates answers using AlgoRAG
- Computes BLEU, ROUGE, BERTScore, pedagogical metrics
- Saves results to `results/` directory

**Expected output:**
```
[1/16] Processing test case...
✓ Completed in X.XX seconds
[2/16] Processing test case...
...
[16/16] Processing test case...

EVALUATION SUMMARY
==================
Total test cases: 16
Successful: 16
Failed: 0

Overall Metrics:
BLEU: 0.XXXX
ROUGE-1 F1: 0.XXXX
ROUGE-L F1: 0.XXXX
...

✓ Results saved to: results/detailed_results_TIMESTAMP.json
```

---

## Step 6: Analyze Results (1 minute)

```bash
python scripts/analyze_results.py \
  --results-file results/detailed_results_*.json \
  --output-dir analysis
```

**What this generates:**
- `analysis/results_table.tex` - LaTeX table for your paper
- `analysis/pedagogical_table.tex` - Pedagogical metrics table
- `analysis/statistics_summary.json` - Complete statistics
- `analysis/statistics_summary.txt` - Human-readable stats
- `analysis/full_report.txt` - Comprehensive report

**Expected output:**
```
✓ Saved LaTeX table: analysis/results_table.tex
✓ Saved pedagogical table: analysis/pedagogical_table.tex
✓ Saved statistics: analysis/statistics_summary.json
✓ Saved full report: analysis/full_report.txt

✓ Analysis complete! All outputs saved to: analysis/
```

---

## 🎉 Success! Your System is Running

You now have:
- ✅ AlgoRAG system fully operational
- ✅ Data ingested into vector database
- ✅ Sample evaluation completed
- ✅ Results and analysis generated

---

## 🌐 Optional: Run Web Interface

Want to try the web interface?

### Terminal 1 - Backend:
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm install  # First time only
npm start
```

**Access:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## 📊 Next Steps for Your Research

### For Paper Publication:

1. **Expand Test Dataset** (CRITICAL)
   - Current: 16 test cases
   - Target: 450+ test cases
   - Create: `evaluation/test_datasets/full_test_set.json`
   - Format: See RESEARCH_GUIDE.md

2. **Run Full Evaluation**
   ```bash
   python scripts/run_research_evaluation.py \
     --test-file evaluation/test_datasets/full_test_set.json \
     --llm-backend gemini
   ```

3. **Generate Paper Tables**
   ```bash
   python scripts/analyze_results.py \
     --results-file results/detailed_results_TIMESTAMP.json
   ```

4. **Copy tables to your paper**
   - Use: `analysis/results_table.tex`
   - Use: `analysis/pedagogical_table.tex`

---

## 🔧 Troubleshooting

### Issue: "No module named 'X'"
**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: "API key not found"
**Solution:**
```bash
# Check .env file exists
cat .env

# If not, copy from example
cp .env.example .env
nano .env  # Add your API key
```

### Issue: "Vector database not found"
**Solution:**
```bash
python scripts/ingest_all_data.py
```

### Issue: Ingestion is slow
**Solution:** Use API embeddings instead of local
```bash
python scripts/ingest_all_data.py --embedding-backend gemini
```

---

## 📞 Need Help?

1. **Validation issues:** Run `python scripts/validate_setup.py`
2. **Complete guide:** See `RESEARCH_GUIDE.md`
3. **Setup details:** See `SETUP_INSTRUCTIONS.md`

---

## ✅ Quick Command Reference

```bash
# Validate environment
python scripts/validate_setup.py

# Ingest data
python scripts/ingest_all_data.py

# Run evaluation
python scripts/run_research_evaluation.py \
  --test-file evaluation/test_datasets/sample_test_cases.json

# Analyze results
python scripts/analyze_results.py \
  --results-file results/detailed_results_*.json

# Start web server (optional)
cd backend && uvicorn app:app --reload --port 8000
```

---

**Good luck with your research! 🚀**
