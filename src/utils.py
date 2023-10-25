"""
Utility tools for the RestContainer.

Author: Namah Shrestha
"""

import os


def get_runtime_environment() -> str:
    """
    Get the runtime environment for the container.
    Right now, kubernetes and docker is supported.

    Reference: https://www.youtube.com/watch?v=mEQXXhniBQo

    Author: Namah Shrestha
    """
    if os.path.exists('/.dockerenv'):
        return "docker"
    elif os.environ.get("KUBERNETES_SERVICE_HOST"):
        return "kubernetes"
    else:
        return "unknown"
