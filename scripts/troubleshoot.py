#!/usr/bin/env python3
"""
Troubleshooting script for AlgoRAG.
Diagnoses common issues and suggests fixes.
"""

import sys
import os
from pathlib import Path
import subprocess

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def check_item(description, success):
    if success:
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description}")
        return False

def main():
    print_header("AlgoRAG Troubleshooting")

    all_ok = True
    issues = []

    # Check 1: Python version
    print_header("1. Python Version")
    import sys
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        check_item(f"Python {version.major}.{version.minor}.{version.micro}", True)
    else:
        all_ok = False
        check_item(f"Python {version.major}.{version.minor} (need 3.8+)", False)
        issues.append("Upgrade Python to 3.8+")

    # Check 2: Critical packages
    print_header("2. Critical Packages")

    required = {
        "sentence_transformers": "Embeddings (local)",
        "chromadb": "Vector database",
        "fastapi": "Web server",
        "torch": "PyTorch (for embeddings)",
    }

    for package, purpose in required.items():
        try:
            __import__(package)
            check_item(f"{package} - {purpose}", True)
        except ImportError:
            all_ok = False
            check_item(f"{package} - {purpose}", False)
            issues.append(f"Install {package}: pip install {package}")

    # Check 3: Ollama
    print_header("3. Ollama")

    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            check_item("Ollama server is running", True)

            # Check for llama3.1:7b
            data = response.json()
            models = [m.get('name', '') for m in data.get('models', [])]
            if any('llama3.1' in m and '7b' in m for m in models):
                check_item("llama3.1:7b model available", True)
            else:
                all_ok = False
                check_item("llama3.1:7b model available", False)
                issues.append("Pull model: ollama pull llama3.1:7b")
        else:
            all_ok = False
            check_item("Ollama server is running", False)
            issues.append("Start Ollama: ollama serve")
    except:
        all_ok = False
        check_item("Ollama server is running", False)
        issues.append("Start Ollama: ollama serve")

    # Check 4: Environment file
    print_header("4. Environment Configuration")

    env_file = Path(".env")
    if env_file.exists():
        check_item(".env file exists", True)

        # Check contents
        with open(env_file) as f:
            content = f.read()
            if "EMBED_BACKEND=local" in content or "EMBED_BACKEND = local" in content:
                check_item("EMBED_BACKEND=local configured", True)
            else:
                all_ok = False
                check_item("EMBED_BACKEND=local configured", False)
                issues.append("Set EMBED_BACKEND=local in .env")

            if "GENERATOR_BACKEND=ollama" in content or "GENERATOR_BACKEND = ollama" in content:
                check_item("GENERATOR_BACKEND=ollama configured", True)
            else:
                all_ok = False
                check_item("GENERATOR_BACKEND=ollama configured", False)
                issues.append("Set GENERATOR_BACKEND=ollama in .env")
    else:
        all_ok = False
        check_item(".env file exists", False)
        issues.append("Create .env: cp .env.example .env")

    # Check 5: Data files
    print_header("5. Data Files")

    data_dir = Path("data/knowledge_base")
    if data_dir.exists():
        check_item("Knowledge base directory exists", True)

        # Count files
        pdf_count = len(list(data_dir.glob("**/*.pdf")))
        txt_count = len(list(data_dir.glob("**/*.txt")))

        if pdf_count >= 3:
            check_item(f"PDFs found: {pdf_count}", True)
        else:
            all_ok = False
            check_item(f"PDFs found: {pdf_count} (expected 3+)", False)
            issues.append("Add PDFs to data/knowledge_base/")

        if txt_count >= 3:
            check_item(f"Text files found: {txt_count}", True)
        else:
            all_ok = False
            check_item(f"Text files found: {txt_count} (expected 3+)", False)
    else:
        all_ok = False
        check_item("Knowledge base directory exists", False)
        issues.append("Create data/knowledge_base/ directory")

    # Check 6: Vector database
    print_header("6. Vector Database")

    vector_db = Path("data/vector_db")
    if vector_db.exists():
        check_item("Vector database directory exists", True)
        # Try to count documents
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(vector_db))
            collections = client.list_collections()
            if collections:
                count = collections[0].count()
                if count > 0:
                    check_item(f"Documents indexed: {count}", True)
                else:
                    all_ok = False
                    check_item("Documents indexed: 0 (need to ingest)", False)
                    issues.append("Run ingestion: python scripts/ingest_all_data.py")
            else:
                all_ok = False
                check_item("Vector database has collections", False)
                issues.append("Run ingestion: python scripts/ingest_all_data.py")
        except:
            check_item("Vector database accessible", False)
            issues.append("Reinitialize: rm -rf data/vector_db && python scripts/ingest_all_data.py")
    else:
        all_ok = False
        check_item("Vector database directory exists", False)
        issues.append("Run ingestion: python scripts/ingest_all_data.py")

    # Check 7: Embedding model
    print_header("7. Embedding Model")

    cache_dir = Path.home() / ".cache" / "sentence_transformers"
    if cache_dir.exists():
        # Check if all-mpnet-base-v2 is downloaded
        model_dirs = list(cache_dir.glob("**/all-mpnet-base-v2*"))
        if model_dirs:
            check_item("Embedding model downloaded (all-mpnet-base-v2)", True)
        else:
            all_ok = False
            check_item("Embedding model downloaded", False)
            issues.append("Download model: python scripts/download_embedding_model.py")
    else:
        all_ok = False
        check_item("Embedding model cache exists", False)
        issues.append("Download model: python scripts/download_embedding_model.py")

    # Check 8: HuggingFace auth issues
    print_header("8. HuggingFace Configuration")

    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if hf_token:
        all_ok = False
        check_item("No HF_TOKEN set (good - not needed)", False)
        issues.append("Unset HF_TOKEN: unset HF_TOKEN (or remove from .env)")
    else:
        check_item("No HF_TOKEN set (good - not needed)", True)

    telemetry = os.environ.get("HF_HUB_DISABLE_TELEMETRY")
    if telemetry == "1":
        check_item("HF telemetry disabled", True)
    else:
        check_item("HF telemetry disabled", False)
        issues.append("Add to .env: HF_HUB_DISABLE_TELEMETRY=1")

    # Summary
    print_header("Summary")

    if all_ok:
        print("✓ All checks passed!")
        print()
        print("You're ready to run:")
        print("  python scripts/run_complete_research.py")
    else:
        print(f"✗ Found {len(issues)} issue(s) to fix:")
        print()
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        print()
        print("Fix these issues and run troubleshoot.py again")

    print()
    print("="*80)

if __name__ == "__main__":
    main()
