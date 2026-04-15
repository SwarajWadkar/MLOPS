#!/bin/bash
# Docker push script

set -e

DOCKER_HUB_USERNAME=${DOCKER_HUB_USERNAME:-"swarajwadkar"}
REPO_NAME="ml-api"
IMAGE_NAME="${DOCKER_HUB_USERNAME}/${REPO_NAME}"
TAG=${1:-"latest"}

echo "======================================"
echo "Docker Push"
echo "======================================"
echo "Pushing ${IMAGE_NAME}:${TAG}"

# Login to Docker Hub
if [ -z "$DOCKER_HUB_PASSWORD" ]; then
    echo "DOCKER_HUB_PASSWORD not set. Please run:"
    echo "  export DOCKER_HUB_USERNAME=your_username"
    echo "  export DOCKER_HUB_PASSWORD=your_password"
    exit 1
fi

echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin

# Push image
docker push ${IMAGE_NAME}:${TAG}

echo "✓ Image pushed successfully"

# Logout
docker logout
