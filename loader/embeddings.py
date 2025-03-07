"""Embeddings management functionality."""
from __future__ import annotations

from typing import Optional

from langchain_community.embeddings import OllamaEmbeddings

from .config import LoaderConfig

class EmbeddingsManager:
    """Manage embeddings operations."""

    def __init__(self, config: Optional[LoaderConfig] = None) -> None:
        """
        Initialize embeddings manager.

        Args:
            config: Loader configuration
        """
        self.config = config or LoaderConfig()
        
        self.embeddings = OllamaEmbeddings(
            base_url=self.config.ollama_host,
            model=self.config.embeddings_model
        )
    
    async def get_embeddings(self, documents: List[Document]) -> List[List[float]]:
        """
        Get embeddings for a list of documents using the embeddings model.

        Args:
            documents: List of documents to embed
        """
        return self.embeddings.aembed_documents(documents)
    
    async def aembed_query(self, query: str) -> List[float]:
        """
        Get embeddings for a query using the embeddings model.

        Args:
            query: Query to embed
        """
        return self.embeddings.aembed_query(query)

    def get_embeddings_model(self) -> OllamaEmbeddings:
        """
        Get embeddings model.

        Returns:
            Ollama embeddings model
        """
        return self.embeddings 