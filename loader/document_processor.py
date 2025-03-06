"""Document processing functionality."""
from __future__ import annotations

from typing import List, Optional

from langchain.docstore.document import Document

from .config import LoaderConfig
from .text_splitter import TextSplitter
from .embeddings import EmbeddingsManager
from .vector_store import VectorStoreManager

class DocumentProcessor:
    """Process and store documents."""

    def __init__(self, config: Optional[LoaderConfig] = None) -> None:
        """
        Initialize document processor.

        Args:
            config: Optional loader configuration
        """
        self.config = config or LoaderConfig()
        self.text_splitter = TextSplitter(self.config)
        self.embeddings_manager = EmbeddingsManager(self.config)
        self.vector_store = VectorStoreManager(self.config)

    def process_documents(self, documents: List[Document]) -> None:
        """
        Process documents and store in vector store.

        Args:
            documents: List of documents to process
        """
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)

        # Get embeddings and store in vector store
        self.vector_store.add_documents(chunks) 