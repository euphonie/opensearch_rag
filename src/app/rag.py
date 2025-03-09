from __future__ import annotations

from typing import TYPE_CHECKING

from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.llms import Bedrock, Ollama

if TYPE_CHECKING:
    from app.loader import LoaderConfig, VectorStore

from app.utils.logging_config import setup_logger

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
            base_url=config.ollama_host,
            model=config.llm_model,
            temperature=0.7,
        )
    else:
        raise ValueError(f'Unsupported LLM type: {llm_type}')


def search(question: str, config: LoaderConfig, vector_store: VectorStore):
    """
    Perform enhanced semantic search and RAG with improved retrieval strategies.

    Args:
        question: Query string
        config: Loader configuration
        vector_store: Vector store instance

    Returns:
        Tuple of (semantic_results, rag_result)
    """
    try:
        llm_type = config.llm_type
        store = vector_store.get_store()

        # Clean and prepare the query
        cleaned_question = question.strip()

        # Create multiple retrieval strategies
        hybrid_retriever = store.as_retriever(
            search_type='similarity_score_threshold',
            search_kwargs={
                'k': 5,  # Increased from 3 to get more context
                'score_threshold': 0.5,  # Only return relevant results
                'fetch_k': 20,  # Fetch more candidates for reranking
            },
        )

        # Get semantic search results with multiple strategies
        semantic_results = []

        # Strategy 1: Direct similarity search
        direct_results = hybrid_retriever.get_relevant_documents(cleaned_question)
        semantic_results.extend(direct_results)

        # Strategy 2: MMR search for diversity
        mmr_retriever = store.as_retriever(
            search_type='mmr',
            search_kwargs={
                'k': 3,
                'fetch_k': 10,
                'lambda_mult': 0.7,  # Balance between relevance and diversity
            },
        )
        mmr_results = mmr_retriever.get_relevant_documents(cleaned_question)
        semantic_results.extend(mmr_results)

        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for doc in semantic_results:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique_results.append(doc)

        # Sort results by relevance (if score is available)
        unique_results.sort(
            key=lambda x: float(x.metadata.get('score', 0)),
            reverse=True,
        )

        context = '\n\n'.join([doc.page_content for doc in unique_results[:5]])

        # Define the prompt template
        prompt = PromptTemplate(
            template="""
                Use the following pieces of context to answer the question.
                If you don't know the answer, just say that you don't know, don't try to make up an answer.
                Try to be as detailed as possible while remaining accurate.
                Always consider the full context including any previous or next sections provided.

                Context: {context}

                Question: {question}

                Answer: Let me help you with that.
            """,
            input_variables=['context', 'question'],
        )

        # Get LLM
        llm = get_llm(config, llm_type)

        # Create the chain using the new style
        retrieval_chain = (
            {
                'context': lambda x: context,
                'question': RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        # Get RAG result with enhanced context
        rag_result = retrieval_chain.invoke(cleaned_question)

        # Add metadata about search quality
        search_metadata = {
            'total_results_found': len(semantic_results),
            'unique_results_used': len(unique_results),
            'search_strategies_used': ['similarity', 'mmr'],
            'top_result_score': float(unique_results[0].metadata.get('score', 0))
            if unique_results
            else 0,
        }

        return unique_results, {
            'result': rag_result,
            'search_metadata': search_metadata,
        }

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
