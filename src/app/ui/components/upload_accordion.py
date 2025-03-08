"""Upload to Vector Store accordion component."""

import shutil
from pathlib import Path

import fitz
import gradio as gr
from app.ui.actions import handle_file_upload
from app.utils.logging_config import setup_logger

# Define the images directory relative to the current file
IMAGES_DIR = Path(__file__).parent.parent / 'images'


def ensure_images_dir() -> None:
    """Ensure the images directory exists and is empty."""
    if IMAGES_DIR.exists():
        shutil.rmtree(IMAGES_DIR)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)


# Set up logger for this module
logger = setup_logger(__name__)


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


def create_upload_accordion(
    document_processor,
) -> tuple[gr.Accordion, gr.Button, gr.Textbox]:
    """
    Create the upload accordion component.

    Args:
        document_processor: Document processor instance

    Returns:
        Tuple of (accordion component, upload button, upload status textbox)
    """

    async def handle_file_upload_wrapper(files):
        """Wrapper to handle the async generator"""
        return await handle_file_upload(files, document_processor)

    with gr.Accordion('Upload to Vector Store', open=False) as accordion:
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

        # Set up event handlers
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

    return accordion, upload_button, upload_status
