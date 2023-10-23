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
        container_password: str,
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
        self.container_password: str = container_password

    @classmethod
    @abc.abstractmethod
    def create_network(cls) -> dict:
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
        container_password: str,
    ) -> None:
        super().__init__(
            image_name, container_name, container_password)

    @classmethod
    def check_client(cls) -> None:
        if cls.client is None:
            environment_mismatch: str = (
                "Container is not running on docker. "
                "Therefore docker client is None."
            )
            raise exceptions.EnvironmentMismatch(environment_mismatch)

    def create_container(self) -> dict:
        try:
            self.check_client()
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
        except exceptions.EnvironmentMismatch as em:
            raise exceptions.EnvironmentMismatch(em)

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
        except exceptions.EnvironmentMismatch as em:
            raise exceptions.EnvironmentMismatch(em)

    @classmethod
    def stop_container(cls, container_id: str) -> dict:
        try:
            cls.check_client()
            container = cls.client.containers.get(container_id=container_id)
            container.stop()
            return {"container_id": container.id, "status": "stopped"}
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except exceptions.EnvironmentMismatch as em:
            raise exceptions.EnvironmentMismatch(em)

    @classmethod
    def delete_container(cls, container_id: str) -> dict:
        try:
            cls.check_client()
            container = cls.client.containers.get(container_id=container_id)
            container.remove()
            return {"container_id": container.id, "status": "deleted"}
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except exceptions.EnvironmentMismatch as em:
            raise exceptions.EnvironmentMismatch(em)


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
        container_password: str,
    ) -> None:
        super().__init__(
            image_name, container_name, container_password)


ENV_CONTAINER_MGR_MAPPING: dict = {
    "docker": DockerContainerManager,
    "kubernetes": KubernetesContainerManager
}
