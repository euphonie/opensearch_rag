from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_community.embeddings import BedrockEmbeddings, OllamaEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from opensearchpy import RequestsHttpConnection

load_dotenv()


def get_vector_store(embedder_type: str):
    if embedder_type == 'bedrock':
        embeddings = BedrockEmbeddings(
            model_id=os.getenv('BEDROCK_LLM_MODEL_ID'),
        )
    elif embedder_type == 'ollama':
        embeddings = OllamaEmbeddings(
            model=os.getenv('OLLAMA_LLM_MODEL'),
        )
    else:
        raise ValueError(f'Unsupported embedder type: {embedder_type}')

    opensearch_index_name = os.getenv('opensearch_index_name')
    opensearch_url = (os.getenv('opensearch_url'),)

    # Define dimension based on the embedding model
    # Ollama's default models typically use 3072 dimensions
    embedding_dimension = 3072

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
        embedding_function=embeddings,
        opensearch_url=opensearch_url,
        index_name=opensearch_index_name,
        engine='nmslib',
        timeout=300,
        connection_class=RequestsHttpConnection,
        index_mapping=index_mapping,
    )

    return store
