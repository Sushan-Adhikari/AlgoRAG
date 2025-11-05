#!/usr/bin/env python3
"""
Validation script to check if AlgoRAG research environment is properly configured.
Run this before starting your research experiments.
"""

import sys
import os
from pathlib import Path
import json

# Colors for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Print section header."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")


def check_python_version():
    """Check Python version."""
    print_header("Checking Python Version")

    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} found. Requires Python 3.8+")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print_header("Checking Dependencies")

    required_packages = [
        "numpy",
        "scipy",
        "torch",
        "sentence_transformers",
        "chromadb",
        "fastapi",
        "uvicorn",
        "PyPDF2",
        "nltk",
        "rouge_score",
        "google.generativeai",
        "openai",
        "tqdm"
    ]

    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} - NOT INSTALLED")
            all_installed = False

    if not all_installed:
        print_warning("\nInstall missing packages:")
        print("  cd backend && pip install -r requirements.txt")

    return all_installed


def check_data_files():
    """Check if data files exist."""
    print_header("Checking Data Files")

    project_root = Path(__file__).parent.parent
    knowledge_base = project_root / "data" / "knowledge_base"

    if not knowledge_base.exists():
        print_error(f"Knowledge base directory not found: {knowledge_base}")
        return False

    # Check categories
    categories = {
        "textbooks": ["*.pdf"],
        "lecture_slides": ["*.pdf"],
        "practice_problems": ["*.txt", "*.json"],
        "proofs": ["*.txt"],
        "worksheets": ["*.txt"]
    }

    total_files = 0
    for category, patterns in categories.items():
        category_path = knowledge_base / category

        if not category_path.exists():
            print_warning(f"{category}: directory not found")
            continue

        files = []
        for pattern in patterns:
            files.extend(list(category_path.glob(pattern)))

        if files:
            print_success(f"{category}: {len(files)} file(s)")
            total_files += len(files)
            for f in files:
                print(f"    - {f.name} ({f.stat().st_size / 1024 / 1024:.1f} MB)")
        else:
            print_warning(f"{category}: no files found")

    if total_files == 0:
        print_error("\nNo data files found!")
        print("Please add PDFs and text files to data/knowledge_base/")
        return False

    print_success(f"\nTotal data files: {total_files}")
    return True


def check_vector_database():
    """Check if vector database exists."""
    print_header("Checking Vector Database")

    project_root = Path(__file__).parent.parent
    vector_db = project_root / "data" / "vector_db"

    if not vector_db.exists():
        print_warning("Vector database not found")
        print("Run: python scripts/ingest_all_data.py")
        return False

    # Try to check ChromaDB
    try:
        sys.path.insert(0, str(project_root / "backend"))
        import chromadb

        client = chromadb.PersistentClient(path=str(vector_db))
        collections = client.list_collections()

        if collections:
            for collection in collections:
                count = collection.count()
                print_success(f"Collection '{collection.name}': {count} documents")

            if count < 100:
                print_warning(f"Only {count} documents indexed. Expected 1000+")
                print("Consider re-running: python scripts/ingest_all_data.py")

            return True
        else:
            print_warning("No collections found in vector database")
            print("Run: python scripts/ingest_all_data.py")
            return False

    except Exception as e:
        print_error(f"Could not check vector database: {e}")
        return False


def check_environment_variables():
    """Check if required environment variables are set."""
    print_header("Checking Environment Variables")

    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"

    if not env_file.exists():
        print_warning(".env file not found")
        print("Copy .env.example to .env and configure API keys")
        return False

    # Read .env
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

    # Check important variables
    important_vars = {
        "GEMINI_API_KEY": False,
        "OPENAI_API_KEY": False
    }

    for var in important_vars:
        if var in env_vars and env_vars[var]:
            print_success(f"{var} configured")
            important_vars[var] = True
        else:
            print_warning(f"{var} not configured")

    if not any(important_vars.values()):
        print_error("\nNo LLM API keys configured!")
        print("At least one of GEMINI_API_KEY or OPENAI_API_KEY is required")
        return False

    return True


def check_test_dataset():
    """Check if test datasets exist."""
    print_header("Checking Test Datasets")

    project_root = Path(__file__).parent.parent
    test_dir = project_root / "evaluation" / "test_datasets"

    if not test_dir.exists():
        print_warning(f"Test datasets directory not found: {test_dir}")
        return False

    # Find test files
    test_files = list(test_dir.glob("*.json"))

    if not test_files:
        print_warning("No test dataset JSON files found")
        print(f"Add test cases to: {test_dir}")
        return False

    total_cases = 0
    for test_file in test_files:
        try:
            with open(test_file, 'r') as f:
                data = json.load(f)

            if isinstance(data, dict) and "test_cases" in data:
                num_cases = len(data["test_cases"])
            elif isinstance(data, list):
                num_cases = len(data)
            else:
                num_cases = 0

            print_success(f"{test_file.name}: {num_cases} test cases")
            total_cases += num_cases

        except Exception as e:
            print_error(f"{test_file.name}: Error loading - {e}")

    print_success(f"\nTotal test cases: {total_cases}")

    if total_cases < 100:
        print_warning(f"Only {total_cases} test cases found")
        print("Your paper targets 450+ test cases for comprehensive evaluation")

    return total_cases > 0


def check_scripts():
    """Check if research scripts exist."""
    print_header("Checking Research Scripts")

    project_root = Path(__file__).parent.parent
    scripts_dir = project_root / "scripts"

    required_scripts = [
        "ingest_all_data.py",
        "run_research_evaluation.py",
        "analyze_results.py"
    ]

    all_exist = True
    for script in required_scripts:
        script_path = scripts_dir / script

        if script_path.exists():
            print_success(f"{script}")
        else:
            print_error(f"{script} - NOT FOUND")
            all_exist = False

    return all_exist


def print_recommendations(results):
    """Print recommendations based on validation results."""
    print_header("Recommendations")

    if not results["python_version"]:
        print("1. Upgrade Python to 3.8 or higher")

    if not results["dependencies"]:
        print("1. Install missing dependencies:")
        print("   cd backend && pip install -r requirements.txt")

    if not results["data_files"]:
        print("2. Add data files to data/knowledge_base/:")
        print("   - PDFs in textbooks/ and lecture_slides/")
        print("   - Text files in practice_problems/, proofs/, worksheets/")

    if not results["environment_vars"]:
        print("3. Configure API keys:")
        print("   - Copy .env.example to .env")
        print("   - Add GEMINI_API_KEY or OPENAI_API_KEY")

    if not results["vector_database"]:
        print("4. Ingest data into vector database:")
        print("   python scripts/ingest_all_data.py")

    if not results["test_dataset"]:
        print("5. Create test dataset:")
        print("   - Add test cases to evaluation/test_datasets/")
        print("   - Target: 450+ test cases (90+ per topic)")

    if all(results.values()):
        print_success("\n🎉 All checks passed! Your environment is ready.")
        print("\nNext steps:")
        print("1. Run ingestion (if not done):")
        print("   python scripts/ingest_all_data.py")
        print("\n2. Run evaluation:")
        print("   python scripts/run_research_evaluation.py --test-file <test_file>")
        print("\n3. Analyze results:")
        print("   python scripts/analyze_results.py --results-file <results_file>")
    else:
        print_warning("\n⚠ Some checks failed. Fix issues above before proceeding.")


def main():
    """Main validation function."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}AlgoRAG Research Environment Validation{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")

    results = {
        "python_version": check_python_version(),
        "dependencies": check_dependencies(),
        "data_files": check_data_files(),
        "environment_vars": check_environment_variables(),
        "vector_database": check_vector_database(),
        "test_dataset": check_test_dataset(),
        "scripts": check_scripts()
    }

    print_recommendations(results)

    # Summary
    passed = sum(results.values())
    total = len(results)

    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}Validation Summary: {passed}/{total} checks passed{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
