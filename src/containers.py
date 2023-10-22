# builtins
import typing
import abc
# third-party
import docker
import kubernetes
# modules
import src.constants as constants
import src.exceptions as exceptions


class ContainerManager:
    """
    Manages containers in the 
    
    """
    def __init__(
        self,
        image_name: str,
        container_name: str,
        container_password: str = "",
        key_based: bool =False
    ) -> None:
        self.image_name: str = image_name
        self.container_name: str = container_name
        self.container_password: str = container_password
        self.key_based: bool = key_based

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
    client = docker.from_env()

    def __init__(
        self,
        image_name: str,
        container_name: str,
        container_password: str = "",
        key_based: bool =False
    ) -> None:
        super().__init__(
            image_name, container_name, container_password, key_based)
    
    def create_container(self) -> dict:
        try:
            image: str = constants.BROWSETERM_IMAGE_NAME_MAPPING.get(
                self.image_name)
            if not image:
                unsupported_image_err: str = (
                    f"Unsupported Image Name: {self.image_name}"
                )
                raise exceptions.UnsupportedImageName(unsupported_image_err)
            container_options: dict = {
                "image": image,
                "name": self.container_name,
                "network": constants.BROWSETERM_DOCKER_NETWORK,
                "detach": True,
                "ports": {
                    "22/tcp": 2222,
                },
                "environment": {
                    "SSH_PASSWORD": self.container_password,
                },
            }
            container = self.client.containers.create(**container_options)
            return {"container_id": container.id}
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)

    @classmethod
    def start_container(cls, container_id: str) -> dict:
        try:
            container = cls.client.containers.get(container_id=container_id)
            container.start()
            return {
                "container_id": container.id,
                "container_ip": container.attrs[
                    'NetworkSettings']['Networks']['mynetwork']['IPAddress'],
            }
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)


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
        container_password: str = "",
        key_based: bool =False
    ) -> None:
        super().__init__(
            image_name, container_name, container_password, key_based
        )


ENV_CONTAINER_MGR_MAPPING: dict = {
    "docker": DockerContainerManager,
    "kubernetes": KubernetesContainerManager
}