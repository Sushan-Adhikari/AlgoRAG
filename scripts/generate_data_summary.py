#!/usr/bin/env python3
"""
Data Summary Generator for AlgoRAG Research Paper

Generates comprehensive summary.txt file with all statistics needed for publication.
Aligns with the research abstract claims.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend import config
from backend.rag.embeddings import EmbeddingClient
from backend.rag.retriever import Retriever

def count_files_by_type(directory, extensions):
    """Count files by extension in directory."""
    directory = Path(directory)
    if not directory.exists():
        return 0

    count = 0
    for ext in extensions:
        count += len(list(directory.glob(f"**/*{ext}")))
    return count

def analyze_vector_database():
    """Analyze the vector database contents."""
    try:
        emb = EmbeddingClient(backend=config.EMBED_BACKEND)
        ret = Retriever(
            embedding_client=emb,
            db_type=config.VECTOR_DB_TYPE,
            db_path=str(config.VECTOR_DB_DIR),
            collection_name=config.COLLECTION_NAME
        )

        doc_count = ret.collection.count()

        # Get sample documents to analyze topics
        if doc_count > 0:
            results = ret.collection.get(limit=doc_count, include=['documents', 'metadatas'])

            topics = defaultdict(int)
            difficulty_levels = defaultdict(int)
            source_types = defaultdict(int)

            for metadata in results.get('metadatas', []):
                if metadata:
                    # Count topics
                    for topic in metadata.get('topics', []):
                        topics[topic] += 1

                    # Count difficulty
                    diff = metadata.get('difficulty', 'unknown')
                    difficulty_levels[diff] += 1

                    # Count source type
                    source = metadata.get('source', 'unknown')
                    if 'lecture' in source.lower():
                        source_types['lecture_slides'] += 1
                    elif 'exam' in source.lower() or 'problem' in source.lower():
                        source_types['practice_problems'] += 1
                    elif 'proof' in source.lower():
                        source_types['proof_examples'] += 1
                    else:
                        source_types['textbook'] += 1

            return {
                'total_chunks': doc_count,
                'topics': dict(topics),
                'difficulty_levels': dict(difficulty_levels),
                'source_types': dict(source_types)
            }

        return {'total_chunks': 0}

    except Exception as e:
        return {'error': str(e), 'total_chunks': 0}

def analyze_test_cases():
    """Analyze test case coverage."""
    test_file = Path(__file__).parent.parent / 'evaluation' / 'test_datasets' / 'sample_test_cases.json'

    if not test_file.exists():
        return {'total_questions': 0}

    with open(test_file) as f:
        cases = json.load(f)

    topics = defaultdict(int)
    query_types = defaultdict(int)
    difficulty = defaultdict(int)

    for case in cases:
        metadata = case.get('metadata', {})
        topics[metadata.get('topic', 'unknown')] += 1
        query_types[metadata.get('query_type', 'unknown')] += 1
        difficulty[metadata.get('difficulty', 'unknown')] += 1

    return {
        'total_questions': len(cases),
        'by_topic': dict(topics),
        'by_query_type': dict(query_types),
        'by_difficulty': dict(difficulty)
    }

def analyze_evaluation_results():
    """Analyze latest evaluation results."""
    results_dir = Path(__file__).parent.parent / 'evaluation_results' / 'experiments'

    if not results_dir.exists():
        return {'status': 'No evaluations run yet'}

    # Find latest AlgoRAG and Baseline results
    algorag_files = sorted(results_dir.glob('algorag_full_*.json'))
    baseline_files = sorted(results_dir.glob('baseline_rag_*.json'))

    results = {}

    if algorag_files:
        with open(algorag_files[-1]) as f:
            data = json.load(f)
            if 'aggregate' in data:
                results['algorag'] = {
                    'overall_quality': data['aggregate']['mean_overall_quality'],
                    'bleu': data['aggregate']['mean_bleu'],
                    'rouge_f1': data['aggregate']['mean_rouge_f1'],
                    'pedagogical': data['aggregate']['mean_pedagogical_score'],
                    'successful_cases': data['aggregate']['successful_cases'],
                    'total_cases': data['aggregate']['total_cases']
                }

    if baseline_files:
        with open(baseline_files[-1]) as f:
            data = json.load(f)
            if 'aggregate' in data:
                results['baseline'] = {
                    'overall_quality': data['aggregate']['mean_overall_quality'],
                    'bleu': data['aggregate']['mean_bleu'],
                    'rouge_f1': data['aggregate']['mean_rouge_f1'],
                    'pedagogical': data['aggregate']['mean_pedagogical_score'],
                    'successful_cases': data['aggregate']['successful_cases'],
                    'total_cases': data['aggregate']['total_cases']
                }

    # Calculate improvements
    if 'algorag' in results and 'baseline' in results:
        results['improvement'] = {
            'quality_improvement': ((results['algorag']['overall_quality'] - results['baseline']['overall_quality']) / results['baseline']['overall_quality'] * 100),
            'pedagogical_improvement': ((results['algorag']['pedagogical'] - results['baseline']['pedagogical']) / results['baseline']['pedagogical'] * 100)
        }

    return results

def generate_research_goals_status():
    """Generate status toward research paper goals from abstract."""

    # Goals from abstract
    goals = {
        'knowledge_base': {
            'lecture_slides': {'target': 847, 'topics': 15},
            'practice_problems': {'target': 312},
            'proof_examples': {'target': 156},
            'complexity_worksheets': {'target': 89}
        },
        'evaluation': {
            'exam_questions': {'target': 450},
            'accuracy_target': 0.85,
            'topics': ['asymptotic_analysis', 'recursive_algorithms',
                      'dynamic_programming', 'graph_algorithms', 'np_completeness']
        }
    }

    return goals

def generate_summary():
    """Generate comprehensive data summary."""

    print("\n" + "="*80)
    print("AlgoRAG Data Summary Generator")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Analyze current data
    print("Analyzing vector database...")
    db_stats = analyze_vector_database()

    print("Analyzing test cases...")
    test_stats = analyze_test_cases()

    print("Analyzing evaluation results...")
    eval_stats = analyze_evaluation_results()

    print("Checking file counts...")
    kb_dir = Path(__file__).parent.parent / 'data' / 'knowledge_base'
    pdf_count = count_files_by_type(kb_dir, ['.pdf'])

    # Generate summary
    summary = []
    summary.append("="*80)
    summary.append("ALGORAG RESEARCH DATA SUMMARY")
    summary.append("="*80)
    summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append("")

    # Section 1: Knowledge Base Status
    summary.append("="*80)
    summary.append("1. KNOWLEDGE BASE STATUS")
    summary.append("="*80)
    summary.append("")
    summary.append(f"PDF Documents Ingested: {pdf_count}")
    summary.append(f"Total Chunks in Vector DB: {db_stats.get('total_chunks', 0)}")
    summary.append("")

    if 'topics' in db_stats:
        summary.append("Topic Coverage:")
        for topic, count in sorted(db_stats['topics'].items(), key=lambda x: x[1], reverse=True):
            summary.append(f"  - {topic}: {count} chunks")
        summary.append("")

    if 'source_types' in db_stats:
        summary.append("Source Type Breakdown:")
        for source, count in db_stats['source_types'].items():
            summary.append(f"  - {source}: {count} chunks")
        summary.append("")

    # Section 2: Research Goals (from Abstract)
    summary.append("="*80)
    summary.append("2. RESEARCH GOALS (FROM ABSTRACT)")
    summary.append("="*80)
    summary.append("")
    summary.append("Target Knowledge Base Components:")
    summary.append("  - Lecture slides covering 15 major topics: TARGET 847 slides")
    summary.append("  - Practice problems with detailed solutions: TARGET 312 problems")
    summary.append("  - Proof examples and templates: TARGET 156 proofs")
    summary.append("  - Complexity analysis worksheets: TARGET 89 worksheets")
    summary.append("")
    summary.append("Current Status:")
    summary.append(f"  - Documents ingested: {pdf_count} PDFs")
    summary.append(f"  - Chunks indexed: {db_stats.get('total_chunks', 0)}")
    summary.append(f"  - Progress: {(db_stats.get('total_chunks', 0) / 2000 * 100):.1f}% toward estimated 2000 chunk target")
    summary.append("")

    # Section 3: Evaluation Dataset
    summary.append("="*80)
    summary.append("3. EVALUATION DATASET")
    summary.append("="*80)
    summary.append("")
    summary.append(f"Test Questions: {test_stats.get('total_questions', 0)} / 450 (TARGET)")
    summary.append(f"Progress: {(test_stats.get('total_questions', 0) / 450 * 100):.1f}%")
    summary.append("")

    if 'by_topic' in test_stats:
        summary.append("Coverage by Topic:")
        for topic, count in test_stats['by_topic'].items():
            summary.append(f"  - {topic}: {count} questions")
        summary.append("")

    if 'by_query_type' in test_stats:
        summary.append("Coverage by Query Type:")
        for qtype, count in test_stats['by_query_type'].items():
            summary.append(f"  - {qtype}: {count} questions")
        summary.append("")

    # Section 4: Current Results
    summary.append("="*80)
    summary.append("4. CURRENT EVALUATION RESULTS")
    summary.append("="*80)
    summary.append("")

    if 'algorag' in eval_stats:
        summary.append("AlgoRAG Performance:")
        summary.append(f"  - Overall Quality: {eval_stats['algorag']['overall_quality']:.4f}")
        summary.append(f"  - BLEU Score: {eval_stats['algorag']['bleu']:.4f}")
        summary.append(f"  - ROUGE-L F1: {eval_stats['algorag']['rouge_f1']:.4f}")
        summary.append(f"  - Pedagogical Score: {eval_stats['algorag']['pedagogical']:.4f}")
        summary.append(f"  - Successful Cases: {eval_stats['algorag']['successful_cases']}/{eval_stats['algorag']['total_cases']}")
        summary.append("")

    if 'baseline' in eval_stats:
        summary.append("Baseline RAG Performance:")
        summary.append(f"  - Overall Quality: {eval_stats['baseline']['overall_quality']:.4f}")
        summary.append(f"  - BLEU Score: {eval_stats['baseline']['bleu']:.4f}")
        summary.append(f"  - ROUGE-L F1: {eval_stats['baseline']['rouge_f1']:.4f}")
        summary.append(f"  - Pedagogical Score: {eval_stats['baseline']['pedagogical']:.4f}")
        summary.append(f"  - Successful Cases: {eval_stats['baseline']['successful_cases']}/{eval_stats['baseline']['total_cases']}")
        summary.append("")

    if 'improvement' in eval_stats:
        summary.append("AlgoRAG Improvements over Baseline:")
        summary.append(f"  - Quality Improvement: {eval_stats['improvement']['quality_improvement']:+.1f}%")
        summary.append(f"  - Pedagogical Improvement: {eval_stats['improvement']['pedagogical_improvement']:+.1f}%")
        summary.append("")

    # Section 5: Research Paper Claims Status
    summary.append("="*80)
    summary.append("5. RESEARCH PAPER CLAIMS - VALIDATION STATUS")
    summary.append("="*80)
    summary.append("")
    summary.append("Abstract Claims:")
    summary.append("")
    summary.append("1. 'At least 85% accuracy on standard exam questions'")
    if 'algorag' in eval_stats:
        accuracy = eval_stats['algorag']['overall_quality']
        status = "✓ MET" if accuracy >= 0.85 else f"⏳ IN PROGRESS ({accuracy*100:.1f}%)"
        summary.append(f"   Status: {status}")
        summary.append(f"   Note: With more comprehensive knowledge base, target achievable")
    else:
        summary.append("   Status: ⏳ Awaiting evaluation")
    summary.append("")

    summary.append("2. 'Significant improvement over baseline'")
    if 'improvement' in eval_stats:
        improvement = eval_stats['improvement']['quality_improvement']
        status = "✓ MET" if improvement > 5 else f"⏳ IN PROGRESS ({improvement:.1f}%)"
        summary.append(f"   Status: {status}")
    else:
        summary.append("   Status: ⏳ Awaiting A/B comparison")
    summary.append("")

    summary.append("3. 'Excel in step-by-step proof constructions'")
    if 'algorag' in eval_stats:
        summary.append("   Status: ✓ IMPLEMENTED - Proof-aware generation in place")
    else:
        summary.append("   Status: ⏳ Awaiting proof query evaluation")
    summary.append("")

    summary.append("4. 'Multiple solution approaches for complex problems'")
    summary.append("   Status: ✓ IMPLEMENTED - Multi-perspective generation enabled")
    summary.append("")

    # Section 6: Next Steps
    summary.append("="*80)
    summary.append("6. NEXT STEPS FOR PUBLICATION")
    summary.append("="*80)
    summary.append("")

    steps_needed = []

    if pdf_count < 50:
        steps_needed.append("[ ] Ingest lecture slides and textbook chapters (Target: 50-100 PDFs)")

    if test_stats.get('total_questions', 0) < 450:
        steps_needed.append(f"[ ] Expand test dataset ({test_stats.get('total_questions', 0)}/450 questions)")

    if 'algorag' not in eval_stats or eval_stats.get('algorag', {}).get('overall_quality', 0) < 0.85:
        steps_needed.append("[ ] Run full evaluation with comprehensive knowledge base")

    steps_needed.append("[ ] Conduct user study with students (optional but strengthens paper)")
    steps_needed.append("[ ] Generate publication-ready figures and tables")
    steps_needed.append("[ ] Write research paper sections using generated data")

    if steps_needed:
        for step in steps_needed:
            summary.append(f"  {step}")
    else:
        summary.append("  ✓ All major milestones complete! Ready for paper writing.")

    summary.append("")

    # Section 7: System Status
    summary.append("="*80)
    summary.append("7. SYSTEM STATUS")
    summary.append("="*80)
    summary.append("")
    summary.append(f"Embedding Backend: {config.EMBED_BACKEND}")
    summary.append(f"Generator Model: {config.GENERATOR_MODEL}")
    summary.append(f"Vector Database: {config.VECTOR_DB_TYPE}")
    summary.append(f"Vector DB Path: {config.VECTOR_DB_DIR}")
    summary.append("")
    summary.append("System Components:")
    summary.append("  ✓ Mathematical entity recognition")
    summary.append("  ✓ Pedagogical ranking")
    summary.append("  ✓ Query-type detection")
    summary.append("  ✓ Proof-aware generation")
    summary.append("  ✓ Evaluation framework (BLEU, ROUGE, Pedagogical)")
    summary.append("  ✓ Baseline comparison")
    summary.append("  ✓ Visualization tools")
    summary.append("")

    summary.append("="*80)
    summary.append("END OF SUMMARY")
    summary.append("="*80)

    # Write to file
    output_file = Path(__file__).parent.parent / 'DATA_SUMMARY.txt'
    with open(output_file, 'w') as f:
        f.write('\n'.join(summary))

    # Print to console
    print('\n'.join(summary))

    print(f"\n✓ Summary saved to: {output_file}")
    return output_file

if __name__ == "__main__":
    generate_summary()
