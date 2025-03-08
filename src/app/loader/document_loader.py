"""Document loading functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from langchain.docstore.document import Document

from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
)

from loader.config import LoaderConfig
from loader.exceptions import LoaderError


class DocumentLoader:
    """Load documents from files and directories."""

    def __init__(self, config: LoaderConfig | None = None) -> None:
        """
        Initialize document loader.

        Args:
            config: Optional loader configuration
        """
        self.config = config or LoaderConfig()

    def load_file(self, file_path: Path) -> list[Document]:
        """
        Load a single file.

        Args:
            file_path: Path to file

        Returns:
            List of loaded documents

        Raises:
            LoaderError: If file cannot be loaded
        """
        if not file_path.exists():
            raise LoaderError(f'File not found: {file_path}')

        if file_path.suffix not in self.config.supported_extensions:
            raise LoaderError(f'Unsupported file type: {file_path.suffix}')

        try:
            if file_path.suffix == '.pdf':
                loader = PyPDFLoader(str(file_path))
            else:
                loader = TextLoader(str(file_path))
            return loader.load()
        except Exception as e:
            raise LoaderError(f'Failed to load file {file_path}: {str(e)}') from e

    def load_directory(self, dir_path: Path) -> list[Document]:
        """
        Load all supported files from directory.

        Args:
            dir_path: Directory path

        Returns:
            List of loaded documents

        Raises:
            LoaderError: If directory cannot be loaded
        """
        if not dir_path.is_dir():
            raise LoaderError(f'Directory not found: {dir_path}')

        try:
            loader = DirectoryLoader(
                str(dir_path),
                glob='**/*.*',
                loader_cls=TextLoader,
            )
            return loader.load()
        except Exception as e:
            raise LoaderError(f'Failed to load directory {dir_path}: {str(e)}') from e
