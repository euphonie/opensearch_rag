import shutil
from pathlib import Path
from typing import List, AsyncGenerator
import traceback
import gradio as gr
from loader import DocumentLoader, LoaderConfig, get_vector_store

async def handle_file_upload(files, document_processor) -> AsyncGenerator[str, None]:
    """
    Handle uploaded PDF files.
    
    Args:
        files: List of uploaded files
        document_processor: Document processor instance
    
    Yields:
        Status messages about the processing progress
    """
    try:
        # Create files directory if it doesn't exist
        files_dir = Path("files")
        files_dir.mkdir(exist_ok=True)
        
        # Clear existing files
        for existing_file in files_dir.glob("*.pdf"):
            existing_file.unlink()
        
        total_files = len(files)
        for idx, file in enumerate(files, 1):
            # Copy file to files directory
            dest_path = files_dir / Path(file.name).name
            shutil.copy2(file.name, dest_path)
            
            # Update status before processing
            status = f"Processing file {idx}/{total_files}: {Path(file.name).name}"
            gr.Info(status)
            yield status
            
            # Process the file and get progress updates
            async for progress in document_processor.load_documents(Path(f"{file.name}")):
                if isinstance(progress, float):
                    percentage = f"{progress:.1f}%"
                    status = f"Processing file {idx}/{total_files}: {Path(file.name).name} - {percentage}"
                    yield status
        
        yield f"Successfully processed {total_files} files"
    except Exception as e:
        traceback.print_exc()
        yield f"Error processing files: {str(e)}"

def clear_chat():
    """Clear the chat history"""
    return None, None, None
