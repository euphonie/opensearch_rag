"""Vector store management functionality."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from opensearchpy import OpenSearch

from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma

from .config import LoaderConfig
from .embeddings import EmbeddingsManager

load_dotenv()

class VectorStore:
    """Vector store implementation for document storage and retrieval."""

    def __init__(self) -> None:
        """Initialize vector store with configuration from environment."""
        # OpenSearch configuration
        self.host = os.getenv("OPENSEARCH_HOST", "localhost")
        self.port = int(os.getenv("OPENSEARCH_PORT", "9200"))
        self.index_name = os.getenv("OPENSEARCH_INDEX_NAME", "document-index")
        
        # Vector store configuration
        self.vector_field = os.getenv("VECTOR_FIELD", "vector_field")
        self.text_field = os.getenv("TEXT_FIELD", "text")
        self.metadata_field = os.getenv("metadata_field", "metadata")

        # Initialize OpenSearch client
        self.client = OpenSearch(
            hosts=[{"host": self.host, "port": self.port}],
            http_auth=None,  # Add authentication if needed
            use_ssl=False,   # Enable SSL if needed
            verify_certs=False,
            ssl_show_warn=False,
        )

    def store_documents(
        self,
        documents: List[Dict[str, Any]],
        vectors: List[List[float]]
    ) -> None:
        """
        Store documents with their vector embeddings.

        Args:
            documents: List of document dictionaries
            vectors: List of vector embeddings
        """
        for doc, vector in zip(documents, vectors):
            if doc.metadata.get("creationdate") == '' or not isinstance(doc.metadata.get("creationdate"), datetime):
                doc.metadata["creationdate"] = datetime.now().strftime("%Y-%m-%d")
            body = {
                self.text_field: doc.page_content,
                self.vector_field: vector,
                self.metadata_field: doc.metadata
            }
            
            self.client.index(
                index=self.index_name,
                body=body,
                refresh=True
            )

    def similarity_search(
        self,
        query_vector: List[float],
        k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search using vector embeddings.

        Args:
            query_vector: Query vector embedding
            k: Number of results to return

        Returns:
            List of similar documents with scores
        """
        script_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": f"cosineSimilarity(params.query_vector, '{self.vector_field}') + 1.0",
                    "params": {"query_vector": query_vector}
                }
            }
        }

        response = self.client.search(
            index=self.index_name,
            body={
                "size": k,
                "query": script_query,
                "_source": [self.text_field, self.metadata_field]
            }
        )

        results = []
        for hit in response["hits"]["hits"]:
            results.append({
                "text": hit["_source"][self.text_field],
                "metadata": hit["_source"].get(self.metadata_field, {}),
                "score": hit["_score"]
            })

        return results

    def clear(self) -> None:
        """Clear all documents from the vector store."""
        try:
            self.client.indices.delete(index=self.index_name)
        except Exception as e:
            print(f"Error clearing index: {e}")

class VectorStoreManager:
    """Manage vector store operations."""

    def __init__(self, config: Optional[LoaderConfig] = None) -> None:
        """
        Initialize vector store manager.

        Args:
            config: Optional loader configuration
        """
        self.config = config or LoaderConfig()
        self.embeddings_manager = EmbeddingsManager(self.config)
        self.vector_store = self._initialize_store()

    def _initialize_store(self) -> VectorStore:
        """Initialize vector store."""
        return VectorStore()

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to vector store.

        Args:
            documents: Documents to add
        """
        vectors = self.embeddings_manager.get_embeddings(documents)
        self.vector_store.store_documents(documents, vectors)

    def similarity_search(
        self,
        query: str,
        k: int = 4
    ) -> List[Document]:
        """
        Search for similar documents.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar documents
        """
        query_vector = self.embeddings_manager.get_embeddings([query])[0]
        results = self.vector_store.similarity_search(query_vector, k=k)
        return [Document(page_content=result["text"], metadata=result["metadata"]) for result in results] 