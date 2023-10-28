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
    def create_container(self) -> list[dict]:
        """
        Contains logic on how to create a container in the specific environment.

        Author: Namah Shrestha
        """
        pass

    @classmethod
    @abc.abstractmethod
    def start_container(cls, container_ids: list[str], container_network: str) -> list[dict]:
        """
        Contains logic on how to start a container in the specific environment.

        Author: Namah Shrestha
        """
        pass

    @classmethod
    @abc.abstractmethod
    def stop_container(cls, container_ids: list[str], container_network: str) -> list[dict]:
        """
        Contains logic on how to stop a container in the specific environment.

        Author: Namah Shrestha
        """
        pass

    @classmethod
    @abc.abstractmethod
    def delete_container(cls, container_ids: list[str], container_network: str) -> list[dict]:
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

    @classmethod
    def create_network(cls, container_network: str) -> None:
        """
        Create a docker network if it does not exist.
        Otherwise ignore the network creation.
        Do not raise errors if network does not exist.
        :params: container_network: str: Name of the container_network.

        Author: Namah Shrestha
        """
        try:
            cls.check_client()
            existing_networks: list = cls.client.networks.list(names=[container_network])
            if not existing_networks:
                # Network does not exist, so create it
                cls.client.networks.create(container_network)
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)

    @classmethod
    def delete_network(cls, container_network: str) -> None:
        """
        TODO: A method to delete an existing network.
        """
        pass

    def create_container(self) -> list[dict]:
        """
        Create a docker container based on all the parameters.
        returns: list[dict]:
            [
                {
                    'container_id': <container_id>,
                    'container_network': <container_network>,
                    'container_port': <container_port> | None,
                },
                {
                    'container_id': <container_id>,
                    'container_network': <container_network>,
                    'container_port': <container_port> | None,
                },
                ...
            ]

        Author: Namah Shrestha
        """
        try:
            self.check_client()
            self.create_network(self.container_network)
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
            # if publish information is missing then, container port will be empty
            # otherwise we return the container id and container network for each publish information.
            # this tells the user that he/she may use any of these configurations to access the container.
            if self.publish_information:
                # there is publish information, meaning for each mapping, return the container info.
                return [
                    {
                        "container_id": container.id,
                        "container_network": self.container_network,
                        "container_port": host_port,
                    }
                    for _, host_port in self.publish_information
                ]
            else:
                # if there is no publish information, it means the user does not want any port to be mapped.
                # in such cases, container port is empty.
                return [
                    {
                        "container_id": container.id,
                        "container_network": self.container_network,
                        "container_port": None,
                    }
                ]
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)

    @classmethod
    def start_container(cls, container_ids: list[str], container_network: str) -> list[dict]:
        '''
        Start the containers based on parameters.
        The containers needs to be created for the id to exist.
        So this method only works if the containers are created.
        :params:
            :container_ids: list[str]: List of container ids to start.
            :container_network: str: Name of the network in which
                                     the container is deployed in.
        :returns: list[dict]:
            [
                {'container_id': <container_id>, 'container_ip': <container_ip_address>},
                {'container_id': <container_id>, 'container_ip': <container_ip_address>},
                ...
            ]
        NOTE: In case of docker, the container id will be the same, since only one container will
              be created. So there will be only one item in list.
              Nevertheless, we should act like there will be multiple.
              If there are multiple publish informations then we will get the same container id
              with different ports.
              In this case, we need to identify the unique sets of container ids that exist within the
              create container's response.

        Author: Namah Shrestha
        '''
        try:
            cls.check_client()
            start_container_results: list[dict] = []
            for container_id in container_ids:
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
                start_container_results.append(
                    {
                        "container_id": container.id,
                        "container_ip": ip_address,
                    }
                )
            return start_container_results
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)

    @classmethod
    def stop_container(cls, container_ids: list[str], container_network: str) -> list[dict]:
        """
        Stop the container based on the parameters.
        The container needs to be created for the id to exist.
        So this method only works if the container is created.
        Will raise errors if the container is not started.
        :params:
            :container_ids: list[str]: List of container ids.
            :container_network: str: Network of the container
        :returns: list[dict]:
            [
                {'container_id': <container_id>, 'container_network': <container_network> ,"status": "stopped"},
                {'container_id': <container_id>, 'container_network': <container_network> ,"status": "stopped"},
                ...
            ]

        Author: Namah Shrestha
        """
        try:
            cls.check_client()
            stop_container_results: list = []
            for container_id in container_ids:
                container = cls.client.containers.get(container_id=container_id)
                container.stop()
                stop_container_results.append(
                    {
                        "container_id": container.id,
                        "container_network": container_network,
                        "status": "stopped"
                    }
                )
            return stop_container_results
        except docker.errors.DockerException as de:
            raise docker.errors.DockerException(de)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)

    @classmethod
    def delete_container(cls, container_ids: list[str], container_network: str) -> list[dict]:
        """
        Delete the container based on the parameters.
        The container needs to be created for the id to exist.
        So this method only works if the container is created.
        Will raise errors if the container is not started.
        :params:
            :container_ids: list[str]: List of container ids.
            :container_network: str: Network of the container
        :returns: list[dict]:
            [
                {'container_id': <container_id>, 'container_network': <container_network> ,"status": "deleted"},
                {'container_id': <container_id>, 'container_network': <container_network> ,"status": "deleted"},
                ...
            ]

        Author: Namah Shrestha
        """
        try:
            cls.check_client()
            delete_container_results: list = []
            for container_id in container_ids:
                container = cls.client.containers.get(container_id=container_id)
                container.stop()
                delete_container_results.append(
                    {
                        "container_id": container.id,
                        "container_network": container_network,
                        "status": "deleted"
                    }
                )
            return delete_container_results
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

    """ 
    Update the client if the runtime environment is kubernetes.
    This means, the client will be set if the application is running inside kubernetes.
    Otherwise, it will be None.

    Author: Namah Shrestha
    """
    if utils.get_runtime_environment() == "kubernetes":
        # kconf.load_kube_config()  # Causes errors when running inside kubernetes
        kconf.load_incluster_config()  # For incluster configurations
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
            self.container_network = constants.RC_KUBERNETES_NAMESPACE

    @classmethod
    def create_namespace(cls, namespace_name: str) -> None:
        """
        Create a namespace in kubernetes.
        The container network provided will serve as the namespace.
        The policy has been created such that,
            one namespace is cannot interact with the other.
        This is done through V1NetworkPolicyIngressRule.

        Author: Namah Shrestha
        """
        try:
            cls.check_client()
            namespaces: list = cls.client.list_namespace()
            namespace_exists: bool = any([ns.metadata.name == namespace_name for ns in namespaces.items])
            if not namespace_exists:
                namespace = kcli.V1Namespace(
                    metadata=kcli.V1ObjectMeta(name=namespace_name)
                )
                cls.client.create_namespace(namespace)
                network_policy = kcli.V1NetworkPolicy(
                    metadata={"name": "deny-from-other-namespaces"},
                    spec={
                        "podSelector": {},
                        "policyTypes": ["Ingress"],
                        "ingress": [kcli.V1NetworkPolicyIngressRule(_from=None)]
                    }
                )
                networking_api = kcli.NetworkingV1Api()
                networking_api.create_namespaced_network_policy(namespace_name, network_policy)
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def delete_namespace(cls, namespace_name: str) -> None:
        """
        TODO: Create delete namespace method.
        """
        pass

    @classmethod
    def create_service(
        cls,
        service_name: str,
        app_name: str,
        namespace: str,
        service_port: int,
        target_port: int,
        protocol: str,
    ) -> dict:
        """
        Create the LoadBalancer Service for the information provided.
        :params:
            :service_name: str: Name of the service.
            :app_name: str: Name of the app to attach the service to.
            :namespace: str: Namespace where the service will be created.
            :service_port: int: The port, the service is listening to.
            :target_port: int: The port, the container is listening to.
            :protocol: str: The protocol of the service.
        :returns: {
            "service_id": service.metadata.uid,
            "service_ip": service._spec.cluster_ip,
            "service_name": service.metadata.name,
            "service_namespace": namespace,
            "service_port": service_port,
        }

        Author: Namah Shrestha
        """
        try:
            cls.check_client()
            service_manifest: kcli.V1Service = kcli.V1Service(
                metadata=kcli.V1ObjectMeta(name=service_name),
                spec=kcli.V1ServiceSpec(
                    selector={"app": app_name},
                    ports=[
                        kcli.V1ServicePort(
                            port=service_port,
                            target_port=target_port,
                            protocol=protocol,
                        )
                    ],
                    type="LoadBalancer"
                )
            )
            service: kcli.V1Service = cls.client.create_namespaced_service(namespace, service_manifest)
            return {
                "service_id": service.metadata.uid,
                "service_ip": service._spec.cluster_ip,
                "service_name": service.metadata.name,
                "service_namespace": namespace,
                "service_port": service_port,
            }
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def create_services_for_app(
        cls,
        service_name: str,
        app_name: str,
        namespace: str,
        service_information_list: list,
    ) -> list[dict]:
        """
        Create a list of services for publish_information_list.
        :params:
            service_name: str: The main name of the service.
                               We will create service_name_1, service_name_2,...and so on.
            app_name: str: The app to link the service to.
            namespace: str: The namespace where the services will live.
            publish_information_list: list:
                    [{'service_port': <int>, 'target_port': <int>, 'protocol': <str>}, ...]
        :returns: [
            {
                "service_id": service.metadata.uid,
                "service_ip": service._spec.cluster_ip,
                "service_name": service.metadata.name,
                "service_namespace": namespace,
                "service_port": service_port,
            },
            {
                "service_id": service.metadata.uid,
                "service_ip": service._spec.cluster_ip,
                "service_name": service.metadata.name,
                "service_namespace": namespace,
                "service_port": service_port,
            },
            ....
        ]

        Author: Namah Shrestha
        """
        try:
            cls.check_client()
            service_list: list = []
            for index, item in enumerate(service_information_list):
                service_list.append(
                    cls.create_service(
                        service_name=f"{service_name}-{index}",
                        app_name=app_name,
                        namespace=namespace,
                        service_port=item["service_port"],
                        target_port=item["target_port"],
                        protocol=item["protocol"],
                    )
                )
            return service_list
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def extract_publish_information(self, publish_information: dict) -> tuple[set, list[dict]]:
        """
        Extract unique target ports and service related information from
        publish_information.
        :params:
            publish_information: dict: {'<containerport>/<protocol>': <hostport>, ...}
        :returns:
            (target_ports: set, service_information_list: list[dict])

        Author: Namah Shrestha
        """
        unique_target_ports: set = set()
        service_information_list: list[dict] = []
        for target_port_name, service_port in publish_information.items():
            target_port, protocol = target_port_name.split("/")
            unique_target_ports.add(int(target_port))
            service_information_list.append(
                {
                    "service_port": service_port,
                    "target_port": int(target_port),
                    "protocol": protocol.upper(),
                }
            )
        return unique_target_ports, service_information_list

    def create_container(self) -> list[dict]:
        """
        Create a kubernetes container based on all the parameters.
        - Check client
        - Extract unique_target_ports and service_information from self.publish_information.
        - Extract environment, Use target_ports, container_name, image_name, namespace name
            to create the pod.
        - Use service_information_list to create services for the pod.

        returns: list[dict]:
            [
                {
                    'container_id': <container_id>,
                    'container_network': <container_network>,
                    'container_port': <container_port> | None,
                },
                {
                    'container_id': <container_id>,
                    'container_network': <container_network>,
                    'container_port': <container_port> | None,
                },
                ...
            ]

        Author: Namah Shrestha
        """
        try:
            self.check_client()
            unique_target_ports, service_information_list = self.extract_publish_information(
                publish_information=self.publish_information
            )

            # create environment variable list
            env_list: list = [
                kcli.V1EnvVar(name=name, value=value)
                for name, value in self.environment.items()
            ]
            # create target port list
            target_port_list: list = [
                kcli.V1ContainerPort(container_port=target_port)
                for target_port in unique_target_ports
            ]

            # create pod manifest
            pod_manifest: kcli.V1Pod = kcli.V1Pod(
                metadata=kcli.V1ObjectMeta(name=self.container_name),
                spec=kcli.V1PodSpec(
                    containers=[
                        kcli.V1Container(
                            name=self.container_name,
                            image=self.image_name,
                            ports=target_port_list,
                            env=env_list,
                        )
                    ]
                )
            )

            # create the namespace
            self.create_namespace(namespace_name=self.container_network)
            # Create the Pod in the namespace
            pod: kcli.V1Pod = self.client.create_namespaced_pod(self.container_network, pod_manifest)
            # Create the services for the Pod
            services_list: list[dict] = self.create_services_for_app(
                service_name=f"{self.container_name}-service",
                app_name=self.container_name,
                namespace=self.container_network,
                service_information_list=service_information_list,
            )
            # if services are not available then return pod id otherwise return service id
            if services_list:
                return [
                    {
                        'container_id': service['service_id'],
                        'container_network': service['service_namespace'],
                        'container_port': service['service_port'],
                    }
                    for service in services_list
                ]
            else:
                # here we will not give back port.
                # Because, no publish information has been provided.
                # This means, the user did not intend to have exposed ports.
                return [
                    {
                        "container_id": pod.metadata.uid,
                        "container_network": pod.metadata.namespace,
                        "container_port": None,
                    }
                ]
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def start_container(cls, container_ids: list[str], container_network: str) -> list[dict]:
        '''
        Start the containers based on parameters.
        In kubernetes, the containers are already started from the create method.
        All we need to do, here is obtain the ip address and return it.
        The thing here is, the container_ids are either pods or services.
        We need to figure that out first and then get their ip addresses.

        :params:
            :container_ids: list[str]: List of container ids to start.
            :container_network: str: Name of the network in which
                                     the container is deployed in.
                                     In case of kubernetes, this is the namespace.
        :returns: list[dict]:
            [
                {'container_id': <container_id>, 'container_ip': <container_ip_address>},
                {'container_id': <container_id>, 'container_ip': <container_ip_address>},
                ...
            ]
        Author: Namah Shrestha
        '''
        try:
            # Get Pod IDs in the namespace
            pod_list = cls.client.list_namespaced_pod(namespace=container_network)
            pod_ids: list = []
            pod_ids_ip_map: dict = {}
            for pod in pod_list.items:
                pod_ids.append(pod.metadata.uid)
                pod_ids_ip_map[pod.metadata.uid] = pod.status.pod_ip

            # Get Service IDs in the namespace
            service_list = cls.client.list_namespaced_service(namespace=container_network)
            service_ids: list = []
            service_ids_ip_map: dict = {}
            for service in service_list.items:
                service_ids.append(service.metadata.uid)
                service_ids_ip_map[service.metadata.uid] = service.spec.cluster_ip

            start_container_results: list[dict] = []
            for container_id in container_ids:
                if container_id in pod_ids:
                    start_container_results.append(
                        {
                            'container_id': container_id,
                            'container_ip': pod_ids_ip_map[container_id],
                        }
                    )
                elif container_id in service_ids:
                    start_container_results.append(
                        {
                            'container_id': container_id,
                            'container_ip': service_ids_ip_map[container_id],
                        }
                    )
            return start_container_results
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def stop_container(cls, container_ids: list[str], container_network: str) -> list[dict]:
        """
        Stop the container based on the parameters.
        The container needs to be created for the id to exist.
        So this method only works if the container is created.
        Will raise errors if the container is not started.
        :params:
            :container_ids: list[str]: List of container ids.
            :container_network: str: Network of the container
        :returns: list[dict]:
            [
                {'container_id': <container_id>, 'container_network': <container_network> ,"status": "deleted"},
                {'container_id': <container_id>, 'container_network': <container_network> ,"status": "deleted"},
                ...
            ]
        NOTE: Stop is not supported in kubernetes. It calls `delete_container`.
    
        Author: Namah Shrestha
        """
        try:
            return cls.delete_container(
                container_ids=container_ids,
                container_network=container_network,
            )
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)
        except Exception as e:
            raise Exception(e)

    @classmethod
    def get_pods_for_service(cls, service_name: str, namespace: str) -> list[str]:
        """
        Get all the pods for a service.
        :params:
            :service_name: str: Service name.
            :namespace: str: Namespace of the service.
        :returns:
            list[str]: names of pods associated with the service.

        Author: Namah Shrestha
        """
        try:
            endpoints = cls.client.list_namespaced_endpoints(namespace=namespace)
            for endpoint in endpoints.items:
                if endpoint.metadata.name == service_name:
                    pods: list = []
                    for subset in endpoint.subsets:
                        for address in subset.addresses:
                            pods.append(address.target_ref.name)
                    return pods
            return []
        except Exception as e:
            print(f"Error: {str(e)}")
            return []

    @classmethod
    def delete_container(cls, container_ids: list[str], container_network: str) -> list[dict]:
        """
        Delete the container based on the parameters.
        The container needs to be created for the id to exist.
        So this method only works if the container is created.
        Will raise errors if the container is not started.

        In kubernetes, container_ids can mean either pod or service.
        - If pod, delete pod.
        - If service, then delete service as well as associated pods.
        :params:
            :container_ids: list[str]: List of container ids.
            :container_network: str: Network of the container
        :returns: list[dict]:
            [
                {'container_id': <container_id>, 'container_network': <container_network> ,"status": "deleted"},
                {'container_id': <container_id>, 'container_network': <container_network> ,"status": "deleted"},
                ...
            ]

        Author: Namah Shrestha
        """
        try:
            # Get Pod IDs in the namespace
            pod_list = cls.client.list_namespaced_pod(namespace=container_network)
            pod_ids: list = []
            pod_ids_name_map: dict = {}
            for pod in pod_list.items:
                pod_ids.append(pod.metadata.uid)
                pod_ids_name_map[pod.metadata.uid] = pod.metadata.name

            # Get Service IDs in the namespace
            service_list = cls.client.list_namespaced_service(namespace=container_network)
            service_ids: list = []
            service_ids_name_map: dict = {}
            for service in service_list.items:
                service_ids.append(service.metadata.uid)
                service_ids_name_map[service.metadata.uid] = service.metadata.name
            
            delete_container_results: list = []
            pods_to_delete: set = set()
            services_to_delete: set = set()
            for container_id in container_ids:
                if container_id in pod_ids:
                    # If we are getting pod ids it means we dont have services.
                    # So just delete the pod and thats it.
                    # Put it on the list of pods to delete.
                    pod_name: str = pod_ids_name_map[container_id]
                    pods_to_delete.add((pod_name, container_id))
                elif container_id in service_ids:
                    # Get associated pods and put them on the list of pods to delete.
                    # Put the service name on services to be deleted.
                    service_name: str = service_ids_name_map[container_id]
                    services_to_delete.add((service_name, container_id))
                    pod_names: list = cls.get_pods_for_service(
                        service_name=service_name,
                        namespace=container_network,
                    )
                    for pod_name in pod_names:
                        pods_to_delete.add((pod_name, container_id))

            # delete all the pods
            for pod_to_delete in pods_to_delete:
                cls.client.delete_namespaced_pod(name=pod_to_delete[0], namespace=container_network)
                delete_container_results.append(
                    {
                        "container_id": pod_to_delete[1],
                        "container_network": container_network,
                        "status": "deleted pod"
                    }
                )
            # delete all the services
            for service_to_delete in services_to_delete:
                cls.client.delete_namespaced_service(name=service_to_delete[0], namespace=container_network)
                delete_container_results.append(
                    {
                        "container_id": pod_to_delete[1],
                        "container_network": container_network,
                        "status": "deleted service"
                    }
                )
            return delete_container_results
        except k8s_rest.ApiException as ka:
            raise k8s_rest.ApiException(ka)
        except exceptions.ContainerClientNotResolved as ccnr:
            raise exceptions.ContainerClientNotResolved(ccnr)
        except Exception as e:
            raise Exception(e)


ENV_CONTAINER_MGR_MAPPING: dict = {
    "docker": DockerContainerManager,
    "kubernetes": KubernetesContainerManager,
}
