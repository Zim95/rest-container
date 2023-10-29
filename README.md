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
    kubectl port-forward svc/rest-container-api-debug-service <host-port>:8003 -n rc-namespace
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


# API Requests using POSTMAN
- Import the REST-Container-APIRequests.postman_collection.json into your POSTMAN.
- Use the requests as follows:
    - Create the container. The response should have multiple container ids.
    - Paste those container ids in the container_ids field for start, stop and delete
      to make those requests..
    - NOTE: For kubernetes you can notice that stop is not available. That is because kubernetes
            does not support stop. 

# API Requests using CURL
- Create Container Request:
    ```
    curl --location 'http://localhost:8003/create' \
    --header 'Content-Type: application/json' \
    --data '{
        "image_name": "<repo_name>/<image_name>:<image_tag>",
        "container_name": "<unique-container-name>",
        "container_network": "<unique-container-network>",
        "publish_information": {
            "<container-port>/<protocol>": <hostport/serviceport>,
            "<container-port>/<protocol>": <hostport/serviceport>,
            ....
        },
        "environment": {
            "<env1>": "<value1>",
            "<env1>": "<value1>",
            ....
        }
    }'
    ```

    Take this example for kubernetes:
    ```
    curl --location 'http://localhost:8003/create' \
    --header 'Content-Type: application/json' \
    --data '{
        "image_name": "zim95/ssh_ubuntu:latest",
        "container_name": "test-ssh",
        "container_network": "test-ssh-network",
        "publish_information": {
            "22/tcp": 2222,
            "23/tcp": 2223
        },
        "environment": {
            "SSH_PASSWORD": "0907namah"
        }
    }'
    ```

    The response of the example would look as follows:
    ```
    {
        "response": [
            {
                "container_id": "26cd4497-5fcd-4237-a525-76cdc4d83da8",
                "container_network": "test-ssh-network",
                "container_port": 2222
            },
            {
                "container_id": "b210058b-b684-48c1-a0a6-6a98bf632914",
                "container_network": "test-ssh-network",
                "container_port": 2223
            }
        ]
    }
    ```
    Now, create a list from the unqiue container_ids and use that for the other requests:
    ```
    {
        "container_ids": ["26cd4497-5fcd-4237-a525-76cdc4d83da8", "b210058b-b684-48c1-a0a6-6a98bf632914"],
        "container_network": "test-ssh-network"
    }
    ```
- Start Container Request:
    Use the above data to create the curl request.
    ```
    curl --location 'http://localhost:8002/start' \
    --header 'Content-Type: application/json' \
    --data '{
        "container_ids": ["26cd4497-5fcd-4237-a525-76cdc4d83da8", "b210058b-b684-48c1-a0a6-6a98bf632914"],
        "container_network": "test-ssh-network"
    }'
    ```

    The response of the example would look as:
    ```
    {
        "response": [
            {
                "container_id": "26cd4497-5fcd-4237-a525-76cdc4d83da8",
                "container_ip": "10.96.77.178"
            },
            {
                "container_id": "b210058b-b684-48c1-a0a6-6a98bf632914",
                "container_ip": "10.96.68.181"
            }
        ]
    }
    ```
- Stop Container Request:
    Use the above data to create the curl request.
    ```
    curl --location 'http://localhost:8002/start' \
    --header 'Content-Type: application/json' \
    --data '{
        "container_ids": ["26cd4497-5fcd-4237-a525-76cdc4d83da8", "b210058b-b684-48c1-a0a6-6a98bf632914"],
        "container_network": "test-ssh-network"
    }'
    ```

    The response of the example would look as:
    ```
    {
    "response": [
            {
                "container_id": "test-ssh",
                "container_network": "test-ssh-network",
                "status": "deleted pod"
            },
            {
                "container_id": "test-ssh-service-0",
                "container_network": "test-ssh-network",
                "status": "deleted service"
            },
            {
                "container_id": "test-ssh-service-1",
                "container_network": "test-ssh-network",
                "status": "deleted service"
            }
        ]
    }
    ```
- Delete Container Request:
    Use the above data to create the curl request.
    ```
    curl --location 'http://localhost:8002/start' \
    --header 'Content-Type: application/json' \
    --data '{
        "container_ids": ["26cd4497-5fcd-4237-a525-76cdc4d83da8", "b210058b-b684-48c1-a0a6-6a98bf632914"],
        "container_network": "test-ssh-network"
    }'
    ```

    The response of the example would look as:
    ```
    {
    "response": [
            {
                "container_id": "test-ssh",
                "container_network": "test-ssh-network",
                "status": "deleted pod"
            },
            {
                "container_id": "test-ssh-service-0",
                "container_network": "test-ssh-network",
                "status": "deleted service"
            },
            {
                "container_id": "test-ssh-service-1",
                "container_network": "test-ssh-network",
                "status": "deleted service"
            }
        ]
    }
    ```

# Pushing the image
- Pushing the image requires the image to be built.
- Pushing the image requires the user to know the password or have access to Personal Access Token.
- Therefore, Pushing is only recommended for the people who have access to zim95 repository.
- Here is the command to push the image:
    ```
    make push
    ```


