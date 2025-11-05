# START HERE - Real Research Workflow

**Your AlgoRAG system is ready for real research with 179 exam questions!**

---

## ✅ What You Have

- **179 real exam questions** in `evaluation/test_datasets/exam_questions/evaluation_dataset.json`
- **Real textbooks:** CLRS (13 MB), Kleinberg & Tardos (1.9 MB)
- **Real lecture slides:** merged.pdf (8.2 MB)
- **Real materials:** practice problems, proofs, worksheets
- **7 topics:** asymptotic_analysis, recurrence_relations, dynamic_programming, graph_algorithms, np_completeness, sorting_algorithms, divide_and_conquer

---

## 🚀 Complete Setup & Run (5 Commands)

### 1. Start Ollama (Keep running)

```bash
ollama serve
```

**Open new terminal for remaining steps:**

### 2. Install Dependencies

```bash
cd AlgoRAG/backend
pip install -r requirements.txt
cd ..
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env
```

Set:
```env
EMBED_BACKEND=local
GENERATOR_BACKEND=ollama
OLLAMA_MODEL=llama3.1:7b
```

Save: Ctrl+X, Y, Enter

### 4. Ingest Your Real Data

```bash
python scripts/ingest_all_data.py
```

⏱️ 10-15 minutes

### 5. Run Complete Research Evaluation

```bash
python scripts/run_complete_research.py
```

⏱️ 20-40 minutes for 179 questions

---

## 📊 What You Get

After completion:

```
results/
├── detailed_results_TIMESTAMP.json  # All 179 evaluations

analysis/
├── results_table.tex           # LaTeX table for your paper (Table 1)
├── pedagogical_table.tex       # Pedagogical metrics (Table 2)
├── statistics_summary.json     # All statistics
├── statistics_summary.txt      # Human-readable stats
├── full_report.txt            # Complete report
└── error_analysis.txt         # Failed cases (if any)
```

---

## 📝 View Results

```bash
# Quick summary
cat analysis/full_report.txt

# Statistics
cat analysis/statistics_summary.txt

# By topic
python3 << 'EOF'
import json
with open('analysis/statistics_summary.json') as f:
    data = json.load(f)
    for topic, metrics in data.get('by_topic', {}).items():
        print(f"\n{topic}: {metrics['count']} questions, BLEU: {metrics.get('bleu', 0):.3f}")
EOF
```

---

## 🎯 Research Targets

Your paper states:
- Answer Accuracy: ≥85%
- BLEU: ≥0.40
- ROUGE-L: ≥0.45
- Response Time: <5s
- Step-by-step explanations: >80%

Check if your results meet these targets!

---

## 📄 For Your Paper

Copy these to your paper:
- `analysis/results_table.tex` → Table 1: Overall results by topic
- `analysis/pedagogical_table.tex` → Table 2: Pedagogical quality
- `analysis/statistics_summary.txt` → Results section numbers

---

## 📚 Detailed Documentation

- **REAL_RESEARCH_WORKFLOW.md** - Complete guide
- **OLLAMA_QUICKSTART.md** - Ollama setup
- **RESEARCH_GUIDE.md** - Full research workflow

---

## ⚡ Quick Commands Reference

```bash
# One-command complete workflow
python scripts/run_complete_research.py

# Or manual steps:
python scripts/ingest_all_data.py
python scripts/run_research_evaluation.py \
  --test-file evaluation/test_datasets/exam_questions/evaluation_dataset.json \
  --llm-backend ollama
python scripts/analyze_results.py \
  --results-file results/detailed_results_*.json
```

---

## 💰 Cost

**Total: $0** (Everything runs locally with Ollama)

---

## ⏱️ Timeline

- Setup: 15 minutes (one-time)
- Data ingestion: 10-15 minutes
- Evaluation (179 questions): 20-40 minutes
- Analysis: 1 minute
- **Total: ~1 hour**

---

## 🐛 Problems?

1. **Ollama not running:** `ollama serve`
2. **Model not found:** `ollama pull llama3.1:7b`
3. **Dependencies missing:** `cd backend && pip install -r requirements.txt`
4. **Vector DB missing:** `python scripts/ingest_all_data.py`

---

**START WITH:** `python scripts/run_complete_research.py`

**This runs everything automatically!** 🚀
