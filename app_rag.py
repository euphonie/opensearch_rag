import gradio as gr
import rag
from dotenv import load_dotenv

# Load environment variables at the start
load_dotenv()

def process_query(question):
    """Process the user query and return results"""
    semantic_results, rag_result = rag.search(question=question)
    
    # Format semantic results for display
    semantic_table = "\nSemantic Search Results:\n"
    for result in semantic_results:
        semantic_table += f"- Score: {result['score']}\n  Text: {result['text']}\n\n"
    
    return rag_result, semantic_table

# Create the Gradio interface
def create_interface():
    with gr.Blocks(title="RAG with OpenSearch and LangChain") as demo:
        gr.Markdown("# RAG with OpenSearch and LangChain")
        
        with gr.Row():
            question_input = gr.Textbox(
                label="Ask a question:",
                placeholder="Enter your question here...",
                lines=2
            )
        
        with gr.Row():
            submit_btn = gr.Button("Submit", variant="primary")
        
        with gr.Row():
            answer_output = gr.Textbox(
                label="Response:",
                lines=10,
                show_copy_button=True
            )
        
        with gr.Accordion("Semantic Search Results", open=False):
            semantic_output = gr.Textbox(
                lines=10,
                show_copy_button=True
            )
        
        # Handle submission
        submit_btn.click(
            fn=process_query,
            inputs=[question_input],
            outputs=[answer_output, semantic_output]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", server_port=8081)