"""Main application entry point."""

import os

from dotenv import load_dotenv

from app import rag
from app.loader import DocumentProcessor, LoaderConfig, VectorStore
from app.query_processor import QueryProcessor
from app.ui.main import create_interface
from app.utils.logging_config import setup_logger

load_dotenv()
logger = setup_logger(__name__)


def main(host: str | None = None, port: int | None = None) -> None:
    """
    Run the main application.

    Args:
        host: Optional host address
        port: Optional port number
    """
    config = LoaderConfig()
    vector_store = VectorStore(config)
    processor = QueryProcessor(rag, config, vector_store)
    document_processor = DocumentProcessor(config, vector_store)
    demo = create_interface(config, processor, document_processor, vector_store)

    logger.info('Starting Gradio server...')
    try:
        app_host = host or os.getenv('APP_HOST', '127.0.0.1')
        app_port = port or int(os.getenv('APP_PORT', '8081'))
        demo.launch(
            server_name=app_host,
            server_port=app_port,
            share=False,
            show_error=True,
        )
    except Exception as e:
        logger.error(f'Error starting Gradio server: {e}')
        raise


if __name__ == '__main__':
    main()
