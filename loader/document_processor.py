"""Document processing functionality."""

from __future__ import annotations

import hashlib
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain.docstore.document import Document

    from .vector_store import VectorStore

import asyncio
import traceback
from datetime import datetime
from pathlib import Path

import fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter

from metadata.redis_service import DocumentMetadata, RedisMetadataService
from utils.logging_config import setup_logger

from .config import LoaderConfig
from .embeddings import EmbeddingsManager

logger = setup_logger(__name__)


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
            vector_store: Optional vector store instance
        """
        self.config = config or LoaderConfig()
        self.embeddings_manager = EmbeddingsManager(self.config)
        self.vector_store = vector_store
        self.metadata_service = RedisMetadataService(
            host=self.config.redis_host,
            port=int(self.config.redis_port),
        )

    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b''):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

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
            # Get total pages and file info
            total_pages = 0
            chunk_count = 0
            file_size = os.path.getsize(file_path)
            file_hash = await self._calculate_file_hash(file_path)

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
                        chunk_count += 1
                        yield overall_progress

                    # Ensure we yield 100% for each page
                    if page_progress < 100:
                        overall_progress = ((i + 1) * 100) / total_pages
                        yield overall_progress

            # Save document metadata
            doc_metadata = DocumentMetadata(
                title=Path(file_path).name,
                file_size=file_size,
                page_count=total_pages,
                chunk_count=chunk_count,
                source_path=str(file_path),
                indexed_date=datetime.now().isoformat(),
                file_hash=file_hash,
                additional_metadata={'processor_version': '1.0'},
            )

            await self.metadata_service.save_document_metadata(file_hash, doc_metadata)

        except Exception as e:
            traceback.print_exc()
            raise ValueError(f'Error processing document: {str(e)}') from e

    async def get_indexed_documents(self):
        """Get list of indexed documents from metadata service."""
        try:
            documents = await self.metadata_service.get_all_documents()
            return [{'title': doc.title, 'id': doc.file_hash} for doc in documents]
        except Exception as e:
            logger.error(f'Error fetching indexed documents: {e}')
            return []

    async def get_document_metadata(self, doc_id: str) -> dict | None:
        """
        Get document metadata by ID.

        Args:
            doc_id: Document identifier

        Returns:
            Document metadata if found
        """
        try:
            metadata = await self.metadata_service.get_document_metadata(doc_id)
            if metadata:
                return metadata.dict()
            return None
        except Exception as e:
            logger.error(f'Error fetching document metadata: {e}')
            return None
