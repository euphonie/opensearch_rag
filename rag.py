from langchain.chains import RetrievalQA
from langchain_community.llms import Bedrock, Ollama

from loader.config import LoaderConfig
from loader.vector_store import VectorStore
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def get_llm(config: LoaderConfig, llm_type: str = None) -> Bedrock | Ollama:
    """
    Get the LLM based on configuration
    Args:
        llm_type: Optional override for LLM type
    Returns:
        LLM instance
    """
    # Use environment variable if not explicitly specified
    llm_type = config.llm_type

    if llm_type.lower() == 'bedrock':
        return Bedrock(
            credentials_profile_name='default',
            region_name=config.region_name,
            endpoint_url=config.endpoint_url,
            model_id=config.model_id,
            model_kwargs={'temperature': 0.7, 'max_tokens_to_sample': 4096},
        )
    elif llm_type.lower() == 'ollama':
        return Ollama(
            base_url=config.base_url,
            model=config.model,
            temperature=0.7,
        )
    else:
        raise ValueError(f'Unsupported LLM type: {llm_type}')


def search(question: str, config: LoaderConfig, vector_store: VectorStore):
    """
    Perform semantic search and RAG
    Args:
        question: Query string
        vector_store: Vector store instance
    Returns:
        Tuple of (semantic_results, rag_result)
    """
    try:
        llm_type = config.llm_type
        # Get vector store with specified embedder
        store = vector_store.get_store()

        # Get LLM
        llm = get_llm(config, llm_type)

        # Create retriever
        retriever = store.as_retriever(
            search_type='similarity',
            search_kwargs={'k': 3},
        )

        # Create RAG chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type='stuff',
            retriever=retriever,
            return_source_documents=True,
        )

        # Get semantic search results
        semantic_results = retriever.get_relevant_documents(question)

        # Get RAG result
        rag_result = qa_chain({'query': question})

        return semantic_results, rag_result

    except Exception as e:
        logger.error(f'Error in search: {str(e)}')
        raise


if __name__ == '__main__':
    # Test the search functionality
    try:
        question = 'What is the main topic of the document?'
        semantic_results, rag_result = search(question)

        logger.info('\nTest Search Results:')
        logger.info(f'Query: {question}')
        logger.info('\nSemantic Search Results:')
        for i, doc in enumerate(semantic_results, 1):
            logger.info(f'\n{i}. {doc.page_content[:200]}...')

        logger.info('\nRAG Response:')
        logger.info(rag_result['result'])

    except Exception as e:
        logger.error(f'Error in test: {str(e)}')
