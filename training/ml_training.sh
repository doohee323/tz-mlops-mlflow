#!/bin/bash

# Build script for ML training Docker image
# This script builds from the project root to ensure all paths are correct

set -e

echo "Building ML training Docker image..."

# Change to project root directory
cd "$(dirname "$0")/.."

# Build the Docker image
docker build -f training/docker/Dockerfile -t doohee323/ml_training:latest .

echo "Build completed successfully!"

# Optionally push the image
if [ "$1" = "--push" ]; then
    echo "Pushing image to registry..."
    docker push doohee323/ml_training:latest
    echo "Push completed successfully!"
fi 