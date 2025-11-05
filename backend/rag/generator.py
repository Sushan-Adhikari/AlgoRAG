"""
Generator module for AlgoRAG.
Uses LLM to generate answers based on retrieved context.
"""
import logging
import os
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Generator:
    """
    Answer generator using LLM with retrieved context.
    Supports Gemini and OpenAI backends.
    """

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash-exp",
        temperature: float = 0.3,
        max_tokens: int = 2048
    ):
        """
        Initialize generator.

        Args:
            model_name: LLM model name
            temperature: Generation temperature
            max_tokens: Maximum tokens in response
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Determine backend from model name
        if "gemini" in model_name.lower():
            self.backend = "gemini"
            self._init_gemini()
        elif "gpt" in model_name.lower() or "openai" in model_name.lower():
            self.backend = "openai"
            self._init_openai()
        elif "llama" in model_name.lower() or "mistral" in model_name.lower() or "gemma" in model_name.lower() or ":" in model_name:
            # Ollama models (e.g., llama3.1:8b, mistral:7b)
            self.backend = "ollama"
            self._init_ollama()
        else:
            # Default to Gemini
            self.backend = "gemini"
            self._init_gemini()

    def _init_gemini(self):
        """Initialize Gemini client."""
        try:
            from google import genai
            from google.genai import types

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")

            self.client = genai.Client(api_key=api_key)
            self.types = types

            logger.info(f"✓ Gemini generator initialized (model: {self.model_name})")

        except ImportError:
            raise ImportError(
                "google-genai not installed. Install with: pip install google-genai"
            )

    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")

            self.client = OpenAI(api_key=api_key)

            logger.info(f"✓ OpenAI generator initialized (model: {self.model_name})")

        except ImportError:
            raise ImportError(
                "openai not installed. Install with: pip install openai"
            )

    def _init_ollama(self):
        """Initialize Ollama client."""
        try:
            import requests

            # Test if Ollama is running
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code != 200:
                    raise ConnectionError("Ollama server not responding")
            except requests.exceptions.RequestException:
                raise ConnectionError(
                    "Ollama not running. Start it with: ollama serve"
                )

            self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            logger.info(f"✓ Ollama generator initialized (model: {self.model_name})")

        except ImportError:
            raise ImportError(
                "requests not installed. Install with: pip install requests"
            )

    def generate(
        self,
        query: str,
        retrieved_docs: List[Dict],
        query_type: str = "general"
    ) -> Dict:
        """
        Generate answer based on query and retrieved documents.

        Args:
            query: User query
            retrieved_docs: List of retrieved documents
            query_type: Type of query (proof, analysis, etc.)

        Returns:
            Dictionary with answer and metadata
        """
        # Build context from retrieved documents
        context = self._build_context(retrieved_docs)

        # Build system instruction based on query type
        system_instruction = self._get_system_instruction(query_type)

        # Create prompt
        prompt = self._create_prompt(query, context, query_type)

        # Generate response
        if self.backend == "gemini":
            response = self._generate_gemini(prompt, system_instruction)
        elif self.backend == "openai":
            response = self._generate_openai(prompt, system_instruction)
        elif self.backend == "ollama":
            response = self._generate_ollama(prompt, system_instruction)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

        return {
            "answer": response,
            "sources": retrieved_docs,
            "query_type": query_type,
            "num_sources": len(retrieved_docs),
        }

    def _build_context(self, retrieved_docs: List[Dict]) -> str:
        """Build context string from retrieved documents."""
        context_parts = []

        for i, doc in enumerate(retrieved_docs, 1):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            sim_score = doc.get("similarity_score", 0)
            ped_score = doc.get("pedagogical_score", 0)

            source_info = []
            if "source_textbook" in metadata:
                source_info.append(f"Source: {metadata['source_textbook']}")
            if "topic" in metadata:
                source_info.append(f"Topic: {metadata['topic']}")
            if "difficulty_level" in metadata:
                source_info.append(f"Level: {metadata['difficulty_level']}")

            context_part = f"""
[Document {i}] {' | '.join(source_info)}
Relevance: Similarity={sim_score:.2f}, Pedagogical={ped_score:.2f}

{content}

---
"""
            context_parts.append(context_part)

        return "\n".join(context_parts)

    def _get_system_instruction(self, query_type: str) -> str:
        """Get system instruction based on query type."""
        base_instruction = """
You are AlgoRAG, an expert AI tutor for theoretical computer science, specializing in:
- Algorithm analysis and complexity theory
- Proof techniques and mathematical reasoning
- Data structures and algorithm design

Your goal is to provide clear, pedagogically sound explanations that help students learn.
"""

        if query_type == "proof":
            return base_instruction + """
For PROOF questions:
1. Start with the theorem or claim to be proven
2. Explain the proof strategy (induction, contradiction, etc.)
3. Break down the proof into clear, logical steps
4. Explain WHY each step follows from the previous
5. Highlight key insights and common pitfalls
6. End with a clear conclusion (QED or ∎)

Use formal mathematical notation where appropriate, but explain every step clearly.
"""

        elif query_type == "complexity_analysis":
            return base_instruction + """
For COMPLEXITY ANALYSIS questions:
1. Identify the algorithm or operation being analyzed
2. Explain the analysis approach (counting operations, recurrence relations, etc.)
3. Show step-by-step calculation
4. Provide both tight bounds and asymptotic notation (O, Ω, Θ)
5. Discuss best, average, and worst cases when relevant
6. Compare with similar algorithms if helpful

Be precise with mathematical notation and explain the reasoning.
"""

        elif query_type == "algorithm":
            return base_instruction + """
For ALGORITHM questions:
1. Explain the algorithm's purpose and key idea
2. Describe how it works (pseudocode or step-by-step)
3. Analyze time and space complexity
4. Discuss correctness and why it works
5. Provide examples or trace through execution if helpful
6. Mention practical considerations and variations

Balance technical precision with clear explanations.
"""

        else:  # general
            return base_instruction + """
Provide clear, accurate explanations that:
- Build on fundamental concepts
- Use examples to illustrate abstract ideas
- Show step-by-step reasoning
- Connect to broader theoretical CS principles
- Help develop intuition along with formal understanding
"""

    def _create_prompt(self, query: str, context: str, query_type: str) -> str:
        """Create the full prompt for the LLM."""
        return f"""
Using the following reference materials from algorithm and complexity theory textbooks and course materials, answer the student's question.

REFERENCE MATERIALS:
{context}

STUDENT QUESTION:
{query}

INSTRUCTIONS:
- Base your answer primarily on the provided reference materials
- If the references don't fully answer the question, clearly indicate what's based on references vs. general knowledge
- Provide a well-structured, pedagogically sound explanation
- Use mathematical notation where appropriate (LaTeX format: $...$ for inline, $$...$$ for display)
- For proofs, show all steps clearly
- For complexity analysis, show calculations explicitly
- If multiple approaches exist, mention the most pedagogically valuable one first

ANSWER:
"""

    def _generate_gemini(self, prompt: str, system_instruction: str) -> str:
        """Generate using Gemini."""
        # Add rate limiting delay to avoid 429 errors (Gemini free tier: 2 req/min)
        time.sleep(2)  # 2 second delay between requests

        response = self.client.models.generate_content(
            model=self.model_name,
            config=self.types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                system_instruction=system_instruction
            ),
            contents=prompt
        )

        return response.text

    def _generate_openai(self, prompt: str, system_instruction: str) -> str:
        """Generate using OpenAI."""
        # Add rate limiting delay to avoid 429 errors
        time.sleep(1)  # 1 second delay between requests

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        return response.choices[0].message.content

    def _generate_ollama(self, prompt: str, system_instruction: str) -> str:
        """Generate using Ollama."""
        import requests

        # Ollama API endpoint
        url = f"{self.ollama_url}/api/chat"

        # Prepare messages
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]

        # Make request
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["message"]["content"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise RuntimeError(f"Ollama generation failed: {e}")


def test_generator():
    """Test the generator."""
    print("\n" + "="*60)
    print("Testing Generator")
    print("="*60)

    # Sample retrieved documents
    retrieved_docs = [
        {
            "content": """
            QuickSort uses a divide-and-conquer strategy. It picks a pivot element and
            partitions the array into elements smaller and larger than the pivot.

            Time Complexity:
            - Best/Average: O(n log n)
            - Worst: O(n^2) when pivot is always min/max

            The average case can be proven using recurrence relations:
            T(n) = 2T(n/2) + O(n)
            By the Master Theorem, T(n) = O(n log n)
            """,
            "metadata": {
                "topic": "sorting_algorithms",
                "source_textbook": "CLRS Chapter 7",
                "difficulty_level": "conceptual"
            },
            "similarity_score": 0.92,
            "pedagogical_score": 0.85
        },
        {
            "content": """
            Master Theorem: For recurrences of the form T(n) = aT(n/b) + f(n):

            Case 1: If f(n) = O(n^c) where c < log_b(a), then T(n) = Θ(n^log_b(a))
            Case 2: If f(n) = Θ(n^c log^k(n)) where c = log_b(a), then T(n) = Θ(n^c log^(k+1)(n))
            Case 3: If f(n) = Ω(n^c) where c > log_b(a), then T(n) = Θ(f(n))

            For QuickSort: T(n) = 2T(n/2) + n
            Here a=2, b=2, f(n)=n
            log_2(2) = 1, so we're in Case 2 with k=0
            Therefore T(n) = Θ(n log n)
            """,
            "metadata": {
                "topic": "recurrence_relations",
                "source_textbook": "CLRS Chapter 4",
                "difficulty_level": "application"
            },
            "similarity_score": 0.78,
            "pedagogical_score": 0.90
        }
    ]

    # Test generation
    generator = Generator()

    query = "Prove that the average case time complexity of QuickSort is O(n log n)."

    print(f"\nQuery: {query}\n")
    print("Generating answer...")

    result = generator.generate(
        query=query,
        retrieved_docs=retrieved_docs,
        query_type="proof"
    )

    print("\n" + "="*60)
    print("GENERATED ANSWER:")
    print("="*60)
    print(result["answer"])
    print("\n" + "="*60)
    print(f"Sources used: {result['num_sources']}")
    print(f"Query type: {result['query_type']}")


if __name__ == "__main__":
    test_generator()
