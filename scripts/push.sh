#!/bin/bash

# Log in to Docker Hub (You'll be prompted to enter your Docker Hub credentials)
docker login -u "$REPO_NAME"

# Optionally, if you've tagged the image with the repository name in the build script
IMAGE_NAME="$REPO_NAME/$BT_REST_IMAGE_NAME"

# Push the Docker image to the repository
docker push "$IMAGE_NAME:$BT_REST_IMAGE_TAG"
