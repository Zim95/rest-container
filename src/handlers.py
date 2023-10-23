# builtins
import json
import abc

# modules
import src.exceptions as exceptions
import src.constants as constants
import src.containers as containers

# third party
import docker


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
    Echoes back request parameters.

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
        return self.request_params


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

    def get_payload(self) -> dict:
        """
        Json load the payload and then raise error if
        Json loading doesn't work.

        Author: Namah Shrestha
        """
        try:
            return json.loads(self.request_params["payload"])
        except json.JSONDecodeError as je:
            raise json.JSONDecodeError(je)

    def handle(self) -> dict | None:
        """
        Handle environment exception.
        Handle container manager exception.

        Author: Namah Shrestha
        """
        container_environment: str = self.request_params["view_args"].get(
            "cnenv", "")
        if container_environment not in constants.SUPPORTED_ENVIRONMENTS:
            container_environment_not_supported: str = (
                "Unsupported container environment: "
                f"{container_environment}"
            )
            raise exceptions.UnsupportedContainerEnvironment(
                container_environment_not_supported
            )
        self.container_manager: containers.ContainerManager = \
                containers.ENV_CONTAINER_MGR_MAPPING.get(
                    container_environment)
        if not self.container_manager:
            cnmgrnf: str = (
                f"Container Manager for {self.container_environment}"
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
        Take the environment: Either docker or kubernetes.
        Take the image name. (Should be a supported image).
        Deploy the image on environment.
        Return the container id.

        Author: Namah Shrestha
        """
        try:
            super().handle()  
            container_payload: dict = self.get_payload()
            container_manager_object: containers.ContainerManager = \
                self.container_manager(
                    image_name=container_payload.get("image_name", ""),
                    container_name=container_payload.get("container_name", ""),
                    container_password=container_payload.get("container_password", "")
                )
            response: dict = container_manager_object.create_container()
            return response
        except exceptions.UnsupportedContainerEnvironment as e:
            return {
                "unsupported_container_env_error": str(e),
            }
        except exceptions.ContainerManagerNotFound as e:
            return {
                "container_mgr_not_found_error": str(e),
            }
        except json.JSONDecodeError as je:
            return {
                "payload_format_error": str(e),
            }
        except docker.errors.DockerException as de:
            return {
                "docker_exception": str(de),
            }


class ReadyContainerHandler(ContainerHandler):
    """
    Checks if the environment provided has the container id.
    If so, it starts the container.

    Author: Namah Shrestha
    """

    def __init__(self, request_params: dict) -> None:
        """
        Initialize request parameters. Call super.__init__.
        
        Author: Namah Shrestha
        """
        super().__init__(request_params)

    @abc.abstractmethod
    def calling_method(self, container_id: str) -> dict:
        pass

    def handle(self) -> dict | None:
        """
        Take the environment: Either docker or kubernetes.
        Take the container id
        Start the container

        Author: Namah Shrestha
        """
        try:
            super().handle()
            container_payload: dict = self.get_payload()
            container_id: str = container_payload.get("container_id", "")
            return self.calling_method(container_id=container_id)
        except exceptions.UnsupportedContainerEnvironment as e:
            return {
                "unsupported_container_env_error": str(e),
            }
        except exceptions.ContainerManagerNotFound as e:
            return {
                "container_mgr_not_found_error": str(e),
            }
        except docker.errors.DockerException as de:
            return {
                "docker_exception": str(de),
            }


class StartContainerHandler(ReadyContainerHandler):

    def __init__(self, request_params: dict) -> None:
        super().__init__(request_params)

    def calling_method(self, container_id: str) -> dict:
        try:
            response: dict = self.container_manager.start_container(
                container_id=container_id)
            return response
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)


class StopContainerHandler(ReadyContainerHandler):

    def __init__(self, request_params: dict) -> None:
        super().__init__(request_params)

    def calling_method(self, container_id: str) -> dict:
        try:
            response: dict = self.container_manager.stop_container(
                container_id=container_id)
            return response
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)


class DeleteContainerHandler(ReadyContainerHandler):

    def __init__(self, request_params: dict) -> None:
        super().__init__(request_params)

    def calling_method(self, container_id: str) -> dict:
        try:
            response: dict = self.container_manager.delete_container(
                container_id=container_id)
            return response
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
