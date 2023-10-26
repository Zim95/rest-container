1. Create container request:
    ```
    curl -XPOST "http://localhost:8002/create" -d '{"image_name": "zim95/ssh_ubuntu:latest", "container_name": "test_ssh", "container_network": "rest-container-ssh-network", "environment": "{\"SSH_PASSWORD\": \"0907namah\"}"}' -H "Content-Type: application/json"
    ```

2. Start container request:
    ```
    curl -XPOST "http://localhost:8002/start" -d '{"container_id": "", "container_network": "rest-container-ssh-network"}' -H "Content-Type: application/json"
    ```

3. Stop container request:
    ```
    curl -XPOST "http://localhost:8002/stop" -d '{"container_id": ""}' -H "Content-Type: application/json"
    ```

4. Delete container request:
    ```
    curl -XPOST "http://localhost:8002/delete" -d '{"container_id": ""}' -H "Content-Type: application/json"
    ```

- Remove localhost from list of known hosts.
    ```
    ssh-keygen -R localhost
    ```
