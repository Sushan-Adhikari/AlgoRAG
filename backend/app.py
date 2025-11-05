"""
FastAPI server for AlgoRAG.
Main entrypoint for the RAG system.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import logging

from rag.embeddings import EmbeddingClient
from rag.retriever import Retriever
from rag.generator import Generator
from rag.preprocessing import MathPreprocessor
import config

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AlgoRAG - Algorithm & Complexity Theory RAG System",
    description="Retrieval-Augmented Generation for Theoretical Computer Science Education",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    question: str = Field(..., description="Student question")
    query_type: Optional[str] = Field(
        None,
        description="Query type: proof, complexity_analysis, algorithm, or general"
    )
    top_k: Optional[int] = Field(5, description="Number of documents to retrieve")


class Source(BaseModel):
    content: str
    similarity_score: float
    pedagogical_score: float
    metadata: Dict


class QueryResponse(BaseModel):
    question: str
    answer: str
    query_type: str
    sources: List[Source]
    num_sources: int


class HealthResponse(BaseModel):
    status: str
    embedding_backend: str
    embedding_dimension: int
    vector_db_type: str
    documents_indexed: int


class StatsResponse(BaseModel):
    total_documents: int
    embedding_backend: str
    vector_db_type: str
    top_topics: List[str]


# Initialize components (singletons)
logger.info("Initializing AlgoRAG components...")

try:
    # Embedding client
    emb_client = EmbeddingClient(
        backend=config.EMBED_BACKEND,
        config=config.EMBEDDING_CONFIGS.get(config.EMBED_BACKEND, {})
    )
    logger.info(f"✓ Embedding client initialized ({config.EMBED_BACKEND})")

    # Retriever with vector DB
    retriever = Retriever(
        embedding_client=emb_client,
        db_type=config.VECTOR_DB_TYPE,
        db_path=str(config.VECTOR_DB_DIR),
        collection_name=config.COLLECTION_NAME
    )
    logger.info(f"✓ Retriever initialized ({config.VECTOR_DB_TYPE})")

    # Generator (LLM)
    generator = Generator(
        model_name=config.GENERATOR_MODEL,
        temperature=config.GENERATOR_TEMPERATURE,
        max_tokens=config.GENERATOR_MAX_TOKENS
    )
    logger.info(f"✓ Generator initialized ({config.GENERATOR_MODEL})")

    # Preprocessor
    preprocessor = MathPreprocessor()
    logger.info("✓ Preprocessor initialized")

    COMPONENTS_INITIALIZED = True

except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    COMPONENTS_INITIALIZED = False
    # Continue with limited functionality


# API Endpoints

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AlgoRAG API",
        "version": "1.0.0",
        "description": "RAG system for theoretical computer science education",
        "endpoints": {
            "query": "/api/query",
            "health": "/api/health",
            "stats": "/api/stats"
        }
    }


@app.get("/api/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    if not COMPONENTS_INITIALIZED:
        raise HTTPException(status_code=503, detail="Components not initialized")

    try:
        doc_count = retriever.collection.count() if config.VECTOR_DB_TYPE == "chroma" else 0

        return HealthResponse(
            status="healthy",
            embedding_backend=emb_client.backend,
            embedding_dimension=emb_client.dimension,
            vector_db_type=config.VECTOR_DB_TYPE,
            documents_indexed=doc_count
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=StatsResponse)
async def stats():
    """Get system statistics."""
    if not COMPONENTS_INITIALIZED:
        raise HTTPException(status_code=503, detail="Components not initialized")

    try:
        doc_count = retriever.collection.count() if config.VECTOR_DB_TYPE == "chroma" else 0

        return StatsResponse(
            total_documents=doc_count,
            embedding_backend=emb_client.backend,
            vector_db_type=config.VECTOR_DB_TYPE,
            top_topics=config.TOPICS[:5]  # Show first 5 topics
        )
    except Exception as e:
        logger.error(f"Stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Main query endpoint for AlgoRAG.

    Process:
    1. Preprocess query (extract math entities, detect type)
    2. Retrieve relevant documents from vector DB
    3. Re-rank with pedagogical scoring
    4. Generate answer using LLM with context
    """
    if not COMPONENTS_INITIALIZED:
        raise HTTPException(status_code=503, detail="RAG components not initialized")

    try:
        logger.info(f"Query received: {request.question[:100]}...")

        # Step 1: Preprocess query
        query_type = request.query_type or preprocessor.detect_query_type(request.question)
        query_topics = preprocessor.extract_topics(request.question)

        query_metadata = {
            "query_type": query_type,
            "topics": list(query_topics),
        }

        logger.info(f"Query type: {query_type}, Topics: {query_topics}")

        # Step 2: Retrieve relevant documents
        retrieved_docs = retriever.retrieve(
            query=request.question,
            query_type=query_type,
            top_k=request.top_k,
            query_metadata=query_metadata
        )

        logger.info(f"Retrieved {len(retrieved_docs)} documents")

        # Step 3: Generate answer
        result = generator.generate(
            query=request.question,
            retrieved_docs=retrieved_docs,
            query_type=query_type
        )

        logger.info("Answer generated successfully")

        # Step 4: Format response
        sources = [
            Source(
                content=doc["content"],
                similarity_score=doc.get("similarity_score", 0.0),
                pedagogical_score=doc.get("pedagogical_score", 0.0),
                metadata=doc.get("metadata", {})
            )
            for doc in retrieved_docs
        ]

        return QueryResponse(
            question=request.question,
            answer=result["answer"],
            query_type=query_type,
            sources=sources,
            num_sources=len(sources)
        )

    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


# Run with: uvicorn app:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("Starting AlgoRAG Server")
    print("="*60)
    print(f"Embedding Backend: {config.EMBED_BACKEND}")
    print(f"Vector DB: {config.VECTOR_DB_TYPE}")
    print(f"Generator Model: {config.GENERATOR_MODEL}")
    print("="*60 + "\n")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
