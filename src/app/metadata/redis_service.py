"""Redis service for document metadata storage."""

from __future__ import annotations

from typing import Any

import redis.asyncio as redis
from pydantic import BaseModel
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class DocumentMetadata(BaseModel):
    """Document metadata model."""

    title: str
    file_size: int
    page_count: int
    chunk_count: int
    source_path: str
    indexed_date: str
    file_hash: str
    additional_metadata: dict[str, Any] = {}


class RedisMetadataService:
    """Redis service for document metadata management."""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0) -> None:
        """
        Initialize Redis metadata service.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
        """
        self.redis_url = f'redis://{host}:{port}/{db}'
        self._redis: redis.Redis | None = None
        self.doc_metadata_key = 'doc_metadata:'

    async def connect(self) -> None:
        """Establish Redis connection."""
        try:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
            await self._redis.ping()
            logger.info('Successfully connected to Redis')
        except Exception as e:
            logger.error(f'Failed to connect to Redis: {e}')
            raise

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            logger.info('Redis connection closed')

    async def save_document_metadata(
        self,
        doc_id: str,
        metadata: DocumentMetadata,
    ) -> bool:
        """
        Save document metadata to Redis.

        Args:
            doc_id: Document identifier
            metadata: Document metadata

        Returns:
            True if successful
        """
        try:
            if not self._redis:
                await self.connect()

            key = f'{self.doc_metadata_key}{doc_id}'
            await self._redis.set(key, metadata.json())

            # Add to document index set
            await self._redis.sadd('indexed_documents', doc_id)

            logger.info(f'Saved metadata for document {doc_id}')
            return True
        except Exception as e:
            logger.error(f'Error saving document metadata: {e}')
            return False

    async def get_document_metadata(self, doc_id: str) -> DocumentMetadata | None:
        """
        Retrieve document metadata from Redis.

        Args:
            doc_id: Document identifier

        Returns:
            Document metadata if found
        """
        try:
            if not self._redis:
                await self.connect()

            key = f'{self.doc_metadata_key}{doc_id}'
            logger.info(f'Retrieving metadata for document {doc_id} from Redis')
            data = await self._redis.get(key)

            if data:
                return DocumentMetadata.parse_raw(data)
            return None
        except Exception as e:
            logger.error(f'Error retrieving document metadata: {e}')
            return None

    async def get_all_documents(self) -> list[DocumentMetadata]:
        """
        Retrieve all document metadata.

        Returns:
            List of document metadata
        """
        try:
            if not self._redis:
                await self.connect()

            # Get all document IDs from index
            doc_ids = await self._redis.smembers('indexed_documents')
            documents = []

            for doc_id in doc_ids:
                metadata = await self.get_document_metadata(doc_id)
                if metadata:
                    documents.append(metadata)

            return documents
        except Exception as e:
            logger.error(f'Error retrieving all documents: {e}')
            return []

    async def delete_document_metadata(self, doc_id: str) -> bool:
        """
        Delete document metadata from Redis.

        Args:
            doc_id: Document identifier

        Returns:
            True if successful
        """
        try:
            if not self._redis:
                await self.connect()

            key = f'{self.doc_metadata_key}{doc_id}'
            await self._redis.delete(key)
            await self._redis.srem('indexed_documents', doc_id)

            logger.info(f'Deleted metadata for document {doc_id}')
            return True
        except Exception as e:
            logger.error(f'Error deleting document metadata: {e}')
            return False
