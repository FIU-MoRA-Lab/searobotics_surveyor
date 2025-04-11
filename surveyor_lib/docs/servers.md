# SeaRobotics Surveyor Server Documentation

This document provides an overview of the `Exo2Server`, `CameraServer`, and `LidarServer` implementations. These servers are designed to interface with their respective sensors and provide data or streams to clients via HTTP endpoints.

---

## Table of Contents

1. [Exo2Server](#exo2server)
2. [CameraServer](#cameraserver)
3. [LidarServer](#lidarserver)

---

## Exo2Server

### Description
The `Exo2Server` provides an interface to communicate with the Exo2 sensor via a serial connection. It supports sending commands to the sensor and retrieving data.

### Endpoints

#### `GET /data`
Fetches data from the Exo2 sensor.

**Response:**
- `200 OK`: Returns the data from the Exo2 sensor as plain text.
- `500 Internal Server Error`: If there is an issue with the serial connection.

#### `POST /data`
Sends a command to the Exo2 sensor and retrieves the response.

**Request Body:**
- `command (str)`: The command to send to the Exo2 sensor.

**Response:**
- `200 OK`: Returns the response from the Exo2 sensor.
- `500 Internal Server Error`: If there is an issue with the serial connection.

---

### Configuration

The server can be configured using command-line arguments:

- `--port`: Port number for the server (default: `5000`).
- `--com_port`: Serial port for the Exo2 sensor (default: `COM4` for Windows, `/dev/ttyUSB1` for Linux).
- `--baud_rate`: Baud rate for the serial connection (default: `9600`).
- `--timeout`: Timeout for the serial connection in seconds (default: `0.1`).

---

## CameraServer

### Description
The `CameraServer` provides a video stream from a connected camera (e.g., PiCamera or USB camera) via HTTP.

### Endpoints

#### `GET /`
Displays a message indicating that the camera stream is online.

**Response:**
- `200 OK`: Returns a plain text message.

#### `GET /video_feed`
Provides an MJPEG video stream from the camera.

**Response:**
- `200 OK`: Returns a multipart MJPEG stream.
- `500 Internal Server Error`: If there is an issue with the camera.

---

### Configuration

The server can be configured using command-line arguments:

- `--host`: Host IP address for the server (default: `192.168.0.20`).
- `--port`: Port number for the server (default: `5001`).
- `--camera_source_type`: Camera source type (`picamera` or `usb`, default: `picamera`).
- `--image_width`: Width of the video frames (default: `800`).
- `--image_height`: Height of the video frames (default: `600`).

---

## LidarServer

### Description
The `LidarServer` provides data and a visual representation of the Lidar sensor's measurements via HTTP. It supports both raw data retrieval and an MJPEG stream of the Lidar plot.

### Endpoints

#### `GET /`
Displays a message indicating that the Lidar stream is online.

**Response:**
- `200 OK`: Returns a plain text message.

#### `GET /video_feed`
Provides an MJPEG video stream of the Lidar plot.

**Response:**
- `200 OK`: Returns a multipart MJPEG stream.
- `500 Internal Server Error`: If there is an issue with the Lidar sensor.

#### `GET /data`
Fetches raw Lidar data as JSON.

**Response:**
- `200 OK`: Returns the raw Lidar data as a JSON object.
- `500 Internal Server Error`: If there is an issue with the Lidar sensor.

---

### Configuration

The server can be configured using command-line arguments:

- `--host`: Host IP address for the server (default: `192.168.0.20`).
- `--port`: Port number for the server (default: `5002`).
- `--lidar_port`: Serial port for the Lidar device (default: `/dev/ttyUSB0`).
- `--baudrate`: Baud rate for the Lidar communication (default: `1000000`).
- `--n`: Number of elements to average for data processing (default: `1`).
- `--lim`: Maximum range for the Lidar plot in meters (default: `3.0`).
- `--op_angle`: Opening angle for the Lidar plot in degrees (default: `120`).
- `--safety_dist`: Safety threshold distance in meters (default: `2.0`).

---

## Creating a New Server for a Sensor

### Overview
To create a new server for a sensor, you can use Flask to handle HTTP requests and responses. Flask provides a lightweight and flexible framework for building RESTful APIs, making it ideal for sensor servers.

### Steps to Create a New Server

1. **Set Up Flask:**
   Import Flask and initialize the app.

    ```python
    from flask import Flask, jsonify, request

    app = Flask(__name__)
    ```

2. **Initialize the Sensor:**
   Create a function to initialize the sensor. This could involve setting up a serial connection, opening a video stream, or initializing hardware-specific libraries.

    ```python
    def initialize_sensor():
        # Example: Initialize a serial connection
        print("Initializing sensor...")
        # Add sensor-specific initialization logic here
    ```

3. **Define Endpoints:**
   Add endpoints for interacting with the sensor. Common endpoints include:
   - `/data`: To fetch data from the sensor.
   - `/command`: To send commands to the sensor.

    ```python
    @app.route("/data", methods=["GET"])
    def get_data():
        # Fetch data from the sensor
        data = {"example_key": "example_value"}  # Replace with actual sensor data
        return jsonify(data)

    @app.route("/command", methods=["POST"])
    def send_command():
        # Send a command to the sensor
        command = request.data.decode("utf-8")
        response = {"command_received": command}
        return jsonify(response)
    ```

4. **Add Error Handling:**
   Ensure the server handles errors gracefully, such as hardware disconnections or invalid requests.

   ```python
   @app.errorhandler(500)
   def handle_internal_error(error):
       return jsonify({"error": "Internal Server Error"}), 500
   ```

5. **Run the Server:**
   Use Flask's `app.run()` to start the server.

   ```python
   if __name__ == "__main__":
       initialize_sensor()
       app.run(host="0.0.0.0", port=5000)
   ```

### Example: Creating a Temperature Sensor Server

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

# Simulated temperature sensor data
TEMPERATURE_DATA = {"temperature": 25.0}


def initialize_sensor():
    """
    Simulate initializing a temperature sensor.
    """
    print("Temperature sensor initialized.")


@app.route("/data", methods=["GET"])
def get_temperature():
    """
    Fetch the current temperature from the sensor.

    Returns:
        Response: JSON object containing the temperature data.
    """
    return jsonify(TEMPERATURE_DATA)


@app.route("/command", methods=["POST"])
def set_temperature():
    """
    Simulate setting a new temperature value.

    Returns:
        Response: JSON object confirming the new temperature value.
    """
    global TEMPERATURE_DATA
    new_temperature = request.json.get("temperature")
    if new_temperature is not None:
        TEMPERATURE_DATA["temperature"] = new_temperature
        return jsonify({"message": "Temperature updated", "new_temperature": new_temperature})
    else:
        return jsonify({"error": "Invalid temperature value"}), 400


if __name__ == "__main__":
    initialize_sensor()
    app.run(host="0.0.0.0", port=5003)
```

### Testing the New Server

1. **Start the Server:**
   Run the script to start the server.

   ```bash
   python temperature_server.py
   ```

2. **Fetch Data:**
   Use `curl` or a browser to fetch the temperature data.

   ```bash
   curl http://localhost:5003/data
   ```

3. **Send a Command:**
   Use `curl` to send a new temperature value.

   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"temperature": 30.5}' http://localhost:5003/command
   ```

By following these steps, you can create a new Flask-based server for any sensor, ensuring consistency and modularity across your project.


## Notes

- All servers are designed to be self-contained and can be started independently.
- Ensure that the respective hardware (e.g., Exo2 sensor, camera, Lidar) is properly connected and configured before starting the servers.
- Use the provided endpoints to interact with the servers and retrieve data or streams.