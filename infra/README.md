# Infrastructure Setup

This folder contains the infrastructure configuration for running the RAG application with LocalStack and Ollama.

## Components

- LocalStack container running AWS Bedrock emulator
- Ollama container running local LLMs
- Python application container running the RAG application

## Prerequisites

Before starting the infrastructure, make sure you have the required models installed locally:

```bash
ollama pull llama2
ollama pull nomic-embed-text
```

The setup will use your local Ollama models from ~/.ollama.

## Usage

1. Start the infrastructure:
```bash
docker-compose up -d
```

2. The application will be available at:
   - RAG Application: http://localhost:8081

3. Service endpoints:
   - LocalStack Bedrock: http://localhost:4566
   - Ollama API: http://localhost:11434

## Environment Variables

The following environment variables are automatically configured:
- AWS_ENDPOINT_URL=http://localstack:4566
- AWS_DEFAULT_REGION=us-east-1
- AWS_ACCESS_KEY_ID=test
- AWS_SECRET_ACCESS_KEY=test
- OLLAMA_HOST=http://ollama:11434

## Notes

- LocalStack is configured to proxy Bedrock requests to local Ollama models:
  - amazon.titan-embed-text-v1 → nomic-embed-text
  - anthropic.claude-v2 → llama2
- The application container mounts the local directory, allowing for real-time code changes
- Ollama uses your local models from ~/.ollama

## Model Information

The setup uses the following Ollama models:
- nomic-embed-text: For text embeddings (replacing Titan)
- llama2: For text generation (replacing Claude)

Make sure these models are installed locally using `ollama pull` before starting the infrastructure. 