from pathlib import Path

import gradio as gr
from utils.logging_config import setup_logger

from ui.actions import show_document_details, update_documents_list
from ui.components.chat_interface import create_chat_interface
from ui.components.documents_accordion import create_documents_accordion
from ui.components.upload_accordion import create_upload_accordion

# Set up logger for this module
logger = setup_logger(__name__)

# Define the resources directory and CSS file path
CSS_FILE = Path(__file__).parent.parent.parent / 'resources' / 'styles.css'


def load_css() -> str:
    """Load CSS from file."""
    try:
        return CSS_FILE.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f'Error loading CSS file: {e}')
        return ''


# Create the Gradio interface
def create_interface(config, processor, document_processor, vector_store):
    logger.info('Initializing Gradio interface')

    async def update_documents_list_wrapper():
        """Wrapper to handle document list updates"""
        logger.info('Updating documents list')
        return await update_documents_list(document_processor)

    async def show_document_details_wrapper(evt: gr.SelectData):
        """Wrapper to handle document details display"""
        logger.info('Showing document details')
        return await show_document_details(evt, document_processor)

    # Load CSS from file
    css = load_css()

    with gr.Blocks(title='RAG with OpenSearch and LangChain', css=css) as demo:
        gr.Markdown(
            """
            <div class="logo-container">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 18H17V16H7V18Z" fill="currentColor"/>
                <path d="M17 14H7V12H17V14Z" fill="currentColor"/>
                <path d="M7 10H11V8H7V10Z" fill="currentColor"/>
                <path fill-rule="evenodd" clip-rule="evenodd"
                        d="M6 2C4.34315 2 3 3.34315 3 5V19C3 20.6569 4.34315 22 6 22H18C19.6569 22 21 20.6569 21 19V9C21 5.13401 17.866 2 14 2H6ZM6 4H13V9H19V19C19 19.5523 18.5523 20 18 20H6C5.44772 20 5 19.5523 5 19V5C5 4.44772 5.44772 4 6 4ZM15 4.10002C16.6113 4.4271 17.9413 5.52906 18.584 7H15V4.10002Z"
                        fill="currentColor"/>
                </svg>
            </div>
            <div class="content-container">
                <h1>RAG with OpenSearch and LangChain</h1>
                <p>Upload PDF documents and ask questions about their content.</p>
            </div>
            """,
        )
        with gr.Blocks(title='Configuration', css=css):
            gr.Markdown(
                f"""
                <div class="configuration-container">
                    <div class="config-grid">
                        <div class="config-item">
                            <h5>Model</h5>
                            <p>{config.llm_type}</p>
                        </div>
                        <div class="config-item">
                            <h5>Embeddings</h5>
                            <p>{config.embedder_type}</p>
                        </div>
                        <div class="config-item">
                            <h5>Store</h5>
                            <p>OpenSearch</p>
                        </div>
                    </div>
                </div>
                """,
            )

        with gr.Row():
            with gr.Column(scale=2):
                # Create chat interface component
                chatbot, question_input, submit_btn, clear_btn, semantic_output = (
                    create_chat_interface(processor)
                )

            with gr.Column(scale=1):
                # Create upload accordion component
                upload_accordion, upload_button, upload_status = (
                    create_upload_accordion(document_processor)
                )

                # Create documents accordion component
                (
                    docs_accordion,
                    documents_list,
                    doc_title,
                    doc_details_box,
                    doc_metadata,
                    doc_stats,
                ) = create_documents_accordion(document_processor)

        # Show document details when clicked
        documents_list.select(
            fn=show_document_details_wrapper,
            outputs=[
                doc_title,
                doc_title,  # For visibility
                doc_details_box,  # For visibility
                doc_metadata,
                doc_stats,
            ],
        )

        # Initial documents list load
        demo.load(
            fn=update_documents_list_wrapper,
            outputs=[documents_list],
        )

        # Connect upload button success event to documents list update
        upload_button.click(
            fn=lambda: None,  # This is handled by the component
            outputs=None,
        ).success(
            fn=update_documents_list_wrapper,
            outputs=[documents_list],
        )

    logger.info('Gradio interface initialized successfully')
    return demo
