#!/bin/bash

REPO_NAME="zim95"
RC_IMAGE_NAME="rest-container"
RC_IMAGE_TAG="latest"

docker image build -t \
    "$RC_IMAGE_NAME:$RC_IMAGE_TAG" \
    -f Dockerfile .

docker image tag \
    "$RC_IMAGE_NAME:$RC_IMAGE_TAG" \
    "$REPO_NAME/$RC_IMAGE_NAME:$RC_IMAGE_TAG"
