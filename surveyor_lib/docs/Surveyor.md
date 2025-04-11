# `surveyor_lib.Surveyor` Class Documentation

A class for managing the Sea Robotics Surveyor ASV, supporting client connections for various sensors and control modes.

---

## Constructor

### `__init__(...)`
Initialize the `Surveyor` object with configuration for sensors and server.

#### Arguments:
- `host` (`str`): Server IP address (default: `192.168.0.50`).
- `port` (`int`): Server port (default: `8003`).
- `sensors_to_use` (`list[str]`): Sensors to initialize (`exo2`, `camera`, `lidar`). Defaults to `["exo2", "camera", "lidar"]`.
- `sensors_config` (`dict`): Sensor-specific configuration dicts. Defaults to:
  ```python
  {
      "exo2": {"exo2_server_ip": "192.168.0.68", "exo2_server_port": 5000},
      "camera": {"camera_server_ip": "192.168.0.20", "camera_server_port": 5001},
      "lidar": {"lidar_server_ip": "192.168.0.20", "lidar_server_port": 5002},
  }
  ```
- `record` (`bool`): Whether to start a recording boat's data into a HDF5 file. It records the state plus the sensors tated in `sensors_to_use`
- `record_rate` (`int`): Record frequency in Hz (default: `1`)
- `logger_level` (`logging.LEVEL`): Logging level

---

## Attributes
### Public Attributes

These attributes are accessible externally and relevant for configuration or interaction:

- `host` (`str`, default=`"192.168.0.50"`):
IP address of the main server to connect to.

- `port` (`int`, default=`8003`):
Port number of the main server.

- `exo2` (`Exo2Client`):
Client for interacting with the EXO2 sensor. Only set if "exo2" is in sensors_to_use.

- `camera` (`CameraClient`):
Client for interacting with the camera sensor. Only set if "camera" is in sensors_to_use.

- `lidar` (`LidarClient`):
Client for interacting with the LiDAR sensor. Only set if "lidar" is in sensors_to_use.

- `record` (`bool`, default=`True`):
Whether the system is actively recording sensor data.

- `socket` (`socket.socket`):
TCP socket used to communicate with the main server. Set in __enter__.

### Private/Protected Attributes

These attributes are used internally for synchronization, logging, and threading (**DO NOT call or change them during execution**):

`_state` (`dict`, default=`{}`):
Dictionary storing the most recent state information from sensors and server messages.

`_parallel_update` (`bool`, default=`True`):
Flag indicating whether the update loop should continue running in a separate thread.

`_logger` (`logging.Logger`, default=`surveyor_lib.helpers.logger.HELPER_LOGGER` with level `logger_level`):
Logger instance used for internal debugging and tracking.

`_receive_and_update_thread` (`threading.Thread`):
Background thread receiving and processing updates from the server. Set in `__enter__`.

`_recording_thread` (`threading.Thread`):
Background thread saving data periodically. Only set if record=True. Created in `__enter__`.

---


## Context Manager Methods

### `__enter__()`
Start socket connection and background threads for updates and recording.

### `__exit__(exc_type, exc_value, traceback)`
Stop update/recording threads and close connection.

### `send(msg)`
Send an NMEA message to the remote server.

- **Arguments**:
  - `msg` (`str`): The NMEA message to be sent.
- **Raises**:
  - `socket.error`: If an error occurs while sending the message.

### `receive(bytes=2048)`
Receive data from the remote server.

- **Arguments**:
  - `bytes` (`int`, optional): Maximum number of bytes to receive. Default is `2048`.
- **Returns**:
  - `str`: The received data as a UTF-8 string.
- **Raises**:
  - `ConnectionError`: If the connection is closed by the remote server.
  - `socket.timeout`: If the socket times out while receiving data.
  - `socket.error`: If an error occurs while receiving data.

### `_receive_and_update()`
Internal method to continuously receive and update the state in parallel while `_parallel_update` is `True`.

### `_save_data_continuously()`
Internal method to save sensor and state data continuously to disk. Saves:
- Data to HDF5: State + sensors used.

Triggered while `self.record` is `True`.

### `set_standby_mode()`
Send a command to set the ASV into standby mode.

### `set_thruster_mode(thrust, thrust_diff, delay=0.05)`
Set the ASV to thruster mode with thrust control.

- **Arguments**:
  - `thrust` (`int`): Thrust value [-70, 70].
  - `thrust_diff` (`int`): Differential thrust [-70, 70].
  - `delay` (`float`, optional): Delay after sending the command. Default is `0.05` seconds.

### `set_station_keep_mode()`
Set the ASV to station keeping mode.

### `set_heading_mode(thrust, degrees)`
Set the ASV to a heading mode with a target angle.

- **Arguments**:
  - `thrust` (`int`): Thrust value (>= 0).
  - `degrees` (`int`): Heading angle in degrees [0, 360].

### `set_waypoint_mode()`
Set the ASV to navigate toward the loaded waypoints.

### `set_erp_mode()`
Send command to navigate to the Emergency Recovery Point (ERP).

### `start_file_download_mode(num_lines)`
Start file download mode to send multiple NMEA commands.

- **Arguments**:
  - `num_lines` (`int`): Number of lines/commands to be sent.

### `end_file_download_mode()`
End file download mode after sending all NMEA commands.

### `set_control_mode(mode, **Arguments)`
Switch ASV to the specified control mode.

- **Arguments**:
  - `mode` (`str`): Control mode. Options:
    - `"Waypoint"`: `thrust` required.
    - `"Standby"`: No arguments.
    - `"Thruster"`: `thrust`, `thrust_diff`, `delay` required.
    - `"Heading"`: `thrust`, `degrees` required.
    - `"Go To ERP"`: No arguments.
    - `"Station Keep"`: No arguments.
    - `"Start File Download"`: `num_lines` required.
    - `"End File Download"`: No arguments.
  - `**Arguments`: Additional arguments based on mode.
- **Raises**:
  - `KeyError`: Missing required argument.
  - `Exception`: On unexpected error.

### `send_waypoints(waypoints, erp, throttle)`
Send a list of waypoints and ERP to the ASV for navigation.

- **Arguments**:
  - `waypoints` (`list` of `(lat, lon)` tuples): Waypoints to follow.
  - `erp` (`list` of `(lat, lon)` tuples): Emergency recovery point.
  - `throttle` (`float`): Throttle setting [0, 70].
- **Raises**:
  - `ValueError`: If no waypoints are provided.
  - `socket.error`: On network error.

### `go_to_waypoint(waypoint, erp, throttle, tolerance_meters=2.0)`
Send a waypoint and set ASV to go toward it.

- **Arguments**:
  - `waypoint` (`tuple`): Target GPS coordinates.
  - `erp` (`list`): Emergency Recovery Point coordinates.
  - `throttle` (`int`): Throttle value.
  - `tolerance_meters` (`float`, optional): Acceptance radius. Default is `2.0`.

### `get_state()`
Retrieve the current internal state of the ASV.

- **Returns**:
  - `dict`: Dictionary of current state variables.

### `get_control_mode()`
Get the current control mode of the ASV.

- **Returns**:
  - `str`: Control mode (or `"Unknown"` if not set).

### `get_gps_coordinates()`
Get the current GPS coordinates.

- **Returns**:
  - `tuple`: `(latitude, longitude)` in decimal degrees.

### `get_exo2_data()`
Fetch data from the connected EXO2 sensor.

- **Returns**:
  - `list`: List of sensor readings.


### `get_image()`
Capture a single frame from the connected camera.

- **Returns**:
  - `tuple`: `(ret, image)`, where `ret` is success flag and `image` is the captured frame.

### `get_lidar_data()`
Get LiDAR scan distances and corresponding angles.

- **Returns**:
  - `tuple`: `(distances, angles)` where:
    - `distances`: List of 360 distance readings.
    - `angles`: List of angles in degrees, 0 degrees is where the robot is ponting forward and the degrees are conted clockwise.

### `get_data(keys=None)`
Collect specified data sources. The possible keys are `"state"`, `"exo2"`, `"camera"`, `"lidar"`.

- **Arguments**:
  - `keys` (`list`, optional): Which data to collect. Default is `["state"] + 'sensors_to_use` i.e. state and the declared used sensors.
- **Returns**:
  - `dict`: Dictionary with sensor/state data by label.