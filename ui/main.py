import gradio as gr
from .actions import handle_file_upload, clear_chat
import asyncio
from typing import List

def preview_pdf(file: gr.File) -> List[gr.Image]:
    """
    Generate preview images for PDF pages.

    Args:
        file: Uploaded PDF file

    Returns:
        List of page images
    """
    if not file:
        return []
    
    try:
        doc = fitz.open(file.name)
        images = []
        
        for page in doc:
            # Convert page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            img_path = f"/tmp/page_{page.number}.png"
            pix.save(img_path)
            images.append(img_path)
            
        return images
    except Exception as e:
        print(f"Error generating PDF preview: {e}")
        return []

# Create the Gradio interface
def create_interface(config, processor, document_processor):
    async def handle_file_upload_wrapper(files):
        """Wrapper to handle the async generator"""
        async for status in handle_file_upload(files, document_processor):
            yield status

    with gr.Blocks(title="RAG with OpenSearch and LangChain") as demo:
        gr.Markdown(
            """
            # RAG with OpenSearch and LangChain
            Upload PDF documents and ask questions about their content.
            """
        )
        
        with gr.Sidebar():
            # File upload section
            file_upload = gr.File(
                label="Upload PDF Documents",
                file_types=[".pdf"],
                file_count="multiple",
                type="filepath"
            )
            upload_button = gr.Button("Process Files", variant="primary")
            upload_status = gr.Textbox(label="Upload Status", interactive=False)
            
            # Configuration info
            gr.Markdown(
                f"""
                ### Current Configuration:
                - Embedder: {config.embedder_type}
                - LLM: {config.llm_type}
                - Model: {config.llm_model}
                """
            )
        
        with gr.Row():
            with gr.Column(scale=2):
                # Chat interface
                chatbot = gr.Chatbot(
                    label="Chat History",
                    height=400,
                    show_copy_button=True,
                    type="messages"
                )
                question_input = gr.Textbox(
                    label="Ask a question:",
                    placeholder="Enter your question here...",
                    lines=2
                )
                
                with gr.Row():
                    submit_btn = gr.Button("Submit", variant="primary")
                    clear_btn = gr.Button("Clear Chat", variant="secondary")
            
            with gr.Column(scale=1):
                # Semantic search results
                semantic_output = gr.Textbox(
                    label="Semantic Search Results",
                    lines=15,
                    show_copy_button=True
                )
        
        # Handle file upload
        upload_button.click(
            fn=handle_file_upload_wrapper,
            inputs=[file_upload],
            outputs=[upload_status],
            show_progress=True,
            queue=True  # Enable queuing for async functions
        ).then(
            lambda: None,  # Reset function
            None,  # No inputs
            [file_upload]  # Reset file upload component
        )
        
        # Handle chat
        submit_btn.click(
            fn=processor.process_query,
            inputs=[question_input],
            outputs=[chatbot, semantic_output]
        )
        
        # Handle clear
        clear_btn.click(
            fn=clear_chat,
            inputs=[],
            outputs=[chatbot, question_input, semantic_output]
        )
    
    return demo
