class BaseClient:
    """
    Base class for all client classes to connect to a server and fetch data.

    Args:
        server_ip (str): IP address of the server.
        server_port (int): Port number of the server.
    """

    def __init__(self, server_ip: str, server_port: int):
        """
        Initializes the base client.

        Args:
            server_ip (str): IP address of the server.
            server_port (int): Port number of the server.
        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_url = f"http://{server_ip}:{server_port}"

    def connect(self):
        """
        Establishes a connection to the server.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_data(self):
        """
        Retrieves data from the server.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        raise NotImplementedError("Subclasses must implement this method.")
