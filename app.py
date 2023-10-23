# third party
import flask

# modules
import src.controller as cn
import src.utils as utils


# setup
app: flask.Flask = flask.Flask(__name__)
controller: cn.Controller = cn.Controller()

runtime_environment: str = utils.get_runtime_environment()
import logging
logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info(f"Runtime environment =======> {runtime_environment}")


# add routes
routes: list = [
    ("/ping", "ping", ["GET", "POST"]),
    ("/create/<string:cnenv>", "create", ["POST"]),
    ("/start/<string:cnenv>", "start", ["POST"]),
    ("/stop/<string:cnenv>", "stop", ["POST"]),
    ("/delete/<string:cnenv>", "delete", ["POST"]),
]
for route in routes:
    app.add_url_rule(route[0], route[1], controller.handle, methods=route[2])


if __name__ == "__main__":
    app.run("0.0.0.0", port=8002, debug=True)
