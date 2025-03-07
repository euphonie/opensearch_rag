"""Document loading and processing entry point."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, List, Generator
import fitz
import traceback
import asyncio
from concurrent.futures import ThreadPoolExecutor
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from loader import (
    DocumentLoader,
    DocumentProcessor,
    LoaderConfig,
    EmbeddingsManager,
    get_vector_store
)

async def process_chunk(
    chunk: Document,
    embeddings_manager: EmbeddingsManager,
    vector_store: Any
) -> None:
    """
    Process a single document chunk in parallel.
    
    Args:
        chunk: Document chunk to process
        embeddings_manager: Embeddings manager instance
        vector_store: Vector store instance
    """
    # Add to vector store - it will handle embeddings internally
    return vector_store.add_texts(
        texts=[chunk.page_content],
        metadatas=[chunk.metadata]
    )

async def process_document_parallel(
    text: str,
    metadata: dict,
    embeddings_manager: EmbeddingsManager,
    vector_store: Any,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
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
        metadatas=[metadata]
    )
    
    total_chunks = len(chunks)
    tasks = []
    
    # Process chunks in parallel
    for i, chunk in enumerate(chunks):
        task = asyncio.create_task(
            process_chunk(chunk, embeddings_manager, vector_store)
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

async def load_documents(file_path: Path):
    """
    Load documents and store in vector database.
    
    Args:
        file_path: Path to document file
        
    Yields:
        Progress percentage
    """
    try:
        config = LoaderConfig()
        loader = DocumentLoader(config)
        embeddings_manager = EmbeddingsManager()
        vector_store = get_vector_store(config.embedder_type)
        
        # Get total pages
        total_pages = 0
        with fitz.open(str(file_path)) as doc:
            total_pages = len(doc)
            
        # Process each page
        with fitz.open(str(file_path)) as doc:
            for i, page in enumerate(doc):
                text = page.get_text()
                metadata = {"source": str(file_path), "page": i + 1}
                
                # Process page in parallel
                async for progress in process_document_parallel(
                    text=text,
                    metadata=metadata,
                    embeddings_manager=embeddings_manager,
                    vector_store=vector_store
                ):
                    # Calculate overall progress including page progress
                    overall_progress = (i * 100 + progress) / total_pages
                    yield overall_progress
                    
    except Exception as e:
        traceback.print_exc()
        raise e