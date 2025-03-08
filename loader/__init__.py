"""Document loading and processing module."""

from __future__ import annotations

from .config import LoaderConfig
from .document_loader import DocumentLoader
from .document_processor import DocumentProcessor
from .embeddings import EmbeddingsManager
from .exceptions import LoaderError
from .vector_store import get_vector_store

__all__ = [
    'DocumentLoader',
    'DocumentProcessor',
    'EmbeddingsManager',
    'LoaderError',
    'LoaderConfig',
    'get_vector_store',
]
