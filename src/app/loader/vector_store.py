from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.loader.config import LoaderConfig

from dotenv import load_dotenv
from langchain_community.embeddings import BedrockEmbeddings, OllamaEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import RequestsHttpConnection

load_dotenv()


class VectorStore:
    def __init__(self, config: LoaderConfig):
        self.config = config
        self.embedder_type = config.embedder_type
        self.embeddings = self.get_embeddings()

    def get_embeddings(self):
        if self.embedder_type == 'bedrock':
            return BedrockEmbeddings(
                model_id=self.config.bedrock_model_id,
            )
        elif self.embedder_type == 'ollama':
            try:
                return OllamaEmbeddings(
                    model=self.config.llm_model,
                )
            except Exception as e:
                raise ValueError(f'Error initializing Ollama embeddings: {e}') from e
        else:
            raise ValueError(f'Unsupported embedder type: {self.embedder_type}')

    def get_store(self):
        opensearch_index_name = self.config.opensearch_index_name
        opensearch_url = (self.config.opensearch_url,)

        # Define dimension based on the embedding model
        # Ollama's default models typically use 3072 dimensions
        embedding_dimension = self.config.embedding_size

        # Create index mapping with proper dimension
        index_mapping = {
            'settings': {
                'index': {
                    'knn': True,
                    'knn.algo_param.ef_search': 100,
                },
            },
            'mappings': {
                'properties': {
                    'vector_field': {
                        'type': 'knn_vector',
                        'dimension': embedding_dimension,
                        'method': {
                            'name': 'hnsw',
                            'space_type': 'cosinesimil',
                            'engine': 'nmslib',
                        },
                    },
                    'text': {'type': 'text'},
                    'metadata': {'type': 'object'},
                },
            },
        }

        store = OpenSearchVectorSearch(
            embedding_function=self.embeddings,
            opensearch_url=opensearch_url,
            index_name=opensearch_index_name,
            engine='nmslib',
            timeout=300,
            connection_class=RequestsHttpConnection,
            index_mapping=index_mapping,
        )

        return store
