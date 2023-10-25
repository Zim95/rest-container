class UnsupportedRuntimeEnvironment(Exception):
    """
    When unsupported container environment is provided.
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


class ContainerClientNotResolved(Exception):
    """
    When container client is None.
    This happens when methods of the wrong container manager are called.
    from a different runtime environment.
    """
    pass
