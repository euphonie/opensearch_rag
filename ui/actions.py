from typing import Any

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
            await document_processor.process_document(file)

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
