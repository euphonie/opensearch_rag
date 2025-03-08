import tempfile
from pathlib import Path

import fitz
import gradio as gr

from utils.logging_config import setup_logger

from .actions import clear_chat, handle_file_upload

# Set up logger for this module
logger = setup_logger(__name__)


def preview_pdf(file: gr.File) -> list[gr.Image]:
    """
    Generate preview images for PDF pages.

    Args:
        file: Uploaded PDF file

    Returns:
        List of page images
    """
    if not file:
        logger.debug('No file provided for preview')
        return []

    try:
        doc = fitz.open(file.name)
        images = []
        logger.info(f'Generating preview for PDF with {doc.page_count} pages')

        # Create a secure temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            for page in doc:
                # Convert page to image
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                )  # 2x zoom for better quality
                # Create secure temporary file path
                temp_path = Path(temp_dir) / f'page_{page.number}.png'
                pix.save(str(temp_path))
                images.append(str(temp_path))
                logger.debug(f'Generated preview for page {page.number}')

        return images
    except Exception as e:
        logger.error(f'Error generating PDF preview: {e}', exc_info=True)
        return []


# Create the Gradio interface
def create_interface(config, processor, document_processor):
    logger.info('Initializing Gradio interface')

    async def handle_file_upload_wrapper(files):
        """Wrapper to handle the async generator"""
        logger.info(f'Processing {len(files)} files')
        async for status in handle_file_upload(files, document_processor):
            yield status

    with gr.Blocks(title='RAG with OpenSearch and LangChain') as demo:
        gr.Markdown(
            """
            # RAG with OpenSearch and LangChain
            Upload PDF documents and ask questions about their content.
            """,
        )

        with gr.Sidebar():
            # File upload section
            file_upload = gr.File(
                label='Upload PDF Documents',
                file_types=['.pdf'],
                file_count='multiple',
                type='filepath',
            )
            upload_button = gr.Button('Process Files', variant='primary')
            upload_status = gr.Textbox(label='Upload Status', interactive=False)

            # Configuration info
            logger.debug('Setting up configuration display')
            gr.Markdown(
                f"""
                ### Current Configuration:
                - Embedder: {config.embedder_type}
                - LLM: {config.llm_type}
                - Model: {config.llm_model}
                """,
            )

        with gr.Row():
            with gr.Column(scale=2):
                # Chat interface
                chatbot = gr.Chatbot(
                    label='Chat History',
                    height=400,
                    show_copy_button=True,
                    type='messages',
                )
                question_input = gr.Textbox(
                    label='Ask a question:',
                    placeholder='Enter your question here...',
                    lines=2,
                )

                with gr.Row():
                    submit_btn = gr.Button('Submit', variant='primary')
                    clear_btn = gr.Button('Clear Chat', variant='secondary')

            with gr.Column(scale=1):
                # Semantic search results
                semantic_output = gr.Textbox(
                    label='Semantic Search Results',
                    lines=15,
                    show_copy_button=True,
                )

        # Handle file upload
        upload_button.click(
            fn=handle_file_upload_wrapper,
            inputs=[file_upload],
            outputs=[upload_status],
            show_progress=True,
            queue=True,
        ).then(
            lambda: None,
            None,
            [file_upload],
        )

        # Handle chat
        submit_btn.click(
            fn=processor.process_query,
            inputs=[question_input],
            outputs=[chatbot, semantic_output],
        )

        # Handle clear
        clear_btn.click(
            fn=clear_chat,
            inputs=[],
            outputs=[chatbot, question_input, semantic_output],
        )

    logger.info('Gradio interface initialized successfully')
    return demo
