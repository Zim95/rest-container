#!/bin/bash

REPO_NAME="zim95"
BT_REST_IMAGE_NAME="browseterm-rest"
BT_REST_IMAGE_TAG="latest"

docker image build -t \
    "$BT_REST_IMAGE_NAME:$BT_REST_IMAGE_TAG" \
    -f Dockerfile .

docker image tag \
    "$BT_REST_IMAGE_NAME:$BT_REST_IMAGE_TAG" \
    "$REPO_NAME/$BT_REST_IMAGE_NAME:$BT_REST_IMAGE_TAG"
