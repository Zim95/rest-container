# builtins
import json
import abc
import requests

# modules
import src.exceptions as exceptions
import src.constants as constants
import src.containers as containers
import src.utils as utils

# third party
import docker
import kubernetes.client.rest as k8s_rest


class Handler:
    """
    Handler abstract class. Receives request data.
    Has a handle method which is an abstract class method.

    Author: Namah Shrestha
    """

    def __init__(self, request_params: dict) -> None:
        """
        Initialize the request params.

        Author: Namah Shrestha
        """
        self.request_params: dict = request_params

    @abc.abstractclassmethod
    def handle(self) -> dict | None:
        """
        Abstract handle logic to be implemented by child classes.

        Author: Namah Shrestha
        """
        pass


class PingHandler(Handler):
    """
    Simple Ping Handler. For test.
    Accepts request parameters.
    Echoes back request parameters and runtime environment.

    Author: Namah Shrestha
    """
    def __init__(self, request_params: dict) -> None:
        """
        Initialize request parameters.

        Author: Namah Shrestha
        """
        super().__init__(request_params)
    
    def handle(self) -> dict | None:
        """
        Return request params for test.

        Author: Namah Shrestha
        """
        return {
            "request_params": self.request_params,
            "runtime": utils.get_runtime_environment()
        }


class ContainerHandler(Handler):
    """
    Base container handler. Will parse the required data.

    Author: Namah Shrestha
    """

    def __init__(self, request_params: dict) -> None:
        """
        Initialize request parameters. Call super.__init__

        Author: Namah Shrestha
        """
        super().__init__(request_params)

    def json_load(self, dictionary: dict, key: str) -> dict:
        """
        Json load the provided key and then raise error if
        Json loading doesn't work.

        Author: Namah Shrestha
        """
        try:
            item: str = dictionary.get(key, "{}")
            # this is for those dictionaries that are enclosed in
            # single quotes.
            if "'" in item:
                item = item.replace("'", "\"")
            return json.loads(item)
        except json.JSONDecodeError as je:
            raise json.JSONDecodeError(je)

    def handle(self) -> dict | None:
        """
        Get runtime environment. Based on that choose the container manager.
        Handle container manager exception and unsupported runtime environment exception.

        This functionality is specific to containers and therefore is only defined in
        Container handler.
        Other handlers may not need to know the runtime environment.

        Author: Namah Shrestha
        """
        runtime_environment: str = utils.get_runtime_environment()
        if runtime_environment not in constants.SUPPORTED_ENVIRONMENTS:
            runtime_environment_not_supported: str = (
                "Unsupported runtime environment: "
                f"{runtime_environment}"
            )
            exceptions.UnsupportedRuntimeEnvironment(
                runtime_environment_not_supported
            )

        self.container_manager: containers.ContainerManager = \
                containers.ENV_CONTAINER_MGR_MAPPING.get(
                    runtime_environment)
        if not self.container_manager:
            cnmgrnf: str = (
                f"Container Manager for {runtime_environment}"
                "has not been assigned yet. We regret the inconvenience."
            )
            raise exceptions.ContainerManagerNotFound(cnmgrnf)


class CreateContainerHandler(ContainerHandler):
    """
    Handler to create containers in either docker or kubernetes.

    Author: Namah Shrestha
    """

    def __init__(self, request_params: dict) -> None:
        """
        Initialize request parameters. Call super.__init__.
        
        Author: Namah Shrestha
        """
        super().__init__(request_params)
    
    def handle(self) -> dict | None:
        """
        Parse the request payload.
        Extract:
            image_name: str: Name of the image.
            container_name: str: Name of the container.
            container_network: str: Name of the network.
            publish_information: dict: Port mappings.
            environment: Environment dictionary.
        Create the container based on these params.

        Author: Namah Shrestha
        """
        try:
            super().handle()
            container_payload: dict = self.json_load(self.request_params, "payload")
            container_manager_object: containers.ContainerManager = \
                self.container_manager(
                    image_name=container_payload.get("image_name", ""),
                    container_name=container_payload.get("container_name", ""),
                    container_network=container_payload.get("container_network", ""),
                    publish_information=container_payload.get("publish_information", {}),
                    environment=container_payload.get("environment", {}),
                )
            response: dict = container_manager_object.create_container()
            return response
        except exceptions.UnsupportedRuntimeEnvironment as e:
            raise exceptions.UnsupportedRuntimeEnvironment(e)
        except exceptions.ContainerManagerNotFound as e:
            raise exceptions.ContainerManagerNotFound(e)
        except json.JSONDecodeError as je:
            raise json.JSONDecodeError(je)
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)
        except Exception as e:
            raise Exception(e)


class ReadyContainerHandler(ContainerHandler):
    """
    Methods for a container which has been created already.
    Has an abstractmethod called calling method which might be start, stop, delete, etc.
    Rest of the logic is handled by handle.

    Author: Namah Shrestha
    """

    def __init__(self, request_params: dict) -> None:
        """
        Initialize request parameters. Call super.__init__.
        
        Author: Namah Shrestha
        """
        super().__init__(request_params)

    @abc.abstractmethod
    def calling_method(self, **container_payload: dict) -> dict:
        """
        Either start, stop or delete. The container should be created prior.
        """
        pass

    def handle(self) -> list | None:
        """
        Take the environment: Either docker or kubernetes.
        Take the container id
        Start the container

        Author: Namah Shrestha
        """
        try:
            super().handle()
            container_payload: dict = self.json_load(self.request_params, "payload")
            container_name: str = container_payload.get("container_name", "")
            calling_response: list = self.calling_method(**container_payload)
            if container_name:
                modified_response = []
                for res in calling_response:
                    res["container_name"] = container_name
                    modified_response.append(res)
                return modified_response
            return calling_response
        except exceptions.UnsupportedRuntimeEnvironment as e:
            raise exceptions.UnsupportedRuntimeEnvironment(e)
        except exceptions.ContainerManagerNotFound as e:
            raise exceptions.ContainerManagerNotFound(e)
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)
        except Exception as e:
            raise Exception(e)



class StartContainerHandler(ReadyContainerHandler):

    def __init__(self, request_params: dict) -> None:
        super().__init__(request_params)

    def calling_method(self, **container_payload: dict) -> list:
        try:
            container_ids: list[str] = container_payload["container_ids"]
            container_network: str = container_payload["container_network"]
            response: dict = self.container_manager.start_container(
                container_ids=container_ids,
                container_network=container_network
            )
            return response
        except KeyError as ke:
            raise KeyError(ke)
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)
        except Exception as e:
            raise Exception(e)


class StopContainerHandler(ReadyContainerHandler):

    def __init__(self, request_params: dict) -> None:
        super().__init__(request_params)

    def calling_method(self, **container_payload: dict) -> list:
        try:
            container_ids: list[str] = container_payload["container_ids"]
            container_network: str = container_payload["container_network"]
            response: dict = self.container_manager.stop_container(
                container_ids=container_ids,
                container_network=container_network
            )
            return response
        except KeyError as ke:
            raise KeyError(ke)
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)
        except Exception as e:
            raise Exception(e)


class DeleteContainerHandler(ReadyContainerHandler):

    def __init__(self, request_params: dict) -> None:
        super().__init__(request_params)

    def calling_method(self, **container_payload: dict) -> list:
        try:
            container_ids: list[str] = container_payload["container_ids"]
            container_network: str = container_payload["container_network"]
            response: dict = self.container_manager.delete_container(
                container_ids=container_ids,
                container_network=container_network
            )
            return response
        except KeyError as ke:
            raise KeyError(ke)
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)
        except Exception as e:
            raise Exception(e)


class BeaconHandler(Handler):

    def __init__(self, request_params: dict) -> None:
        super().__init__(request_params)

    def handle(self) -> dict | None:
        try:
            beacon_payload: list[dict] = json.loads(self.request_params["payload"])
            for payload in beacon_payload:
                response = requests.request(
                    method=payload["method"],
                    url=payload["url"],
                    headers=payload["headers"],
                    data=payload["body"]
                )
                if response.status_code != 200:
                    raise Exception(response.text)
        except KeyError as ke:
            raise KeyError(ke)
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)
        except Exception as e:
            raise Exception(e)
