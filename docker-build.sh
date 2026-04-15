#!/bin/bash
# Docker build and push script

set -e

echo "======================================"
echo "Docker Build & Push"
echo "======================================"

# Configuration
DOCKER_HUB_USERNAME=${DOCKER_HUB_USERNAME:-"swarajwadkar"}
REPO_NAME="ml-api"
IMAGE_NAME="${DOCKER_HUB_USERNAME}/${REPO_NAME}"
BUILD_TAG=$(date +%Y%m%d%H%M%S)
LATEST_TAG="latest"

echo "Building Docker image..."
echo "Image: ${IMAGE_NAME}:${BUILD_TAG}"

# Build image
docker build -t ${IMAGE_NAME}:${BUILD_TAG} .
docker tag ${IMAGE_NAME}:${BUILD_TAG} ${IMAGE_NAME}:${LATEST_TAG}

echo ""
echo "✓ Docker image built successfully"
echo ""
echo "Images created:"
docker images ${IMAGE_NAME}

echo ""
echo "To push to Docker Hub, run:"
echo "  docker push ${IMAGE_NAME}:${BUILD_TAG}"
echo "  docker push ${IMAGE_NAME}:${LATEST_TAG}"

echo ""
echo "To run locally:"
echo "  docker run -p 8000:8000 ${IMAGE_NAME}:${LATEST_TAG}"
