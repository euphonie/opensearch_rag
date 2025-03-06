"""Text splitting functionality."""
from __future__ import annotations

from typing import List, Optional

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .config import LoaderConfig

class TextSplitter:
    """Split documents into chunks."""

    def __init__(self, config: Optional[LoaderConfig] = None) -> None:
        """
        Initialize text splitter.

        Args:
            config: Optional loader configuration
        """
        self.config = config or LoaderConfig()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.

        Args:
            documents: Documents to split

        Returns:
            List of document chunks
        """
        return self.splitter.split_documents(documents) 