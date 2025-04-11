import numpy as np

from surveyor_lib.surveyor import Surveyor


class MockSurveyor(Surveyor):
    """
    MockSurveyor class that mimics the Surveyor class for testing purposes.
    It overrides methods to provide mock data instead of interacting with real hardware or servers.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the MockSurveyor object.
        Inherits all attributes from the Surveyor class but overrides specific methods for testing.
        """
        kwargs["host"] = "localhost"
        kwargs["port"] = 1234
        kwargs["sensors_to_use"] = []
        super().__init__(*args, **kwargs)

    def get_state(self):
        """
        Mock implementation of the get_state method.

        Returns:
            dict: A mock state dictionary.
        """
        return {
            "Latitude": 26.0,
            "Longitude": -81.0,
            "Control Mode": "autonomous",
        }

    def get_exo2_data(self):
        """
        Mock implementation of the get_exo2_data method.

        Returns:
            dict: A dictionary with mock EXO2 sensor data.
        """
        return {
            "Temperature (C)": 25.0,
            "pH": 7.5,
            "Conductivity (mS/cm)": 1.2,
        }

    def get_image(self):
        """
        Mock implementation of the get_image method.

        Returns:
            tuple: A tuple containing a boolean indicating success and a mock image (numpy array).
        """
        mock_image = np.random.randint(0, 255, (64, 128, 3), dtype=np.uint8)
        return True, mock_image

    def get_lidar_data(self):
        """
        Mock implementation of the get_lidar_data method.

        Returns:
            tuple: A tuple containing mock Lidar distances and angles.
        """
        mock_distances = (
            np.random.rand(360).astype(np.float32) * 3.0
        )  # Random distances up to 3 meters
        mock_angles = np.linspace(
            0, 360, 360, dtype=np.float32
        )  # Angles from 0 to 360 degrees
        return mock_distances, mock_angles

    def send(self, msg):
        """
        Mock implementation of the send method.
        Logs the message instead of sending it to a real server.

        Args:
            msg (str): The message to be sent.
        """
        print(f"[Mock Send] {msg}")

    def receive(self, bytes=2048):
        """
        Mock implementation of the receive method.
        Yields mock NMEA messages instead of receiving data from a real server.

        Args:
            bytes (int, optional): The maximum number of bytes to receive. Default is 2048.

        Yields:
            str: Mock NMEA messages.
        """
        mock_messages = [
            "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47",
            "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A",
            "$GPGLL,4916.45,N,12311.12,W,225444,A,*1D",
        ]
        for message in mock_messages:
            yield message

    def _save_data_continuously(self):
        """
        Mock implementation of the _save_data_continuously method.
        Logs a message instead of saving data to a file.
        """
        print("[Mock Save Data] Continuous data logging simulated.")

    def get_data(self, keys=None):
        """
        Mock implementation of the get_data method.

        Args:
            keys (list, optional): A list of keys indicating the types of data to retrieve. Defaults to None.

        Returns:
            dict: A dictionary containing mock data for the specified keys.
        """
        keys = keys or ["state", "exo2", "camera", "lidar"]
        getter_functions = {
            "exo2": self.get_exo2_data,  # Dictionary with Exo2 sonde data
            "state": self.get_state,
            "camera": self.get_image,
            "lidar": self.get_lidar_data,
        }
        data_labels = {
            "camera": ["Image ret", "Image"],
            "lidar": ["Distances", "Angles"],
        }
        data_dict = {}

        # Iterate over specified keys and retrieve data using corresponding getter functions
        for key in keys:
            data = getter_functions[key]()
            if isinstance(data, float):
                data = [data]
            if not isinstance(data, dict):
                data = dict(zip(data_labels[key], data))
            data_dict.update(data)

        return data_dict
