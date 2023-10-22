#!/bin/bash

docker container run -d \
    --name browseterm-rest-container \
    --network browseterm-rest-network \
    -v ./:/app/ \
    -p 0.0.0.0:8002:9000 \
    browseterm-rest:latest

