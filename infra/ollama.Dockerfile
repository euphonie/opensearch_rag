FROM ollama/ollama:latest

# Install curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

if [ "$DOWNLOAD_MODELS" = "true" ]; then
    for model in $MODELS; do
        ollama pull $model
    done
fi
