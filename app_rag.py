from __future__ import annotations

from typing import List
import gradio as gr
import rag
import load
from pathlib import Path
import shutil
from dotenv import load_dotenv
import os
import traceback
import fitz  # PyMuPDF for PDF rendering
from query_processor import QueryProcessor

# Load environment variables at the start
load_dotenv()

from loader.document_loader import DocumentLoader
from loader.vector_store import get_vector_store
from loader.config import LoaderConfig
from loader.embeddings import EmbeddingsManager


processor = QueryProcessor(rag)

def handle_file_upload(files):
    """Handle uploaded PDF files"""
    try:
        # Create files directory if it doesn't exist
        files_dir = Path("files")
        files_dir.mkdir(exist_ok=True)
        
        # Clear existing files
        for existing_file in files_dir.glob("*.pdf"):
            existing_file.unlink()
        
        # Save uploaded files
        for file in files:
            # Copy file to files directory
            dest_path = files_dir / Path(file.name).name
            shutil.copy2(file.name, dest_path)
        
            # Process the files
            load.load_documents(Path(f"{file.name}"))
        
        return f"Successfully processed {len(files)} files"
    except Exception as e:
        traceback.print_exc()
        return f"Error processing files: {str(e)}"

def process_query(question):
    """Process the user query and return results"""
    return processor.process_query(question)

def clear_chat():
    """Clear the chat history"""
    return None, None, None

def process_files(files: List[str]) -> str:
    """Process uploaded files and store in vector database."""
    try:
        config = LoaderConfig()
        loader = DocumentLoader(config)
        documents = loader.load_documents(files)
        
        embeddings_manager = EmbeddingsManager()
        vector_store = get_vector_store(embeddings_manager)
        vector_store.add_documents(documents)
        
        return f"Successfully processed {len(files)} files"
    except Exception as e:
        traceback.print_exc()
        return f"Error processing files: {str(e)}"

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
def create_interface():
    with gr.Blocks(title="RAG with OpenSearch and LangChain") as demo:
        gr.Markdown(
            """
            # RAG with OpenSearch and LangChain
            Upload PDF documents and ask questions about their content.
            """
        )
        
        with gr.Row():
            with gr.Column(scale=2):
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
                    - Embedder: {os.getenv('EMBEDDER_TYPE', 'bedrock')}
                    - LLM: {os.getenv('LLM_TYPE', 'bedrock')}
                    - Model: {os.getenv('OLLAMA_LLM_MODEL') if os.getenv('LLM_TYPE') == 'ollama' else os.getenv('BEDROCK_LLM_MODEL_ID')}
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
            fn=handle_file_upload,
            inputs=[file_upload],
            outputs=[upload_status]
        )
        
        # Handle chat
        submit_btn.click(
            fn=process_query,
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

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=8081,
        share=False,
        show_error=True
    )