#!/bin/bash
set -e

# Function to load environment variables from Docker secrets
load_secrets() {
    # Check if we have a mounted secrets directory
    if [ -d "/app/secrets" ]; then
        export $(cat /app/secrets/.env | grep -v '^#' | sed 's/=$//' | sed 's/\r$//' | xargs)
    fi
}

# Function to create .env file from secrets
create_env_file() {
    # Create .env file if it doesn't exist
    touch "$ENV_FILE"

    # If we have a mounted .env file, don't overwrite it
    if [ -s "$ENV_FILE" ]; then
        echo "Using mounted .env file"
        return
    fi

    # Otherwise, create from secrets
    echo "Creating .env file from secrets"
    for secret in /app/secrets/; do
        if [ -f "$secret" ]; then
            secret_name=$(basename "$secret")
            echo "$secret_name=$(cat $secret)" >> "$ENV_FILE"
        fi
    done
}


# Create or update .env file
create_env_file

# Load secrets into environment
load_secrets

# Execute the main command
exec python -m "$@"
