# AlgoRAG System Architecture & Logic

This document details the end-to-end logic of the AlgoRAG system, explaining how we transform raw educational content into pedogogically-sound answers.

## 1. Data Ingestion & Chunking
**Goal:** Convert diverse educational materials (PDFs, JSON, Text) into a format suitable for retrieval.

*   **Source Loading**: We handle standard textbooks (PDF), lecture notes, and structured JSON datasets. `PyPDF2` is used for text extraction.
*   **Chunking Strategy**: We do **not** use naive character splitting.
    *   **Method**: Sliding Window Chunking.
    *   **Size**: 500 words per chunk.
    *   **Overlap**: 50 words (10%) to ensure concepts aren't split mid-sentence.
    *   **Context Preservation**: Short documents (e.g., individual JSON questions) are never chunked to maintain their integrity.
*   **Preprocessing & Enrichment**: *Before* embedding, every chunk goes through a `MathPreprocessor`:
    *   **Math Normalization**: Unifies formatting (e.g., standardizing `n^2` vs `n**2` vs `n squared`).
    *   **Entity Recognition**: Uses Regex patterns to detect:
        *   **Complexity**: `O(...)`, `Ω(...)`, `Θ(...)`
        *   **LaTeX**: `$...$`, `\begin{equation}...`
        *   **Key Algorithms**: "QuickSort", "Dijkstra", etc.
    *   **Metadata Tagging**: Adds tags like `has_proof=True`, `has_complexity_analysis=True` based on keyword density.

## 2. Embedding & Vector Database
**Goal:** Create a semantic representation of the educational content.

*   **Model**: We use `all-mpnet-base-v2` (768 dimensions) via SentenceTransformers. This model is chosen for its strong performance on semantic search tasks.
*   **Storage**:
    *   **Vector DB**: ChromaDB (configured for local persistence).
    *   **Data Stored**: The vector embedding + the raw text + full metadata (JSON-serialized topic tags, etc.).

## 3. Retrieval Pipeline (The "Algo" in AlgoRAG)
**Goal:** Retrieve not just *semantically* similar documents, but *pedagogically* useful ones.

This is a two-step process:

1.  **Semantic Search (Step 1)**:
    *   The user's query is embedded.
    *   We retrieve the top-k (default 5) raw candidates using Cosine Similarity.

    2.  **Pedagogical Re-ranking (Step 2 - The AlgoRAG Core)**:
    *   The top-k (default 10) semantic matches are re-scored using specific weights:
        *   **Step Granularity (40%)**: `score = 1.0` if chunk contains enumerated steps (1., 2., 3.) or bullets AND user asks for Proof.
        *   **Topic Coverage (30%)**: `score = intersection(query_topics, chunk_topics) / len(query_topics)`.
        *   **Difficulty Match (30%)**: Matches the source difficulty (e.g., "Intro Text") to query difficulty.
        *   **Query Term Coverage**: Ensures retrieved docs actually contain the specific math terms requested.
    *   **Final Score**: `0.7 * similarity + 0.3 * pedagogical_score`.

## 4. Generation (RAG)
**Goal:** Synthesize the retrieved context into a clear, educational answer.

*   **Model**: DeepSeek-V3 (via API) is used for its strong reasoning capabilities.
*   **Query Analysis**:
    *   The `MathPreprocessor` classifies the user's question into types: `proof`, `complexity_analysis`, `concept_explanation`, or `comparison`.
*   **Dynamic Prompting**:
    *   We construct a prompt that includes:
        *   **System Prompt**: "You are an expert Computer Science tutor. Your goal is to provide rigorous, step-by-step explanations..."
    *   **Dynamic Injection**: Based on query type, we inject specific instructions:
        *   *Proof*: "Format your answer as a formal proof with 'Theorem', 'Proof Strategy', 'Steps', and 'Conclusion'."
        *   *Analysis*: "Focus on worst-case and average-case time complexity."
*   **Enforced Output Structure**: The system enforces a rigorous template for answers:
    *   `## Theorem`: State clearly what is being proven.
    *   `## Proof Strategy`: High-level approach (e.g., "induction", "contradiction").
    *   `## Proof Steps`: The actual derivation.
    *   `## Key Insights`: Pedagogical notes for the student.

## 5. System Integration (API Layer)
**Goal:** Expose the RAG pipeline to the frontend/students.

*   **Framework**: FastAPI (Python).
*   **Endpoints**:
    *   `POST /api/query`: The main pipeline entry point. Orchestrates `Preprocess` -> `Retrieve` -> `Re-rank` -> `Generate`.
    *   `GET /api/stats`: Returns corpus statistics (topic distribution, doc counts).
    *   `GET /api/health`: Health checks for VectorDB and Embedding services.

## 6. Evaluation Loop (Research Paper Mode)
**Goal:** Rigorous, quantitative assessment of the system.

We do NOT just "ask and see." We run a formal evaluation script (`run_paper_evaluation.py`):

1.  **Dataset**: 179 curated algorithm questions (Proofs, Analysis, True/False) with ground-truth reference answers.
2.  **Metric Computation**:
    *   **Standard NLP**: BLEU-4 (n-gram overlap), ROUGE-L (recall).
    *   **Custom Pedagogical Metrics**:
        *   **Step Granularity**: (Boolean/Float) Checks for numbered lists or bullet points indicating structured reasoning.
        *   **Explanation Depth**: Detects reasoning keywords ("because", "therefore", "implies") and sentence complexity.
        *   **Math Richness**: Measures density of LaTeX/Math symbols vs text.
        *   **Proof Structure**: Checks for formal markers: "Theorem", "Proof Strategy", "Steps", "Q.E.D.".
        *   **Query Term Coverage**: Measures how many key terms from the question appear in the answer.
        *   **Has Example**: Detects if a concrete example is provided.

### Baseline Comparison
To prove AlgoRAG's effectiveness, we compare it against a **Baseline RAG**:
*   **Baseline**: Standard Chunks -> Cosine Similarity -> Generic Prompt.
*   **AlgoRAG**: Enriched Chunks -> P-Ranker -> Specialized Prompt.
*   **A/B Testing**: We run both systems on the same 179 questions and compare the metrics side-by-side using `baseline_comparison.py`.

## 7. Infrastructure & Resilience
*   **Hybrid Embeddings**: The `EmbeddingClient` supports fallback.
    *   Primary: Gemini/OpenAI (if keys present).
    *   Fallback: `all-mpnet-base-v2` (Local/Free) if APIs fail.
*   **Vector Persistence**: ChromaDB saves to disk, allowing the knowledge base to persist across restarts.

## Summary of Data Flow
`PDF/Text` -> **Ingest** (Chunk + Enrich) -> **Embed** -> **VectorDB**
`User Query` -> **Classify** (Type) -> **Retrieve** (Vector) -> **Re-rank** (Pedagogical) -> **Generate** (LLM) -> **Evaluate** (Metrics)
