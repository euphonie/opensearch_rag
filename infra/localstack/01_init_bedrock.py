#!/usr/bin/env python
import boto3
import json
import requests
import time
from botocore.exceptions import ClientError

def check_ollama_models():
    """Check if required models are available in Ollama"""
    ollama_host = "http://ollama:11434"
    required_models = [
        "llama2",  # For text generation (Claude replacement)
        "nomic-embed-text"  # For embeddings (Titan replacement)
    ]
    
    max_retries = 5
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            # Check Ollama health
            health_response = requests.get(f"{ollama_host}/api/health")
            if health_response.status_code == 200:
                # List available models
                response = requests.get(f"{ollama_host}/api/tags")
                available_models = [model['name'] for model in response.json().get('models', [])]
                
                missing_models = []
                for model in required_models:
                    if model not in available_models:
                        print(f"Warning: Required model '{model}' is not available locally")
                        print(f"Please run 'ollama pull {model}' on your local machine first")
                        missing_models.append(model)
                    else:
                        print(f"Found required model: {model}")
                
                if not missing_models:
                    return True
            else:
                print(f"Ollama health check failed: {health_response.status_code}")
        except Exception as e:
            print(f"Error checking models (attempt {attempt + 1}/{max_retries}): {str(e)}")
        
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    return False

def create_bedrock_config():
    """Configure Bedrock models in LocalStack"""
    # Create a boto3 client for bedrock using localstack endpoint
    bedrock = boto3.client(
        'bedrock-runtime',  # Changed to bedrock-runtime for model invocation
        endpoint_url='http://localhost:4566',
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )

    # Configure mock models
    models = [
        {
            'modelId': 'anthropic.claude-v2',
            'provider': 'Anthropic',
            'customizationType': 'API_GATEWAY',
            'ollama': {
                'model': 'llama2',
                'type': 'completion',
                'endpoint': '/v1/completions'
            }
        },
        {
            'modelId': 'amazon.titan-embed-text-v1',
            'provider': 'Amazon',
            'customizationType': 'API_GATEWAY',
            'ollama': {
                'model': 'nomic-embed-text',
                'type': 'embedding',
                'endpoint': '/v1/embeddings'
            }
        }
    ]

    # Register models with LocalStack
    for model in models:
        try:
            # Create a custom response handler for this model
            handler = {
                'ollama_config': model.pop('ollama'),
                'endpoint': 'http://ollama:11434/api',
                'operations': {
                    'InvokeModel': {
                        'method': 'POST',
                        'path': f"/model/{model['modelId']}/invoke"
                    }
                }
            }
            
            try:
                bedrock.delete_custom_model(modelId=model['modelId'])
            except:
                pass
                
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