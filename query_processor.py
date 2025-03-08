# query_processor.py

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class QueryProcessor:
    def __init__(self, rag_system, config, vector_store):
        """
        Initialize QueryProcessor with a RAG system.

        Args:
            rag_system: The RAG system instance used for searching
            vector_store: The vector store instance used for semantic search
        """
        self.rag = rag_system
        self.vector_store = vector_store
        self.config = config

    def process_query(self, question):
        """
        Process the user query and return formatted results.

        Args:
            question (str): The user's question

        Returns:
            tuple: (answer, semantic_table) where answer is the processed RAG result
                  and semantic_table is the formatted semantic search results
        """
        semantic_results, rag_result = self.rag.search(
            question=question,
            config=self.config,
            vector_store=self.vector_store,
        )

        semantic_table = self._format_semantic_results(semantic_results)
        answer = self._process_rag_result(rag_result)

        history = [
            {
                'role': 'user',
                'content': question,
            },
            {
                'role': 'assistant',
                'content': answer,
            },
        ]

        return history, semantic_table

    def _format_semantic_results(self, semantic_results):
        """
        Format semantic search results into a readable table.

        Args:
            semantic_results (list): List of semantic search results

        Returns:
            str: Formatted semantic results table
        """
        semantic_table = ''
        processed_results = []
        for result in semantic_results:
            if result.page_content not in processed_results:
                processed_results.append(result.page_content)
                semantic_table += f"- Score: {result.metadata.get('score', 'N/A')} <br>  Page: {result.metadata.get('page', 'N/A')} <br>  Text: {result.page_content} <br> <br>"
        return semantic_table

    def _process_rag_result(self, rag_result):
        """
        Process RAG result into a consistent format.

        Args:
            rag_result: The RAG system's response (can be dict, str, or other)

        Returns:
            str: Processed answer
        """
        # Log the response format for debugging
        logger.info(f'Model response type: {type(rag_result)}')

        if isinstance(rag_result, dict):
            # Standard LangChain output format (e.g., from Claude)
            answer = rag_result.get(
                'result',
                rag_result.get('response', str(rag_result)),
            )
        elif isinstance(rag_result, str):
            # Direct string output (e.g., from phi3.5)
            answer = rag_result
        else:
            # Fallback for unexpected formats
            answer = str(rag_result)

        logger.info(f'Processed answer: {answer[:100]}...')  # Print first 100 chars
        return answer
