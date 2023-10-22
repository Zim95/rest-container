#!/bin/bash

docker image build -t \
    "$BT_REST_IMAGE_NAME:$BT_REST_IMAGE_TAG" \
    -f Dockerfile .

docker image tag \
    "$BT_REST_IMAGE_NAME:$BT_REST_IMAGE_TAG" \
    "$REPO_NAME/$BT_REST_IMAGE_NAME:$BT_REST_IMAGE_TAG"
