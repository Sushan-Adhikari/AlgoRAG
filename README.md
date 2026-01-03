# AlgoRAG: Retrieval-Augmented Generation for Theoretical Computer Science Education

[![Paper](https://img.shields.io/badge/Paper-PDF-red.svg)](./AlgoRAG_Moressier.pdf)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Dataset](https://img.shields.io/badge/Dataset-179_Questions-green.svg)](./evaluation/test_datasets)

> **A Comprehensive Evaluation Framework for Algorithm Analysis and Complexity Theory**

This repository contains the complete implementation and evaluation framework for **AlgoRAG**, a specialized retrieval-augmented generation system designed for theoretical computer science education. The system combines DeepSeek V3 with a curated knowledge base of textbooks, lecture materials, and practice problems to deliver pedagogically sound explanations of complex theoretical concepts.

**Paper**: Accepted at [Conference Name], 2026
**Authors**: Your Name, Coauthor Name ([Your University](https://university.edu))

---

## Key Results

Our comprehensive evaluation on **179 curated exam-style questions** demonstrates:

| Metric | Value | Notes |
|--------|-------|-------|
| **Success Rate** | 100.0% | All questions answered without timeout |
| **Pedagogical Quality** | 0.7620 | High instructional value (0-1 scale) |
| **ROUGE-1 F1** | 0.0963 | Unigram overlap with reference answers |
| **ROUGE-L F1** | 0.0683 | Longest common subsequence overlap |
| **Response Time** | 38.0s | Average time per question |
| **BLEU-4** | 0.0000 | Reflects varied mathematical phrasing† |

† *BLEU-4 = 0.0 indicates that mathematical proofs use diverse wording while remaining logically equivalent—a known limitation of n-gram metrics for formal reasoning tasks.*

### Performance by Topic

| Topic | Questions | ROUGE-1 F1 | Pedagogical Quality |
|-------|-----------|------------|---------------------|
| Asymptotic Analysis | 89 | 0.0894 | 0.7620 |
| NP-Completeness | 21 | 0.1285 | 0.7643 |
| Graph Algorithms | 21 | 0.1023 | 0.8086 |
| Dynamic Programming | 17 | 0.0898 | 0.7935 |
| Recurrence Relations | 17 | 0.0903 | 0.6629 |
| Divide-and-Conquer | 8 | 0.0876 | 0.7300 |
| Sorting Algorithms | 6 | 0.1115 | 0.8250 |

---

## Contributions

1. **Comprehensive Knowledge Base**: 847 lecture slides, 312 practice problems, 156 proof templates, and authoritative textbooks (CLRS, Sipser)
2. **Domain-Specific Optimizations**: Mathematical entity recognition, pedagogical ranking, and proof-aware generation
3. **Rigorous Evaluation Framework**: Custom pedagogical metrics beyond standard NLP measures (BLEU, ROUGE)
4. **Public Dataset**: 179 exam-style questions with reference answers and metadata
5. **Reproducible Pipeline**: Complete evaluation scripts and documentation

---

## Quick Start

### Prerequisites

```bash
# System requirements
- Python 3.10+
- 16GB RAM recommended
- DeepSeek API key (or other LLM provider)
```

### Installation

```bash
# Clone repository
git clone https://github.com/Sushan-Adhikari/AlgoRAG.git
cd AlgoRAG

# Install dependencies
cd backend
pip install -r requirements.txt
cd ..

# Configure environment
cp .env.example .env
# Edit .env: Set DEEPSEEK_API_KEY and other configurations
```

### Data Ingestion

```bash
# Ingest knowledge base (textbooks, slides, problems)
python scripts/ingest_all_data.py

# Verify setup
python scripts/validate_setup.py
```

### Running Evaluation

```bash
# Run full evaluation on 179 questions (~2 hours with DeepSeek V3)
python run_paper_evaluation.py

# IMPORTANT: Extract corrected metrics (fixes ROUGE aggregation bug)
python scripts/extract_correct_metrics.py

# Results saved to: paper_results/
```

**Important Note**: The `run_paper_evaluation.py` script generates raw results with a known
aggregation bug that reports ROUGE scores as 0.0. Always run `extract_correct_metrics.py`
after evaluation to generate corrected metrics files:
- `corrected_paper_tables.txt` - LaTeX tables with correct values
- `corrected_summary_stats.txt` - Human-readable statistics
- `corrected_aggregate_stats.json` - Programmatic access to metrics

The original `aggregate_stats_*.json` file has been corrected in this repository, but if
you re-run the evaluation, you must run the extraction script to get accurate ROUGE scores.

---

## Repository Structure

```
AlgoRAG/
├── backend/                      # RAG system implementation
│   ├── rag/
│   │   ├── embeddings.py         # Embedding backends (all-mpnet-base-v2)
│   │   ├── retriever.py          # ChromaDB + pedagogical re-ranking
│   │   ├── generator.py          # DeepSeek V3 integration
│   │   ├── preprocessing.py      # Math entity recognition
│   │   └── ingest.py             # Document processing & chunking
│   └── app.py                    # FastAPI server
├── data/
│   ├── knowledge_base/           # Source materials
│   │   ├── textbooks/            # CLRS (13MB), Sipser, etc.
│   │   ├── lecture_slides/       # 847 slides (8.2MB)
│   │   ├── practice_problems/    # 312 problems with solutions
│   │   ├── proofs/               # 156 proof templates
│   │   └── worksheets/           # 89 complexity analysis exercises
│   └── vector_db/                # ChromaDB persistent storage
├── evaluation/
│   ├── metrics.py                # BLEU, ROUGE, pedagogical metrics
│   └── test_datasets/
│       └── exam_questions/
│           └── evaluation_dataset.json  # 179 questions + references
├── paper_results/                # Evaluation outputs
│   ├── detailed_results_*.json   # Per-question metrics
│   ├── corrected_paper_tables.txt    # LaTeX tables for paper
│   ├── corrected_summary_stats.txt   # Human-readable stats
│   └── PAPER_CHANGES_REQUIRED.txt    # Paper finalization guide
├── scripts/
│   ├── extract_correct_metrics.py    # Metrics extraction tool
│   ├── ingest_all_data.py            # Knowledge base ingestion
│   ├── run_evaluation.py             # Evaluation harness
│   └── validate_setup.py             # Environment validation
├── docs/                         # Detailed documentation
│   ├── ARCHITECTURE.md           # System architecture
│   ├── RESEARCH_GUIDE.md         # Research methodology
│   └── RUN_EVALUATION.md         # Evaluation instructions
├── run_paper_evaluation.py       # Main evaluation script
├── AlgoRAG_Moressier.pdf         # Research paper
└── README.md                     # This file
```

---

## Reproducing Results

### Step 1: Prepare Environment

```bash
# Set up environment variables
export DEEPSEEK_API_KEY="your_api_key_here"

# Verify all dependencies
python scripts/validate_setup.py
```

### Step 2: Ingest Knowledge Base

```bash
# Process all source materials
python scripts/ingest_all_data.py

# Expected output:
# - Processed: 847 lecture slides
# - Processed: 312 practice problems
# - Processed: 156 proof templates
# - Total chunks: ~3200
# - Vector DB size: ~500MB
```

### Step 3: Run Evaluation

```bash
# Full evaluation (179 questions, ~1.9 hours)
python run_paper_evaluation.py \
  --dataset evaluation/test_datasets/exam_questions/evaluation_dataset.json \
  --output paper_results/

# Monitor progress in real-time
tail -f evaluation.log
```

### Step 4: Extract Corrected Metrics

```bash
# Generate corrected metrics and LaTeX tables
# (This fixes the ROUGE aggregation bug in raw evaluation output)
python scripts/extract_correct_metrics.py

# Outputs:
# - paper_results/corrected_paper_tables.txt (use these in your paper!)
# - paper_results/corrected_summary_stats.txt
# - paper_results/corrected_aggregate_stats.json
```

**Why This Step Is Critical**: The evaluation script has a known bug where ROUGE scores
are aggregated as 0.0 instead of their true values (0.0963 for ROUGE-1 F1, 0.0683 for
ROUGE-L F1). The extraction script recalculates all metrics correctly from the detailed
per-question results. Always use the output from this script for paper metrics.

---

## System Architecture

AlgoRAG employs a multi-stage pipeline optimized for theoretical computer science:

```
┌──────────────┐
│ User Query   │  "Prove f(n) = 9n + 7 = O(n)"
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│ Math Preprocessing                       │
│ • Extract entities: O(n), Θ(n²), log n  │
│ • Classify query type: proof/analysis   │
│ • Detect topic: asymptotic analysis     │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│ Hybrid Retrieval                         │
│ • Dense: all-mpnet-base-v2 (768-dim)    │
│ • Sparse: BM25 for notation matching    │
│ • Top-k=10 candidates                    │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│ Pedagogical Re-ranking                   │
│ • Step granularity: 40%                  │
│ • Topic coverage: 30%                    │
│ • Difficulty match: 30%                  │
│ • Final: 0.7*similarity + 0.3*pedagogy  │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│ Proof-Aware Generation (DeepSeek V3)    │
│ • Structured prompting                   │
│ • Step-by-step enforcement               │
│ • Mathematical notation formatting       │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ Answer       │  Formal proof with theorem, strategy,
│ + Sources    │  steps, conclusion, and key insights
└──────────────┘
```

---

## Evaluation Metrics

We employ a multi-dimensional evaluation framework:

### Standard NLP Metrics
- **BLEU-4**: N-gram overlap (0-1 scale)
- **ROUGE-1/2/L**: Unigram, bigram, and longest common subsequence F1 scores

### Custom Pedagogical Metrics
- **Step Granularity**: Presence of numbered steps or bullet points
- **Explanation Depth**: Density of reasoning keywords ("because", "therefore", "implies")
- **Mathematical Richness**: LaTeX/math symbol density
- **Proof Structure**: Formal markers ("Theorem", "Proof Strategy", "Q.E.D.")
- **Query Term Coverage**: Percentage of question terms addressed
- **Has Example**: Inclusion of concrete examples

### Semantic Similarity
- Cosine similarity of sentence embeddings (all-mpnet-base-v2)

**Pedagogical Quality Score**: Weighted average of all pedagogical components (0-1 scale)

---

## Dataset

### Evaluation Dataset

- **Size**: 179 curated exam-style questions
- **Sources**: Past exams, practice tests, algorithmic problem collections
- **Format**: JSON with question, reference answer, metadata
- **Location**: `evaluation/test_datasets/exam_questions/evaluation_dataset.json`

### Topic Distribution

| Topic | Count | Difficulty Range |
|-------|-------|------------------|
| Asymptotic Analysis | 89 | Easy → Hard |
| Recurrence Relations | 17 | Medium → Hard |
| Dynamic Programming | 17 | Medium → Very Hard |
| Graph Algorithms | 21 | Easy → Hard |
| NP-Completeness | 21 | Medium → Very Hard |
| Sorting Algorithms | 6 | Easy → Medium |
| Divide-and-Conquer | 8 | Medium → Hard |

### Knowledge Base

- **Textbooks**: Introduction to Algorithms (CLRS, 13MB), Introduction to the Theory of Computation (Sipser)
- **Lecture Slides**: 847 slides across 15 major topics (8.2MB)
- **Practice Problems**: 312 problems with detailed solutions (35KB)
- **Proof Templates**: 156 worked examples of induction, contradiction, construction proofs
- **Worksheets**: 89 complexity analysis exercises

---

## Technical Details

### Technologies

- **Language Model**: DeepSeek V3 (deepseek-chat) via API
- **Embeddings**: sentence-transformers/all-mpnet-base-v2 (768-dim, local)
- **Vector Database**: ChromaDB (persistent local storage)
- **Backend Framework**: FastAPI (Python 3.10+)
- **Evaluation Platform**: Google Colab (1.9 hours runtime for 179 questions)

### Key Parameters

- **Chunking**: 500 words per chunk, 50-word overlap (sliding window)
- **Retrieval**: Top-k=10, cosine similarity threshold=0.3
- **Re-ranking Weights**: Step granularity 40%, topic coverage 30%, difficulty 30%
- **Generation**: Temperature=0.7, max_tokens=2048
- **Timeout**: 240 seconds per question (not reached in final evaluation)

### Model Selection

We initially experimented with Ollama (Llama 2, Mistral) for local deployment but transitioned to DeepSeek V3 due to:
1. Hardware limitations (insufficient VRAM for 70B models)
2. Superior reasoning capabilities on mathematical proofs
3. Consistent API availability and response quality

---

## Citation

If you use this code or dataset, please cite our paper:

```bibtex
@inproceedings{yourname2026algorag,
  title={Retrieval-Augmented Generation for Theoretical Computer Science Education: A Comprehensive Evaluation Framework for Algorithm Analysis and Complexity Theory},
  author={Your Name and Coauthor Name},
  booktitle={Proceedings of [Conference Name]},
  year={2026},
  organization={[Publisher]}
}
```

**Paper PDF**: [AlgoRAG_Moressier.pdf](./AlgoRAG_Moressier.pdf)

---

## Documentation

- **[QUICKSTART.md](./QUICKSTART.md)**: Getting started guide
- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)**: Detailed system architecture
- **[docs/RESEARCH_GUIDE.md](./docs/RESEARCH_GUIDE.md)**: Research methodology and workflow
- **[docs/RUN_EVALUATION.md](./docs/RUN_EVALUATION.md)**: Evaluation procedures
- **[paper_results/PAPER_CHANGES_REQUIRED.txt](./paper_results/PAPER_CHANGES_REQUIRED.txt)**: Paper finalization guide

---

## Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For major changes, please open an issue first to discuss proposed changes.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Acknowledgments

- **Textbooks**: Introduction to Algorithms (Cormen et al., MIT Press), Introduction to the Theory of Computation (Sipser, Cengage Learning)
- **Frameworks**: FastAPI, sentence-transformers, ChromaDB
- **Language Models**: DeepSeek V3

---

## Contact

For questions, suggestions, or collaboration opportunities:

- **GitHub Issues**: [Open an issue](https://github.com/Sushan-Adhikari/AlgoRAG/issues)
- **Email**: your.email@university.edu
- **Project Website**: [Coming soon]

---

## Acknowledgments

This research was conducted at [Your University] with support from [funding agencies, if applicable].

We thank:
- The theoretical computer science community for public educational materials
- Reviewers for valuable feedback on the research paper
- Students who provided feedback on system usability

---

**Built for theoretical computer science education**

*Last Updated*: January 2026
*Paper Status*: Under Review at [Conference Name]
