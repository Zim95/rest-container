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