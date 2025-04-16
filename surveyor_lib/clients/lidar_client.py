import argparse
import sys

import requests

from .base_client import BaseClient


class LidarClient(BaseClient):
    """
    LidarClient class represents a client to receive video stream from a Lidar server.

    Args:
        server_ip (str): IP address of the server (default is "192.168.0.20").
        server_port (str): Port number of the server (default is "5002").
    """

    def __init__(
        self,
        server_ip="192.168.0.20",
        server_port="5002",
    ):
        """
        Initializes a LidarClient object.

        Attributes:
            server_ip (str): IP address of the server.
            server_port (str): Port number of the server.
            server_url (str): URL of the lidar data feed provided by the server.
        """
        super().__init__(server_ip, server_port)
        self.server_url += "/data"
        self._angles = list(range(0, 360))

    def get_data(self):
        """
        Retrieves the lidar measurements the lidar stream.

        Returns:
            list: A 360 list containing the lidar measurements (one per degree in clockwise sense) im meters or None if the data was not correclty fetched.
        """
        # Send a GET request to the Flask server
        response = requests.get(self.server_url)

        if response.status_code == 200:
            return response.json(), self._angles
        else:
            print(f"Failed to get RPLidar data: {response.status_code}")
            return None


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    # Create an ArgumentParser object
    print(f"Run {sys.argv[0]} -h  for help")
    parser = argparse.ArgumentParser(
        description="Client script for the Lidar."
    )

    # Add arguments
    parser.add_argument(
        "--host",
        type=str,
        default="192.168.0.20",
        help="IP address of the host (default: 192.168.0.20).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5002,
        help="Port number (default: 5002).",
    )

    # Parse the command line arguments
    args = vars(parser.parse_args())

    lidar_client = LidarClient(args["host"], args["port"])

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, polar=True)
    scatter = ax.scatter([], [], c="b", s=10)  # LIDAR trace
    ax.set_ylim(0, 2)  # Adjust max range to your LIDAR's range
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    angles = np.deg2rad(np.arange(0, 360, 1))
    while True:
        distances, _ = lidar_client.get_data()
        scatter.set_offsets(np.c_[angles, distances])  # Update the plot
        plt.draw()  # Refresh the plot
        plt.pause(0.01)
    plt.show()
