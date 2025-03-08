import os

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.embeddings import BedrockEmbeddings, OllamaEmbeddings
from langchain_community.llms import Bedrock, Ollama

from loader.vector_store import get_vector_store
from utils.logging_config import setup_logger

# Load environment variables
load_dotenv()

logger = setup_logger(__name__)


def get_embedder(embedder_type: str = None) -> BedrockEmbeddings | OllamaEmbeddings:
    """
    Get the embedder based on configuration
    Args:
        embedder_type: Optional override for embedder type
    Returns:
        Embeddings instance
    """
    # Use environment variable if not explicitly specified
    embedder_type = embedder_type or os.getenv('EMBEDDER_TYPE', 'bedrock')

    if embedder_type.lower() == 'bedrock':
        return BedrockEmbeddings(
            credentials_profile_name='default',
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
            endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
            model_id=os.getenv('BEDROCK_MODEL_ID', 'amazon.titan-embed-text-v1'),
        )
    elif embedder_type.lower() == 'ollama':
        return OllamaEmbeddings(
            base_url=os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            model=os.getenv('OLLAMA_MODEL', 'mxbai-embed-large'),
        )
    else:
        raise ValueError(f'Unsupported embedder type: {embedder_type}')


def get_llm(llm_type: str = None) -> Bedrock | Ollama:
    """
    Get the LLM based on configuration
    Args:
        llm_type: Optional override for LLM type
    Returns:
        LLM instance
    """
    # Use environment variable if not explicitly specified
    llm_type = llm_type or os.getenv('LLM_TYPE', 'bedrock')

    if llm_type.lower() == 'bedrock':
        return Bedrock(
            credentials_profile_name='default',
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
            endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
            model_id=os.getenv('BEDROCK_LLM_MODEL_ID', 'anthropic.claude-v2'),
            model_kwargs={'temperature': 0.7, 'max_tokens_to_sample': 4096},
        )
    elif llm_type.lower() == 'ollama':
        return Ollama(
            base_url=os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            model=os.getenv('OLLAMA_LLM_MODEL', 'llama2'),
            temperature=0.7,
        )
    else:
        raise ValueError(f'Unsupported LLM type: {llm_type}')


def search(question: str):
    """
    Perform semantic search and RAG
    Args:
        question: Query string
        embedder_type: Optional override for embedder type
        llm_type: Optional override for LLM type
    Returns:
        Tuple of (semantic_results, rag_result)
    """
    try:
        embedder_type = os.getenv('EMBEDDER_TYPE', 'bedrock')
        llm_type = os.getenv('LLM_TYPE', 'bedrock')
        # Get vector store with specified embedder
        vector_store = get_vector_store(embedder_type)

        # Get LLM
        llm = get_llm(llm_type)

        # Create retriever
        retriever = vector_store.as_retriever(
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
