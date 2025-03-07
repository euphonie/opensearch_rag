"""Configuration for document loading and processing."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any, Literal

class LoaderConfig:
    """Configuration for document loading."""
    
    SUPPORTED_PROVIDERS = Literal["openai", "ollama"]
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize configuration."""
        config = config or {}
        
        # Provider selection
        self.embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama").lower()
        if self.embedding_provider not in ["openai", "ollama"]:
            raise ValueError("EMBEDDING_PROVIDER must be either 'openai' or 'ollama'")
        
        # OpenAI settings
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_org_id = os.getenv("OPENAI_ORGANIZATION")
        
        # Ollama settings
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.embeddings_model = os.getenv("EMBEDDINGS_MODEL", "mxbai-embed-large")
        self.llm_model = os.getenv("LLM_MODEL", "phi3.5")
        self.embedder_type = os.getenv("EMBEDDER_TYPE", "bedrock")
        self.llm_type = os.getenv("LLM_TYPE", "bedrock")

        # General settings
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        self.vector_store_path = Path(os.getenv("VECTOR_STORE_PATH", "vector_store"))
        self.supported_extensions = os.getenv("SUPPORTED_EXTENSIONS", ".txt,.md,.py").split(",")

    def validate(self):
        """
        Validate the configuration.
        
        Raises:
            ValueError: If required settings are missing
        """
        if self.embedding_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required when using OpenAI provider")
        elif self.embedding_provider == "ollama" and not self.ollama_host:
            raise ValueError("OLLAMA_HOST environment variable is required when using Ollama provider")
        
        if not self.vector_store_path.parent.exists():
            self.vector_store_path.parent.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "embedding_provider": self.embedding_provider,
            "vector_store_path": str(self.vector_store_path),
            "supported_extensions": self.supported_extensions,
            "openai_api_key": self.openai_api_key,
            "openai_org_id": self.openai_org_id,
            "ollama_host": self.ollama_host,
            "embeddings_model": self.embeddings_model,
            "llm_model": self.llm_model,
            "embedder_type": self.embedder_type
        } 