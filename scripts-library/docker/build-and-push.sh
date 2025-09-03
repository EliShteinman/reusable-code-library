#!/bin/bash
# scripts-library/docker/build-and-push.sh
# Universal Docker build and push script

# Configuration
DOCKERHUB_USERNAME="${1:-}"
IMAGE_NAME="${2:-}"
IMAGE_TAG="${3:-latest}"

if [ -z "$DOCKERHUB_USERNAME" ] || [ -z "$IMAGE_NAME" ]; then
    echo "Usage: $0 <dockerhub-username> <image-name> [tag]"
    echo "Example: $0 myuser my-app latest"
    exit 1
fi

FULL_IMAGE_NAME="docker.io/${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "🐳 Building and pushing: $FULL_IMAGE_NAME"

# Build multi-platform image and push
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t "$FULL_IMAGE_NAME" \
    --push .

if [ $? -eq 0 ]; then
    echo "✅ Successfully built and pushed: $FULL_IMAGE_NAME"
else
    echo "❌ Build/push failed"
    exit 1
fi