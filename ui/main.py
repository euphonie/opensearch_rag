import shutil
from pathlib import Path

import fitz
import gradio as gr

from utils.logging_config import setup_logger

from .actions import (
    clear_chat,
    handle_file_upload,
    show_document_details,
    update_documents_list,
)

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
def create_interface(config, processor, document_processor, vector_store):
    logger.info('Initializing Gradio interface')

    async def handle_file_upload_wrapper(files):
        """Wrapper to handle the async generator"""
        logger.info(f'Processing {len(files)} files')
        return await handle_file_upload(files, document_processor)

    async def update_documents_list_wrapper():
        """Wrapper to handle document list updates"""
        logger.info('Updating documents list')
        return await update_documents_list(document_processor)

    async def show_document_details_wrapper(evt: gr.SelectData):
        """Wrapper to handle document details display"""
        logger.info('Showing document details')
        return await show_document_details(evt, document_processor)

    css = """
        div.logo-container { display: flex; justify-content: center; padding: 1rem; }
        div.logo-container svg { width: 30px; height: 30px; transition: all 0.3s ease; }
        div.content-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 1rem; }
        div.configuration-container {
            padding: 0.75rem;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            background-color: #f8f9fa;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            margin: 0.5rem 0;
            font-size: 0.9rem;
        }
        div.config-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.5rem;
        }
        div.config-item {
            background: white;
            padding: 0.5rem;
            border-radius: 4px;
            border: 1px solid #eaeaea;
        }
        div.config-item h5 {
            margin: 0;
            color: #666;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        div.config-item p {
            margin: 0;
            color: #2d2d2d;
            font-size: 0.8rem;
            font-weight: 500;
        }
        """

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
                # Chat interface
                chatbot = gr.Chatbot(
                    label='Chat History',
                    height=400,
                    show_copy_button=True,
                    type='messages',
                )

                with gr.Accordion('Semantic Search Results', open=False):
                    semantic_output = gr.Markdown(
                        show_copy_button=True,
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
                with gr.Accordion('Upload to Vector Store', open=False):
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

                # Indexed Documents List
                with gr.Accordion('Documents in Vector Store', open=False):
                    # List of documents, on click send id
                    documents_list = gr.Dataframe(
                        headers=['Document'],
                        row_count=(10, 'fixed'),
                        interactive=False,
                        elem_classes='documents-list',
                    )

                    # Document Details Dialog Components
                    doc_title = gr.Markdown('')
                    doc_details_box = gr.Group()
                    with doc_details_box:
                        doc_metadata = gr.JSON(label='Metadata')
                        doc_stats = gr.DataFrame(
                            headers=['Property', 'Value'],
                            label='Document Statistics',
                        )

        # Add custom CSS for document list and details
        css = (
            css
            + """
        .documents-list { max-height: 200px; overflow-y: auto; margin-bottom: 1rem; }
        .documents-list::-webkit-scrollbar { width: 6px; }
        .documents-list::-webkit-scrollbar-thumb { background: #666; border-radius: 3px; }
        """
        )

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
        ).success(
            fn=update_documents_list_wrapper,
            outputs=[documents_list],
        ).then(
            lambda: None,
            None,
            [file_upload],
        )

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

        # Initial documents list load
        demo.load(
            fn=update_documents_list_wrapper,
            outputs=[documents_list],
        )

    logger.info('Gradio interface initialized successfully')
    return demo
