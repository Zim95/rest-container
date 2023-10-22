#!/bin/bash

BT_REST_IMAGE_NAME="browseterm-rest"
BT_REST_IMAGE_TAG="latest"
BT_REST_CONTAINER_NAME="browseterm-rest-container"
BT_REST_CONTAINER_BIND="0.0.0.0:8002:8002"
BT_REST_NETWORK="browseterm-network"

docker network create "$BT_REST_NETWORK"

docker container run -d \
    --name "$BT_REST_CONTAINER_NAME" \
    -p "$BT_REST_CONTAINER_BIND" \
    -v ./:/app/ \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --network "$BT_REST_NETWORK" \
    "$BT_REST_IMAGE_NAME:$BT_REST_IMAGE_TAG"
