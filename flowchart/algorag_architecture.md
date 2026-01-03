# AlgoRAG System Architecture Flowchart

This document contains the MermaidJS code for the AlgoRAG system architecture. You can render this in any Markdown viewer that supports Mermaid (like GitHub, VS Code, or Obsidian) or use the [Mermaid Live Editor](https://mermaid.live).

```mermaid
graph TD
    %% Global Styles
    classDef database fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;
    classDef model fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef input fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,rx:10,ry:10;
    classDef logic fill:#fce4ec,stroke:#880e4f,stroke-width:2px,stroke-dasharray: 5 5;

    %% ==========================================
    %% 1. Data Ingestion Pipeline (Offline)
    %% ==========================================
    subgraph "Data Pipeline (Offline)"
        direction TB
        RawData([Raw Content<br/>PDF, JSON, Text]):::input
        
        Chunker[Chunking Engine<br/>Sliding Window: 500w / 50 overlap]:::process
        Preprocessor[Math Preprocessor<br/>Regex Entity Extraction]:::process
        
        EmbModel_Offline[Embedding Model<br/>all-mpnet-base-v2]:::model
        VectorDB[(Vector Database<br/>ChromaDB)]:::database
        
        RawData --> Chunker
        Chunker --> Preprocessor
        
        subgraph "Enrichment Steps"
            Preprocessor -- "Extract" --> Meta1(Complexity: O/Θ/Ω)
            Preprocessor -- "Normalize" --> Meta2(Math: LaTeX)
            Preprocessor -- "Tag" --> Meta3(Type: Proof/Algo)
        end
        
        Preprocessor --> EmbModel_Offline
        EmbModel_Offline -- "768d Vector + Metadata" --> VectorDB
    end

    %% ==========================================
    %% 2. Retrieval & Generation (Online)
    %% ==========================================
    subgraph "RAG Pipeline (Online)"
        direction TB
        UserQuery([Student Query]):::input
        
        QueryPrep[Query Preprocessor<br/>Type Detection & Topic Extraction]:::process
        EmbModel_Online[Embedding Model<br/>all-mpnet-base-v2]:::model
        
        UserQuery --> QueryPrep
        QueryPrep --> EmbModel_Online
        
        %% Retrieval
        EmbModel_Online -- "Query Vector" --> VectorDB
        VectorDB -- "Top-k Candidates<br/>(Cosine Similarity)" --> Ranker[Pedagogical Re-ranker]:::process
        
        %% Re-ranking Logic
        subgraph "Pedagogical Scoring"
            Ranker -.-> Score1(Step Granularity - 40%):::logic
            Ranker -.-> Score2(Topic Coverage - 30%):::logic
            Ranker -.-> Score3(Difficulty Match - 30%):::logic
            Score1 & Score2 & Score3 -.-> FinalScore(Weighted Score):::logic
        end
        
        FinalScore --> Selection[Top-N Best Context]
        
        %% Prompting
        PromptEngine[Dynamic Prompt Engine]:::process
        QueryPrep -- "Query Type<br/>(Proof/Analysis)" --> PromptEngine
        Selection --> PromptEngine
        
        %% Generation
        LLM[Generator Model<br/>DeepSeek-V3]:::model
        PromptEngine -- "System Prompt +<br/>Injected Instructions +<br/>Context" --> LLM
        
        %% Output
        FinalOutput([Structured Answer<br/>Theorem/Strategy/Steps]):::input
        LLM --> FinalOutput
    end

    %% Cross-Links
    class VectorDB database
```
