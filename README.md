# BrowseTerm REST
Browseterm's REST API which creates browseterm's SSH Containers on either docker or kubernetes.

This REST API is specific to Browseterm. It can only create containers with images supported by browseterm.

# Supported Image Names
- We have mentioned that this REST API is specific to browseterm.
- It can only create containers with supported image names.
- Here are the supported image names:
    1. ubuntu

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

# Docker Related Requests
- Once the code has run on docker you may use the following requests.
    1. Create container request:
        ```
        curl -XPOST "http://localhost:8002/create/docker" -d '{"image_name": "enter-a-supported-image-name", "container_name": "enter-a-name-here", "container_password": "enter-a-password-here"}' -H "Content-Type: application/json"
        ```
        NOTE: The supported image names are mentioned in the Supported Image Names section.

        The response will include a `container_id` which can be used with the next requests.

    2. Start container request:
        ```
        curl -XPOST "http://localhost:8002/start/docker" -d '{"container_id": "<container-id>"}' -H "Content-Type: application/json"
        ```

    3. Stop container request:
        ```
        curl -XPOST "http://localhost:8002/stop/docker" -d '{"container_id": "<container-id>"}' -H "Content-Type: application/json"
        ```

    4. Delete container request:
        ```
        curl -XPOST "http://localhost:8002/delete/docker" -d '{"container_id": "<container-id>"}' -H "Content-Type: application/json"
        ```

# Pushing the image
- Pushing the image requires the image to be built.
- Pushing the image requires the user to know the password or have access to Personal Access Token.
- Therefore, Pushing is only recommended for the people who have access to zim95 repository.
- Here is the command to push the image:
    ```
    make push
    ```


