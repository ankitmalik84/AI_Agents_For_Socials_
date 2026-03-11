# System Design RAG API

A Retrieval-Augmented Generation (RAG) system built with LangGraph for querying information about System Design concepts, patterns, and best practices from "System Design Interview" by Alex Xu and "Designing Data-Intensive Applications."

## Features

- **Intelligent Query Processing**: Uses LangGraph for structured conversation flow with question rewriting, classification, and routing
- **Real-time Streaming**: Supports Server-Sent Events (SSE) for real-time responses
- **Advanced RAG Pipeline**: Combines Pinecone vector search with Tavily online research as a fallback
- **Context-Aware Responses**: Maintains conversation context via thread-based memory
- **Automatic Research**: Falls back to online search when the knowledge base lacks relevant documents
- **System Design Focus**: Specialized in system design, distributed systems, and software architecture

## Project Structure

```
AI_Agents_For_Socials_/
├── client/                        # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx         # Root layout
│   │   │   ├── page.tsx           # Main chat page
│   │   │   └── globals.css        # Global styles
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx     # Chat message list
│   │   │   ├── MessageBubble.tsx  # User/assistant messages
│   │   │   ├── TextArea.tsx       # Input field
│   │   │   ├── SearchResults.tsx  # Tavily search results
│   │   │   ├── MarkdownRenderer.tsx
│   │   │   ├── ArrowIcon.tsx
│   │   │   └── Output.tsx
│   │   └── types/
│   │       ├── stream.ts          # SSE stream types
│   │       └── types.ts           # Shared types
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── server/                        # FastAPI backend
│   ├── app/
│   │   ├── main.py                # FastAPI entry point
│   │   ├── config.py              # Configuration settings
│   │   ├── models/
│   │   │   └── schemas.py         # Pydantic models
│   │   ├── routes/
│   │   │   └── query.py           # API endpoints
│   │   ├── services/
│   │   │   ├── rag.py             # RAG service
│   │   │   ├── vector_store.py    # Pinecone vector store
│   │   │   └── graph.py           # LangGraph workflow
│   │   └── utils/
│   │       └── helpers.py         # Utility functions
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Container configuration
│   ├── .dockerignore
│   └── README.md                  # Server-specific docs
└── README.md                      # This file
```

## Tech Stack

| Layer     | Technology                                       |
| --------- | ------------------------------------------------ |
| Frontend  | Next.js 15, React 19, TypeScript, Tailwind CSS   |
| Backend   | FastAPI, Python 3.12                             |
| RAG       | LangGraph, LangChain, OpenAI                    |
| Vector DB | Pinecone                                         |
| Search    | Tavily                                           |

## Prerequisites

- Python 3.12+
- Node.js 18+
- API keys for: **OpenAI**, **Pinecone**, **Tavily**
- Docker (optional, for containerized deployment)

## Setup Instructions

### 1. Backend (Server)

```bash
cd server
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `server/` directory:

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

Start the server:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend (Client)

```bash
cd client
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000` and connects to the backend at `http://localhost:8000`.

### 3. Docker (Server Only)

```bash
cd server
docker build -t system-design-rag:latest .
docker run -d -p 8000:8000 --env-file .env system-design-rag:latest
```

## API Endpoints

### POST `/invoke`

Non-streaming query endpoint.

**Request:**

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

### GET `/stream/{message}`

Streaming query endpoint via Server-Sent Events.

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

## Usage Examples

### Python (Non-Streaming)

```python
import requests

response = requests.post(
    "http://localhost:8000/invoke",
    json={
        "content": "Explain microservices architecture",
        "thread_id": None
    }
)
print(response.json())
```

### JavaScript (Streaming)

```javascript
const eventSource = new EventSource(
  "http://localhost:8000/stream/Explain%20microservices%20architecture"
);

eventSource.addEventListener("content", (event) => {
  const data = JSON.parse(event.data);
  console.log(data.content);
});

eventSource.addEventListener("end", () => {
  eventSource.close();
});
```

## RAG Pipeline

The LangGraph workflow processes queries through these stages:

1. **Question Rewriter** -- Converts follow-up questions into standalone queries
2. **Question Classifier** -- Determines if the query is about system design
3. **Router** -- Routes on-topic queries to retrieval, off-topic to a fallback response
4. **Retrieve** -- Fetches relevant documents from Pinecone
5. **Retrieval Grader** -- Filters documents by relevance
6. **Generate / Refine / Research** -- Generates an answer, refines the query for retry (up to 2 attempts), or falls back to Tavily search

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
