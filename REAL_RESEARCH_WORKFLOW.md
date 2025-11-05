# AlgoRAG Real Research Workflow

**Complete steps for running your actual research evaluation with 179 real exam questions**

---

## 📊 Your Real Data

✅ **Textbooks:**
- cormen.pdf (13 MB) - Introduction to Algorithms
- DGW2.pdf (1.9 MB) - Kleinberg & Tardos

✅ **Lecture Slides:**
- merged.pdf (8.2 MB) - Complete lecture slides

✅ **Practice Materials:**
- questions.txt (19 KB) - Practice problems with solutions
- proofs.txt (9.5 KB) - Proof examples and templates
- worksheets.txt (6 KB) - Complexity analysis worksheets

✅ **Evaluation Dataset:**
- **179 real exam questions** covering:
  - Asymptotic analysis
  - Recurrence relations
  - Dynamic programming
  - Graph algorithms
  - NP-completeness
  - Sorting algorithms
  - Divide and conquer

---

## 🚀 Complete Setup (One-Time, ~25 minutes)

### Step 1: Start Ollama

```bash
# Terminal 1 - Keep running
ollama serve
```

### Step 2: Install Dependencies

```bash
# Terminal 2
cd AlgoRAG/backend
pip install -r requirements.txt
cd ..
```

⏱️ **5 minutes**

### Step 3: Configure Environment

```bash
cp .env.example .env
nano .env
```

**Set these values:**
```env
EMBED_BACKEND=local
GENERATOR_BACKEND=ollama
OLLAMA_MODEL=llama3.1:7b

# Leave blank
GEMINI_API_KEY=
OPENAI_API_KEY=
```

**Save:** Ctrl+X, Y, Enter

### Step 4: Validate Setup

```bash
python scripts/validate_setup.py
```

**Check for:**
- ✅ Python 3.8+
- ✅ Dependencies installed
- ✅ Data files (6 files, 23.1 MB)
- ✅ Environment configured
- ⚠️ Vector DB not found (normal, we create it next)

### Step 5: Ingest All Your Data

```bash
python scripts/ingest_all_data.py
```

**What this does:**
- Processes all 3 PDFs (23 MB)
- Processes all 3 text files
- Extracts mathematical notation
- Generates embeddings locally
- Creates vector database

⏱️ **10-15 minutes**

**Expected output:**
```
✓ Ingested XXX chunks from textbooks/cormen.pdf
✓ Ingested XXX chunks from textbooks/DGW2.pdf
✓ Ingested XXX chunks from lecture_slides/merged.pdf
✓ Ingested XXX chunks from practice_problems/questions.txt
✓ Ingested XXX chunks from proofs/proofs.txt
✓ Ingested XXX chunks from worksheets/worksheets.txt

Total chunks ingested: ~800-1200
Vector database now contains: XXX documents
✓ Data ingestion complete!
```

---

## 🎯 Run Your Research Evaluation (20-40 minutes)

### Option 1: Automated Complete Workflow (Recommended)

```bash
python scripts/run_complete_research.py
```

This script will:
1. Check prerequisites
2. Validate environment
3. Run evaluation on 179 questions
4. Generate analysis and tables
5. Show you where results are saved

⏱️ **20-40 minutes** (depends on your machine)

### Option 2: Manual Step-by-Step

#### A. Run Evaluation

```bash
python scripts/run_research_evaluation.py \
  --test-file evaluation/test_datasets/exam_questions/evaluation_dataset.json \
  --llm-backend ollama \
  --results-dir results
```

⏱️ **20-40 minutes** for 179 questions

**Progress output:**
```
[1/179] Processing test case...
✓ Completed in 6.2 seconds
[2/179] Processing test case...
✓ Completed in 5.8 seconds
...
[179/179] Processing test case...

EVALUATION SUMMARY
==================
Total test cases: 179
Successful: 179
Failed: 0

Overall Metrics:
bleu: 0.XXXX
rouge1_f: 0.XXXX
rougeL_f: 0.XXXX
avg_response_time: X.XX seconds

✓ Results saved to: results/detailed_results_TIMESTAMP.json
```

#### B. Analyze Results

```bash
python scripts/analyze_results.py \
  --results-file results/detailed_results_*.json \
  --output-dir analysis
```

⏱️ **1 minute**

**Generated files:**
- `analysis/results_table.tex` - Main results table (LaTeX)
- `analysis/pedagogical_table.tex` - Pedagogical metrics (LaTeX)
- `analysis/statistics_summary.json` - All statistics
- `analysis/statistics_summary.txt` - Human-readable stats
- `analysis/error_analysis.txt` - Failed cases analysis
- `analysis/full_report.txt` - Complete report

---

## 📝 View Your Results

### Quick Summary

```bash
cat analysis/full_report.txt
```

### Detailed Statistics

```bash
cat analysis/statistics_summary.txt
```

### Results by Topic

```bash
python3 << 'EOF'
import json
with open('analysis/statistics_summary.json') as f:
    data = json.load(f)
    print("\nResults by Topic:")
    print("="*60)
    for topic, metrics in data['by_topic'].items():
        print(f"\n{topic.replace('_', ' ').title()}:")
        print(f"  Questions: {metrics['count']}")
        print(f"  BLEU: {metrics['bleu']:.3f}")
        print(f"  ROUGE-L: {metrics['rougeL_f']:.3f}")
        print(f"  Avg time: {metrics['avg_response_time']:.2f}s")
EOF
```

---

## 📊 Using Results in Your Paper

### Table 1: Overall Results

Copy from: `analysis/results_table.tex`

```latex
\begin{table}[h]
\centering
\caption{AlgoRAG Evaluation Results by Topic}
\label{tab:results}
...
\end{table}
```

### Table 2: Pedagogical Quality

Copy from: `analysis/pedagogical_table.tex`

```latex
\begin{table}[h]
\centering
\caption{Pedagogical Quality Metrics by Query Type}
\label{tab:pedagogical}
...
\end{table}
```

### Writing Results Section

Use statistics from `statistics_summary.txt`:

```
Our evaluation on 179 exam questions from theoretical computer science courses showed:

- Average BLEU score: 0.XXX (±0.XXX)
- Average ROUGE-1 F1: 0.XXX (±0.XXX)
- Average ROUGE-L F1: 0.XXX (±0.XXX)
- Average response time: X.XX seconds

The system achieved strong performance across all seven topic areas:
- Asymptotic analysis: XX questions, BLEU 0.XXX
- Recurrence relations: XX questions, BLEU 0.XXX
- Dynamic programming: XX questions, BLEU 0.XXX
- Graph algorithms: XX questions, BLEU 0.XXX
- NP-completeness: XX questions, BLEU 0.XXX
...

Pedagogical quality metrics showed:
- XX% of responses included step-by-step explanations
- XX% used proper mathematical notation
- XX% included relevant examples
```

---

## 🎯 Research Targets vs Your Results

Your paper states these targets:

| Metric | Target | Your Result |
|--------|--------|-------------|
| Answer Accuracy | ≥85% | Check `full_report.txt` |
| BLEU Score | ≥0.40 | Check `statistics_summary.txt` |
| ROUGE-L F1 | ≥0.45 | Check `statistics_summary.txt` |
| Response Time | <5s | Check avg_response_time |
| Step-by-step | >80% | Check pedagogical metrics |

---

## 🔄 Re-running with Different Settings

### Try Different LLM Backends

```bash
# With Ollama (default - free)
python scripts/run_research_evaluation.py \
  --test-file evaluation/test_datasets/exam_questions/evaluation_dataset.json \
  --llm-backend ollama

# With Gemini (if you have API key)
python scripts/run_research_evaluation.py \
  --test-file evaluation/test_datasets/exam_questions/evaluation_dataset.json \
  --llm-backend gemini

# Compare results
python scripts/analyze_results.py --results-file results/detailed_results_ollama_*.json --output-dir analysis/ollama
python scripts/analyze_results.py --results-file results/detailed_results_gemini_*.json --output-dir analysis/gemini
```

### Try Different Ollama Models

Edit `.env`:
```env
# Faster, smaller
OLLAMA_MODEL=llama3.1:3b

# Better quality (if you have RAM)
OLLAMA_MODEL=llama3.1:70b

# Alternative models
OLLAMA_MODEL=mistral:7b
OLLAMA_MODEL=gemma2:9b
```

Then re-run evaluation.

---

## 📈 Performance Expectations

### With Ollama (llama3.1:7b):

- **Per question:** 5-15 seconds (depends on hardware)
- **Total time (179 questions):** 20-40 minutes
- **RAM usage:** ~8-12 GB
- **Cost:** $0

### Metrics Expectations:

Based on similar RAG systems:

- **BLEU:** 0.30-0.50 (higher is better)
- **ROUGE-1:** 0.40-0.60
- **ROUGE-L:** 0.35-0.55
- **Pedagogical features:** 70-90%

Your results may vary based on:
- Quality of reference answers
- LLM model used
- Document retrieval quality

---

## 🐛 Troubleshooting

### Evaluation is slow

**Normal:** llama3.1:7b takes 5-15 seconds per question
**Solutions:**
1. Use smaller model: `llama3.1:3b` (faster, slightly lower quality)
2. Use cloud LLM: Gemini or OpenAI (requires API key)
3. Let it run overnight

### Out of memory

**Solutions:**
1. Close other applications
2. Use smaller model: `ollama pull llama3.1:3b`
3. Increase swap space (Linux)

### Some questions fail

**Check:**
- Ollama is running: `curl http://localhost:11434/api/tags`
- Vector DB exists: `ls data/vector_db/`
- Review error in `analysis/error_analysis.txt`

### Results seem poor

**Possible reasons:**
1. Vector DB not properly ingested - re-run ingestion
2. Reference answers very different from generated style
3. Model not suitable for theoretical CS - try different model

---

## 🎓 Next Steps After Evaluation

1. **Review results thoroughly**
   ```bash
   cat analysis/full_report.txt
   cat analysis/statistics_summary.txt
   cat analysis/error_analysis.txt
   ```

2. **Analyze by topic**
   - Which topics perform best?
   - Which need improvement?

3. **Check pedagogical quality**
   - Are proofs step-by-step?
   - Is mathematical notation correct?

4. **Compare with baselines** (optional)
   - Run with different LLMs
   - Compare with GPT-4 (if budget allows)

5. **User study** (optional but recommended)
   - Test with real students
   - Measure learning improvement
   - Get qualitative feedback

6. **Write your paper**
   - Use generated tables
   - Report statistics
   - Discuss results

---

## 📁 File Locations

```
AlgoRAG/
├── data/
│   ├── knowledge_base/       # Your PDFs and text files (23.1 MB)
│   └── vector_db/           # Generated after ingestion
├── evaluation/
│   └── test_datasets/
│       └── exam_questions/
│           └── evaluation_dataset.json  # 179 real questions
├── results/                 # Evaluation results (generated)
│   └── detailed_results_*.json
├── analysis/               # Analysis outputs (generated)
│   ├── results_table.tex
│   ├── pedagogical_table.tex
│   ├── statistics_summary.json
│   └── full_report.txt
└── scripts/
    ├── run_complete_research.py  # Automated workflow
    ├── ingest_all_data.py
    ├── run_research_evaluation.py
    └── analyze_results.py
```

---

## ✅ Research Checklist

Before submission:

- [ ] Data ingested successfully (~800-1200 chunks)
- [ ] Evaluation completed on 179 questions
- [ ] Results analyzed and tables generated
- [ ] BLEU score ≥0.40 achieved
- [ ] ROUGE-L ≥0.45 achieved
- [ ] Response time <5s on average
- [ ] LaTeX tables copied to paper
- [ ] Statistics reported in results section
- [ ] Error analysis reviewed
- [ ] (Optional) User study conducted

---

## 🎉 Summary

You have:
- ✅ 179 real exam questions
- ✅ 23.1 MB of real textbooks and materials
- ✅ Complete evaluation pipeline
- ✅ Automated analysis and table generation
- ✅ 100% free local setup with Ollama

**Total cost: $0**
**Total time: ~1 hour (mostly automated)**

---

## 📞 Need Help?

Check these files:
- **This guide:** `REAL_RESEARCH_WORKFLOW.md` (you're here)
- **Ollama setup:** `OLLAMA_SETUP.md`
- **Complete guide:** `RESEARCH_GUIDE.md`
- **Quick start:** `OLLAMA_QUICKSTART.md`

---

**Start with: `python scripts/run_complete_research.py`**

**Good luck with your research! 🚀**
