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

# Debug on Docker
- PreRequisites:
    - Run on Docker by following the above mentioned steps.
- If you notice, the docker container created has two ports open `8002` and `8003`.
    - `8002` is your actual running container and `8003` is for debugging.
- Once the container is running, `exec` into the container.
    ```
    docker container exec -it <container_id> bash
    ```
- Then run `app.py` with `python`.
    ```
    python app.py
    ```
- This will start your debug `flask` application on `8003`.
- Now make the API Requests to port `8003`.
- You can also use the debugger, `import pdb; pdb.set_trace()` or `breakpoint()` to
    debug parts of your code.

# Run on kubernetes
- PreRequisites:
    - `kubectl` needs to be installed and working.
    - Have a working kubernetes cluster.
- To run the dev environment:
    ```
    kubectl apply -f k8s_yamls/rest-container-dev.yaml
    ```
- This remove everything:
    ```
    kubectl delete -f k8s_yamls/rest-container-dev.yaml
    ```
- Now use port forwarding on the api:
    ```
    kubectl port-forward svc/rest-container-api-service <host-port>:8002 -n rc-namespace
    ```
- You can now make the API requests on `http://localhost:<host-port>`.
- For example, try doing:
    ```
    kubectl port-forward svc/rest-container-api-service 8002:8002 -n rc-namespace
    ```
    Then
    ```
    curl -XGET 'http://localhost:8002/ping'
    ```
    You should get a ping response back.

# Debug on kubernetes
- PreRequisites:
    - Run on Kubernetes by following the above mentioned steps.
- If you notice, there are two kubernetes services, one is mapped to `8002` and the other to `8003`.
- First get the id of the pod you are running:
    ```
    kubectl get pods -n rc-namespace
    ```
- Exec into the pod:
    ```
    kubectl exec -it <podid> -n rc-namespace /bin/bash
    ```
    NOTE: Ingore deprecated warnings. Using kubectl exec -- command doesn't work.
- Run the python application
    ```
    python app.py
    ```
- You should have an application running on port `8003`. You already have a service which maps listens to `8003`.
  This service itself also runs on `8003`.
- Next we need to port forward `8003`.
    ```
    kubectl port-forward svc/rest-container-api-service <host-port>:8003 -n rc-namespace
    ```
- Now make the API Requests to port `8003`.
- You can also use the debugger, `import pdb; pdb.set_trace()` or `breakpoint()` to
    debug parts of your code.
- NOTE: The source code on the host machine is not mapped to the container yet. This is being worked on.
        Therefore changes in the code will not be reflected inside the pod.
        Apologies for the inconvinience.
        Upon any change in the code. Currently, we need to build the image.
        Then we need to delete the resources and restart them.
        Instructions on deleting and restarting are mentioned above.
        Its as simple as doing `kubectl apply -f <file>.yaml` and `kubectl delete -f <file>.yaml`


# API Requests
- The API Requests will create/stop/start/delete containers on which ever environment they are run on.
- For example,
    - If the container is run on docker, these APIs will create/start/stop/delete docker containers.
- Here are the requests.
    1. Create container request:
        ```
        curl -XPOST "http://localhost:8002/create" -d '{"image_name": "enter-an-image-name", "container_name": "enter-a-name-here", "container_network": "<enter a network name>", "publish_information": "{\"<container-port>\/tcp\": <host-port>}", "environment": "{\"keya\": \"valuea\"}"
        }' -H "Content-Type: application/json"
        ```
        NOTE: `container_name`, `publish_information` and `environment` are optional request parameters.
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


