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
    
    if ollama_config['type'] == 'embedding':
        return handle_embedding_request(request, ollama_endpoint, ollama_config)
    else:
        return handle_completion_request(request, ollama_endpoint, ollama_config)

def handle_embedding_request(request: Dict[Any, Any], endpoint: str, config: Dict[str, Any]) -> Dict[Any, Any]:
    """Handle embedding requests using Ollama"""
    input_text = request['inputText']
    
    response = requests.post(
        f"{endpoint}/embeddings",
        json={
            "model": config['model'],
            "prompt": input_text
        }
    )
    
    result = response.json()
    return {
        "embedding": result['embedding'],
        "dimensions": len(result['embedding'])
    }

def handle_completion_request(request: Dict[Any, Any], endpoint: str, config: Dict[str, Any]) -> Dict[Any, Any]:
    """Handle text completion requests using Ollama"""
    prompt = request['prompt']
    
    response = requests.post(
        f"{endpoint}/generate",
        json={
            "model": config['model'],
            "prompt": prompt,
            "stream": False
        }
    )
    
    result = response.json()
    return {
        "completion": result['response'],
        "stop_reason": "stop",
        "stop_sequence": None
    }

if __name__ == '__main__':
    # Register this handler with LocalStack
    from localstack.services.bedrock import BedrockProvider
    BedrockProvider.register_handler(handle_bedrock_request) 