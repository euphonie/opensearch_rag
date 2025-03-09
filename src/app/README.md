# Application Code

This directory contains the main application code for the LangChain OpenSearch RAG system.

## Overview

The application is built around several key components:
- Document loading and processing
- Embedding generation
- Vector storage and retrieval
- LLM-based question answering
- Web interface for user interaction

## Components

### Main Application (`main.py`)

The entry point for the application that:
- Initializes configuration
- Sets up logging
- Launches the Gradio web interface
- Handles application lifecycle

### Document Loader (`loader/`)

The document loader module handles:

#### Configuration (`loader/config.py`)

Manages application configuration through environment variables:
- Embedding provider settings (Ollama or OpenAI)
- Document processing parameters
- Database connection details
- Model selection

#### Document Processing (`loader/document_loader.py`)

Handles:
- Loading documents from various formats
- Text extraction
- Document chunking
- Metadata extraction

#### Embedding Generation (`loader/embeddings.py`)

Responsible for:
- Generating embeddings using Ollama or OpenAI
- Caching embeddings for performance
- Handling embedding errors and retries

#### Vector Store (`loader/vector_store.py`)

Manages:
- OpenSearch connection and index creation
- Document storage and retrieval
- Vector search operations

### UI Components (`ui/`)

The UI module provides:

#### Gradio App (`ui/gradio_app.py`)

Implements:
- Web interface layout
- File upload functionality
- Chat interface
- Result display

#### Components (`ui/components.py`)

Contains:
- Reusable UI components
- Styling and layout definitions
- Input validation

#### Callbacks (`ui/callbacks.py`)

Handles:
- User interaction events
- Document processing workflows
- Query processing
- Error handling and user feedback

## Data Flow

### Document Processing

1. User uploads document through the UI
2. Document is loaded and text is extracted
3. Text is split into chunks with overlap
4. Embeddings are generated for each chunk
5. Chunks and embeddings are stored in OpenSearch
6. Confirmation is displayed to the user

### Query Processing

1. User enters a question in the chat interface
2. Question is embedded using the same model as documents
3. OpenSearch is queried for relevant document chunks
4. Retrieved chunks are assembled into context
5. Question and context are sent to the LLM
6. LLM generates an answer
7. Answer and source references are displayed to the user

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| OLLAMA_HOST | URL for Ollama API | http://host.docker.internal:11434 |
| EMBEDDINGS_MODEL | Model for generating embeddings | mxbai-embed-large |
| LLM_MODEL | Model for text generation | phi3.5 |
| EMBEDDER_TYPE | Type of embedder to use | ollama |
| LLM_TYPE | Type of LLM to use | ollama |
| CHUNK_SIZE | Size of document chunks | 1000 |
| CHUNK_OVERLAP | Overlap between chunks | 200 |
| OPENSEARCH_URL | URL for OpenSearch | http://localhost:9200 |
| OPENSEARCH_INDEX_NAME | Index name for documents | documents |
| REDIS_HOST | Hostname for Redis | localhost |
| REDIS_PORT | Port for Redis | 6379 |

## Error Handling

The application implements comprehensive error handling:

- **Document Loading Errors**: Reported to the user with specific error messages
- **Embedding Generation Errors**: Retried with exponential backoff
- **OpenSearch Connection Issues**: Handled with connection pooling and retries
- **LLM Generation Errors**: Fallback responses provided
- **UI Errors**: Displayed to the user with helpful messages

## Performance Considerations

The application includes several performance optimizations:

- **Redis Caching**: Frequently used embeddings and queries are cached
- **Batch Processing**: Documents are processed in batches for efficiency
- **Connection Pooling**: Database connections are reused
- **Asynchronous Operations**: Non-blocking operations for UI responsiveness

## Security Considerations

Important security aspects:

- **Input Validation**: All user inputs are validated
- **Error Handling**: Errors are logged without exposing sensitive information
- **Authentication**: Optional authentication can be enabled
- **Environment Variables**: Sensitive information is stored in environment variables

## Extending the Application

### Adding New Document Types

To add support for new document types:
1. Implement a new loader in `loader/document_loader.py`
2. Register the loader in the document processing pipeline
3. Update the supported extensions list in `loader/config.py`

### Using Different Models

To use different models:
1. Ensure the models are available in Ollama
2. Update the environment variables for model names
3. Adjust embedding dimensions if necessary

### Adding New Features

The modular architecture makes it easy to add new features:
1. Implement new functionality in the appropriate module
2. Update the UI to expose the new features
3. Add any necessary configuration options
