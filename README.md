# LangChain OpenSearch RAG

A Retrieval-Augmented Generation (RAG) application using LangChain, OpenSearch, and Ollama for local LLM inference.

![Demo](demo.gif)

## Overview

This project implements a document processing and question-answering system that:

1. Processes documents from various formats (PDF, TXT, MD, PY)
2. Generates embeddings using local models via Ollama
3. Stores document chunks and embeddings in OpenSearch
4. Provides a Gradio web interface for document upload and querying
5. Uses Redis for caching to improve performance

## Architecture

The system consists of the following components:

- **App Service**: Python application with Gradio web interface
- **OpenSearch**: Vector database for storing document embeddings
- **OpenSearch Dashboards**: Web interface for OpenSearch management
- **Redis**: Caching layer that saves metadata from processed documents
- **Ollama**: Local inference for embeddings and LLM responses

## Prerequisites

- Docker and Docker Compose
- Ollama installed locally (optional, can use containerized version)
- At least 8GB RAM for running all services
- Git

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/langchain-opensearch-rag.git
   cd langchain-opensearch-rag
   ```

2. Create a `.env` file in the `infra/secrets` directory:
   ```bash
   mkdir -p infra/secrets
   touch infra/secrets/.env
   ```

3. Start the services:
   ```bash
   docker-compose -f infra/docker-compose.yml up -d
   ```

4. Access the web interface at http://localhost:8081

## Configuration

### Environment Variables

Key environment variables that can be configured:

| Variable | Description | Default |
|----------|-------------|---------|
| OLLAMA_HOST | URL for Ollama API | http://host.docker.internal:11434 |
| EMBEDDINGS_MODEL | Model for generating embeddings | mxbai-embed-large |
| LLM_MODEL | Model for text generation | phi3.5 |
| OPENSEARCH_URL | URL for OpenSearch | http://opensearch:9200 |
| REDIS_HOST | Hostname for Redis | redis |
| CHUNK_SIZE | Size of document chunks | 1000 |
| CHUNK_OVERLAP | Overlap between chunks | 200 |

### Using Local Ollama

The default configuration uses your local Ollama installation. Make sure Ollama is running:

```bash
ollama serve
```

And that you have the required models:

```bash
ollama pull mxbai-embed-large
ollama pull phi3.5
```

## Usage

1. **Upload Documents**: Use the web interface to upload documents (PDF, TXT, MD, PY)
2. **Process Documents**: The system will chunk, embed, and store the documents
3. **Ask Questions**: Query the system about the content of your documents
4. **View Sources**: See which document chunks were used to generate the answer

## Development

### Project Structure

```
langchain-opensearch-rag/
├── infra/                  # Infrastructure configuration
│   ├── docker-compose.yml  # Docker Compose configuration
│   ├── redis/              # Redis configuration
│   └── scripts/            # Helper scripts
├── src/                    # Source code
│   └── app/                # Application code
│       ├── loader/         # Document loading and processing
│       ├── retriever/      # Vector retrieval
│       ├── ui/             # Gradio UI components
│       └── main.py         # Application entry point
└── README.md               # This file
```

### Local Development

To develop locally:

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python src/app/main.py
   ```

## Troubleshooting

### Common Issues

1. **Redis Connection Issues**: Ensure Redis is running and accessible from the app container
2. **Ollama Connection Issues**: Verify Ollama is running and the OLLAMA_HOST is correctly set
3. **OpenSearch Connection Issues**: Check OpenSearch logs and ensure it's healthy

### Logs

To view logs:

```bash
# All services
docker-compose -f infra/docker-compose.yml logs -f

# Specific service
docker-compose -f infra/docker-compose.yml logs -f app
```

## License

[MIT License](LICENSE)
