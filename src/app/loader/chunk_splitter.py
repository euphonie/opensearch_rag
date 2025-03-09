import re
from datetime import datetime
from typing import Any

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.utils.logging_config import setup_logger

logger = setup_logger(__name__)


class ChunkSplitter:
    """Strategy for splitting a document into processable parts with enhanced context."""

    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = self.get_splitter()

    def get_splitter(self) -> RecursiveCharacterTextSplitter:
        """
        Get configured text splitter with optimized separators.

        Returns:
            Configured RecursiveCharacterTextSplitter instance
        """
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=[
                '\n\n',  # Paragraphs
                '\n',  # Lines
                '. ',  # Sentences with space
                '? ',  # Questions with space
                '! ',  # Exclamations with space
                ';',  # Semicolons
                ':',  # Colons
                ',',  # Commas
                ' ',  # Words
                '',  # Characters
            ],
            keep_separator=True,
        )

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text for better splitting.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned and normalized text
        """
        # Replace multiple newlines and whitespace
        text = re.sub(r'\n{2,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)

        # Normalize sentence endings
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)

        # Remove excessive whitespace while preserving paragraph breaks
        text = '\n\n'.join(line.strip() for line in text.split('\n\n'))

        return text.strip()

    def split_into_chunks(self, text: str, metadata: dict[str, Any]) -> list[Document]:
        """
        Split text into chunks with enhanced metadata.

        Args:
            text: Text to split
            metadata: Base metadata for chunks

        Returns:
            List of Document objects with enhanced metadata
        """
        # Clean and normalize text
        text = self.clean_text(text)

        # Add processing metadata
        enhanced_metadata = {
            **metadata,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'total_length': len(text),
            'processing_timestamp': datetime.now().isoformat(),
        }

        # Create initial chunks
        chunks = self.text_splitter.create_documents(
            texts=[text],
            metadatas=[enhanced_metadata],
        )

        # Add chunk-specific metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata.update(
                {
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'chunk_length': len(chunk.page_content),
                    'is_first_chunk': i == 0,
                    'is_last_chunk': i == len(chunks) - 1,
                },
            )

        return chunks

    def add_neighbouring_content(self, chunks: list[Document]) -> list[Document]:
        """
        Enhance chunks with context from neighboring chunks.

        Args:
            chunks: List of document chunks

        Returns:
            List of enhanced Document objects with context
        """
        enhanced_chunks = []

        for i, chunk in enumerate(chunks):
            # Get context chunks
            prev_chunk = chunks[i - 1] if i > 0 else None
            next_chunk = chunks[i + 1] if i < len(chunks) - 1 else None

            # Build enhanced content sections
            content_sections = []

            # Add previous context if available
            if prev_chunk:
                prev_text = self._extract_relevant_context(
                    prev_chunk.page_content,
                    is_previous=True,
                )
                if prev_text:
                    content_sections.append(f'Previous Context: {prev_text}')

            # Add current content
            current_text = chunk.page_content.strip()
            if current_text:
                content_sections.append(f'Current Content: {current_text}')

            # Add next context if available
            if next_chunk:
                next_text = self._extract_relevant_context(
                    next_chunk.page_content,
                    is_previous=False,
                )
                if next_text:
                    content_sections.append(f'Next Context: {next_text}')

            # Create enhanced metadata
            enhanced_metadata = {
                **chunk.metadata,
                'has_previous': bool(prev_chunk),
                'has_next': bool(next_chunk),
                'context_length': len('\n'.join(content_sections)),
            }

            # Create enhanced chunk
            enhanced_chunk = Document(
                page_content='\n'.join(content_sections),
                metadata=enhanced_metadata,
            )
            enhanced_chunks.append(enhanced_chunk)

        return enhanced_chunks

    def _extract_relevant_context(
        self,
        text: str,
        is_previous: bool,
        max_length: int = 200,
    ) -> str:
        """
        Extract most relevant context from neighboring chunk.

        Args:
            text: Text to extract context from
            is_previous: Whether this is previous context
            max_length: Maximum length of context to extract

        Returns:
            Extracted context string
        """
        text = text.strip()
        if not text:
            return ''

        # For previous context, prefer end of text
        if is_previous:
            # Try to find last complete sentence
            sentences = re.split(r'[.!?]+\s+', text)
            if len(sentences) > 1:
                context = sentences[-2:] if len(sentences) > 2 else sentences
                return ' '.join(context)[:max_length].strip()
            return text[-max_length:].strip()

        # For next context, prefer start of text
        else:
            # Try to find first complete sentences
            sentences = re.split(r'[.!?]+\s+', text)
            if len(sentences) > 1:
                context = sentences[:2]
                return ' '.join(context)[:max_length].strip()
            return text[:max_length].strip()
