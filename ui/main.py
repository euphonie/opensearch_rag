import shutil
from pathlib import Path

import fitz
import gradio as gr

from utils.logging_config import setup_logger

from .actions import clear_chat, handle_file_upload

# Set up logger for this module
logger = setup_logger(__name__)

# Define the images directory relative to the current file
IMAGES_DIR = Path(__file__).parent.parent / 'images'


def ensure_images_dir() -> None:
    """Ensure the images directory exists and is empty."""
    if IMAGES_DIR.exists():
        shutil.rmtree(IMAGES_DIR)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)


async def preview_pdf(files: list[gr.File]) -> list[gr.Image]:
    """
    Generate preview images for PDF pages.

    Args:
        files: List of uploaded PDF files

    Returns:
        List of page images
    """
    if not files:
        logger.debug('No files provided for preview')
        return []

    # Ensure clean images directory
    ensure_images_dir()

    images = []
    try:
        for file_idx, file in enumerate(files):
            doc = fitz.open(file.name)
            logger.info(
                f'Generating preview for PDF {file_idx + 1} with {doc.page_count} pages',
            )

            for page in doc:
                # Convert page to image
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                )  # 2x zoom for better quality
                # Create preview image path
                image_path = IMAGES_DIR / f'doc_{file_idx}_page_{page.number}.png'
                pix.save(str(image_path))
                images.append(str(image_path))
                logger.debug(
                    f'Generated preview for document {file_idx + 1}, page {page.number}',
                )

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

            # PDF Preview Gallery
            preview_gallery = gr.Gallery(
                label='PDF Previews',
                show_label=True,
                columns=[2],
                rows=[2],
                height='auto',
                allow_preview=True,
            )

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

        # Handle file upload and preview
        file_upload.change(
            fn=preview_pdf,
            inputs=[file_upload],
            outputs=[preview_gallery],
        )

        # Handle file processing
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
