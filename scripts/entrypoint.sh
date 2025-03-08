#!/bin/bash
set -e

# Function to load environment variables from Docker secrets
load_secrets() {
    # Check if we have a mounted secrets directory
    if [ -d "/run/secrets" ]; then
        # Load each secret into environment variables
        for secret in /run/secrets/*; do
            if [ -f "$secret" ]; then
                # Get the secret name from the filename
                secret_name=$(basename "$secret")
                # Export the secret value to an environment variable
                export "$secret_name"="$(cat $secret)"
            fi
        done
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
    for secret in /run/secrets/*; do
        if [ -f "$secret" ]; then
            secret_name=$(basename "$secret")
            echo "$secret_name=$(cat $secret)" >> "$ENV_FILE"
        fi
    done
}

# Load secrets into environment
load_secrets

# Create or update .env file
create_env_file

# Execute the main command
exec python -m "$@"
