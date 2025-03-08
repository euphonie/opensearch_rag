import os

from dotenv import load_dotenv

import rag
from loader import DocumentProcessor, LoaderConfig, VectorStore
from query_processor import QueryProcessor
from ui.main import create_interface
from utils.logging_config import setup_logger

load_dotenv()
logger = setup_logger(__name__)

if __name__ == '__main__':
    config = LoaderConfig()
    vector_store = VectorStore(config)
    processor = QueryProcessor(rag, config, vector_store)
    document_processor = DocumentProcessor(config, vector_store)
    demo = create_interface(config, processor, document_processor, vector_store)
    logger.info('Starting Gradio server...')
    try:
        APP_HOST = os.getenv('APP_HOST', '127.0.0.1')
        APP_PORT = os.getenv('APP_PORT', 8081)
        demo.launch(
            server_name=APP_HOST,
            server_port=APP_PORT,
            share=False,
            show_error=True,
        )
    except Exception as e:
        logger.error(f'Error starting Gradio server: {e}')
        raise e
