class UnsupportedContainerEnvironment(Exception):
    """
    When unsupported container environment is provided.
    """
    pass


class UnsupportedImageName(Exception):
    """
    When unsupported image name is provided.
    """
    pass


class ContainerManagerNotFound(Exception):
    """
    When environment is supported but container manager
    for that environment is not yet assigned.
    """
    pass


class ContainerIpUnresolved(Exception):
    """
    When container ip address cannot be resolved when starting a container.
    """
    pass


class EnvironmentMismatch(Exception):
    """
    When the requests are coming for a different container environment
    than the one in which the application is deployed on.

    For example:
        A /create/docker request is invalid if the application is deployed
        on kubernetes.
    """
    pass