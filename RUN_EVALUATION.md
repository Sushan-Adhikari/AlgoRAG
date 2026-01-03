# Running AlgoRAG Evaluation

## Quick Start (Colab with DeepSeek - Cheapest!)

### Step 1: Upload to Google Colab

1. Zip this folder: `zip -r AlgoRAG.zip AlgoRAG`
2. Upload to Google Drive
3. Open Colab: https://colab.research.google.com

### Step 2: Run Evaluation

Copy-paste into Colab:

```python
# Mount Drive
from google.colab import drive
drive.mount('/content/drive')

# Navigate to your folder
import os
os.chdir('/content/drive/MyDrive/AlgoRAG')  # Adjust path!

# Install dependencies
!pip install -q -r requirements_eval.txt

# Set DeepSeek API key (get from: https://platform.deepseek.com)
os.environ['DEEPSEEK_API_KEY'] = 'YOUR_KEY_HERE'

# Run evaluation on ALL 179 questions
!python run_paper_evaluation.py
```

**Cost: ~$0.09 for full run (179 questions)**

### Step 3: Download Results

Results will be in `paper_results/` folder. Download:
- `aggregate_stats_TIMESTAMP.json`
- `paper_tables_TIMESTAMP.txt`

---

## Alternative APIs

### Gemini (Free tier available)
```python
os.environ['GEMINI_API_KEY'] = 'your-key'
# Get key: https://aistudio.google.com/app/apikey
```

### OpenAI (Paid)
```python
os.environ['OPENAI_API_KEY'] = 'your-key'
```

---

## Configuration

### Run subset for testing
```python
os.environ['NUM_QUESTIONS'] = '20'  # Test with 20 questions
```

### Manual backend selection
```python
os.environ['GENERATOR_BACKEND'] = 'deepseek'  # or 'gemini' or 'openai'
```

---

## Cost Comparison (179 questions)

| API | Cost per run | Notes |
|-----|--------------|-------|
| **DeepSeek** | **$0.09** | Cheapest, OpenAI-compatible |
| Gemini | $0.20-0.50 | Free tier available |
| OpenAI GPT-4 | $2-5 | Most expensive |

**Your $1.60 budget:**
- DeepSeek: ~17 runs
- Gemini: ~3-8 runs
- GPT-4: 1 run

---

## Expected Runtime

- **20 questions**: 1-2 hours
- **50 questions**: 3-4 hours
- **179 questions (full)**: 8-12 hours

Let it run overnight!

---

## Troubleshooting

### "No API key found"
Set the API key before running:
```python
os.environ['DEEPSEEK_API_KEY'] = 'your-key-here'
```

### "Vector database not found"
Ensure `data/vector_db/` folder is included when you upload.

### "Out of memory"
Use Colab Pro or run in batches:
```python
os.environ['NUM_QUESTIONS'] = '50'
```

---

## Output Files

After completion, `paper_results/` contains:

1. **detailed_results_TIMESTAMP.json** - All Q&A pairs
2. **aggregate_stats_TIMESTAMP.json** - Summary statistics for paper
3. **paper_tables_TIMESTAMP.txt** - LaTeX tables ready to copy

Use these to update your PDF paper!

---

## Next Steps

1. Run evaluation (tonight)
2. Download results
3. Update PDF paper with real statistics
4. Fix author placeholder names
5. Submit!
