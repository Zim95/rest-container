# builtins
import os
import abc
# third-party
import docker
import kubernetes
# modules
import src.constants as constants
import src.exceptions as exceptions
import src.utils as utils


class ContainerManager:
    """
    Manages containers in the supported environment.
    This is an abstract class. To be implemented for each
    new supported environment.

    Author: Namah Shrestha
    """
    def __init__(
        self,
        image_name: str,
        container_name: str,
        container_network: str = "",
        environment: dict = {},
    ) -> None:
        """
        Initialize parameters:
        :params:
            :image_name: str: Supported image name. e.g. ubuntu
            :container_name: str: Name of the container.
            :container_password: str: Password of the container.
                                      Required for sudo commands as well.

        Author: Namah Shrestha
        """
        self.image_name: str = image_name
        self.container_name: str = container_name
        self.container_network: str = constants.BROWSETERM_DOCKER_NETWORK if not \
            container_network else container_network
        self.environment: dict = environment

    @abc.abstractmethod
    def create_network(self) -> dict:
        pass

    @abc.abstractmethod
    def create_container(self) -> dict:
        pass

    @classmethod
    @abc.abstractmethod
    def stop_container(cls, container_id: str) -> dict:
        pass

    @classmethod
    @abc.abstractmethod
    def start_container(cls, container_id: str) -> dict:
        pass

    @classmethod
    @abc.abstractmethod
    def delete_container(cls, container_id: str) -> dict:
        pass


class DockerContainerManager(ContainerManager):
    if utils.get_runtime_environment() == "docker":
        client = docker.from_env()
    else:
        client = None

    def __init__(
        self,
        image_name: str,
        container_name: str,
        container_network: str = "",
        environment: dict = {},
    ) -> None:
        super().__init__(
            image_name,
            container_name,
            container_network=container_network,
            environment=environment
        )

    @classmethod
    def check_client(cls) -> None:
        if cls.client is None:
            client_is_none: str = (
                "The client is None. "
                "This happens when the methods of a different container manager is called "
                "than the runtime environment"
            )
            raise exceptions.ContainerClientNotResolved(client_is_none)

    def create_network(self) -> dict:
        try:
            existing_networks: list = self.client.networks.list(names=[self.container_network])
            if not existing_networks:
                # Network does not exist, so create it
                self.client.networks.create(self.container_network)
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)

    def create_container(self) -> dict:
        try:
            self.check_client()
            self.create_network()
            container_options: dict = {
                "image": self.image_name,
                "name": self.container_name,
                "network": constants.BROWSETERM_DOCKER_NETWORK,
                "detach": True,
                "ports": {
                    "22/tcp": 2222,
                },
                "environment": {
                    **os.environ,
                    **self.environment,
                },
            }
            # TODO: Remove ports
            container = self.client.containers.create(**container_options)
            return {"container_id": container.id}
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)

    @classmethod
    def start_container(cls, container_id: str) -> dict:
        try:
            cls.check_client()
            container = cls.client.containers.get(container_id=container_id)
            container.start()
            container.reload()
            ip_address: str = container.attrs[
                    'NetworkSettings']['Networks'][
                        constants.BROWSETERM_DOCKER_NETWORK]['IPAddress']
            if not ip_address:
                raise exceptions.ContainerIpUnresolved(
                    "Containers ip address is not resolved."
                )
            return {
                "container_id": container.id,
                "container_ip": ip_address,
            }
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)

    @classmethod
    def stop_container(cls, container_id: str) -> dict:
        try:
            cls.check_client()
            container = cls.client.containers.get(container_id=container_id)
            container.stop()
            return {"container_id": container.id, "status": "stopped"}
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)

    @classmethod
    def delete_container(cls, container_id: str) -> dict:
        try:
            cls.check_client()
            container = cls.client.containers.get(container_id=container_id)
            container.remove()
            return {"container_id": container.id, "status": "deleted"}
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)


class KubernetesContainerManager(ContainerManager):
    """
    Manage containers aka pods in Kubernetes.
    It creates a POD and a SERVICE as well.

    Author: Namah Shrestha
    """
    def __init__(
        self,
        image_name: str,
        container_name: str,
        container_network: str = "",
        environment: dict = {},
    ) -> None:
        super().__init__(
            image_name,
            container_name,
            container_network=container_network,
            environment=environment
        )


ENV_CONTAINER_MGR_MAPPING: dict = {
    "docker": DockerContainerManager,
    "kubernetes": KubernetesContainerManager
}
