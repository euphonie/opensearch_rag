# Source Code Documentation

This directory contains the source code for the LangChain OpenSearch RAG application.

## Directory Structure

```
src/
├── app/                # Main application code
│   ├── loader/         # Document loading and processing
│   ├── retriever/      # Vector retrieval
│   ├── ui/             # Gradio UI components
│   └── main.py         # Application entry point
└── README.md           # This file
```

## Components

### Main Application (`app/main.py`)

The entry point for the application that:
- Initializes the Gradio web interface
- Sets up document processing pipelines
- Configures the retrieval system
- Handles user interactions

### Document Loader (`app/loader/`)

Responsible for:
- Loading documents from various formats (PDF, TXT, MD, PY)
- Chunking documents into smaller pieces
- Generating embeddings using Ollama
- Storing document chunks and embeddings in OpenSearch

Key files:
- `config.py`: Configuration for document loading
- `document_loader.py`: Document loading and processing
- `embeddings.py`: Embedding generation
- `vector_store.py`: OpenSearch integration

### Retriever (`app/retriever/`)

Handles:
- Querying OpenSearch for relevant document chunks
- Ranking and filtering results
- Preparing context for the LLM

Key files:
- `opensearch_retriever.py`: OpenSearch query logic
- `context_builder.py`: Context preparation for LLM

### UI Components (`app/ui/`)

Contains:
- Gradio interface components
- User interaction handlers
- Result formatting and display

Key files:
- `gradio_app.py`: Gradio application setup
- `components.py`: UI component definitions
- `callbacks.py`: Event handlers for UI interactions

## Configuration

The application is configured through environment variables, with defaults defined in `app/loader/config.py`. Key configuration options:

### Ollama Settings

```python
self.ollama_host = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
self.embeddings_model = os.getenv('EMBEDDINGS_MODEL', 'mxbai-embed-large')
self.llm_model = os.getenv('LLM_MODEL', 'phi3.5')
self.embedder_type = os.getenv('EMBEDDER_TYPE', 'ollama')
self.llm_type = os.getenv('LLM_TYPE', 'ollama')
```

### Document Processing Settings

```python
self.chunk_size = int(os.getenv('CHUNK_SIZE', '1000'))
self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '200'))
```

### Database Settings

```python
self.opensearch_url = os.getenv('OPENSEARCH_URL', 'http://localhost:9200')
self.opensearch_username = os.getenv('OPENSEARCH_USERNAME', 'admin')
self.opensearch_password = os.getenv('OPENSEARCH_PASSWORD', 'admin')
self.opensearch_index_name = os.getenv('OPENSEARCH_INDEX_NAME', 'documents')
self.redis_host = os.getenv('REDIS_HOST', 'localhost')
self.redis_port = os.getenv('REDIS_PORT', '6379')
```

## Flow Diagrams

### Document Processing Flow

```
┌─────────┐     ┌───────────┐     ┌────────────┐     ┌────────────┐
│ Document│────▶│  Chunking │────▶│  Embedding │────▶│ OpenSearch │
│ Loading │     │           │     │ Generation │     │  Storage   │
└─────────┘     └───────────┘     └────────────┘     └────────────┘
```

### Query Processing Flow

```
┌─────────┐     ┌───────────┐     ┌────────────┐     ┌────────────┐
│  User   │────▶│  Embedding│────▶│ OpenSearch │────▶│    LLM     │
│  Query  │     │ Generation│     │  Retrieval │     │  Response  │
└─────────┘     └───────────┘     └────────────┘     └────────────┘
                                        │                  │
                                        ▼                  ▼
                                  ┌────────────┐    ┌────────────┐
                                  │   Redis    │    │    User    │
                                  │   Cache    │    │  Interface │
                                  └────────────┘    └────────────┘
```

## Development

### Adding New Document Types

To add support for new document types:
1. Update the `supported_extensions` list in `app/loader/config.py`
2. Implement a new loader in `app/loader/document_loader.py`
3. Register the loader in the document processing pipeline

### Changing Embedding Models

To use a different embedding model:
1. Ensure the model is available in Ollama
2. Update the `EMBEDDINGS_MODEL` environment variable
3. Adjust the embedding dimension in `app/loader/config.py` if necessary

### Customizing the UI

The Gradio interface can be customized by modifying the components in `app/ui/gradio_app.py`.

## Testing

Unit tests are located in the `tests/` directory at the project root. Run tests with:

```bash
pytest tests/
```

## Logging

The application uses Python's logging module, configured in `app/main.py`. Logs are written to:
- Console (for development)
- Log files in the `logs/` directory (for production)

## Error Handling

Error handling is implemented at multiple levels:
- Document processing errors are caught and reported
- OpenSearch connection issues are handled with retries
- UI errors are displayed to the user with helpful messages
