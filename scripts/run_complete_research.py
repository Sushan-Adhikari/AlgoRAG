#!/usr/bin/env python3
"""
Complete Research Evaluation Workflow for AlgoRAG
Uses the real evaluation dataset with 179 exam questions
"""

import sys
import subprocess
from pathlib import Path
import time
from datetime import datetime

def print_header(text):
    """Print section header."""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"▶ {description}...")
    print(f"  Command: {' '.join(cmd)}")
    print()

    start = time.time()
    result = subprocess.run(cmd, capture_output=False)
    elapsed = time.time() - start

    if result.returncode == 0:
        print(f"✓ {description} completed ({elapsed:.1f}s)")
        return True
    else:
        print(f"✗ {description} failed!")
        return False

def main():
    """Run complete research workflow."""
    project_root = Path(__file__).parent.parent

    print_header("AlgoRAG Complete Research Evaluation Workflow")
    print(f"Project: {project_root}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Configuration
    real_dataset = project_root / "evaluation" / "test_datasets" / "exam_questions" / "evaluation_dataset.json"
    vector_db = project_root / "data" / "vector_db"
    results_dir = project_root / "results"
    analysis_dir = project_root / "analysis"

    # Check prerequisites
    print_header("Step 1: Checking Prerequisites")

    if not real_dataset.exists():
        print(f"✗ Real dataset not found: {real_dataset}")
        print("  Please ensure evaluation_dataset.json exists!")
        sys.exit(1)
    print(f"✓ Found real dataset: {real_dataset}")
    print(f"  (179 exam questions covering 7 topics)")

    if not vector_db.exists():
        print(f"⚠ Vector database not found: {vector_db}")
        print("  You need to run data ingestion first!")
        print(f"\n  Run: python {project_root}/scripts/ingest_all_data.py\n")

        response = input("Run data ingestion now? (y/n): ").lower()
        if response == 'y':
            print_header("Running Data Ingestion")
            success = run_command(
                [sys.executable, str(project_root / "scripts" / "ingest_all_data.py")],
                "Data ingestion"
            )
            if not success:
                print("✗ Ingestion failed! Please fix errors and try again.")
                sys.exit(1)
        else:
            print("✗ Cannot proceed without vector database!")
            sys.exit(1)
    else:
        print(f"✓ Vector database exists: {vector_db}")

    # Validate setup
    print_header("Step 2: Validating Environment")

    success = run_command(
        [sys.executable, str(project_root / "scripts" / "validate_setup.py")],
        "Environment validation"
    )

    if not success:
        print("\n⚠ Validation found issues. Please fix them before continuing.")
        response = input("Continue anyway? (y/n): ").lower()
        if response != 'y':
            sys.exit(1)

    # Run evaluation
    print_header("Step 3: Running Evaluation on Real Dataset")
    print("Dataset: evaluation_dataset.json")
    print("Questions: 179 exam questions")
    print("Topics: asymptotic_analysis, recurrence_relations, dynamic_programming,")
    print("        graph_algorithms, np_completeness, sorting_algorithms, divide_and_conquer")
    print("Estimated time: 10-30 minutes (depending on LLM speed)")
    print()

    response = input("Start evaluation? (y/n): ").lower()
    if response != 'y':
        print("Evaluation cancelled.")
        sys.exit(0)

    success = run_command(
        [
            sys.executable,
            str(project_root / "scripts" / "run_research_evaluation.py"),
            "--test-file", str(real_dataset),
            "--llm-backend", "ollama",
            "--results-dir", str(results_dir)
        ],
        "Complete evaluation on 179 questions"
    )

    if not success:
        print("\n✗ Evaluation failed!")
        print("Check the error messages above and try again.")
        sys.exit(1)

    # Find latest results file
    print_header("Step 4: Analyzing Results")

    results_files = sorted(results_dir.glob("detailed_results_*.json"))
    if not results_files:
        print("✗ No results files found!")
        sys.exit(1)

    latest_results = results_files[-1]
    print(f"Latest results: {latest_results.name}")

    success = run_command(
        [
            sys.executable,
            str(project_root / "scripts" / "analyze_results.py"),
            "--results-file", str(latest_results),
            "--output-dir", str(analysis_dir)
        ],
        "Results analysis and table generation"
    )

    if not success:
        print("\n✗ Analysis failed!")
        sys.exit(1)

    # Summary
    print_header("🎉 Research Evaluation Complete!")

    print("Results saved to:")
    print(f"  📄 Detailed results: {latest_results}")
    print(f"  📊 Analysis: {analysis_dir}/")
    print()
    print("Files generated for your paper:")
    print(f"  📝 {analysis_dir}/results_table.tex")
    print(f"  📝 {analysis_dir}/pedagogical_table.tex")
    print(f"  📝 {analysis_dir}/statistics_summary.json")
    print(f"  📝 {analysis_dir}/full_report.txt")
    print()
    print("Next steps:")
    print("  1. Review: cat analysis/full_report.txt")
    print("  2. Copy LaTeX tables to your paper")
    print("  3. Use statistics_summary.json for results section")
    print()
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

if __name__ == "__main__":
    main()
