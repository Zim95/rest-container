# builtins
import requests
import unittest


class TestSystem(unittest.TestCase):
    """
    Test APIs responses. The APIs will automatically call
    the associated containermanager methods.
    Our job is to only test the response.

    Our asserts will need to use different APIs based on
    the runtime environment.
    Therefore, we need to create different methods to check the status
    of each supported runtime. 

    NOTE: For this test suite to run, the application
    needs to be running inside one of the supported
    runtime environments.

    Author: Namah Shrestha
    """
    def setUp(self) -> None:
        """
        Get the runtime.
        
        """
        pass

    def test_create_container(self) -> None:
        """
        Make a create container request and assert the response.

        Author: Namah Shrestha
        """
        pass