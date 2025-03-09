# UI Module

This module implements the Gradio web interface for the RAG application, providing document upload, chat functionality, and result display.

## Components

### Gradio App (`gradio_app.py`)

The `GradioApp` class manages the web interface:

```python
class GradioApp:
    """Gradio web interface for RAG application."""

    def __init__(self, config: LoaderConfig, document_processor, retriever, llm):
        self.config = config
        self.document_processor = document_processor
        self.retriever = retriever
        self.llm = llm
        self.interface = self._build_interface()
```

Key features:
- Document upload interface
- Chat interface for queries
- Result display with source attribution
- Processing status indicators
- Error handling and user feedback

### Components (`components.py`)

Contains reusable UI components:

```python
def create_file_upload_component():
    """Create file upload component with supported extensions."""
    return gr.File(
        label="Upload Document",
        file_types=[".pdf", ".txt", ".md", ".py"],
        file_count="multiple"
    )

def create_chat_interface(on_message):
    """Create chat interface component."""
    return gr.ChatInterface(
        fn=on_message,
        title="Document Q&A",
        description="Ask questions about your documents",
        examples=["What is the main topic?", "Summarize the key points"]
    )
```

Key features:
- Modular component design
- Consistent styling
- Input validation
- Responsive layout

### Callbacks (`callbacks.py`)

Handles user interaction events:

```python
class UICallbacks:
    """Callback handlers for UI events."""

    def __init__(self, document_processor, retriever, llm):
        self.document_processor = document_processor
        self.retriever = retriever
        self.llm = llm

    async def on_document_upload(self, files):
        """Handle document upload event."""
        results = []
        for file in files:
            try:
                result = await self.document_processor.process(file.name)
                results.append(f"Processed {file.name}: {result}")
            except Exception as e:
                results.append(f"Error processing {file.name}: {str(e)}")
        return "\n".join(results)

    async def on_chat_message(self, message, history):
        """Handle chat message event."""
        try:
            # Retrieve relevant documents
            results = await self.retriever.retrieve(message)

            # Generate response with LLM
            response = await self.llm.generate(message, results)

            # Format response with sources
            formatted_response = self._format_response(response, results)
            return formatted_response
        except Exception as e:
            return f"Error: {str(e)}"
```

Key features:
- Asynchronous event handling
- Error handling and user feedback
- Progress reporting
- Result formatting

## User Interface

The application provides two main interfaces:

### Document Upload Interface

![Document Upload Interface](../../../docs/images/upload_interface.png)

Features:
- Drag-and-drop file upload
- Multiple file selection
- Progress indicators
- Processing status updates
- Error reporting

### Chat Interface

![Chat Interface](../../../docs/images/chat_interface.png)

Features:
- Natural language query input
- Conversation history
- Source attribution for answers
- Confidence indicators
- Example questions

## Usage Examples

### Starting the UI

```python
# Initialize components
config = LoaderConfig()
document_processor = DocumentProcessor(config)
retriever = OpenSearchRetriever(config)
llm = OllamaLLM(config)

# Create and launch UI
app = GradioApp(config, document_processor, retriever, llm)
app.launch(server_name="0.0.0.0", server_port=8081)
```

### Customizing the UI

```python
# Custom theme
app = GradioApp(
    config,
    document_processor,
    retriever,
    llm,
    theme="dark",
    title="Custom RAG Application",
    description="Ask questions about your documents"
)

# Custom CSS
app.interface.launch(
    css="""
    .gradio-container {
        background-color: #f0f0f0;
    }
    .chat-message {
        border-radius: 10px;
    }
    """
)
```

## Configuration Options

### UI Settings

Key UI settings that can be configured:

- **Theme**: Light or dark theme
- **Title**: Application title
- **Description**: Application description
- **Examples**: Example questions for the chat interface
- **File Types**: Supported file types for upload

### Gradio Settings

Gradio-specific settings:

- **Server Name**: Host to bind to (default: 0.0.0.0)
- **Server Port**: Port to listen on (default: 8081)
- **Share**: Whether to create a public link (default: False)
- **Auth**: Authentication function (default: None)

## Customization

### Adding New Components

To add new UI components:

1. Define the component in `components.py`:
   ```python
   def create_custom_component():
       return gr.Textbox(
           label="Custom Component",
           placeholder="Enter text here"
       )
   ```

2. Add the component to the interface in `gradio_app.py`:
   ```python
   def _build_interface(self):
       with gr.Blocks() as interface:
           # Existing components

           # New component
           custom_component = create_custom_component()
           custom_component.change(
               fn=self.callbacks.on_custom_event,
               inputs=[custom_component],
               outputs=[result_component]
           )
   ```

3. Implement the callback in `callbacks.py`:
   ```python
   def on_custom_event(self, value):
       # Handle the event
       return f"Processed: {value}"
   ```

### Styling the UI

Customize the appearance with CSS:

```python
custom_css = """
.container {
    max-width: 1200px;
    margin: 0 auto;
}

.result-box {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 12px;
    background-color: #f9f9f9;
}

.source-reference {
    font-size: 0.8em;
    color: #666;
    margin-top: 8px;
}
"""

app.interface.launch(css=custom_css)
```

### Adding Authentication

Implement user authentication:

```python
def auth_function(username, password):
    # Check credentials
    return username == "admin" and password == "password"

app.interface.launch(auth=auth_function)
```

## Error Handling

The UI implements comprehensive error handling:

- **Input Validation**: Validate user inputs before processing
- **Processing Errors**: Catch and display document processing errors
- **Retrieval Errors**: Handle search failures gracefully
- **LLM Errors**: Provide fallback responses for LLM failures
- **Network Errors**: Detect and report connection issues

## Performance Considerations

Several optimizations are implemented:

- **Asynchronous Processing**: Non-blocking operations for UI responsiveness
- **Progress Reporting**: Keep users informed during long operations
- **Lazy Loading**: Load components only when needed
- **Caching**: Cache frequent operations for better performance

## Accessibility

The UI is designed with accessibility in mind:

- **Keyboard Navigation**: All functions accessible via keyboard
- **Screen Reader Support**: Proper labels and ARIA attributes
- **Color Contrast**: Sufficient contrast for readability
- **Responsive Design**: Works on various screen sizes
