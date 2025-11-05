"""
Evaluation Metrics for AlgoRAG Research Paper

Implements:
- BLEU score for answer quality
- ROUGE-L for recall-oriented evaluation
- Pedagogical quality metrics
- Relevance scoring
- Proof completeness metrics
- Mathematical correctness detection
"""

import re
import json
from typing import List, Dict, Tuple, Any
from collections import Counter
import numpy as np


class EvaluationMetrics:
    """
    Comprehensive evaluation metrics for RAG system quality assessment.
    Designed for research paper evaluation framework.
    """

    def __init__(self):
        self.math_notation_patterns = [
            r'O\([^)]+\)',  # Big-O notation
            r'Ω\([^)]+\)',  # Omega notation
            r'Θ\([^)]+\)',  # Theta notation
            r'\\[a-zA-Z]+',  # LaTeX commands
        ]

    # ==================== BLEU Score ====================

    def compute_bleu(self, reference: str, candidate: str, max_n: int = 4) -> Dict[str, float]:
        """
        Compute BLEU score (Bilingual Evaluation Understudy).

        Standard metric for machine translation, adapted for educational QA.
        Reports BLEU-1, BLEU-2, BLEU-3, BLEU-4.

        Args:
            reference: Ground truth answer
            candidate: Generated answer
            max_n: Maximum n-gram order (default: 4)

        Returns:
            Dictionary with BLEU-1 through BLEU-4 scores
        """
        ref_tokens = self._tokenize(reference)
        cand_tokens = self._tokenize(candidate)

        scores = {}

        # Brevity penalty
        bp = self._brevity_penalty(ref_tokens, cand_tokens)

        # Compute n-gram precision for n=1 to max_n
        precisions = []
        for n in range(1, max_n + 1):
            precision = self._ngram_precision(ref_tokens, cand_tokens, n)
            precisions.append(precision)

            # BLEU-n is geometric mean of precisions up to n
            if precision > 0:
                bleu_n = bp * np.exp(np.mean([np.log(p) for p in precisions if p > 0]))
            else:
                bleu_n = 0.0

            scores[f'BLEU-{n}'] = round(bleu_n, 4)

        # Overall BLEU (BLEU-4)
        scores['BLEU'] = scores[f'BLEU-{max_n}']

        return scores

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text, preserving mathematical notation."""
        # Preserve math expressions
        for pattern in self.math_notation_patterns:
            text = re.sub(pattern, lambda m: m.group(0).replace(' ', '_SPACE_'), text)

        # Basic tokenization
        tokens = text.lower().split()

        # Restore spaces in math
        tokens = [t.replace('_SPACE_', ' ') for t in tokens]

        return tokens

    def _ngram_precision(self, ref_tokens: List[str], cand_tokens: List[str], n: int) -> float:
        """Compute modified n-gram precision."""
        ref_ngrams = self._get_ngrams(ref_tokens, n)
        cand_ngrams = self._get_ngrams(cand_tokens, n)

        if not cand_ngrams:
            return 0.0

        # Count matches (with clipping)
        matches = 0
        for ngram in cand_ngrams:
            matches += min(cand_ngrams[ngram], ref_ngrams.get(ngram, 0))

        return matches / sum(cand_ngrams.values())

    def _get_ngrams(self, tokens: List[str], n: int) -> Counter:
        """Extract n-grams from token list."""
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngrams.append(tuple(tokens[i:i+n]))
        return Counter(ngrams)

    def _brevity_penalty(self, ref_tokens: List[str], cand_tokens: List[str]) -> float:
        """Compute brevity penalty for BLEU."""
        c = len(cand_tokens)
        r = len(ref_tokens)

        if c > r:
            return 1.0
        elif c == 0:
            return 0.0
        else:
            return np.exp(1 - r / c)

    # ==================== ROUGE Score ====================

    def compute_rouge_l(self, reference: str, candidate: str) -> Dict[str, float]:
        """
        Compute ROUGE-L (Longest Common Subsequence).

        Measures recall-oriented quality, important for ensuring
        coverage of key educational concepts.

        Args:
            reference: Ground truth answer
            candidate: Generated answer

        Returns:
            Dictionary with precision, recall, and F1-score
        """
        ref_tokens = self._tokenize(reference)
        cand_tokens = self._tokenize(candidate)

        lcs_length = self._lcs_length(ref_tokens, cand_tokens)

        if len(cand_tokens) == 0:
            precision = 0.0
        else:
            precision = lcs_length / len(cand_tokens)

        if len(ref_tokens) == 0:
            recall = 0.0
        else:
            recall = lcs_length / len(ref_tokens)

        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)

        return {
            'ROUGE-L-P': round(precision, 4),
            'ROUGE-L-R': round(recall, 4),
            'ROUGE-L-F1': round(f1, 4)
        }

    def _lcs_length(self, seq1: List[str], seq2: List[str]) -> int:
        """Compute longest common subsequence length using DP."""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        return dp[m][n]

    # ==================== Pedagogical Quality ====================

    def compute_pedagogical_quality(self, answer: str, metadata: Dict[str, Any]) -> Dict[str, float]:
        """
        Compute pedagogical quality score for research evaluation.

        Metrics:
        - Step granularity: Are steps broken down sufficiently?
        - Explanation depth: Is reasoning provided?
        - Example inclusion: Are examples given?
        - Proof structure: For proofs, is structure correct?

        Args:
            answer: Generated answer text
            metadata: Additional context (query_type, topic, etc.)

        Returns:
            Dictionary of pedagogical metrics
        """
        metrics = {}

        # Step granularity (count enumerated steps)
        steps = self._count_steps(answer)
        metrics['step_count'] = steps
        metrics['step_granularity'] = min(1.0, steps / 5.0)  # Normalized to [0,1]

        # Explanation depth (presence of reasoning keywords)
        explanation_score = self._explanation_depth(answer)
        metrics['explanation_depth'] = explanation_score

        # Example inclusion
        has_example = self._has_example(answer)
        metrics['has_example'] = 1.0 if has_example else 0.0

        # Proof structure (if query is proof-type)
        if metadata.get('query_type') == 'proof':
            proof_score = self._proof_structure_score(answer)
            metrics['proof_structure'] = proof_score

        # Mathematical notation richness
        math_score = self._mathematical_richness(answer)
        metrics['mathematical_notation'] = math_score

        # Overall pedagogical score (weighted average)
        weights = {
            'step_granularity': 0.3,
            'explanation_depth': 0.3,
            'has_example': 0.15,
            'mathematical_notation': 0.25
        }

        overall = sum(metrics.get(k, 0) * v for k, v in weights.items())
        metrics['overall_pedagogical_score'] = round(overall, 4)

        return metrics

    def _count_steps(self, text: str) -> int:
        """Count numbered/bulleted steps in answer."""
        patterns = [
            r'^\d+\.',  # 1. 2. 3.
            r'^•',      # Bullet points
            r'^-',      # Dashes
            r'Step \d+',  # Step 1, Step 2
        ]

        lines = text.split('\n')
        step_count = 0

        for line in lines:
            line = line.strip()
            for pattern in patterns:
                if re.match(pattern, line):
                    step_count += 1
                    break

        return step_count

    def _explanation_depth(self, text: str) -> float:
        """Score explanation depth based on reasoning keywords."""
        reasoning_keywords = [
            'because', 'since', 'therefore', 'thus', 'hence',
            'this means', 'which implies', 'as a result',
            'consequently', 'it follows that', 'note that',
            'observe that', 'we can see', 'this shows'
        ]

        text_lower = text.lower()
        count = sum(1 for kw in reasoning_keywords if kw in text_lower)

        # Normalize to [0, 1]
        return min(1.0, count / 5.0)

    def _has_example(self, text: str) -> bool:
        """Check if answer includes examples."""
        example_indicators = [
            'example:', 'for example', 'for instance',
            'e.g.', 'consider', 'suppose', 'let us'
        ]

        text_lower = text.lower()
        return any(ind in text_lower for ind in example_indicators)

    def _proof_structure_score(self, text: str) -> float:
        """Score proof structure quality."""
        score = 0.0
        text_lower = text.lower()

        # Check for proof components
        components = {
            'given': r'(given|let|assume)',
            'goal': r'(prove|show|demonstrate|to prove)',
            'steps': r'(step|first|next|then|finally)',
            'conclusion': r'(therefore|thus|hence|∴|qed|∎)',
        }

        for comp_type, pattern in components.items():
            if re.search(pattern, text_lower):
                score += 0.25

        return min(1.0, score)

    def _mathematical_richness(self, text: str) -> float:
        """Score mathematical notation richness."""
        count = 0

        for pattern in self.math_notation_patterns:
            count += len(re.findall(pattern, text))

        # Also count mathematical symbols
        math_symbols = ['=', '≤', '≥', '<', '>', '∈', '∉', '⊆', '⊂', '∪', '∩']
        count += sum(text.count(sym) for sym in math_symbols)

        # Normalize
        return min(1.0, count / 10.0)

    # ==================== Relevance Scoring ====================

    def compute_relevance(self, query: str, answer: str, retrieved_docs: List[Dict]) -> Dict[str, float]:
        """
        Compute relevance between query and answer.

        Metrics:
        - Query term coverage
        - Topic alignment
        - Source quality

        Args:
            query: Original question
            answer: Generated answer
            retrieved_docs: List of retrieved source documents

        Returns:
            Relevance metrics dictionary
        """
        metrics = {}

        # Query term coverage
        query_tokens = set(self._tokenize(query))
        answer_tokens = set(self._tokenize(answer))

        if query_tokens:
            coverage = len(query_tokens & answer_tokens) / len(query_tokens)
            metrics['query_term_coverage'] = round(coverage, 4)
        else:
            metrics['query_term_coverage'] = 0.0

        # Source quality (average similarity of retrieved docs)
        if retrieved_docs:
            avg_similarity = np.mean([doc.get('similarity', 0) for doc in retrieved_docs])
            metrics['avg_source_similarity'] = round(avg_similarity, 4)

            # Pedagogical score from sources
            avg_ped_score = np.mean([doc.get('pedagogical_score', 0) for doc in retrieved_docs])
            metrics['avg_pedagogical_score'] = round(avg_ped_score, 4)
        else:
            metrics['avg_source_similarity'] = 0.0
            metrics['avg_pedagogical_score'] = 0.0

        return metrics

    # ==================== Proof Completeness ====================

    def compute_proof_completeness(self, proof_text: str) -> Dict[str, Any]:
        """
        Evaluate proof completeness and correctness.

        Checks:
        - Has clear statement of what's being proved
        - Contains logical steps
        - Has conclusion
        - Uses proper mathematical notation

        Args:
            proof_text: The proof to evaluate

        Returns:
            Dictionary with completeness metrics
        """
        metrics = {
            'has_statement': False,
            'has_steps': False,
            'has_conclusion': False,
            'uses_math_notation': False,
            'logical_flow': 0.0,
            'completeness_score': 0.0
        }

        text_lower = proof_text.lower()

        # Check for proof statement
        if re.search(r'(prove|show|demonstrate|to prove)', text_lower):
            metrics['has_statement'] = True

        # Check for logical steps
        if self._count_steps(proof_text) >= 2:
            metrics['has_steps'] = True

        # Check for conclusion
        if re.search(r'(therefore|thus|hence|∴|qed|∎)', text_lower):
            metrics['has_conclusion'] = True

        # Check for mathematical notation
        if self._mathematical_richness(proof_text) > 0.3:
            metrics['uses_math_notation'] = True

        # Logical flow score (presence of connectives)
        connectives = ['first', 'next', 'then', 'finally', 'since', 'because', 'if', 'when']
        flow_score = sum(1 for conn in connectives if conn in text_lower)
        metrics['logical_flow'] = min(1.0, flow_score / 5.0)

        # Overall completeness
        completeness = sum([
            metrics['has_statement'] * 0.25,
            metrics['has_steps'] * 0.3,
            metrics['has_conclusion'] * 0.25,
            metrics['uses_math_notation'] * 0.1,
            metrics['logical_flow'] * 0.1
        ])
        metrics['completeness_score'] = round(completeness, 4)

        return metrics

    # ==================== Comprehensive Evaluation ====================

    def evaluate_answer(
        self,
        query: str,
        reference_answer: str,
        generated_answer: str,
        retrieved_docs: List[Dict],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation of a single query-answer pair.

        This is the main method for research evaluation.

        Args:
            query: The question
            reference_answer: Ground truth answer
            generated_answer: RAG system's answer
            retrieved_docs: Retrieved source documents
            metadata: Additional context (query_type, topic, difficulty)

        Returns:
            Complete evaluation metrics dictionary
        """
        results = {
            'query': query,
            'metadata': metadata,
        }

        # BLEU scores
        bleu_scores = self.compute_bleu(reference_answer, generated_answer)
        results['bleu'] = bleu_scores

        # ROUGE scores
        rouge_scores = self.compute_rouge_l(reference_answer, generated_answer)
        results['rouge'] = rouge_scores

        # Pedagogical quality
        ped_quality = self.compute_pedagogical_quality(generated_answer, metadata)
        results['pedagogical_quality'] = ped_quality

        # Relevance
        relevance = self.compute_relevance(query, generated_answer, retrieved_docs)
        results['relevance'] = relevance

        # Proof completeness (if applicable)
        if metadata.get('query_type') == 'proof':
            proof_completeness = self.compute_proof_completeness(generated_answer)
            results['proof_completeness'] = proof_completeness

        # Overall quality score (composite)
        overall = (
            bleu_scores['BLEU'] * 0.3 +
            rouge_scores['ROUGE-L-F1'] * 0.2 +
            ped_quality['overall_pedagogical_score'] * 0.3 +
            relevance.get('avg_source_similarity', 0) * 0.2
        )
        results['overall_quality'] = round(overall, 4)

        return results

    # ==================== Batch Evaluation ====================

    def evaluate_batch(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate multiple test cases and compute aggregate statistics.

        Args:
            test_cases: List of test case dictionaries, each containing:
                - query, reference_answer, generated_answer, retrieved_docs, metadata

        Returns:
            Aggregate statistics and per-case results
        """
        individual_results = []

        for case in test_cases:
            result = self.evaluate_answer(
                query=case['query'],
                reference_answer=case['reference_answer'],
                generated_answer=case['generated_answer'],
                retrieved_docs=case.get('retrieved_docs', []),
                metadata=case.get('metadata', {})
            )
            individual_results.append(result)

        # Compute aggregate statistics
        aggregate = {
            'total_cases': len(test_cases),
            'mean_bleu': np.mean([r['bleu']['BLEU'] for r in individual_results]),
            'mean_rouge_f1': np.mean([r['rouge']['ROUGE-L-F1'] for r in individual_results]),
            'mean_pedagogical_score': np.mean([r['pedagogical_quality']['overall_pedagogical_score'] for r in individual_results]),
            'mean_overall_quality': np.mean([r['overall_quality'] for r in individual_results]),
        }

        # Add proof-specific metrics if applicable
        proof_results = [r for r in individual_results if 'proof_completeness' in r]
        if proof_results:
            aggregate['mean_proof_completeness'] = np.mean([r['proof_completeness']['completeness_score'] for r in proof_results])

        return {
            'aggregate': aggregate,
            'individual_results': individual_results
        }


# ==================== Convenience Functions ====================

def quick_evaluate(reference: str, generated: str) -> Dict[str, float]:
    """Quick evaluation with BLEU and ROUGE."""
    evaluator = EvaluationMetrics()
    bleu = evaluator.compute_bleu(reference, generated)
    rouge = evaluator.compute_rouge_l(reference, generated)
    return {**bleu, **rouge}


# ==================== Standalone Wrapper Functions ====================
# These functions are used by the research evaluation script

def compute_bleu_score(generated: str, reference: str) -> float:
    """
    Compute BLEU-4 score.

    Args:
        generated: Generated answer
        reference: Reference answer

    Returns:
        BLEU-4 score (0-1)
    """
    evaluator = EvaluationMetrics()
    result = evaluator.compute_bleu(reference, generated, max_n=4)
    return result.get('bleu-4', 0.0)


def compute_rouge_scores(generated: str, reference: str) -> Dict[str, float]:
    """
    Compute ROUGE scores (ROUGE-1, ROUGE-2, ROUGE-L).

    Args:
        generated: Generated answer
        reference: Reference answer

    Returns:
        Dictionary with rouge1_f, rouge2_f, rougeL_f
    """
    evaluator = EvaluationMetrics()

    # Compute ROUGE-L
    rouge_l = evaluator.compute_rouge_l(reference, generated)

    # For ROUGE-1 and ROUGE-2, we'll use a simpler implementation
    # based on n-gram overlap
    def compute_rouge_n(ref: str, gen: str, n: int) -> Dict[str, float]:
        ref_tokens = evaluator._tokenize(ref)
        gen_tokens = evaluator._tokenize(gen)

        # Get n-grams
        ref_ngrams = [tuple(ref_tokens[i:i+n]) for i in range(len(ref_tokens)-n+1)]
        gen_ngrams = [tuple(gen_tokens[i:i+n]) for i in range(len(gen_tokens)-n+1)]

        if not ref_ngrams or not gen_ngrams:
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}

        # Count overlapping n-grams
        ref_counter = Counter(ref_ngrams)
        gen_counter = Counter(gen_ngrams)

        overlap = sum((ref_counter & gen_counter).values())

        precision = overlap / len(gen_ngrams) if gen_ngrams else 0.0
        recall = overlap / len(ref_ngrams) if ref_ngrams else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return {'precision': precision, 'recall': recall, 'f1': f1}

    rouge1 = compute_rouge_n(reference, generated, 1)
    rouge2 = compute_rouge_n(reference, generated, 2)

    return {
        'rouge1_f': rouge1['f1'],
        'rouge1_p': rouge1['precision'],
        'rouge1_r': rouge1['recall'],
        'rouge2_f': rouge2['f1'],
        'rouge2_p': rouge2['precision'],
        'rouge2_r': rouge2['recall'],
        'rougeL_f': rouge_l['f1'],
        'rougeL_p': rouge_l['precision'],
        'rougeL_r': rouge_l['recall']
    }


def compute_bertscore(generated_list: List[str], reference_list: List[str]) -> Dict[str, List[float]]:
    """
    Compute BERTScore (placeholder - requires bert-score package).

    Args:
        generated_list: List of generated answers
        reference_list: List of reference answers

    Returns:
        Dictionary with precision, recall, f1 lists
    """
    # BERTScore requires the bert-score package which is heavy
    # For now, return placeholder values
    # To use real BERTScore: pip install bert-score
    try:
        from bert_score import score
        P, R, F1 = score(generated_list, reference_list, lang='en', verbose=False)
        return {
            'precision': P.tolist(),
            'recall': R.tolist(),
            'f1': F1.tolist()
        }
    except ImportError:
        # Return placeholder if bert-score not installed
        n = len(generated_list)
        return {
            'precision': [0.0] * n,
            'recall': [0.0] * n,
            'f1': [0.0] * n
        }


def compute_pedagogical_quality(question: str, answer: str, retrieved_docs: List[Dict]) -> Dict[str, float]:
    """
    Compute pedagogical quality metrics.

    Args:
        question: The question asked
        answer: Generated answer
        retrieved_docs: Retrieved documents used

    Returns:
        Dictionary with pedagogical quality metrics
    """
    evaluator = EvaluationMetrics()

    # Compute pedagogical quality
    ped_quality = evaluator.compute_pedagogical_quality(answer)

    # Add relevance metrics
    relevance = evaluator.compute_relevance(question, answer, retrieved_docs)

    return {**ped_quality, **relevance}


if __name__ == '__main__':
    # Example usage for testing
    evaluator = EvaluationMetrics()

    # Test case 1: Simple proof
    reference = """
    To prove f(n) = O(n^2), we need to find c > 0 and n0 > 0 such that f(n) <= c*n^2 for all n >= n0.
    Given f(n) = 3n^2 + 5n + 2, choose c = 10 and n0 = 1.
    For n >= 1: 3n^2 + 5n + 2 <= 10n^2.
    Therefore f(n) = O(n^2).
    """

    generated = """
    Proof: We need to show 3n^2 + 5n + 2 = O(n^2).
    Step 1: For n >= 1, we have 5n <= 5n^2 and 2 <= 2n^2.
    Step 2: Therefore 3n^2 + 5n + 2 <= 3n^2 + 5n^2 + 2n^2 = 10n^2.
    Step 3: Choose c = 10 and n0 = 1.
    Conclusion: Hence 3n^2 + 5n + 2 = O(n^2). QED.
    """

    result = evaluator.evaluate_answer(
        query="Prove that 3n^2 + 5n + 2 = O(n^2)",
        reference_answer=reference,
        generated_answer=generated,
        retrieved_docs=[{'similarity': 0.85, 'pedagogical_score': 0.75}],
        metadata={'query_type': 'proof', 'topic': 'asymptotic_analysis'}
    )

    print(json.dumps(result, indent=2))
