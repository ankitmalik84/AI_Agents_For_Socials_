# System Design RAG API -- Server

FastAPI backend for the System Design RAG application. Provides a LangGraph-powered RAG pipeline for answering questions about system design concepts from "System Design Interview" by Alex Xu and "Designing Data-Intensive Applications."

## Project Structure

```
server/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic request/response models
│   ├── routes/
│   │   ├── __init__.py
│   │   └── query.py         # API endpoints (/invoke, /stream)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag.py           # RAG service orchestration
│   │   ├── vector_store.py  # Pinecone vector store operations
│   │   └── graph.py         # LangGraph workflow definition
│   └── utils/
│       ├── __init__.py
│       └── helpers.py       # Utility functions
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container configuration
├── .dockerignore            # Docker ignore rules
└── README.md                # This file
```

## Setup

### Local Development

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:

```env
# OpenAI
OPENAI_API_KEY=your_openai_key

# Pinecone
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=system-design
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Tavily
TAVILY_API_KEY=your_tavily_key

# Model settings
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini

# LangSmith (optional)
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
LANGSMITH_ENDPOINT=
LANGSMITH_TRACING=
```

4. Run the server:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### Docker

```bash
docker build -t system-design-rag:latest .
docker run -d -p 8000:8000 --env-file .env system-design-rag:latest
```

## API Endpoints

### `POST /invoke`

Non-streaming query endpoint.

**Request Body:**

```json
{
  "content": "What is load balancing?",
  "thread_id": "optional-thread-id"
}
```

**Response:**

```json
{
  "answer": "Detailed response about load balancing...",
  "success": true
}
```

### `GET /stream/{message}`

Streaming query endpoint via Server-Sent Events (SSE).

**Query Parameters:**

- `thread_id` (optional): For conversation continuity

**SSE Event Types:**

| Event            | Description                      |
| ---------------- | -------------------------------- |
| `thread_id`      | New conversation thread ID       |
| `content`        | Response content chunks          |
| `search_start`   | Research fallback started        |
| `search_results` | Tavily research results          |
| `search_error`   | Research error                   |
| `end`            | Stream completed                 |
| `error`          | Error message                    |

## LangGraph Pipeline

The RAG workflow processes queries through these nodes:

1. **question_rewriter** -- Converts follow-up questions into standalone queries
2. **question_classifier** -- Determines if the query is about system design
3. **on_topic_router** -- Routes to retrieval or off-topic handler
4. **retrieve** -- Fetches documents from Pinecone
5. **retrieval_grader** -- Filters retrieved documents by relevance
6. **proceed_router** -- Chooses: generate answer, refine question, or cannot answer
7. **refine_question** -- Rephrases and retries retrieval (up to 2 attempts)
8. **generate_answer** -- Builds the answer from retrieved context
9. **cannot_answer** -- Hands off to research when retrieval fails
10. **research_node** -- Uses Tavily search as a fallback
11. **off_topic_response** -- Handles non-system-design questions

## Frontend Integration

This API is designed to work with the Next.js frontend in the `client/` directory. The frontend connects to `http://localhost:8000` and uses the `/stream/{message}` endpoint for real-time chat.

## Dependencies

| Category     | Packages                                                          |
| ------------ | ----------------------------------------------------------------- |
| Web          | FastAPI 0.115, Uvicorn 0.34                                       |
| Validation   | Pydantic 2.11, pydantic-settings 2.8                             |
| LangChain    | langchain 0.3, langchain-openai 0.3, langchain-community 0.3     |
| Graph        | LangGraph 0.3                                                     |
| Vector Store | langchain-pinecone 0.2, pinecone-client 6.0                      |
| LLM / Search | OpenAI 1.75, Tavily 0.5                                          |
