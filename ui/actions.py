from typing import Any

import gradio as gr

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


async def handle_file_upload(files: list[str], document_processor: Any) -> str:
    """
    Handle file upload and processing.

    Args:
        files: List of file paths
        document_processor: Document processor instance

    Returns:
        Status message
    """
    if not files:
        logger.warning('No files provided for upload')
        return 'No files selected'

    try:
        logger.info(f'Processing {len(files)} files')
        for file in files:
            logger.debug(f'Processing file: {file}')
            # Consume the async generator
            progress = 0
            async for current_progress in document_processor.load_documents(file):
                progress = current_progress
                logger.debug(f'Processing progress: {progress:.2f}%')

        logger.info('File processing completed successfully')
        return 'Files processed successfully'
    except Exception as e:
        logger.error(f'Error processing files: {e}', exc_info=True)
        return f'Error processing files: {str(e)}'


def clear_chat() -> tuple[list, str, str]:
    """
    Clear chat history and inputs.

    Returns:
        tuple of (chat history, question input, semantic output)
    """
    logger.debug('Clearing chat history and inputs')
    return [], '', ''


async def update_documents_list(document_processor: Any):
    """Get list of indexed documents from OpenSearch."""
    try:
        docs = await document_processor.get_indexed_documents()
        return [[doc['title']] for doc in docs]
    except Exception as e:
        logger.error(f'Error fetching indexed documents: {e}', exc_info=True)
        return []


async def show_document_details(evt: gr.SelectData, document_processor: Any):
    """Show document metadata when clicked."""
    try:
        doc_info = await document_processor.get_document_metadata(evt.value)
        if doc_info:
            # Prepare statistics
            stats = [
                ['File Name', doc_info.get('title', 'N/A')],
                ['File Size', f"{doc_info.get('file_size', 0) / 1024:.2f} KB"],
                ['Pages', str(doc_info.get('page_count', 0))],
                ['Indexed Date', doc_info.get('indexed_date', 'N/A')],
                ['Chunks', str(doc_info.get('chunk_count', 0))],
            ]
            return (
                f"### Document Details: {doc_info.get('title', 'Unknown')}",
                True,  # Show title
                True,  # Show details box
                doc_info,
                stats,
            )
        return '### Document Not Found', True, True, {}, []
    except Exception as e:
        logger.error(f'Error fetching document details: {e}', exc_info=True)
        return '### Error Loading Document', True, True, {'error': str(e)}, []
