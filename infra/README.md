# Infrastructure Configuration

This directory contains the infrastructure configuration for the LangChain OpenSearch RAG application.

## Components

- **Docker Compose**: Configuration for all services
- **Redis**: Configuration for Redis cache
- **Scripts**: Helper scripts for health checks and maintenance
- **Secrets**: Environment variables and secrets

## Docker Compose Services

### OpenSearch

Vector database for storing document embeddings and metadata.

- **Image**: opensearchproject/opensearch:2.11.1
- **Ports**: 9200 (HTTP), 9600 (Performance Analyzer)
- **Volume**: opensearch-data (persistent storage)
- **Environment Variables**:
  - `DISABLE_SECURITY_PLUGIN=true`: Disables security for development
  - `OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m`: Memory settings

### OpenSearch Dashboards

Web interface for OpenSearch management.

- **Image**: opensearchproject/opensearch-dashboards:2.11.1
- **Port**: 5601
- **Dependencies**: Requires OpenSearch to be healthy

### Ollama

Local LLM inference service.

- **Build**: Custom Dockerfile with curl for health checks
- **Port**: 11434
- **Volume**: Maps local ~/.ollama to container for model sharing
- **Environment Variables**:
  - `DOWNLOAD_MODELS`: Set to false to prevent automatic downloads
  - `MODELS`: Comma-separated list of models to use
- **Resource Limits**: 8GB memory, 4 CPUs

### App

Main application service with Gradio web interface.

- **Build**: Custom Dockerfile from project root
- **Port**: 8081
- **Volumes**:
  - Source code: For live development
  - Logs: For persistent logging
  - Secrets: For environment variables
- **Environment Variables**:
  - `OLLAMA_HOST`: URL for Ollama API
  - `EMBEDDINGS_MODEL`: Model for embeddings
  - `LLM_MODEL`: Model for text generation
  - `OPENSEARCH_URL`: URL for OpenSearch
  - `REDIS_HOST`: Hostname for Redis

### Redis

Caching service for improved performance.

- **Image**: redis:7.2-alpine
- **Port**: 6379
- **Volume**: redis_data (persistent storage)
- **Configuration**: Custom redis.conf file

## Network Configuration

All services are connected to the `opensearch-network` bridge network, allowing them to communicate using service names as hostnames.

## Volumes

- **opensearch-data**: Persistent storage for OpenSearch
- **redis_data**: Persistent storage for Redis

## Configuration

### Redis Configuration

Redis is configured using the `redis/redis.conf` file. Key settings:

- **maxmemory**: 512MB
- **maxmemory-policy**: allkeys-lru (Least Recently Used eviction)

### Environment Variables

Create a `.env` file in the `secrets` directory with any custom environment variables.

## Health Checks

All services include health checks to ensure dependencies are properly managed:

- **OpenSearch**: Checks HTTP endpoint
- **OpenSearch Dashboards**: Checks status endpoint
- **Ollama**: Checks API version endpoint
- **App**: Checks HTTP endpoint
- **Redis**: Uses redis-cli ping

## Troubleshooting

### Common Issues

1. **Service Dependencies**: If services fail to start, check the health of their dependencies
2. **Resource Constraints**: Reduce resource limits if your system has limited memory
3. **Network Issues**: Ensure all services are on the same network
4. **Volume Permissions**: Check permissions if volume mounts fail

### Debugging Commands

```bash
# Check service status
docker-compose -f docker-compose.yml ps

# View service logs
docker-compose -f docker-compose.yml logs -f [service_name]

# Check network connectivity
docker-compose -f docker-compose.yml exec app ping redis
docker-compose -f docker-compose.yml exec app curl -f http://opensearch:9200

# Check Redis connectivity
docker-compose -f docker-compose.yml exec app redis-cli -h redis ping

# Check Ollama API
docker-compose -f docker-compose.yml exec app curl -f http://host.docker.internal:11434/api/version
```

## Customization

### Using Different Models

To use different models with Ollama:

1. Pull the models locally:
   ```bash
   ollama pull your-model-name
   ```

2. Update the `EMBEDDINGS_MODEL` and `LLM_MODEL` environment variables in docker-compose.yml

### Scaling Services

For production deployments, consider:

1. Increasing OpenSearch resources
2. Adding multiple OpenSearch nodes
3. Implementing proper security (disable `DISABLE_SECURITY_PLUGIN`)
4. Using a production-ready Redis configuration
