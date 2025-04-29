# System Design RAG API

A Retrieval-Augmented Generation (RAG) system built with LangGraph for querying information about System Design concepts, patterns, and best practices from "System Design Interview" by Alex Xu and "Designing Data-Intensive Applications".

## Features

- **Intelligent Query Processing**: Uses LangGraph for structured conversation flow
- **Real-time Streaming**: Supports Server-Sent Events (SSE) for real-time responses
- **Advanced RAG Pipeline**: Combines vector search with online research capabilities
- **Context-Aware Responses**: Maintains conversation context for better answers
- **Automatic Research**: Falls back to online search when needed using Tavily
- **System Design Focus**: Specialized in system design, distributed systems, and software architecture

## Project Structure

```
system-design-rag/server/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── models/              # Pydantic models
│   │   └── schemas.py       # Data models and schemas
│   ├── routes/              # API routes
│   │   └── query.py        # Query endpoints
│   ├── services/           # Business logic
│   │   ├── rag.py         # RAG service
│   │   ├── vector_store.py # Vector store operations
│   │   └── graph.py       # LangGraph definition
│   └── utils/             # Utility functions
│       └── helpers.py
├── requirements.txt        # Dependencies
├── Dockerfile             # Container configuration
├── .dockerignore         # Docker ignore rules
└── README.md             # Documentation
```

## Prerequisites

- Python 3.12 or higher
- Docker (optional)
- API keys for:
  - OpenAI
  - Pinecone
  - Tavily

## Setup Instructions

### Local Development

1. Clone the repository:

```bash
git clone <repository-url>
cd system-design-rag/server
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file with required API keys:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_key

# Pinecone settings
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=system-design
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Tavily settings
TAVILY_API_KEY=your_tavily_key

# Model settings
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4-turbo-preview
```

5. Run the server:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

1. Build the Docker image:

```bash
docker build -t your-username/system-design-rag:latest .
```

2. Run the container:

```bash
docker run -d -p 8000:8000 --env-file .env your-username/system-design-rag:latest
```

## API Endpoints

### Regular Query Endpoint

- **POST** `/invoke`
  - Request Body:
    ```json
    {
      "content": "What is load balancing?",
      "thread_id": "optional-thread-id"
    }
    ```
  - Response:
    ```json
    {
      "answer": "Detailed response about load balancing...",
      "success": true
    }
    ```

### Streaming Query Endpoint

- **GET** `/stream/{message}`
  - Query Parameters:
    - `thread_id` (optional): For conversation continuity
  - Returns: Server-Sent Events (SSE) stream
  - Event Types:
    - `thread_id`: New conversation thread ID
    - `content`: Response content chunks
    - `search_results`: Research results
    - `error`: Error messages
    - `end`: Stream completion

## Usage Examples

### Regular Query

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

### Streaming Query

```javascript
const eventSource = new EventSource(
  `http://localhost:8000/stream/Explain%20microservices%20architecture`
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.content);
};
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Successful response
- 400: Bad request
- 500: Server error

Detailed error messages are included in the response body.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
