# BrowseTerm REST
Browseterm's REST API which creates browseterm's SSH Containers on either docker or kubernetes.

This REST API is specific to Browseterm. It can only create containers with images supported by browseterm.

# Run on Docker
- First build the image:
    ```
    make build
    ```
- Deploy the docker container:
    ```
    make dockerrun    
    ```
NOTE: All the commands in Makefile do not work as intended. This is being fixed.

# Docker Related Requests
- Once the code has run on docker you may use the following requests.
    1. Create container request:
        ```
        curl -XPOST "http://localhost:8002/create/docker" -d '{"image_name": "ubuntu", "container_name": "test_ssh", "container_password": "0907namah"}' -H "Content-Type: application/json"
        ```

    2. Start container request:
        ```
        curl -XPOST "http://localhost:8002/start/docker" -d '{"container_id": ""}' -H "Content-Type: application/json"
        ```

    3. Stop container request:
        ```
        curl -XPOST "http://localhost:8002/stop/docker" -d '{"container_id": ""}' -H "Content-Type: application/json"
        ```

    4. Delete container request:
        ```
        curl -XPOST "http://localhost:8002/delete/docker" -d '{"container_id": ""}' -H "Content-Type: application/json"
        ```

# Pushing the image
NOTE:
    - Pushing the image requires the image to be built.
    - Pushing the image requires the user to know the password or have access to Personal Access Token.
    - Therefore, Pushing is only recommended for the people who have access to zim95 repository.
- Here is the command to push the image:
    ```
    make push
    ```


