# Amazon OpenSearch and LangChain demos

## Before you start

- Make sure you have Python installed
- Clone this repo

## Setup Amazon OpenSearch

Create an Amazon OpenSearch Serverless collection (type **Vector search** and choose **Easy create** option) - [documentation](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-manage.html). 

![](images/collection.png)

Create an index with below configuration:

![](images/index.png)

## Load data into OpenSearch

Choose a PDF file and place it in the `files` folder.

Create a `.env` file and provide the following configuration:

```bash
# OpenSearch Configuration
opensearch_index_name='<enter name>'
opensearch_url='<enter URL>'
engine='faiss'
vector_field='vector_field'
text_field='text'
metadata_field='metadata'

# Embedder Configuration
EMBEDDER_TYPE=bedrock  # Use 'bedrock' for AWS Bedrock or 'ollama' for local Ollama

# AWS Configuration (for Bedrock)
AWS_DEFAULT_REGION=us-east-1
AWS_ENDPOINT_URL=http://localhost:4566  # For LocalStack

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434  # For local Ollama
```

### Using AWS Bedrock (Default)

Make sure you have [configured Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/setting-up.html) for access from your local machine. Also, you need access to `amazon.titan-embed-text-v1` embedding model and `anthropic.claude-v2` model in Amazon Bedrock - [follow these instructions](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) for details.

### Using Local Ollama

If using Ollama, ensure you have the required models installed:

```bash
ollama pull nomic-embed-text
```

### Loading the Data

```bash
python3 -m venv myenv
source myenv/bin/activate
pip3 install -r requirements.txt

python3 load.py
```

> Verify data in OpenSearch collection

## Run RAG application

```bash
python3 app_rag.py
```

The application will be available at http://localhost:8081

You can ask questions about your loaded documents.
