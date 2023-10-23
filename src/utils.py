import os


def get_runtime_environment() -> str:
    if os.path.exists('/.dockerenv'):
        return "docker"
    else:
        return "unknown"