#!/bin/bash

RC_IMAGE_NAME="rest-container"
RC_IMAGE_TAG="latest"
RC_CONTAINER_NAME="rest-container-container"
RC_CONTAINER_BIND="0.0.0.0:8002:8002"
RC_CONTAINER_DEBUG_BIND="0.0.0.0:8003:8003"
RC_NETWORK="rest-container-network"

docker network create "$RC_NETWORK"

docker container run -d \
    --name "$RC_CONTAINER_NAME" \
    -p "$RC_CONTAINER_BIND" \
    -p "$RC_CONTAINER_DEBUG_BIND" \
    -v ./:/app/ \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --network "$RC_NETWORK" \
    "$RC_IMAGE_NAME:$RC_IMAGE_TAG"
