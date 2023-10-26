# REST Container
A REST API interface to create containers in whichever container environment you are running.
Currently supported:
1. Docker
2. Kubernetes

# Run on Docker
- PreRequisites:
    - Make sure `docker` is installed.
    - Make sure `docker` commands can be used without `sudo`.
- First build the image:
    ```
    make build
    ```
- Deploy the docker container:
    ```
    make dockerrun    
    ```
NOTE: All the commands in Makefile do not work as intended. This is being fixed.

# API Requests
- The API Requests will create/stop/start/delete containers on which ever environment they are run on.
- For example,
    - If the container is run on docker, these APIs will create/start/stop/delete docker containers.
- Here are the requests.
    1. Create container request:
        ```
        curl -XPOST "http://localhost:8002/create" -d '{"image_name": "enter-an-image-name", "container_name": "enter-a-name-here", "container_network": "<optional, enter a network name>", "environment": "{\"keya\": \"valuea\"}"
        }' -H "Content-Type: application/json"
        ```

        The response will include a `container_id` and `container_network` which can be used with the next requests.

    2. Start container request:
        ```
        curl -XPOST "http://localhost:8002/start" -d '{"container_id": "<container-id>","container_network": "<container_network>"}' -H "Content-Type: application/json"
        ```

    3. Stop container request:
        ```
        curl -XPOST "http://localhost:8002/stop" -d '{"container_id": "<container-id>"}' -H "Content-Type: application/json"
        ```

    4. Delete container request:
        ```
        curl -XPOST "http://localhost:8002/delete" -d '{"container_id": "<container-id>"}' -H "Content-Type: application/json"
        ```

# Pushing the image
- Pushing the image requires the image to be built.
- Pushing the image requires the user to know the password or have access to Personal Access Token.
- Therefore, Pushing is only recommended for the people who have access to zim95 repository.
- Here is the command to push the image:
    ```
    make push
    ```


