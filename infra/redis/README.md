# Redis Configuration

This directory contains configuration files for the Redis cache used in the LangChain OpenSearch RAG application.

## Overview

Redis is used as a caching layer to improve performance by:
- Caching embeddings to avoid regeneration
- Storing frequently accessed document chunks
- Caching query results
- Managing session data

## Configuration Files

### redis.conf

The main Redis configuration file with optimized settings for the RAG application:

```
# Memory settings
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence settings
save 900 1
save 300 10
save 60 10000

# Performance settings
tcp-keepalive 300
timeout 0
tcp-backlog 511

# Security settings
protected-mode yes
```

Key configuration options:

- **maxmemory**: Maximum memory Redis can use (512MB)
- **maxmemory-policy**: Eviction policy when memory limit is reached (LRU)
- **save**: Persistence configuration (RDB snapshots)
- **tcp-keepalive**: Keep connections alive
- **timeout**: Connection timeout (0 = disabled)

## Docker Configuration

In the Docker Compose file, Redis is configured with:

```yaml
redis:
  image: redis:7.2-alpine
  command: redis-server /usr/local/etc/redis/redis.conf
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
    - ./redis/redis.conf:/usr/local/etc/redis/redis.conf
  environment:
    - REDIS_MAXMEMORY=512mb
    - REDIS_MAXMEMORY_POLICY=allkeys-lru
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 5s
    timeout: 3s
    retries: 3
  networks:
    opensearch-network:
      aliases:
        - redis
  restart: unless-stopped
```

Key features:
- Alpine-based image for smaller footprint
- Custom configuration file mounted from host
- Persistent volume for data
- Health check for container orchestration
- Network configuration for service discovery

## Usage in the Application

Redis is used in the application for:

### Embedding Cache

```python
class CachedEmbeddings:
    """Cache embeddings in Redis."""

    def __init__(self, config, redis_client):
        self.config = config
        self.redis = redis_client
        self.embedder = OllamaEmbeddings(config)

    async def embed_query(self, text):
        # Generate cache key
        cache_key = f"embed:{hashlib.md5(text.encode()).hexdigest()}"

        # Check cache
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Generate embedding
        embedding = await self.embedder.embed_query(text)

        # Cache result
        await self.redis.set(
            cache_key,
            json.dumps(embedding),
            ex=86400  # 24 hour expiry
        )

        return embedding
```

### Memory Settings

The default memory limit is 512MB, which is suitable for most deployments. For larger deployments, consider increasing this value:

```
maxmemory 1gb
```

### Eviction Policies

The default eviction policy is `allkeys-lru` (Least Recently Used), which is appropriate for caching. Other options include:

- **allkeys-random**: Random eviction
- **volatile-lru**: Evict keys with expiry set using LRU
- **volatile-ttl**: Evict keys with shortest TTL first
- **noeviction**: Return errors when memory limit is reached

### Persistence

By default, Redis is configured with RDB persistence. For more durability, consider enabling AOF:

```
appendonly yes
appendfsync everysec
```

## Monitoring

To monitor Redis performance:

```bash
# Connect to Redis CLI
docker-compose -f infra/docker-compose.yml exec redis redis-cli

# Check memory usage
INFO memory

# Check hit rate
INFO stats

# Monitor commands in real-time
MONITOR
```

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Check if Redis is running: `docker-compose -f infra/docker-compose.yml ps redis`
   - Verify network configuration: `docker network inspect infra_opensearch-network`

2. **Memory Limit Reached**:
   - Check memory usage: `docker-compose -f infra/docker-compose.yml exec redis redis-cli INFO memory`
   - Increase maxmemory in redis.conf

3. **Slow Performance**:
   - Check for slow commands: `docker-compose -f infra/docker-compose.yml exec redis redis-cli SLOWLOG GET 10`
   - Consider enabling pipelining in the application

### Debugging Commands

```bash
# Check Redis logs
docker-compose -f infra/docker-compose.yml logs redis

# Check Redis configuration
docker-compose -f infra/docker-compose.yml exec redis redis-cli CONFIG GET '*'

# Test Redis connectivity from app container
docker-compose -f infra/docker-compose.yml exec app redis-cli -h redis ping
```

## Security Considerations

The default configuration assumes Redis is only accessible within the Docker network. For production deployments, consider:

1. **Password Authentication**:
   ```
   requirepass your_strong_password
   ```

2. **Network Security**:
   - Bind to specific interfaces
   - Use TLS for encryption

3. **Command Restrictions**:
   - Disable dangerous commands
   - Use Redis ACLs for fine-grained access control
