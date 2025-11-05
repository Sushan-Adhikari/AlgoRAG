# AlgoRAG Research Project Guide

**Retrieval-Augmented Generation for Theoretical Computer Science Education**

This guide provides complete instructions for running the AlgoRAG research project, from data ingestion through evaluation and analysis for publication.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Data Preparation](#data-preparation)
4. [Research Workflow](#research-workflow)
5. [Evaluation Metrics](#evaluation-metrics)
6. [Generating Paper Results](#generating-paper-results)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Environment variables** configured (see [Configuration](#configuration))
3. **Data files** in place (PDFs and .txt files in `data/knowledge_base/`)

### 5-Step Quick Start

```bash
# Step 1: Install dependencies
cd /home/user/AlgoRAG/backend
pip install -r requirements.txt

# Step 2: Configure environment
cp ../.env.example ../.env
# Edit .env with your API keys (GEMINI_API_KEY, OPENAI_API_KEY, etc.)

# Step 3: Ingest all data
cd ../scripts
python ingest_all_data.py

# Step 4: Run evaluation
python run_research_evaluation.py --test-file ../evaluation/test_datasets/sample_test_cases.json

# Step 5: Analyze results
python analyze_results.py --results-file ../results/detailed_results_*.json
```

---

## System Overview

### Architecture

AlgoRAG implements a specialized RAG pipeline for theoretical CS education:

```
User Query
    ↓
[Preprocessing] → Mathematical entity extraction, query type detection
    ↓
[Embedding] → Multi-backend support (Local/Gemini/OpenAI)
    ↓
[Retrieval] → Vector DB search + Pedagogical re-ranking
    ↓
[Generation] → LLM-based answer with educational focus
    ↓
Answer with sources & pedagogical quality
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| Preprocessing | `backend/rag/preprocessing.py` | Math entity recognition, query analysis |
| Embeddings | `backend/rag/embeddings.py` | Multi-backend embedding generation |
| Retriever | `backend/rag/retriever.py` | Vector DB + pedagogical ranking |
| Generator | `backend/rag/generator.py` | LLM answer generation |
| Ingestion | `backend/rag/ingest.py` | Document processing & indexing |
| Evaluation | `evaluation/metrics.py` | BLEU, ROUGE, pedagogical metrics |

### Data Structure

```
data/
├── knowledge_base/
│   ├── textbooks/         # Cormen, DGW2, etc.
│   ├── lecture_slides/    # Course slides
│   ├── practice_problems/ # Questions & solutions
│   ├── proofs/           # Proof examples
│   └── worksheets/       # Complexity analysis
└── vector_db/            # ChromaDB storage (generated)
```

---

## Data Preparation

### Current Data Files

Your knowledge base should contain:

1. **Textbooks** (PDFs):
   - `cormen.pdf` - Introduction to Algorithms (CLRS)
   - `DGW2.pdf` - Algorithm Design (Kleinberg & Tardos)

2. **Lecture Slides** (PDFs):
   - `merged.pdf` - Combined lecture slides

3. **Practice Problems** (TXT):
   - `questions.txt` - Practice questions with solutions

4. **Proofs** (TXT):
   - `proofs.txt` - Proof examples and templates

5. **Worksheets** (TXT):
   - `worksheets.txt` - Complexity analysis worksheets

### Adding More Data

To expand your knowledge base:

```bash
# Add PDFs to appropriate directory
cp new_textbook.pdf data/knowledge_base/textbooks/

# Add text files with structured content
cp new_problems.txt data/knowledge_base/practice_problems/

# Re-run ingestion
python scripts/ingest_all_data.py
```

### Test Dataset Format

Test datasets should be in JSON format (`evaluation/test_datasets/`):

```json
[
  {
    "question": "What is the time complexity of QuickSort?",
    "expected_answer": "The average case time complexity is O(n log n)...",
    "topic": "sorting_algorithms",
    "query_type": "complexity_analysis",
    "difficulty": "medium"
  },
  ...
]
```

**For your research, you need 450+ test cases covering:**
- Asymptotic analysis (90+ questions)
- Recursive algorithms (90+ questions)
- Dynamic programming (90+ questions)
- Graph algorithms (90+ questions)
- NP-completeness (90+ questions)

---

## Research Workflow

### Phase 1: Data Ingestion

**Goal:** Index all knowledge base materials into vector database.

```bash
cd scripts

# Full ingestion with local embeddings (free, slower)
python ingest_all_data.py

# With Gemini embeddings (faster, requires API key)
python ingest_all_data.py --embedding-backend gemini

# With custom paths
python ingest_all_data.py \
  --knowledge-base /path/to/knowledge_base \
  --vector-db /path/to/vector_db \
  --embedding-backend local
```

**Expected output:**
- Number of files processed
- Number of chunks ingested
- Vector database size
- Processing time

**Success criteria:**
- All PDFs and text files successfully processed
- ~2000+ chunks indexed (depends on your data size)
- No failed ingestion errors

### Phase 2: System Validation

**Goal:** Verify the system works correctly before full evaluation.

```bash
# Test with small sample dataset
python run_research_evaluation.py \
  --test-file ../evaluation/test_datasets/sample_test_cases.json \
  --llm-backend gemini

# Check results
ls -lh ../results/
```

**What to verify:**
- All test cases process successfully
- Answers are generated correctly
- Metrics are computed
- No errors in logs

### Phase 3: Full Evaluation

**Goal:** Run comprehensive evaluation on full test dataset (450+ cases).

```bash
# Run full evaluation
python run_research_evaluation.py \
  --test-file ../evaluation/test_datasets/full_test_set.json \
  --vector-db ../data/vector_db \
  --results-dir ../results \
  --embedding-backend local \
  --llm-backend gemini
```

**This will generate:**
- `detailed_results_TIMESTAMP.json` - All evaluation details
- `aggregated_results_TIMESTAMP.json` - Summary statistics
- `paper_summary_TIMESTAMP.txt` - Human-readable summary

**Expected duration:**
- ~450 test cases at ~3-5 seconds each
- Total: 20-40 minutes

### Phase 4: Results Analysis

**Goal:** Generate publication-ready tables and statistics.

```bash
# Analyze latest results
python analyze_results.py \
  --results-file ../results/detailed_results_20250105_143022.json \
  --output-dir ../analysis
```

**This generates:**
- `results_table.tex` - LaTeX table for paper (Table 1)
- `pedagogical_table.tex` - Pedagogical metrics (Table 2)
- `statistics_summary.json` - Complete statistics
- `statistics_summary.txt` - Human-readable stats
- `error_analysis.txt` - Failed cases analysis
- `full_report.txt` - Comprehensive report

### Phase 5: Comparative Analysis

**Goal:** Compare different configurations for ablation study.

```bash
# Run with different backends
python run_research_evaluation.py --llm-backend gemini --results-dir ../results/gemini
python run_research_evaluation.py --llm-backend openai --results-dir ../results/openai

# Compare results
python analyze_results.py --results-file ../results/gemini/detailed_results_*.json --output-dir ../analysis/gemini
python analyze_results.py --results-file ../results/openai/detailed_results_*.json --output-dir ../analysis/openai
```

---

## Evaluation Metrics

### Implemented Metrics

#### 1. Answer Quality Metrics

| Metric | Range | Purpose | Target |
|--------|-------|---------|--------|
| **BLEU** | 0-1 | N-gram overlap with reference | >0.40 |
| **ROUGE-1** | 0-1 | Unigram recall | >0.50 |
| **ROUGE-2** | 0-1 | Bigram recall | >0.35 |
| **ROUGE-L** | 0-1 | Longest common subsequence | >0.45 |
| **BERTScore** | 0-1 | Semantic similarity | >0.80 |

#### 2. Pedagogical Quality Metrics

| Metric | Type | Purpose |
|--------|------|---------|
| **has_step_by_step** | Binary | Includes step-by-step explanation |
| **has_mathematical_notation** | Binary | Uses proper mathematical notation |
| **has_examples** | Binary | Includes examples |
| **avg_similarity** | 0-1 | Retrieval relevance |
| **avg_pedagogical_score** | 0-1 | Pedagogical value of sources |

#### 3. System Performance Metrics

| Metric | Unit | Purpose | Target |
|--------|------|---------|--------|
| **response_time** | seconds | System latency | <5s |
| **num_retrieved** | count | Documents retrieved | 3-5 |

### Interpreting Results

**Strong performance:**
- BLEU > 0.40
- ROUGE-L > 0.45
- BERTScore > 0.80
- Response time < 5s
- Pedagogical features > 80%

**Research claims:**
Your paper states the system should achieve:
- ✅ **85%+ accuracy** on standard exam questions
- ✅ **Step-by-step proof constructions**
- ✅ **Multiple solution approaches**
- ✅ **Improved student understanding** (requires user study)

---

## Generating Paper Results

### Tables for Paper

After running analysis, you'll have LaTeX tables ready for your paper:

#### Table 1: Overall Results by Topic

```latex
% Copy from: analysis/results_table.tex
\begin{table}[h]
\centering
\caption{AlgoRAG Evaluation Results by Topic}
...
\end{table}
```

#### Table 2: Pedagogical Quality

```latex
% Copy from: analysis/pedagogical_table.tex
\begin{table}[h]
\centering
\caption{Pedagogical Quality Metrics by Query Type}
...
\end{table}
```

### Writing Results Section

Use the statistics from `statistics_summary.txt`:

```
Our evaluation on 450 exam questions showed:
- Average BLEU score: 0.XXX (±0.XXX)
- Average ROUGE-1 F1: 0.XXX (±0.XXX)
- Average ROUGE-L F1: 0.XXX (±0.XXX)
- Average response time: X.XX seconds

The system achieved XX% accuracy on standard exam questions,
exceeding our target of 85%...
```

### Ablation Study

Compare different configurations:

1. **Without pedagogical ranking:** Run with basic retrieval
2. **Different LLM backends:** Gemini vs OpenAI vs Ollama
3. **Different embedding models:** Local vs API-based

Report the differences in your paper.

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Required for LLM generation
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional for embeddings
GEMINI_EMBEDDING_MODEL=models/embedding-001
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Optional for Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Getting API Keys

- **Gemini API:** https://makersuite.google.com/app/apikey
- **OpenAI API:** https://platform.openai.com/api-keys

### Backend Options

| Backend | Cost | Speed | Quality |
|---------|------|-------|---------|
| **Local** | Free | Slow | Good |
| **Gemini** | Paid | Fast | Excellent |
| **OpenAI** | Paid | Fast | Excellent |
| **Ollama** | Free | Medium | Good |

**Recommendation for research:** Use Gemini or OpenAI for final evaluation.

---

## Troubleshooting

### Common Issues

#### 1. Import errors

```bash
# Ensure backend is in path
export PYTHONPATH=/home/user/AlgoRAG/backend:$PYTHONPATH

# Or run from scripts directory
cd /home/user/AlgoRAG/scripts
python ingest_all_data.py
```

#### 2. API key errors

```
Error: GEMINI_API_KEY not found
```

**Solution:** Ensure `.env` file exists with valid API keys.

#### 3. Vector database not found

```
Error: Vector database not found
```

**Solution:** Run ingestion first:
```bash
python scripts/ingest_all_data.py
```

#### 4. Empty/small knowledge base

```
Warning: Only 32 chunks indexed
```

**Solution:** Verify your data files are in `data/knowledge_base/` and re-run ingestion.

#### 5. PyPDF2 extraction issues

Some PDFs may have extraction issues. Check logs for:
```
Failed to ingest PDF X: ...
```

**Solution:** Try alternative PDF processing or convert to text manually.

### Getting Help

1. Check logs in console output
2. Verify all data files exist
3. Ensure API keys are valid
4. Test with small sample first

---

## Research Checklist

### Before Running Evaluation

- [ ] All PDFs and text files in `data/knowledge_base/`
- [ ] API keys configured in `.env`
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Data ingestion completed successfully
- [ ] Vector database contains 1000+ chunks
- [ ] Sample evaluation works correctly

### For Paper Submission

- [ ] Full evaluation on 450+ test cases completed
- [ ] Results tables generated (LaTeX format)
- [ ] Statistics summary computed
- [ ] Ablation study completed (optional)
- [ ] Error analysis reviewed
- [ ] User study conducted (if applicable)

### Final Deliverables

From your evaluation, you should have:

1. **Results**
   - `detailed_results_*.json` - Full evaluation data
   - `aggregated_results_*.json` - Summary statistics

2. **Analysis**
   - `results_table.tex` - Main results table
   - `pedagogical_table.tex` - Pedagogical metrics
   - `statistics_summary.json` - All statistics
   - `full_report.txt` - Comprehensive report

3. **Paper Materials**
   - LaTeX tables ready for insertion
   - Statistics for results section
   - Error analysis for discussion section

---

## Next Steps

### Expanding the System

1. **Add more test cases** to reach 450+ target
2. **Enhance preprocessing** for better mathematical notation handling
3. **Implement proof validation** to verify proof correctness
4. **Add caching** to improve response times
5. **Build web interface** for user studies

### Publishing Your Research

1. Run full evaluation on complete test dataset
2. Generate all tables and statistics
3. Conduct user study with students (optional but recommended)
4. Write paper using generated results
5. Include system description and methodology
6. Submit to relevant conference/journal

---

## Contact & Support

For questions about this research project:

- **Primary Author:** Sushan Adhikari (sushan.adhikari2060@gmail.com)
- **Institution:** Kathmandu University

---

## Citation

If you use this system in your research, please cite:

```bibtex
@inproceedings{adhikari2025algorag,
  title={Retrieval-Augmented Generation for Theoretical Computer Science Education:
         A Comprehensive Evaluation Framework for Algorithm Analysis and Complexity Theory},
  author={Adhikari, Sushan and Sharma, Sunidhi and Lamichhane, Darshan and Adhikari, Usan},
  year={2025},
  organization={Kathmandu University}
}
```

---

## License

[Specify your license here]

---

**Last Updated:** 2025-11-05

**Status:** Research in Progress ✅
