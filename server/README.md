# Sapiens RAG API

A RAG (Retrieval-Augmented Generation) system built with LangGraph that enables document ingestion and intelligent querying using Large Language Models (LLMs).

## System Overview

This system provides two main functionalities:

1. Document ingestion and processing
2. Intelligent query processing with or without document context

## Project Structure

```
sapiens-rag/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   └── schemas.py       # Data validation schemas
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   ├── query.py        # Query processing endpoints
│   │   └── upload.py       # Document upload endpoints
│   ├── services/           # Core business logic
│   │   ├── __init__.py
│   │   ├── rag.py          # RAG pipeline orchestration
│   │   ├── vector_store.py # Vector storage management
│   │   ├── graph.py        # LangGraph processing definition
│   │   └── document_processor.py # Document processing logic
│   └── utils/              # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── requirements.txt        # Project dependencies
├── .env.example           # Environment variables template
└── README.md             # Project documentation
```

## Core Components

### 1. Document Processing Pipeline

- Handles document uploads and preprocessing
- Splits documents into optimal chunks
- Generates embeddings for semantic search
- Stores document vectors for retrieval

### 2. RAG Pipeline

- Manages the retrieval and generation workflow
- Utilizes LangGraph for orchestration
- Provides caching for improved performance
- Supports conversation threading

### 3. Vector Store

- Manages document embeddings
- Enables semantic similarity search
- Provides persistent storage
- Optimizes retrieval performance

## API Endpoints

### Document Upload

```http
POST /upload
Content-Type: multipart/form-data
```

Parameters:

- `file`: Document file to upload (Supported formats: PDF, TXT, DOCX)

Response:

```json
{
  "status": "success",
  "message": "Document processed successfully",
  "document_id": "doc123"
}
```

### Query Processing

```http
POST /query
Content-Type: application/json
```

Request Body:

```json
{
  "content": "Your question here",
  "thread_id": "optional-conversation-123"
}
```

Response:

```json
{
  "answer": "Generated response based on the context",
  "sources": ["Relevant document references"],
  "thread_id": "conversation-123"
}
```

## Environment Variables

```bash
# Required environment variables
OPENAI_API_KEY=your_openai_api_key
VECTOR_STORE_PATH=./data/vector_store
MODEL_NAME=gpt-3.5-turbo  # or your preferred model

# Optional configurations
MAX_CHUNK_SIZE=500
OVERLAP_SIZE=50
```

## System Requirements

- Python 3.9+
- 4GB RAM minimum
- Sufficient disk space for vector store
- Internet connection for API calls

## Setup Instructions

1. Clone the repository:

```bash
git clone <repository-url>
cd sapiens-rag
```

2. Set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create and configure environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration:
# - Vector store settings
# - API keys
# - Model configurations
```

5. Run the API server:

```bash
python -m app.main
```

The API will be available at http://localhost:8000

## Usage Examples

### Upload a Document

```python
import requests

files = {
    'file': ('document.pdf', open('document.pdf', 'rb'))
}
response = requests.post('http://localhost:8000/upload', files=files)
```

### Query the System

```python
import requests

query_data = {
    'content': 'What are the key points in chapter 1?',
    'thread_id': 'conversation-123'  # Optional
}
response = requests.post('http://localhost:8000/query', json=query_data)
```

## Development Mode

To run the server in development mode with hot reloading:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Best Practices

1. **Document Processing**

   - Use clear, well-formatted documents
   - Consider document size and chunking strategy
   - Verify successful upload and processing

2. **Query Optimization**

   - Be specific with queries
   - Use thread_ids for maintaining conversation context
   - Consider rate limits and response times

3. **System Maintenance**
   - Monitor vector store size and performance
   - Regularly clean up unused thread contexts
   - Keep dependencies updated

## Error Handling

The API uses standard HTTP status codes:

- 200: Successful operation
- 400: Bad request (invalid input)
- 404: Resource not found
- 500: Server error

## Security Considerations

- API authentication required for production use
- Rate limiting implemented for API endpoints
- Secure storage of sensitive configurations
- Input validation for all requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Limitations

- Maximum document size: 10MB per file
- Supported file formats: PDF, TXT, DOCX
- Rate limits:
  - 10 requests/minute for document uploads
  - 60 requests/minute for queries
- Maximum query length: 1000 characters

## Troubleshooting

Common issues and solutions:

1. **Vector Store Connection Error**

   - Verify VECTOR_STORE_PATH is correctly set
   - Check disk space availability

2. **Document Processing Failures**

   - Ensure document is not corrupted
   - Verify file format is supported
   - Check document size limits

3. **Query Processing Issues**
   - Verify API key is valid
   - Check rate limits
   - Ensure proper JSON formatting
