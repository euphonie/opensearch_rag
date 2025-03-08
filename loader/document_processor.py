"""Document processing functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from langchain.docstore.document import Document

    from .vector_store import VectorStore

import asyncio
import traceback

import fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .config import LoaderConfig
from .embeddings import EmbeddingsManager


class DocumentProcessor:
    """Process and store documents."""

    def __init__(
        self,
        config: LoaderConfig | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        """
        Initialize document processor.

        Args:
            config: Optional loader configuration
        """
        self.config = config or LoaderConfig()
        self.embeddings_manager = EmbeddingsManager(self.config)
        self.vector_store = vector_store

    async def process_chunk(
        self,
        chunk: Document,
    ) -> None:
        """
        Process a single document chunk in parallel.

        Args:
            chunk: Document chunk to process
            embeddings_manager: Embeddings manager instance
            vector_store: Vector store instance
        """
        # Add to vector store - it will handle embeddings internally
        return self.vector_store.get_store().add_texts(
            texts=[chunk.page_content],
            metadatas=[chunk.metadata],
        )

    async def process_document_parallel(
        self,
        text: str,
        metadata: dict,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Process document text in parallel with chunking and embedding.

        Args:
            text: Document text to process
            metadata: Document metadata
            embeddings_manager: Embeddings manager instance
            vector_store: Vector store instance
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks

        Yields:
            Progress percentage
        """
        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

        # Split text into chunks
        chunks = text_splitter.create_documents(
            texts=[text],
            metadatas=[metadata],
        )

        total_chunks = len(chunks)
        tasks = []

        # Process chunks in parallel
        for i, chunk in enumerate(chunks):
            task = asyncio.create_task(
                self.process_chunk(chunk),
            )
            tasks.append(task)

            # Yield progress
            progress = ((i + 1) / total_chunks) * 100
            yield progress

            # Process in batches to avoid overwhelming the system
            if len(tasks) >= 5:  # Process 5 chunks at a time
                await asyncio.gather(*tasks)
                tasks = []

        # Process any remaining tasks
        if tasks:
            await asyncio.gather(*tasks)

    async def load_documents(self, file_path: Path):
        """
        Load documents and store in vector database.

        Args:
            file_path: Path to document file

        Yields:
            Progress percentage (float between 0 and 100)
        """
        try:
            # Get total pages
            total_pages = 0
            with fitz.open(str(file_path)) as doc:
                total_pages = len(doc)
                if total_pages == 0:
                    raise ValueError('Document contains no pages')

            # Process each page
            with fitz.open(str(file_path)) as doc:
                for i, page in enumerate(doc):
                    text = page.get_text()
                    metadata = {
                        'source': str(file_path),
                        'page': i + 1,
                        'total_pages': total_pages,
                    }

                    # Process page in parallel
                    page_progress = 0
                    async for progress in self.process_document_parallel(
                        text=text,
                        metadata=metadata,
                    ):
                        # Calculate overall progress including page progress
                        page_progress = progress
                        overall_progress = ((i * 100) + page_progress) / total_pages
                        yield overall_progress

                    # Ensure we yield 100% for each page
                    if page_progress < 100:
                        overall_progress = ((i + 1) * 100) / total_pages
                        yield overall_progress

        except Exception as e:
            traceback.print_exc()
            raise ValueError(f'Error processing document: {str(e)}') from e

    async def get_indexed_documents(self):
        """Get list of indexed documents from OpenSearch."""
        return []
