SUPPORTED_ENVIRONMENTS: list = ["docker", "kubernetes"]

BROWSETERM_IMAGE_NAME_MAPPING: dict = {
    "ubuntu": "zim95/ssh_ubuntu:latest"
}
BROWSETERM_DOCKER_NETWORK: str = "browseterm-rest-network"
