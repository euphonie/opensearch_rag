from ui.main import create_interface
from query_processor import QueryProcessor
from dotenv import load_dotenv
import os
import rag 
from loader import LoaderConfig, DocumentProcessor

load_dotenv()

if __name__ == "__main__":
    processor = QueryProcessor(rag)
    config = LoaderConfig()
    document_processor = DocumentProcessor(config)
    demo = create_interface(config, processor, document_processor)
    print("Starting Gradio server...")
    try:
        APP_HOST = os.getenv("APP_HOST", "0.0.0.0") 
        APP_PORT = os.getenv("APP_PORT", 8081)
        demo.launch(
            server_name=APP_HOST,
            server_port=APP_PORT,
            share=False,
            show_error=True
        )
    except Exception as e:
        print(f"Error starting Gradio server: {e}")
        raise e
