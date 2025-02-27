#!/usr/bin/env python
import boto3
import json
import requests
from botocore.exceptions import ClientError

def check_ollama_models():
    """Check if required models are available in Ollama"""
    ollama_host = "http://ollama:11434"
    required_models = [
        "llama2",  # For text generation (Claude replacement)
        "nomic-embed-text"  # For embeddings (Titan replacement)
    ]
    
    # List available models
    try:
        response = requests.get(f"{ollama_host}/api/tags")
        available_models = [model['name'] for model in response.json()['models']]
        
        for model in required_models:
            if model not in available_models:
                print(f"Warning: Required model '{model}' is not available locally")
                print(f"Please run 'ollama pull {model}' on your local machine first")
            else:
                print(f"Found required model: {model}")
    except Exception as e:
        print(f"Error checking models: {str(e)}")

def create_bedrock_config():
    # Create a boto3 client for bedrock using localstack endpoint
    bedrock = boto3.client(
        'bedrock',
        endpoint_url='http://localhost:4566',
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )

    # Configure mock models that will proxy to Ollama
    models = [
        {
            'modelId': 'amazon.titan-embed-text-v1',
            'provider': 'Amazon',
            'customizationType': 'NONE',
            'ollama': {
                'model': 'nomic-embed-text',
                'type': 'embedding'
            }
        },
        {
            'modelId': 'anthropic.claude-v2',
            'provider': 'Anthropic',
            'customizationType': 'NONE',
            'ollama': {
                'model': 'llama2',
                'type': 'completion'
            }
        }
    ]

    # First check if required Ollama models are available
    check_ollama_models()

    # Register models with LocalStack
    for model in models:
        try:
            # Create a custom response handler for this model
            handler = {
                'ollama_config': model.pop('ollama'),
                'endpoint': 'http://ollama:11434/api'
            }
            
            # Register the model with the handler configuration
            bedrock.create_custom_model(
                modelId=model['modelId'],
                customizationType='API_GATEWAY',
                handlerConfiguration=json.dumps(handler)
            )
            print(f"Created model: {model['modelId']}")
        except Exception as e:
            print(f"Error creating model {model['modelId']}: {str(e)}")

if __name__ == '__main__':
    create_bedrock_config() 