# modules
import tests.system_tests.test_system as ts
# third-party
import docker


class TestSystem(ts.TestSystem):
    """
    Test APIs responses for docker.

    Use docker related commands to test and see if the
    docker environment is getting affected in the way it should.

    NOTE: For this test suite to run, the application needs
    to be running inside docker

    Author: Namah Shrestha
    """
    def setUp(self) -> None:
        """
        Get the runtime
        """
        pass

    def test_create_container(self) -> None:
        """
        Get the runtime envi
        """
        pass