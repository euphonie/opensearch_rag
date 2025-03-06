"""Document loading and processing entry point."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from loader import (
    DocumentLoader,
    DocumentProcessor,
    LoaderConfig
)

def load_documents(
    path: Path,
    config: Optional[LoaderConfig] = None
) -> None:
    """
    Load and process documents from path.

    Args:
        path: Path to file or directory
        config: Optional loader configuration
    """
    loader = DocumentLoader(config)
    processor = DocumentProcessor(config)

    # Load documents
    documents = (
        loader.load_directory(path)
        if path.is_dir()
        else loader.load_file(path)
    )

    # Process and store documents
    processor.process_documents(documents)