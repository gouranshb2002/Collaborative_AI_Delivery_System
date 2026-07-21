#!/bin/bash
# Builds the Docker image and forces a fresh download of all dependencies

echo "Building Docker image: collab_ai_delivery_img..."
docker build --no-cache -t collab_ai_delivery_img .
echo "Build complete."
