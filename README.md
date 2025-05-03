# System Design Assistant with WhatsApp Integration

An AI-powered system design assistant that combines RAG (Retrieval Augmented Generation) with WhatsApp integration for easy access to system design knowledge and best practices.

## 🚀 Features

### Currently Available

- ✅ **WhatsApp Integration**: Query the assistant directly through WhatsApp
- ✅ **Document Processing**: Upload PDF/DOCX files for knowledge base expansion
- ✅ **RAG Pipeline**: Smart retrieval and response generation
- ✅ **API Endpoints**: RESTful and streaming interfaces
- ✅ **Docker Support**: Easy deployment with Docker

### 🚧 In Development

- 🔄 **Multi-language Support**: Support for different languages (Coming Soon)
- 🔄 **Voice Messages**: WhatsApp voice message processing
- 🔄 **Image Generation**: System architecture diagram generation
- 🔄 **Advanced Analytics**: Usage tracking and insights

## 🛠️ Tech Stack

- FastAPI
- LangGraph
- OpenAI
- Pinecone
- Twilio
- Docker

## 📱 WhatsApp Usage

1. Send message to: **+14155238886**
2. Available commands:
   - Text questions about system design
   - PDF/DOCX document uploads
   - "help" for command list

## 🔧 Development Setup

### Prerequisites

- Python 3.12+
- Docker
- API Keys:
  - OpenAI
  - Pinecone
  - Twilio

### Quick Start

````bash
# Clone repository
git clone <repository-url>

# Setup environment
cd server
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Add your API keys to .env

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
````

5. Run the server:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

1. Build the Docker image:

```bash
docker build -t your-username/system-design-rag:latest .
```

## 📚 Documentation

- [Server Documentation](server/README.md)
- [API Documentation](https://your-domain.com/docs) (when server is running)

## 🌟 Key Features in Detail

### WhatsApp Integration

- Direct messaging interface
- Document upload support
- Context-aware conversations
- Automatic error handling

### RAG Implementation

- Smart document processing
- Vector-based retrieval
- Context-aware responses
- Fallback research capability

### Document Processing

- PDF support
- DOCX support
- Text extraction
- Knowledge base integration

## 🔜 Roadmap

### Phase 1 (Current)

- ✅ Basic WhatsApp integration
- ✅ Document upload
- ✅ RAG implementation
- ✅ Docker support

### Phase 2 (In Progress)

- 🔄 Voice message support
- 🔄 Multi-language capabilities
- 🔄 Image generation
- 🔄 Enhanced error handling

### Phase 3 (Planned)

- 📋 Advanced analytics
- 📋 Custom training data
- 📋 API rate limiting

## 🤝 Contributing

### Frontend Development

We welcome frontend contributions! The project needs a modern, responsive web interface.

#### Planned Frontend Features

1. **Core Features**

- 🎯 Real-time chat interface
- 🎯 Document upload UI
- 🎯 Response streaming display
- 🎯 Syntax highlighting for code
- 🎯 Dark/Light theme support

2. **Advanced Features**

- 🎯 System design diagram viewer
- 🎯 Chat history management
- 🎯 Document library interface
- 🎯 User preferences settings
- 🎯 Mobile-responsive design

#### Tech Stack Requirements

- React/Next.js
- TypeScript
- Tailwind CSS
- WebSocket/SSE support
- Component library (MUI/Chakra UI)

#### Getting Started with Frontend

1. Setup development:

```bash
# Clone the repository
git clone https://github.com/ankitmalik84/AI_Agents_For_Socials_.git

# Navigate to frontend directory
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

2. Key areas for contribution:

- Component development
- State management
- API integration
- UI/UX improvements
- Testing implementation

3. Design guidelines:

- Modern, clean interface
- Responsive design
- Accessibility compliance
- Performance optimization

### How to Contribute

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to your fork
5. Create a Pull Request

### Development Guidelines

- Follow TypeScript best practices
- Write unit tests for components
- Maintain responsive design
- Document component usage
- Follow accessibility guidelines

Contributions are welcome!

## 🔗 Links

- [Docker Hub](https://hub.docker.com/u/ankitmalik84)

## 📞 Support

For support:

- Create an issue
- Contact: ankitmalik844903@gmail.com
