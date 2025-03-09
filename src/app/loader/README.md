# Document Loader Module

This module handles document loading, processing, embedding generation, and vector storage for the RAG application.

## Components

### Configuration (`config.py`)

The `LoaderConfig` class manages all configuration settings for document processing:

```python
class LoaderConfig:
    """Configuration for document loading."""

    def __init__(self, config: dict[str, Any] = None):
        # Provider selection
        self.embedding_provider = os.getenv('EMBEDDING_PROVIDER', 'ollama').lower()

        # Ollama settings
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
        self.embeddings_model = os.getenv('EMBEDDINGS_MODEL', 'mxbai-embed-large')
        self.llm_model = os.getenv('LLM_MODEL', 'phi3.5')

        # Document processing settings
        self.chunk_size = int(os.getenv('CHUNK_SIZE', '1000'))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '200'))

        # Database settings
        self.opensearch_url = os.getenv('OPENSEARCH_URL', 'http://localhost:9200')
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
```

Key features:
- Environment variable integration
- Default values for all settings
- Configuration validation
- Support for multiple embedding providers

### Document Loader (`document_loader.py`)

Handles loading and processing documents from various formats:

```python
class DocumentLoader:
    """Load and process documents for RAG."""

    def __init__(self, config: LoaderConfig):
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
```

Key features:
- Support for multiple document formats (PDF, TXT, MD, PY)
- Text extraction and cleaning
- Document chunking with configurable size and overlap
- Metadata extraction and preservation

### Embeddings (`embeddings.py`)

Manages embedding generation for documents and queries:

```python
class OllamaEmbeddings:
    """Generate embeddings using Ollama."""

    def __init__(self, config: LoaderConfig):
        self.config = config
        self.client = httpx.Client(timeout=60.0)
        self.cache = {}
```

Key features:
- Integration with Ollama for local embedding generation
- Optional OpenAI integration
- Caching for performance optimization
- Error handling and retries
- Batch processing for efficiency

### Vector Store (`vector_store.py`)

Handles storage and retrieval of document chunks and embeddings:

```python
class OpenSearchVectorStore:
    """Store and retrieve vectors in OpenSearch."""

    def __init__(self, config: LoaderConfig):
        self.config = config
        self.client = self._create_client()
        self._ensure_index()
```

Key features:
- OpenSearch connection management
- Index creation and configuration
- Document storage with metadata
- Vector search with similarity scoring
- Filtering and result ranking

## Usage Examples

### Loading and Processing Documents

```python
# Initialize configuration
config = LoaderConfig()

# Create document loader
loader = DocumentLoader(config)

# Load and process a document
document_path = "path/to/document.pdf"
chunks = loader.load_and_split(document_path)

# Generate embeddings
embedder = OllamaEmbeddings(config)
embeddings = [embedder.embed_query(chunk.page_content) for chunk in chunks]

# Store in OpenSearch
vector_store = OpenSearchVectorStore(config)
vector_store.add_documents(chunks, embeddings)
```

### Retrieving Documents

```python
# Initialize components
config = LoaderConfig()
embedder = OllamaEmbeddings(config)
vector_store = OpenSearchVectorStore(config)

# Generate query embedding
query = "What is the main topic of the document?"
query_embedding = embedder.embed_query(query)

# Retrieve relevant chunks
results = vector_store.similarity_search_with_score(
    query_embedding,
    k=5  # Number of results
)

# Process results
for doc, score in results:
    print(f"Score: {score}")
    print(f"Content: {doc.page_content}")
    print(f"Source: {doc.metadata['source']}")
```

## Configuration Options

### Embedding Providers

The module supports multiple embedding providers:

1. **Ollama** (default):
   - Local embedding generation
   - Configurable models
   - No API key required

2. **OpenAI**:
   - Cloud-based embedding generation
   - Higher quality embeddings
   - Requires API key

### Document Processing

Document processing can be customized with:

- **Chunk Size**: Controls the size of document chunks (default: 1000)
- **Chunk Overlap**: Controls the overlap between chunks (default: 200)
- **Supported Extensions**: File types that can be processed

### Vector Storage

OpenSearch vector storage options:

- **Index Name**: Name of the OpenSearch index (default: documents)
- **Embedding Size**: Dimension of the embedding vectors
- **Similarity Metric**: Method for calculating similarity (default: cosine)

## Error Handling

The module implements comprehensive error handling:

- **Document Loading Errors**: Invalid formats, encoding issues
- **Embedding Generation Errors**: API failures, model issues
- **OpenSearch Errors**: Connection issues, index problems

## Performance Optimization

Several optimizations are implemented:

- **Embedding Caching**: Frequently used embeddings are cached
- **Batch Processing**: Documents are processed in batches
- **Connection Pooling**: Database connections are reused
- **Asynchronous Operations**: Non-blocking operations where possible

## Extending the Module

### Adding New Document Types

To add support for new document types:

1. Implement a new loader function in `document_loader.py`:
   ```python
   def load_custom_format(file_path: str) -> str:
       # Implementation for loading custom format
       return text
   ```

2. Register the loader in the file extension mapping:
   ```python
   self.loaders = {
       ".pdf": self._load_pdf,
       ".txt": self._load_text,
       ".custom": load_custom_format
   }
   ```

### Using Different Embedding Models

To use a different embedding model:

1. Update the `EMBEDDINGS_MODEL` environment variable
2. Adjust the embedding dimension in `config.py` if necessary
3. Update any model-specific parameters in `embeddings.py`
