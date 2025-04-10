# SeaRobotics Surveyor Client API Documentation

This document provides an overview of the `BaseClient` and its derived classes (`CameraClient`, `LidarClient`, and `Exo2Client`) used for interacting with various server endpoints. These classes are designed to provide a unified interface for connecting to and retrieving data from different types of servers.

---

## Table of Contents

1. [BaseClient](#baseclient)
2. [CameraClient](#cameraclient)
3. [LidarClient](#lidarclient)
4. [Exo2Client](#exo2client)
5. [Creating Your Own Client](#creating-your-own-client)

---

## BaseClient

### Description
`BaseClient` is an abstract base class that defines the structure for all client classes. It provides a template for connecting to a server and retrieving data.

### Attributes
- `server_ip (str)`: IP address of the server.
- `server_port (int)`: Port number of the server.
- `server_url (str)`: URL constructed from the server IP and port.

### Methods
#### `__init__(server_ip: str, server_port: int)`
Initializes the base client.

**Arguments:**
- `server_ip (str)`: IP address of the server.
- `server_port (int)`: Port number of the server.

#### `connect()`
Establishes a connection to the server.

**Raises:**
- `NotImplementedError`: If the method is not implemented in the subclass.

#### `get_data()`
Retrieves data from the server.

**Raises:**
- `NotImplementedError`: If the method is not implemented in the subclass.

---

## CameraClient

### Description
`CameraClient` is a client for receiving video streams from a camera server.

### Attributes
- `server_ip (str)`: IP address of the server.
- `server_port (int)`: Port number of the server.
- `server_url (str)`: URL of the video feed provided by the server.
- `cap (cv2.VideoCapture)`: OpenCV VideoCapture object for capturing frames.
- `_current_frame (numpy.ndarray)`: The current frame captured from the video stream.
- `_frame_thread (threading.Thread)`: Thread that continuously updates the current frame.

### Methods
#### `__init__(server_ip="192.168.0.20", server_port=5001)`
Initializes a `CameraClient` object.

**Arguments:**
- `server_ip (str)`: IP address of the server.
- `server_port (int)`: Port number of the server.

#### `get_image()`
Retrieves the most recent frame from the video stream.

**Returns:**
- `tuple`: A tuple containing a boolean indicating success and the frame itself.

---

## LidarClient

### Description
`LidarClient` is a client for receiving lidar data from a lidar server.

### Attributes
- `server_ip (str)`: IP address of the server.
- `server_port (int)`: Port number of the server.
- `server_url (str)`: URL of the lidar data feed provided by the server.
- `_angles (list)`: List of angles (0-359 degrees) corresponding to lidar measurements.

### Methods
#### `__init__(server_ip="192.168.0.20", server_port=5002)`
Initializes a `LidarClient` object.

**Arguments:**
- `server_ip (str)`: IP address of the server.
- `server_port (int)`: Port number of the server.

#### `get_data()`
Retrieves the lidar measurements.

**Returns:**
- `tuple`: A tuple containing a list of distances and a list of angles, or `None` if the data could not be fetched.

---

## Exo2Client

### Description
`Exo2Client` is a client for interacting with the Exo2 sensor server.

### Attributes
- `server_ip (str)`: IP address of the server.
- `server_port (int)`: Port number of the server.
- `server_url (str)`: URL of the Exo2 data feed provided by the server.
- `exo2_params (dict)`: Dictionary mapping parameter IDs to their names.

### Methods
#### `__init__(server_ip="192.168.0.68", server_port=5000)`
Initializes an `Exo2Client` object.

**Arguments:**
- `server_ip (str)`: IP address of the server.
- `server_port (int)`: Port number of the server.

#### `get_data()`
Retrieves data from the Exo2 sensor.

**Returns:**
- `dict`: A dictionary mapping parameter names to their values.

#### `get_data_from_command(command: str)`
Sends a command to the server and retrieves the response.

**Arguments:**
- `command (str)`: The command to send.

**Returns:**
- `str`: The server's response.

#### `get_exo2_params()`
Retrieves the Exo2 sensor parameters.

**Returns:**
- `dict`: A dictionary mapping parameter IDs to their names.

#### `initialize_server_serial_connection()`
Initializes the serial connection on the server.

---

## Creating Your Own Client

To create a new client class, follow these steps:

1. **Inherit from `BaseClient`:**
   Create a new class that inherits from `BaseClient`.

2. **Implement the `connect` and `get_data` methods:**
   These methods must be implemented to define how the client connects to the server and retrieves data.

3. **Add any additional functionality:**
   Include any attributes or methods specific to your client.

### Example
```python
from base_client import BaseClient

class CustomClient(BaseClient):
    """
    CustomClient class for interacting with a custom server.

    Arguments:
        server_ip (str): IP address of the server.
        server_port (int): Port number of the server.
    """

    def __init__(self, server_ip, server_port):
        super().__init__(server_ip, server_port)
        self.server_url += "/custom_endpoint"

    def connect(self):
        """
        Establishes a connection to the custom server.
        """
        print(f"Connecting to {self.server_url}...")

    def get_data(self):
        """
        Retrieves data from the custom server.

        Returns:
            str: The data retrieved from the server.
        """
        # Example implementation
        return "Custom data"