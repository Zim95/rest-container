# third party
import flask
# builtins
import typing
import os
# modules
import src.handlers as handlers
import src.exceptions as exceptions


HANDLERS_MAP: dict = {
    "create": handlers.CreateContainerHandler,
    "start": handlers.StartContainerHandler,
    "stop": handlers.StopContainerHandler,
    "delete": handlers.DeleteContainerHandler,
    "ping": handlers.PingHandler,
}


class Controller:
    """
    Controls the route logic.
    1. Extracts request data.
    2. Sends the request data to appropriate handler methods
        based on route.
    3. Returns the response of the handler.
    4. Handles exceptions.

    Author: Namah Shrestha
    """

    def get_request_params(self, **kwargs: dict) -> dict:
        """
        Extract all request data.

        Author: Namah Shrestha
        """
        request_params: dict = {
            "query_params": dict(flask.request.args),
            "headers": dict(flask.request.headers),
            "payload": flask.request.data.decode("utf-8"),
            "form_data": dict(flask.request.form),
            "view_args": kwargs,
        }
        return request_params

    def get_runtime_environment(self) -> str:
        if "DOCKER_HOST" in os.environ:
            return "docker"
        elif "KUBERNETES_SERVICE_HOST" in os.environ:
            return "kubernetes"

    def handle(self, **kwargs: dict) -> typing.Any:
        """
        1. Sends the request data to appropriate handler methods
            based on route.
        2. Returns the response of the handler.
        3. Handles exceptions.
        4. Makes sure that only docker requests are accepted in docker environment
            and only kubernetes requests are accepted in kubernetes environment
        Author: Namah Shrestha
        """
        try:
            request_params: dict = self.get_request_params(**kwargs)
            runtime_environment: str = self.get_runtime_environment()
            container_environment: str = self.request_params[
                "view_args"].get("cnenv", "")
            if runtime_environment != container_environment:
                environment_mismatch: str = (
                    f"Runtime Environment is: {runtime_environment}. "
                    f"Requests is made for: {container_environment}. "
                    f"Please make sure the environments match. "
                )
                raise exceptions.EnvironmentMismatch(environment_mismatch)
            handler_name: str = flask.request.path
            if handler_name != "/":
                handler_name: str = handler_name.split("/")[1]
            handler: handlers.Handler = HANDLERS_MAP.get(
                handler_name, None
            )
            if not handler:
                return flask.jsonify(
                    {
                        "error": f"Invalid route: {handler_name}"
                    }
                ), 404
            return flask.jsonify(
                {
                    "response": handler(
                        request_params=request_params).handle()
                }
            ), 200
        except Exception as e:
            return flask.jsonify(
                {
                    "error": f"Internal Server Error: {e}"
                }
            ), 500
