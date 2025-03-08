"""Documents in Vector Store accordion component."""

import gradio as gr
from utils.logging_config import setup_logger

from ui.actions import show_document_details

# Set up logger for this module
logger = setup_logger(__name__)


def create_documents_accordion(document_processor) -> tuple[gr.Accordion, gr.Dataframe]:
    """
    Create the documents accordion component.

    Args:
        document_processor: Document processor instance

    Returns:
        Tuple of (accordion component, documents list dataframe)
    """

    async def show_document_details_wrapper(evt: gr.SelectData):
        """Wrapper to handle document details display"""
        logger.info('Showing document details')
        return await show_document_details(evt, document_processor)

    with gr.Accordion('Documents in Vector Store', open=False) as accordion:
        # List of documents
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

    return (
        accordion,
        documents_list,
        doc_title,
        doc_details_box,
        doc_metadata,
        doc_stats,
    )
