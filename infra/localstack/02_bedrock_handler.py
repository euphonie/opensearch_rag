#!/usr/bin/env python
import json
import requests
from typing import Dict, Any

def handle_bedrock_request(request: Dict[Any, Any], model_config: Dict[str, Any]) -> Dict[Any, Any]:
    """
    Handle Bedrock API requests by proxying them to Ollama
    """
    ollama_endpoint = f"{model_config['endpoint']}"
    ollama_config = model_config['ollama_config']
    
    # Extract the request body
    if isinstance(request, str):
        request = json.loads(request)
    elif isinstance(request, bytes):
        request = json.loads(request.decode('utf-8'))
    
    # Get the operation from the request
    operation = request.get('operation', 'InvokeModel')
    
    if ollama_config['type'] == 'embedding':
        return handle_embedding_request(request, ollama_endpoint, ollama_config)
    else:
        return handle_completion_request(request, ollama_endpoint, ollama_config)

def handle_embedding_request(request: Dict[Any, Any], endpoint: str, config: Dict[str, Any]) -> Dict[Any, Any]:
    """Handle embedding requests using Ollama"""
    # Handle both Bedrock and direct input formats
    input_text = (
        request.get('inputText') or 
        request.get('text') or 
        request.get('input') or
        request.get('body', {}).get('inputText')
    )
    
    if not input_text:
        raise ValueError("No input text found in request")
    
    try:
        response = requests.post(
            f"{endpoint}/embeddings",
            json={
                "model": config['model'],
                "prompt": input_text
            }
        )
        response.raise_for_status()
        result = response.json()
        
        # Return in Bedrock format
        return {
            "embedding": result['embedding'],
            "dimensions": len(result['embedding']),
            "mediaType": "application/json"
        }
    except Exception as e:
        print(f"Error in embedding request: {str(e)}")
        raise

def handle_completion_request(request: Dict[Any, Any], endpoint: str, config: Dict[str, Any]) -> Dict[Any, Any]:
    """Handle text completion requests using Ollama"""
    # Handle both Bedrock and direct input formats
    prompt = (
        request.get('prompt') or 
        request.get('text') or 
        request.get('input') or
        request.get('body', {}).get('prompt')
    )
    
    if not prompt:
        raise ValueError("No prompt found in request")
    
    try:
        response = requests.post(
            f"{endpoint}/generate",
            json={
                "model": config['model'],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
        )
        response.raise_for_status()
        result = response.json()
        
        # Return in Bedrock format
        return {
            "completion": result['response'],
            "stop_reason": "stop",
            "stop_sequence": None,
            "mediaType": "application/json"
        }
    except Exception as e:
        print(f"Error in completion request: {str(e)}")
        raise

def init():
    """Initialize the handler with LocalStack"""
    try:
        from localstack.services.bedrock import BedrockProvider
        BedrockProvider.register_handler(handle_bedrock_request)
        print("Successfully registered Bedrock handler")
    except Exception as e:
        print(f"Error registering handler: {str(e)}")

if __name__ == '__main__':
    init() 