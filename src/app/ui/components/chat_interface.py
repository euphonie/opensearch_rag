"""Chat interface component."""

import gradio as gr
from utils.logging_config import setup_logger

from ui.actions import clear_chat

# Set up logger for this module
logger = setup_logger(__name__)


def create_chat_interface(
    processor,
) -> tuple[gr.Chatbot, gr.Textbox, gr.Button, gr.Button, gr.Markdown]:
    """
    Create the chat interface component.

    Args:
        processor: Query processor instance

    Returns:
        Tuple of (chatbot, question input, submit button, clear button, semantic output)
    """
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

    # Handle chat submission
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

    return chatbot, question_input, submit_btn, clear_btn, semantic_output
