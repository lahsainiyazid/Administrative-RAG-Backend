# RAG Chatbot Backend — Ministry Digital Services

A production-oriented **Retrieval-Augmented Generation (RAG) backend** developed during my internship. The system allows users to ask questions about Moroccan digital public services and generates answers grounded in the project's document knowledge base.

## Overview

The project combines document ingestion, hybrid information retrieval, reranking, query expansion, LLM generation, caching, and API services into a complete RAG pipeline.

### Architecture

```text
                    ┌──────────────────┐
                    │   User Question  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Query Expansion  │
                    │      Qwen        │
                    └────────┬─────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │      Hybrid Retrieval       │
              │                             │
              │  BM25        +    Chroma    │
              │  Sparse           Dense     │
              └──────────────┬──────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Reranker      │
                    │  Cross-Encoder   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      LLM         │
                    │   GPT-OSS 120B   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     Answer       │
                    └──────────────────┘
```

## Data Ingestion Pipeline

Documents are automatically processed before being added to the knowledge base.

```text
Documents
    │
    ▼
Text Extraction
    │
    ▼
Chunking
    │
    ▼
Embeddings
    │
    ▼
ChromaDB
    │
    └──► MongoDB metadata / document management
```

The ingestion system supports document management operations, allowing the knowledge base to be updated without rebuilding the entire system manually.

## Main Technologies

| Component        | Technology                       |
| ---------------- | -------------------------------- |
| Language         | Python                           |
| API              | FastAPI                          |
| RAG Framework    | LangChain                        |
| Dense Retrieval  | ChromaDB                         |
| Sparse Retrieval | BM25                             |
| Embeddings       | `intfloat/multilingual-e5-large` |
| Reranking        | Cross-Encoder                    |
| Query Expansion  | Qwen                             |
| LLM              | GPT-OSS 120B                     |
| Database         | MongoDB Atlas                    |
| Cache            | Redis                            |
| Containerization | Docker                           |

## Retrieval Strategy

The project uses **hybrid retrieval** instead of relying exclusively on vector search.

### Sparse Retrieval — BM25

Useful for exact terms, names, keywords, and Arabic/French terminology.

### Dense Retrieval — ChromaDB

Uses multilingual embeddings to retrieve semantically similar documents, even when the wording of the question differs from the source document.

### Reranking

Retrieved documents are passed through a cross-encoder to identify the most relevant chunks before sending the context to the LLM.

```text
Question
   │
   ├──► BM25 ──────────┐
   │                   │
   └──► ChromaDB ──────┤
                       ▼
                Combined Results
                       │
                       ▼
                   Reranker
                       │
                       ▼
                Relevant Context
                       │
                       ▼
                     LLM
```

## Query Expansion

The system can expand the original question into alternative formulations before retrieval.

This improves retrieval when the user's wording differs significantly from the terminology used in the documents.

```text
Original Question
       │
       ▼
   Qwen Model
       │
       ▼
Expanded Queries
       │
       ▼
Hybrid Retrieval
```

## Caching

Redis is used to cache frequently requested queries and reduce unnecessary computation and LLM calls.

```text
User Query
    │
    ▼
 Redis Cache ────► Cached Answer
    │
    │ Cache Miss
    ▼
 RAG Pipeline
    │
    ▼
 Answer
    │
    ▼
 Redis
```

## API

The backend is exposed through a FastAPI REST API.

Example request:

```http
POST /ask
Content-Type: application/json
```

```json
{
  "question": "Comment obtenir un document administratif ?"
}
```

Example response:

```json
{
  "answer": "..."
}
```

The API also includes document-management functionality for maintaining the knowledge base.

## Project Structure

```text
rag/
│
├── app/
│   ├── main.py
│   ├── rag.py
│   ├── retrieval.py
│   ├── ingestion.py
│   └── database.py
│
├── data/
│
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env.example
└── README.md
```

> The exact structure may differ depending on the final deployment version.

## Running Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_key
MONGODB_URI=your_uri
REDIS_URL=your_url
```

Never commit `.env` or API keys to Git.

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

The API documentation will be available through FastAPI's Swagger interface.

## Docker

The application can also be containerized:

```bash
docker build -t rag-backend .
```

```bash
docker run --env-file .env -p 8000:8000 rag-backend
```

## Performance

During development, the RAG pipeline was optimized by testing different:

* embedding models
* retrieval weights
* rerankers
* LLMs
* caching strategies
* query-expansion approaches

A later optimized configuration achieved approximately **2 seconds average response time** in testing, while maintaining strong retrieval and answer quality.

Example evaluation results:

```text
Faithfulness       : 1.00
Answer Relevancy   : 0.86
Context Precision  : 1.00
Context Recall     : 0.74
```

These values are evaluation results from the development test set and may vary depending on the dataset and configuration.

## Key Features

* Multilingual document retrieval
* Hybrid BM25 + vector search
* Query expansion
* Cross-encoder reranking
* RAG-based answer generation
* MongoDB document management
* Redis caching
* FastAPI REST API
* Docker containerization
* Automatic document/chunk updates
* Retrieval and response-time monitoring

## What I Worked On

During the internship, I worked on the backend RAG pipeline, including:

* Data preparation and document ingestion
* Text chunking and embedding
* Hybrid retrieval
* Reranking
* Query expansion
* LLM integration
* MongoDB integration
* Redis caching
* FastAPI API development
* Document CRUD operations
* Performance optimization
* Dockerization

## Future Improvements

Possible improvements include:

* Better multilingual reranking
* Streaming LLM responses
* Authentication and authorization
* More extensive RAG evaluation
* Automated ingestion pipelines
* Monitoring and observability
* Improved document versioning
* Production deployment and scaling

---

## Internship Project

**RAG Chatbot Backend — Moroccan Digital Public Services**

Developed as part of an internship focused on applying **LLMs, RAG, information retrieval, data processing, and backend engineering** to a real-world public-service use case.
