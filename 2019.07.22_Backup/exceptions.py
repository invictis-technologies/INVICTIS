class Error(Exception):
    """Base class for exceptions in this module."""
    pass
    
class OutofBoundsError(Error):
    # Exception used to enforce boundary conditions
    def __init__(self, message):
        self.message = message

class InvalidResponseError(Error):
    # Exception verify responses from other programs
    def __init__(self, message):
        self.message = message

class ConnectionError(Error):
    # Exception used to verify connection to other programs
    def __init__(self, message):
        self.message = message
