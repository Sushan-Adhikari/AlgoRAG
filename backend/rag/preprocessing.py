"""
Preprocessing module for AlgoRAG.
Handles mathematical entity recognition, LaTeX normalization, and text preprocessing.
"""
import re
import logging
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MathEntity:
    """Represents a recognized mathematical entity."""
    original: str
    canonical: str
    entity_type: str
    position: Tuple[int, int]


class MathPreprocessor:
    """
    Preprocessor for mathematical and algorithmic content.
    Extracts and normalizes mathematical entities for better retrieval.
    """

    def __init__(self):
        # Complexity notation patterns
        self.complexity_patterns = {
            "big_o": r"O\s*\(\s*([^)]+)\s*\)",
            "omega": r"[ΩΩ]\s*\(\s*([^)]+)\s*\)",
            "theta": r"[ΘΘ]\s*\(\s*([^)]+)\s*\)",
            "little_o": r"o\s*\(\s*([^)]+)\s*\)",
            "little_omega": r"[ωω]\s*\(\s*([^)]+)\s*\)",
        }

        # LaTeX math patterns
        self.latex_patterns = {
            "inline_math": r"\$([^$]+)\$",
            "display_math": r"\$\$([^$]+)\$\$",
            "equation": r"\\begin\{equation\}(.*?)\\end\{equation\}",
            "align": r"\\begin\{align\*?\}(.*?)\\end\{align\*?\}",
        }

        # Common algorithm names
        self.algorithm_names = {
            "quicksort", "mergesort", "heapsort", "insertion sort", "bubble sort",
            "dijkstra", "bellman-ford", "floyd-warshall", "kruskal", "prim",
            "dfs", "bfs", "topological sort", "binary search",
            "dynamic programming", "greedy", "divide and conquer",
            "master theorem", "recursion tree"
        }

        # Proof keywords
        self.proof_keywords = {
            "proof", "theorem", "lemma", "corollary", "proposition",
            "induction", "contradiction", "contrapositive",
            "base case", "inductive step", "qed", "therefore"
        }

    def extract_math_entities(self, text: str) -> List[MathEntity]:
        """
        Extract mathematical entities from text.

        Args:
            text: Input text containing mathematical notation

        Returns:
            List of MathEntity objects
        """
        entities = []

        # Extract complexity notations
        for entity_type, pattern in self.complexity_patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                original = match.group(0)
                inner = match.group(1).strip()
                canonical = self._normalize_complexity(inner, entity_type)

                entities.append(MathEntity(
                    original=original,
                    canonical=canonical,
                    entity_type=entity_type,
                    position=(match.start(), match.end())
                ))

        # Extract LaTeX expressions
        for latex_type, pattern in self.latex_patterns.items():
            for match in re.finditer(pattern, text, re.DOTALL):
                original = match.group(0)
                inner = match.group(1).strip()
                canonical = self._normalize_latex(inner)

                entities.append(MathEntity(
                    original=original,
                    canonical=canonical,
                    entity_type=latex_type,
                    position=(match.start(), match.end())
                ))

        return entities

    def _normalize_complexity(self, expr: str, notation_type: str) -> str:
        """
        Normalize complexity expressions to canonical form.

        Examples:
            "n^2" -> "n_squared"
            "log n" -> "log_n"
            "n log n" -> "n_log_n"
        """
        expr = expr.lower().strip()

        # Remove spaces
        expr = expr.replace(" ", "_")

        # Normalize common patterns
        replacements = {
            "^2": "_squared",
            "^3": "_cubed",
            "^k": "_to_k",
            "log": "log",
            "ln": "log",
            "sqrt": "sqrt",
        }

        for old, new in replacements.items():
            expr = expr.replace(old, new)

        return f"{notation_type}_{expr}"

    def _normalize_latex(self, latex: str) -> str:
        """
        Normalize LaTeX expressions for comparison.

        Args:
            latex: LaTeX expression

        Returns:
            Normalized form
        """
        # Remove excessive whitespace
        latex = re.sub(r'\s+', ' ', latex).strip()

        # Normalize common LaTeX commands
        replacements = {
            r'\\frac\s*\{([^}]+)\}\s*\{([^}]+)\}': r'(\1)/(\2)',
            r'\\sqrt\s*\{([^}]+)\}': r'sqrt(\1)',
            r'\\log': 'log',
            r'\\ln': 'log',
            r'\\sum': 'sum',
            r'\\prod': 'prod',
            r'\^': '**',
            r'_': '_',
        }

        for pattern, replacement in replacements.items():
            latex = re.sub(pattern, replacement, latex)

        return latex.lower()

    def detect_query_type(self, query: str) -> str:
        """
        Detect the type of query (proof, analysis, general).

        Args:
            query: User query

        Returns:
            Query type: "proof", "complexity_analysis", "algorithm", "general"
        """
        query_lower = query.lower()

        # Check for proof-related queries
        proof_indicators = ["prove", "proof", "show that", "demonstrate",
                           "induction", "contradiction", "by induction"]
        if any(indicator in query_lower for indicator in proof_indicators):
            return "proof"

        # Check for complexity analysis queries
        complexity_indicators = ["time complexity", "space complexity",
                                "running time", "asymptotic", "big-o",
                                "worst case", "best case", "average case"]
        if any(indicator in query_lower for indicator in complexity_indicators):
            return "complexity_analysis"

        # Check for algorithm-related queries
        if any(algo in query_lower for algo in self.algorithm_names):
            return "algorithm"

        return "general"

    def extract_topics(self, text: str) -> Set[str]:
        """
        Extract theoretical CS topics from text.

        Args:
            text: Input text

        Returns:
            Set of detected topics
        """
        text_lower = text.lower()
        topics = set()

        topic_keywords = {
            "asymptotic_analysis": ["big-o", "asymptotic", "growth rate", "theta", "omega"],
            "recurrence_relations": ["recurrence", "master theorem", "recursion tree"],
            "dynamic_programming": ["dynamic programming", "dp", "memoization", "optimal substructure"],
            "graph_algorithms": ["graph", "dijkstra", "bfs", "dfs", "shortest path"],
            "greedy_algorithms": ["greedy", "optimal choice", "greedy choice"],
            "divide_and_conquer": ["divide and conquer", "merge sort", "quick sort"],
            "np_completeness": ["np-complete", "np-hard", "reduction", "polynomial time"],
            "sorting_algorithms": ["sort", "quicksort", "mergesort", "heapsort"],
            "data_structures": ["tree", "heap", "hash", "array", "linked list"],
            "proof_techniques": ["proof", "induction", "contradiction"],
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                topics.add(topic)

        return topics

    def preprocess_for_embedding(self, text: str) -> str:
        """
        Preprocess text for embedding generation.

        Args:
            text: Raw input text

        Returns:
            Preprocessed text optimized for embedding
        """
        # Extract math entities
        entities = self.extract_math_entities(text)

        # Replace math entities with normalized forms
        processed = text
        for entity in sorted(entities, key=lambda e: e.position[0], reverse=True):
            start, end = entity.position
            processed = processed[:start] + f" [{entity.canonical}] " + processed[end:]

        # Clean up whitespace
        processed = re.sub(r'\s+', ' ', processed).strip()

        return processed

    def enrich_document(self, document: Dict) -> Dict:
        """
        Enrich document with extracted metadata.

        Args:
            document: Document dictionary with 'content' field

        Returns:
            Enriched document with metadata
        """
        content = document.get("content", "")

        # Extract entities and topics
        math_entities = self.extract_math_entities(content)
        topics = self.extract_topics(content)
        query_type = self.detect_query_type(content)

        # Add metadata
        document["metadata"] = document.get("metadata", {})
        document["metadata"].update({
            "math_entities": [
                {"original": e.original, "canonical": e.canonical, "type": e.entity_type}
                for e in math_entities
            ],
            "topics": list(topics),
            "query_type": query_type,
            "has_proof": any(kw in content.lower() for kw in self.proof_keywords),
        })

        # Add preprocessed version for embedding
        document["preprocessed"] = self.preprocess_for_embedding(content)

        return document

    def extract_query_features(self, query: str) -> dict:
        """
        Extract comprehensive features from query for retrieval and evaluation.
        
        This method combines multiple extraction techniques to provide a complete
        feature set for the RAG pipeline.
        
        Args:
            query: User query text
            
        Returns:
            Dictionary containing:
                - query_type: Type of query (proof/complexity_analysis/algorithm/general)
                - topics: Set of detected CS topics
                - math_entities: List of mathematical entities found
                - difficulty: Estimated difficulty level (optional)
        """
        features = {
            "query_type": self.detect_query_type(query),
            "topics": list(self.extract_topics(query)),
            "math_entities": [
                {
                    "original": e.original,
                    "canonical": e.canonical,
                    "type": e.entity_type
                }
                for e in self.extract_math_entities(query)
            ],
            "difficulty": None  # Could be enhanced with difficulty detection
        }
        
        return features


def test_preprocessing():
    """Test mathematical preprocessing."""
    print("\n" + "="*60)
    print("Testing Math Preprocessing")
    print("="*60)

    preprocessor = MathPreprocessor()

    # Test cases
    test_cases = [
        {
            "text": "The time complexity of quicksort is O(n log n) in the average case and O(n^2) in the worst case.",
            "expected_type": "complexity_analysis"
        },
        {
            "text": "Prove by induction that the sum $\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$",
            "expected_type": "proof"
        },
        {
            "text": "Dijkstra's algorithm finds the shortest path in Θ(V log V + E) time using a Fibonacci heap.",
            "expected_type": "algorithm"
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"  Original: {test['text']}")

        # Extract entities
        entities = preprocessor.extract_math_entities(test['text'])
        print(f"  Math Entities: {len(entities)}")
        for entity in entities:
            print(f"    - {entity.original} → {entity.canonical} ({entity.entity_type})")

        # Detect query type
        query_type = preprocessor.detect_query_type(test['text'])
        print(f"  Query Type: {query_type}")
        print(f"  Expected: {test['expected_type']}")
        print(f"  ✓ Match" if query_type == test['expected_type'] else "  ✗ Mismatch")

        # Extract topics
        topics = preprocessor.extract_topics(test['text'])
        print(f"  Topics: {', '.join(topics) if topics else 'None detected'}")

        # Preprocessed version
        preprocessed = preprocessor.preprocess_for_embedding(test['text'])
        print(f"  Preprocessed: {preprocessed}")

    print("\n" + "="*60)


if __name__ == "__main__":
    test_preprocessing()
