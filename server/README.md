# System Design Assistant - Server

FastAPI server implementation with WhatsApp integration for the System Design Assistant.

## Server Architecture

### Core Components

- FastAPI for API endpoints
- LangGraph for conversation flow
- Pinecone for vector storage
- Twilio for WhatsApp integration
- PyPDF2 & python-docx for document processing

### Key Features

- **Real-time Streaming**: Server-Sent Events (SSE) for real-time responses
- **Advanced RAG Pipeline**: Combines vector search with online research
- **Context-Aware Responses**: Maintains conversation context for better answers
- **Automatic Research**: Falls back to online search when needed using Tavily
- **System Design Focus**: Specialized in system design and architecture
- **WhatsApp Integration**: Direct interaction through WhatsApp
- **Document Processing**: Support for PDF and DOCX uploads

### Key Services

```
services/
├── rag.py           # RAG pipeline implementation
├── vector_store.py  # Pinecone operations
├── graph.py         # LangGraph conversation flow
└── twilio_service.py # WhatsApp messaging
```

### API Routes

```
routes/
├── query.py          # Query processing endpoints
├── upload.py         # Document upload handling
└── twilio_webhook.py # WhatsApp webhook handling
```

## Setup Instructions

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment:

```bash
cp .env.example .env
# Add your API keys to .env
```

3. Run locally:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Build Docker image:

```bash
docker build -t ankitmalik84/agent-whatsapp:latest .
docker push ankitmalik84/agent-whatsapp:latest
```

## WhatsApp Configuration

1. Twilio Setup:

   - Use sandbox number: +14155238886
   - Configure webhook: your-domain.com/twilio/webhook
   - Select POST method
   - Enable required webhooks:
     - Pre-webhooks: onMessageAdd
     - Post-webhooks: onMessageAdded, onDeliveryUpdated

2. Test Integration:
   - Send "join <code>" to Twilio number
   - Test with simple queries
   - Try document uploads

## API Documentation

Available at `/docs` when server is running.

### Endpoints Overview

- `POST /invoke`: Process queries synchronously
- `GET /stream/{message}`: Stream responses
- `POST /upload`: Handle document uploads
- `POST /twilio/webhook`: WhatsApp webhook
- `GET /twilio/webhook`: Webhook validation

## Environment Variables

Required in `.env`:

```env
# OpenAI Configuration
OPENAI_API_KEY=xxx
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4-turbo-preview

# Pinecone Configuration
PINECONE_API_KEY=xxx
PINECONE_INDEX_NAME=xxx
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Twilio Configuration
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=xxx
```

## Development

Run with hot reload:

```bash
uvicorn app.main:app --reload
```

### Testing

```bash
# Run tests
pytest

# Test WhatsApp integration locally
ngrok http 8000
# Update Twilio webhook URL with ngrok URL
```

### Logging

- Server logs: `server.log`
- WhatsApp webhook logs: `whatsapp.log`
- Error logs: `error.log`

### Error Handling

1. Document Processing:

   - Invalid file types
   - File size limits
   - Processing failures

2. WhatsApp Integration:

   - Message validation
   - Delivery failures
   - Webhook verification

3. Query Processing:
   - Invalid queries
   - Context retrieval issues
   - Response generation errors

### Performance Considerations

- Rate limiting on endpoints
- Document size restrictions
- Concurrent request handling
- Memory management for large documents

### Security

- Webhook signature validation
- API key management
- File upload validation
- Error message sanitization

## Deployment

### Docker Commands

```bash
# Build with specific tag
docker build -t ankitmalik84/agent-whatsapp:v1.0 .

# Run container
docker run -p 8000:8000 --env-file .env ankitmalik84/agent-whatsapp:latest

# View logs
docker logs -f container_id
```

### Health Checks

- `/health`: Server status
- `/metrics`: Performance metrics
- `/ready`: Readiness probe

### Monitoring

- Request/Response times
- Error rates
- Memory usage
- Document processing stats
- WhatsApp message delivery rates

## Troubleshooting

Common Issues:

1. WhatsApp Connection:

   - Check Twilio credentials
   - Verify webhook URL
   - Confirm sandbox joining

2. Document Processing:

   - Verify file formats
   - Check file permissions
   - Monitor memory usage

3. Vector Store:

   - Verify Pinecone connection
   - Check index existence
   - Monitor embedding process

4. API Issues:
   - Validate API keys
   - Check rate limits
   - Monitor response times
