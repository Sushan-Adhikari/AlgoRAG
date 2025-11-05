#!/usr/bin/env python3
"""
Pre-download embedding model to avoid issues during ingestion.
Run this once before running the main pipeline.
"""

import os
import sys
from pathlib import Path

# Disable HuggingFace telemetry and auth
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "0"

# Remove any auth tokens that might cause issues
for token_var in ["HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_TOKEN"]:
    if token_var in os.environ:
        del os.environ[token_var]

print("="*80)
print("AlgoRAG - Pre-downloading Embedding Model")
print("="*80)
print()
print("This will download the sentence-transformers model (~500MB)")
print("This is a ONE-TIME download and will be cached locally.")
print("No HuggingFace account or authentication needed!")
print()

try:
    print("▶ Installing/checking sentence-transformers...")
    from sentence_transformers import SentenceTransformer
    print("✓ sentence-transformers is installed")
    print()

    model_name = "all-mpnet-base-v2"
    cache_folder = os.path.expanduser("~/.cache/sentence_transformers")

    print(f"▶ Downloading model: {model_name}")
    print(f"  Cache location: {cache_folder}")
    print("  This may take 2-5 minutes depending on your internet speed...")
    print()

    model = SentenceTransformer(
        model_name,
        device="cpu",
        cache_folder=cache_folder
    )

    dim = model.get_sentence_embedding_dimension()

    print()
    print("="*80)
    print("✓ SUCCESS! Embedding model ready")
    print("="*80)
    print(f"Model: {model_name}")
    print(f"Dimension: {dim}")
    print(f"Cached at: {cache_folder}")
    print()
    print("You can now run:")
    print("  python scripts/ingest_all_data.py")
    print("  python scripts/run_complete_research.py")
    print()

except ImportError:
    print()
    print("✗ ERROR: sentence-transformers not installed")
    print()
    print("Install it with:")
    print("  pip install sentence-transformers")
    print()
    sys.exit(1)

except Exception as e:
    print()
    print(f"✗ ERROR: {e}")
    print()
    print("Common fixes:")
    print("1. Check your internet connection")
    print("2. Try running again (downloads can be interrupted)")
    print("3. Clear cache and retry:")
    print(f"   rm -rf {cache_folder}")
    print("   python scripts/download_embedding_model.py")
    print()
    sys.exit(1)
