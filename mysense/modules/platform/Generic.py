from core.modules import PlatformModule

class Generic(PlatformModule):
    """
    This is a generic platform class.
    It's main purpose is to be able to run the application code on more platforms for testing.
    """

    def __init__(self):
        pass

    def is_run_tests(self):
        return True

    def test(self):
        pass

    def get_config_definition():
        return None
