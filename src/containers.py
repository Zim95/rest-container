# builtins
import os
import abc
# third-party
import docker
import kubernetes.client as kcli
import kubernetes.config as kconf
import kubernetes.client.rest as k8s_rest
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
        publish_information: dict = {},
        environment: dict = {},
    ) -> None:
        """
        Initialize parameters:
        :params:
            :image_name: str: Supported image name. e.g. ubuntu
            :container_name: str: Name of the container.
            :container_network: str: Name of the network in which the container is deployed.
                                     There should be some default value for this for each
                                     container environment.
            :publish_information: dict: Port and host mapping information.
            :environment: dict: Environment variables as a dictionary.
        Author: Namah Shrestha
        """
        self.image_name: str = image_name
        self.container_name: str = container_name
        self.container_network: str = container_network
        self.publish_information: dict = publish_information
        self.environment: dict = environment

    @classmethod
    def check_client(cls) -> None:
        """
        Check the client. If it is None, then raise an exception.

        Author: Namah Shrestha
        """
        if cls.client is None:
            client_is_none: str = (
                "The client is None. "
                "This happens when the methods of a different container manager is called "
                "than the runtime environment"
            )
            raise exceptions.ContainerClientNotResolved(client_is_none)

    @abc.abstractmethod
    def create_container(self) -> dict:
        """
        Contains logic on how to create a container in the specific environment.

        Author: Namah Shrestha
        """
        pass

    @classmethod
    @abc.abstractmethod
    def start_container(cls, container_id: str, container_network: str) -> dict:
        """
        Contains logic on how to start a container in the specific environment.

        Author: Namah Shrestha
        """
        pass

    @classmethod
    @abc.abstractmethod
    def stop_container(cls, container_id: str) -> dict:
        """
        Contains logic on how to stop a container in the specific environment.

        Author: Namah Shrestha
        """
        pass

    @classmethod
    @abc.abstractmethod
    def delete_container(cls, container_id: str) -> dict:
        """
        Contains logic on how to delete a container in the specific environment.

        Author: Namah Shrestha
        """
        pass


class DockerContainerManager(ContainerManager):
    """
    Docker Container Related methods.

    Author: Namah Shrestha
    """

    """ 
    Update the client if the runtime environment is docker.
    This means, the client will be set if the application is running inside docker.
    Otherwise, it will be None.

    Author: Namah Shrestha
    """
    if utils.get_runtime_environment() == "docker":
        client = docker.from_env()
    else:
        client = None

    def __init__(
        self,
        image_name: str,
        container_name: str,
        container_network: str = "",
        publish_information: dict = {},
        environment: dict = {},
    ) -> None:
        """
        Initialize parameters by calling the super method.
        Set default value for container_network if not provided.

        Author: Namah Shrestha
        """
        super().__init__(
            image_name,
            container_name,
            container_network=container_network,
            publish_information=publish_information,
            environment=environment,
        )
        if not self.container_network:
            self.container_network = constants.RC_DOCKER_NETWORK

    def create_network(self) -> None:
        """
        Create a docker network if it does not exist.
        Otherwise ignore the network creation.
        Do not raise errors if network does not exist.

        Author: Namah Shrestha
        """
        try:
            self.check_client()
            existing_networks: list = self.client.networks.list(names=[self.container_network])
            if not existing_networks:
                # Network does not exist, so create it
                self.client.networks.create(self.container_network)
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)

    def create_container(self) -> dict:
        """
        Create a docker container based on all the parameters.
        returns: dict: {'container_id': <container_id>, 'container_network': <container_network>}

        Author: Namah Shrestha
        """
        try:
            self.check_client()
            self.create_network()
            container_options: dict = {
                "image": self.image_name,
                "name": self.container_name,
                "network": self.container_network,
                "detach": True,
                "ports": self.publish_information,
                "environment": {
                    **os.environ,
                    **self.environment,
                },
            }
            # TODO: Remove ports
            container = self.client.containers.create(**container_options)
            return {"container_id": container.id, "container_network": self.container_network}
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)

    @classmethod
    def start_container(cls, container_id: str, container_network: str) -> dict:
        '''
        Start the container based on parameters.
        The container needs to be created for the id to exist.
        So this method only works if the container is created.
        :params:
            :container_id: str: Id of the container.
            :container_network: str: Name of the network in which
                                     the container is deployed in.
        :returns: dict: {'container_id': <container_id>, 'container_ip': <container_ip_address>}

        Author: Namah Shrestha
        '''
        try:
            cls.check_client()
            container = cls.client.containers.get(container_id=container_id)
            container.start()
            container.reload()
            ip_address: str = container.attrs[
                    'NetworkSettings']['Networks'][
                        container_network]['IPAddress']
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
        """
        Stop the container based on the parameters.
        The container needs to be created for the id to exist.
        So this method only works if the container is created.
        Will raise errors if the container is not started.
        :params:
            :container_id: str: Id of the container.
        :returns: dict: {'container_id': <container_id>, "status": "stopped"}

        Author: Namah Shrestha
        """
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
        """
        Delete the container based on the parameters.
        The container needs to be created for the id to exist.
        So this method only works if the container is created.
        Will raise errors if the container is not started.
        :params:
            :container_id: str: Id of the container.
        :returns: dict: {'container_id': <container_id>, "status": "deleted"}

        Author: Namah Shrestha
        """
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
    if utils.get_runtime_environment() == "kubernetes":
        kconf.load_kube_config()
        client = kcli.CoreV1Api()
    else:
        client = None
    def __init__(
        self,
        image_name: str,
        container_name: str,
        container_network: str = "",
        publish_information: dict = {},
        environment: dict = {},
    ) -> None:
        super().__init__(
            image_name,
            container_name,
            container_network=container_network,
            publish_information=publish_information,
            environment=environment,
        )
        if not self.container_network:
            self.container_network = constants.RC_KUBERNETES_NAMESPACE

    def create_namespace(self) -> dict:
        """
        Create a namespace in kubernetes. The container network provided
        will serve as the namespace. The policy has been created such that,
        one namespace is cannot interact with the other. This is done through
        V1NetworkPolicyIngressRule.

        Author: Namah Shrestha
        """
        try:
            self.check_client()
            namespaces: list = self.client.list_namespace()
            namespace_exists: bool = any([ns.metadata.name == self.container_network for ns in namespaces])
            if not namespace_exists:
                namespace = kcli.V1Namespace(
                    metadata=kcli.V1ObjectMeta(name=self.container_network)
                )
                self.client.create_namespace(namespace)
                network_policy = kcli.V1NetworkPolicy(
                    metadata={"name": "deny-from-other-namespaces"},
                    spec={
                        "podSelector": {},
                        "policyTypes": ["Ingress"],
                        "ingress": [kcli.V1NetworkPolicyIngressRule(from_=[{}])]
                    }
                )
                networking_api = kcli.NetworkingV1Api()
                networking_api.create_namespaced_network_policy(self.container_network, network_policy)
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)

ENV_CONTAINER_MGR_MAPPING: dict = {
    "docker": DockerContainerManager,
    "kubernetes": KubernetesContainerManager
}
