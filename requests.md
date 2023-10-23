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