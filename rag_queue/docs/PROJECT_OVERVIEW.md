# RAG Queue - Project Overview

## Table of Contents
- [Introduction](#introduction)
- [What is This Project?](#what-is-this-project)
- [Architecture Overview](#architecture-overview)
- [System Components](#system-components)
- [Technology Stack](#technology-stack)
- [Key Features](#key-features)
- [Data Flow](#data-flow)
- [System Architecture Diagram](#system-architecture-diagram)
- [Component Interaction Flow](#component-interaction-flow)
- [Project Structure](#project-structure)
- [Understanding RAG (Retrieval-Augmented Generation)](#understanding-rag-retrieval-augmented-generation)
- [Why Use a Queue System?](#why-use-a-queue-system)
- [Design Decisions](#design-decisions)

---

## Introduction

This project implements a **Retrieval-Augmented Generation (RAG)** system with an asynchronous job queue architecture. It allows users to ask questions about documents (PDFs) and receive AI-generated answers based on the content of those documents. The system uses a queue-based approach to handle multiple queries efficiently without blocking the API server.

---

## What is This Project?

**RAG Queue** is a production-ready, scalable question-answering system that:

- Accepts natural language queries from users via a REST API
- Processes queries asynchronously using a distributed task queue
- Searches through pre-indexed document embeddings stored in a vector database
- Generates contextual answers using OpenAI's GPT models
- Returns results with page number references for further exploration

Think of it as an intelligent document assistant that can answer questions about your documents while handling multiple requests simultaneously.

---

## Architecture Overview

The project follows a **microservices-inspired architecture** with clear separation of concerns:

### Three Main Layers:

1. **API Layer (FastAPI Server)**
   - Receives HTTP requests from clients
   - Validates input and enqueues jobs
   - Returns job IDs immediately (non-blocking)
   - Provides endpoints to check job status and retrieve results

2. **Queue Layer (Redis Queue - RQ)**
   - Manages asynchronous job processing
   - Decouples request handling from heavy processing
   - Enables horizontal scaling of workers
   - Persists job state and results

3. **Worker Layer (Background Processors)**
   - Executes the actual RAG pipeline
   - Searches the vector database for relevant context
   - Generates AI responses using OpenAI
   - Stores results back in the queue

---

## System Components

### 1. **FastAPI Server** ([server.py](server.py))

The web server that exposes REST API endpoints for client interaction.

**Responsibilities:**
- Handle incoming HTTP requests
- Validate query parameters
- Enqueue processing jobs to Redis Queue
- Track job status and retrieve results
- Provide health check endpoints

**Key Endpoints:**
- `GET /` - Health check endpoint
- `POST /chat` - Submit a query for processing
- `GET /job-status` - Retrieve results for a completed job

### 2. **RQ Client** ([client/rq_client.py](client/rq_client.py))

Establishes connection to Redis and creates a queue instance for job management.

**Responsibilities:**
- Configure Redis connection settings
- Create a named queue for consistent worker targeting
- Provide queue interface for job enqueueing

**Configuration:**
- Queue Name: `rag_queue.queue.worker`
- Redis Host: `localhost`
- Redis Port: `6379`

### 3. **Worker Process** ([queue/worker.py](queue/worker.py))

The background worker that processes queries using the RAG pipeline.

**Responsibilities:**
- Retrieve user queries from the queue
- Search vector database for relevant document chunks
- Format context from search results
- Generate AI responses using OpenAI's chat completions
- Return structured answers with page references

**Processing Pipeline:**
1. Receive query from queue
2. Embed query using OpenAI embeddings
3. Perform similarity search in Qdrant vector store
4. Extract and format context with metadata
5. Send context + query to GPT-4o
6. Return response with page number citations

### 4. **Vector Database (Qdrant)**

External service that stores document embeddings for semantic search.

**Responsibilities:**
- Store high-dimensional vector embeddings of document chunks
- Perform fast similarity searches
- Return relevant document sections with metadata

**Configuration:**
- URL: `http://localhost:6333`
- Collection: `learning-rag`
- Embedding Model: `text-embedding-3-large`

### 5. **Redis/Valkey Instance**

Message broker and result backend for the queue system.

**Responsibilities:**
- Store queued jobs
- Persist job results
- Enable communication between API and workers
- Provide job status tracking

**Deployment:**
- Containerized using Docker Compose
- Exposed on port `6379`

### 6. **Application Entry Point** ([main.py](main.py))

Bootstrap script that initializes and runs the FastAPI server.

**Responsibilities:**
- Load environment variables from `.env` file
- Start Uvicorn server with proper configuration
- Bind to all network interfaces on port 8000

---

## Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework for building APIs with Python
  - Automatic API documentation (Swagger UI)
  - Built-in data validation using Pydantic
  - Asynchronous request handling

### Queue Management
- **RQ (Redis Queue)**: Simple Python library for job queuing
  - Lightweight and easy to configure
  - Built on Redis for reliability
  - Supports worker pools and job retries

- **Redis/Valkey**: In-memory data structure store
  - Used as message broker
  - Persists job state and results
  - Fast and reliable

### AI & Machine Learning
- **OpenAI API**: State-of-the-art language models
  - GPT-4o for answer generation
  - text-embedding-3-large for query embeddings

- **LangChain**: Framework for building LLM applications
  - Simplifies vector store integration
  - Provides OpenAI embeddings wrapper
  - Offers consistent API across different services

- **Qdrant**: Vector database for semantic search
  - Stores document embeddings
  - Fast similarity search
  - Supports filtering and metadata

### Infrastructure
- **Docker Compose**: Container orchestration
  - Simplifies Redis/Valkey deployment
  - Ensures consistent development environment

- **Uvicorn**: ASGI server for FastAPI
  - High-performance Python server
  - Supports asynchronous request handling

### Additional Libraries
- **python-dotenv**: Environment variable management
- **Pydantic**: Data validation and settings management
- **httpx, aiohttp**: HTTP client libraries for async operations

---

## Key Features

### 1. **Asynchronous Processing**
Queries are processed in the background, preventing API timeouts and improving user experience for long-running operations.

### 2. **Scalable Architecture**
Multiple worker processes can be spawned to handle increased load. Each worker independently pulls jobs from the queue.

### 3. **Job Tracking**
Every query receives a unique job ID, allowing clients to poll for results at their convenience.

### 4. **Contextual Answers**
The RAG system retrieves relevant document sections before generating answers, ensuring responses are grounded in actual document content.

### 5. **Page Number Citations**
Responses include page numbers from source documents, allowing users to verify information and explore further.

### 6. **Semantic Search**
Uses vector embeddings to find conceptually similar content, not just keyword matches.

### 7. **Persistent Results**
Job results are stored in Redis, allowing retrieval even after the original request completes.

---

## Data Flow

### Request Flow Diagram

```
┌─────────────┐
│   Client    │
│ (HTTP API)  │
└──────┬──────┘
       │
       │ POST /chat?query="What is RAG?"
       ▼
┌─────────────────────┐
│   FastAPI Server    │
│   - Validates input │
│   - Enqueues job    │
│   - Returns job_id  │
└──────┬──────────────┘
       │
       │ queue.enqueue(process_query, query)
       ▼
┌──────────────────────┐
│   Redis/Valkey       │
│   - Stores job       │
│   - Persists state   │
└──────┬───────────────┘
       │
       │ Worker pulls job
       ▼
┌──────────────────────────────┐
│   Worker Process             │
│   1. Embed query             │
│   2. Search vector DB        │
│   3. Format context          │
│   4. Call OpenAI API         │
│   5. Return result           │
└──────┬───────────────────────┘
       │
       │ Store result in Redis
       ▼
┌──────────────────────┐
│   Redis/Valkey       │
│   - Stores result    │
└──────┬───────────────┘
       │
       │ Client polls: GET /job-status?job_id=abc123
       ▼
┌─────────────────────┐
│   FastAPI Server    │
│   - Fetches result  │
│   - Returns to user │
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│   Client    │
│  (Receives  │
│   answer)   │
└─────────────┘
```

---

## System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                         CLIENT APPLICATION                          │
│              (Web Browser / Mobile App / API Consumer)             │
└───────────────────────────┬────────────────────────────────────────┘
                            │
                            │ HTTP REST API
                            │
                            ▼
┌────────────────────────────────────────────────────────────────────┐
│                        API LAYER (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │ GET /        │  │ POST /chat   │  │ GET /job-status      │    │
│  │ Health Check │  │ Enqueue Job  │  │ Fetch Job Result     │    │
│  └──────────────┘  └──────┬───────┘  └──────┬───────────────┘    │
│                            │                  │                     │
└────────────────────────────┼──────────────────┼─────────────────────┘
                             │                  │
                             │                  │
                    Enqueue  │                  │ Fetch Result
                             │                  │
                             ▼                  ▼
┌────────────────────────────────────────────────────────────────────┐
│                    QUEUE LAYER (Redis/Valkey)                       │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │  Job Queue: rag_queue.queue.worker                       │     │
│  │  - Pending Jobs                                          │     │
│  │  - Processing Jobs                                       │     │
│  │  - Completed Jobs (with results)                         │     │
│  └──────────────────────────────────────────────────────────┘     │
└────────────────────────────┬───────────────────────────────────────┘
                             │
                             │ Workers pull jobs
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                  WORKER LAYER (Background Processors)               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │  Worker 1   │  │  Worker 2   │  │  Worker N   │  (Scalable)   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │
│         │                │                │                        │
│         └────────────────┴────────────────┘                        │
│                          │                                          │
│                   process_query()                                  │
│                          │                                          │
└──────────────────────────┼──────────────────────────────────────────┘
                           │
                           │
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
┌───────────────────────┐         ┌──────────────────────┐
│  VECTOR DATABASE      │         │   OPENAI API         │
│  (Qdrant)             │         │                      │
│                       │         │  ┌────────────────┐  │
│  ┌──────────────────┐ │         │  │ Embeddings API │  │
│  │ Collection:      │ │         │  │ (Embed query)  │  │
│  │ learning-rag     │ │         │  └────────────────┘  │
│  │                  │ │         │                      │
│  │ - Embeddings     │ │         │  ┌────────────────┐  │
│  │ - Metadata       │ │         │  │ Chat API       │  │
│  │ - Page numbers   │ │         │  │ (GPT-4o)       │  │
│  └──────────────────┘ │         │  │ Generate answer│  │
│                       │         │  └────────────────┘  │
└───────────────────────┘         └──────────────────────┘
```

---

## Component Interaction Flow

### Detailed Processing Sequence

```
1. Client Request Initiated
   │
   ├─► FastAPI receives POST /chat with query parameter
   │
   ├─► Query validation performed by Pydantic
   │
   └─► Job enqueued to Redis Queue
       │
       └─► Immediate response with job_id returned to client
           (Client doesn't wait for processing)

2. Background Processing Begins
   │
   ├─► Worker pulls job from queue
   │
   ├─► Worker executes process_query(query)
   │   │
   │   ├─► Step 1: Query Embedding
   │   │   └─► Send query to OpenAI embeddings API
   │   │       └─► Receive 3072-dimensional vector
   │   │
   │   ├─► Step 2: Similarity Search
   │   │   └─► Query Qdrant vector database
   │   │       └─► Find most similar document chunks
   │   │           └─► Retrieve top K results with metadata
   │   │
   │   ├─► Step 3: Context Preparation
   │   │   └─► Format search results into context string
   │   │       └─► Include: page content, page number, file location
   │   │
   │   ├─► Step 4: System Prompt Construction
   │   │   └─► Build prompt with retrieved context
   │   │       └─► Add instructions for answer generation
   │   │
   │   ├─► Step 5: OpenAI Chat Completion
   │   │   └─► Send system prompt + user query to GPT-4o
   │   │       └─► Receive AI-generated answer
   │   │
   │   └─► Step 6: Return Result
   │       └─► Store result in Redis via RQ
   │
   └─► Job marked as completed

3. Result Retrieval
   │
   ├─► Client polls GET /job-status?job_id=xxx
   │
   ├─► FastAPI fetches job from Redis
   │
   ├─► Extract return_value from job object
   │
   └─► Return result to client
       └─► Client receives AI-generated answer with citations
```

---

## Project Structure

```
rag_queue/
│
├── main.py                    # Application entry point
│   └── Loads environment and starts Uvicorn server
│
├── server.py                  # FastAPI application definition
│   ├── Defines API endpoints
│   ├── Handles job enqueueing
│   └── Manages result retrieval
│
├── client/
│   ├── __init__.py           # Python package marker
│   └── rq_client.py          # Redis Queue client configuration
│       └── Establishes Redis connection and queue instance
│
├── queue/
│   ├── __init__.py           # Python package marker
│   └── worker.py             # Worker process logic
│       ├── Initializes OpenAI client
│       ├── Configures embedding model
│       ├── Connects to Qdrant vector store
│       └── Defines process_query() function
│
├── docker-compose.yml         # Redis/Valkey container configuration
│   └── Defines Valkey service on port 6379
│
├── requirements.txt           # Python dependencies
│   └── Lists all required packages with versions
│
└── .env                       # Environment variables (not in repo)
    ├── OPENAI_API_KEY
    └── Other sensitive configuration
```

---

## Understanding RAG (Retrieval-Augmented Generation)

### What is RAG?

RAG is a technique that enhances Large Language Models (LLMs) by combining:

1. **Retrieval**: Finding relevant information from external knowledge sources
2. **Augmentation**: Adding that information to the model's context
3. **Generation**: Producing answers based on both the model's training and retrieved information

### Why Use RAG?

**Traditional LLM Problems:**
- Limited to knowledge from training data (static, potentially outdated)
- Cannot access private or proprietary documents
- May hallucinate information not in training data

**RAG Solutions:**
- Grounds responses in actual documents
- Enables question-answering over private data
- Reduces hallucinations by providing factual context
- Allows models to cite sources

### RAG Pipeline in This Project

```
User Query
    │
    ▼
[Embed Query] ──► Vector (3072 dimensions)
    │
    ▼
[Similarity Search in Vector DB]
    │
    ├─► Document Chunk 1 (similarity: 0.89)
    ├─► Document Chunk 2 (similarity: 0.85)
    └─► Document Chunk 3 (similarity: 0.82)
    │
    ▼
[Format Context]
    │
    └─► Combined context with page numbers
    │
    ▼
[Build System Prompt]
    │
    └─► "You are an AI assistant. Answer based on this context: ..."
    │
    ▼
[Send to GPT-4o]
    │
    ├─► System Prompt + Context
    └─► User Query
    │
    ▼
[AI Generated Answer]
    │
    └─► "Based on page 42, RAG is a technique that..."
```

---

## Why Use a Queue System?

### Problem Without Queues

Traditional synchronous API processing:
- Client sends request
- Server processes immediately
- Client waits until completion (could be 10-30 seconds)
- Blocks server resources during processing
- Risk of timeout errors
- Cannot handle concurrent requests efficiently

### Benefits of Queue-Based Architecture

#### 1. **Non-Blocking Responses**
   - API returns immediately with job ID
   - Client can continue with other tasks
   - Improves user experience

#### 2. **Scalability**
   - Multiple workers can process jobs in parallel
   - Easy to add more workers during high load
   - Workers can run on different machines

#### 3. **Reliability**
   - Jobs persist in Redis even if worker crashes
   - Failed jobs can be retried automatically
   - System continues working even if components restart

#### 4. **Resource Management**
   - Control how many jobs process concurrently
   - Prevent overwhelming external APIs
   - Better memory and CPU utilization

#### 5. **Decoupling**
   - API layer independent from processing layer
   - Can update workers without restarting API
   - Easier to maintain and debug

---

## Design Decisions

### Why FastAPI?

- **Performance**: Async support and high throughput
- **Developer Experience**: Automatic API documentation
- **Type Safety**: Built-in validation with Pydantic
- **Modern**: Native async/await support

### Why Redis Queue (RQ)?

- **Simplicity**: Minimal configuration compared to Celery
- **Python-Native**: Uses Python functions directly as tasks
- **Lightweight**: Perfect for small to medium projects
- **Redis-Based**: Reliable and fast message broker

### Why Qdrant?

- **Performance**: Optimized for vector similarity search
- **Scalability**: Handles millions of vectors efficiently
- **Features**: Supports filtering, metadata, and hybrid search
- **Developer-Friendly**: Good documentation and Python SDK

### Why OpenAI Embeddings?

- **Quality**: State-of-the-art semantic understanding
- **Consistency**: Reliable and well-maintained
- **Integration**: Seamless with LangChain ecosystem

### Why Docker Compose for Redis?

- **Portability**: Same environment across all machines
- **Simplicity**: One command to start dependencies
- **Isolation**: Doesn't interfere with system packages

---

## Use Cases

This system is ideal for:

1. **Document Q&A Systems**
   - Legal document search
   - Technical documentation assistant
   - Research paper exploration

2. **Knowledge Base Systems**
   - Internal company knowledge search
   - Product documentation queries
   - Training material assistance

3. **Customer Support**
   - Automated support ticket responses
   - FAQ system with contextual answers
   - Product manual search

4. **Educational Applications**
   - Textbook question answering
   - Study guide generation
   - Concept explanation

---

## Security Considerations

**Environment Variables:**
- All sensitive keys stored in `.env` file (excluded from version control)
- OpenAI API keys never hardcoded

**Network Security:**
- Services bind to localhost by default
- Qdrant and Redis should be behind firewall in production
- Consider adding authentication to API endpoints

**Rate Limiting:**
- Implement API rate limiting to prevent abuse
- Control concurrent worker count to manage costs

**Data Privacy:**
- Document embeddings stored locally in Qdrant
- Queries and results temporarily stored in Redis
- Consider data retention policies

---

## Performance Characteristics

**Typical Response Times:**
- Job Enqueueing: < 50ms
- Vector Search: 50-200ms
- OpenAI API Call: 2-10 seconds
- Total Processing: 3-15 seconds

**Scalability:**
- API can handle 100s of concurrent connections
- Each worker processes 1 job at a time
- Scale horizontally by adding more workers

**Bottlenecks:**
- OpenAI API rate limits (primary constraint)
- Vector database query speed (secondary)
- Redis memory for large result sets

---

## Future Enhancements

Potential improvements to consider:

1. **Caching Layer**: Cache common queries to reduce API calls
2. **Streaming Responses**: Stream partial answers as they generate
3. **Authentication**: Add user authentication and authorization
4. **Multiple Collections**: Support querying different document sets
5. **Feedback Loop**: Allow users to rate answers for continuous improvement
6. **Monitoring**: Add metrics and logging for production observability
7. **WebSocket Support**: Real-time updates instead of polling
8. **Retry Logic**: Automatic retry for failed jobs
9. **Admin Dashboard**: UI for monitoring jobs and system health

---

## Conclusion

This RAG Queue project demonstrates a production-ready architecture for building scalable, document-based question-answering systems. The queue-based design ensures reliability and scalability, while the RAG approach ensures accurate, source-grounded answers.

The clear separation of concerns (API, Queue, Worker) makes the system easy to understand, maintain, and extend. Whether you're building an internal knowledge base or a customer-facing Q&A system, this architecture provides a solid foundation.
