from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.loader.config import LoaderConfig

from dotenv import load_dotenv
from langchain_community.embeddings import BedrockEmbeddings, OllamaEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import OpenSearch, RequestsHttpConnection

from app.utils.logging_config import setup_logger

logger = setup_logger(__name__)

load_dotenv()


class VectorStore:
    def __init__(self, config: LoaderConfig):
        self.config = config
        self.embedder_type = config.embedder_type
        self.embeddings = self.get_embeddings()
        self._ensure_index()

    def get_embeddings(self):
        if self.embedder_type == 'bedrock':
            return BedrockEmbeddings(
                model_id=self.config.bedrock_model_id,
            )
        elif self.embedder_type == 'ollama':
            try:
                return OllamaEmbeddings(
                    base_url=self.config.ollama_host,
                    model=self.config.llm_model,
                )
            except Exception as e:
                raise ValueError(f'Error initializing Ollama embeddings: {e}') from e
        else:
            raise ValueError(f'Unsupported embedder type: {self.embedder_type}')

    def _ensure_index(self):
        """Ensure the OpenSearch index exists with proper configuration."""
        try:
            client = OpenSearch(
                hosts=[self.config.opensearch_url],
                connection_class=RequestsHttpConnection,
                timeout=30,
            )

            index_name = self.config.opensearch_index_name
            if not client.indices.exists(index=index_name):
                logger.info(f'Creating index {index_name} with optimized settings')
                client.indices.create(
                    index=index_name,
                    body=self._get_index_mapping(),
                )
        except Exception as e:
            logger.error(f'Error ensuring index: {e}')
            raise

    def _get_index_mapping(self):
        """Get optimized index mapping for better search results."""
        embedding_dimension = self.config.embedding_size

        return {
            'settings': {
                'index': {
                    'knn': True,
                    'knn.algo_param.ef_search': 512,  # Increased for better recall
                    'knn.algo_param.ef_construction': 512,  # Better index construction
                    'knn.algo_param.m': 48,  # Increased neighborhood size
                    'number_of_shards': 1,  # Single shard for better kNN
                    'number_of_replicas': 1,
                    'refresh_interval': '1s',  # Faster refresh for testing
                    'analysis': {
                        'analyzer': {
                            'default': {
                                'type': 'standard',
                                'stopwords': '_english_',
                            },
                        },
                    },
                },
            },
            'mappings': {
                'properties': {
                    'vector_field': {
                        'type': 'knn_vector',
                        'dimension': embedding_dimension,
                        'method': {
                            'name': 'hnsw',
                            'engine': 'nmslib',
                            'space_type': 'l2',
                            'parameters': {
                                'ef_construction': 512,
                                'm': 48,
                            },
                        },
                    },
                    'text': {
                        'type': 'text',
                        'analyzer': 'standard',
                        'term_vector': 'with_positions_offsets',
                        'fields': {
                            'keyword': {
                                'type': 'keyword',
                                'ignore_above': 256,
                            },
                        },
                    },
                    'metadata': {
                        'type': 'object',
                        'properties': {
                            'source': {'type': 'keyword'},
                            'page': {'type': 'integer'},
                            'chunk_index': {'type': 'integer'},
                            'total_chunks': {'type': 'integer'},
                            'chunk_size': {'type': 'integer'},
                            'chunk_overlap': {'type': 'integer'},
                            'total_pages': {'type': 'integer'},
                            'processing_timestamp': {'type': 'date'},
                            'score': {'type': 'float'},
                        },
                    },
                },
            },
        }

    def get_store(self):
        """Get configured vector store with optimized settings."""
        store = OpenSearchVectorSearch(
            embedding_function=self.embeddings,
            opensearch_url=self.config.opensearch_url,
            index_name=self.config.opensearch_index_name,
            engine='nmslib',
            timeout=300,
            connection_class=RequestsHttpConnection,
            is_aoss=False,
            vector_field='vector_field',
            text_field='text',
            method='hnsw',
            space_type='l2',
            ef_search=512,
            m=48,
            index_mapping=self._get_index_mapping(),
        )

        return store
