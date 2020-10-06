import log

class NodeOutOfBounds(Exception):
    pass

class CannotFetchNode(Exception):
    """Exception raised for nodes that cannot be fetched (disallowed by robots.txt)

    Attributes:
        node_url -- url which caused the error
        message -- explanation of the error
    """

    def __init__(self, node_url, extra_message=""):
        self.node_url = node_url
        self.extra_message = extra_message
        super().__init__(self.extra_message)

    def __str__(self):
        return f'Node url ({self.node_url}) cannot be fetched. {self.extra_message}'
