# Helpers Documentation
## 📚 Table of Contents
- [HDF5Logger](#HDF5Logger)
- [CSV Logging Utility Module](#csv-logging-utility-module)
- [Messages Utility Module](#messages-utility-module)
- [Waypiont Utility Module](#waypiont-utility-module)


## HDF5Logger

Logs structured data to an HDF5 file at regular intervals, either manually or continuously in the background.

---

## Class `surveyor_lib.helpers.HDF5Logger`

### Constructor
```python
HDF5Logger(filepath, data_getter_func, interval=1.0)
```

#### Parameters:
- **`filepath`** (`str`):  
  Path to the HDF5 file where data will be logged.

- **`data_getter_func`** (`Callable[[], dict]`):  
  Function returning a dictionary of data to be logged.

- **`interval`** (`float`, optional):  
  Time interval (in seconds) between logs during continuous logging. Default is `1.0`.

## Attributes

- **`filepath`** (`str`): Path to the HDF5 file.
- **`interval`** (`float`): Time interval for continuous logging.
- **`file`** (`h5py.File or None`): HDF5 file handle.
- **`thread`** (`threading.Thread or None`): Background logging thread.
- **`state_dtype`** (`np.dtype`): Structured dtype inferred from sample data.
- **`interval`** (`float`): Time interval (in seconds) between logs during continuous logging.

## Private Attributes
- **`_stopped`** (`bool`): Controls whether data is being recorded.
- **`_file`** (`h5py.File`): File handler, it keeps the file open.
- **`_thread`** (`h5py.File or None`): Separate thread calling `data_getter_func` and logging the received info.


## Methods

### `log_once()`
```python
log_once()
```
Logs a single data sample to the HDF5 file. Opens the file if not already open.

---

### `start_continuous_logging()`
```python
start_continuous_logging()
```
Starts a background thread that logs data continuously at the specified time interval.

---

### `stop()`
```python
stop()
```
Stops the background logging thread and closes the HDF5 file safely.

---

## Private/Internal Methods

### `_init_file()`
```python
_init_file()
```
Initializes a new HDF5 file with an extendable structured dataset if it doesn't already exist.

---

### `_infer_state_dtype(data_example_dict)`
```python
_infer_state_dtype(data_example_dict: dict) -> np.dtype
```

Infers a NumPy structured `dtype` from an example dictionary.

#### Parameters:
- **`data_example_dict`** (`dict`): Example data dictionary.

#### Returns:
- **`np.dtype`**: Structured dtype for use in the HDF5 dataset.

#### Raises:
- `TypeError`: If any value has an unsupported type.

---

### `_dict_to_structured_array(d)`
```python
_dict_to_structured_array(d: dict) -> np.ndarray
```

Converts a dictionary to a one-element structured NumPy array.

#### Parameters:
- **`d`** (`dict`): Dictionary with fields matching `state_dtype`.

#### Returns:
- **`np.ndarray`**: Structured array with shape `(1,)`.

---

### `_open_file()`
```python
_open_file() -> h5py.File
```

Opens the HDF5 file in append mode and caches the file handle.

#### Returns:
- **`h5py.File`**: Open HDF5 file handle.

---

### `_run_logger()`
```python
_run_logger()
```

Main loop for the background logging thread, repeatedly logging data and sleeping for the defined interval.

---

### `_normalize_types_for_hdf5(data_dict)`
```python
_normalize_types_for_hdf5(data_dict: dict) -> dict
```

Normalizes data for HDF5 compatibility.

#### Normalization Rules:
- Bools → `int`
- Strings → `np.str_`

#### Parameters:
- **`data_dict`** (`dict`): Original data dictionary.

#### Returns:
- **`dict`**: Normalized data dictionary.

---


## CSV Logging Utility Module 
`surveyor_lib.helpers.read_save_helper`

This module provides utility functions for logging and retrieving GPS and sensor data to and from CSV files. It is designed to support structured data collection workflows, particularly in field robotics or environmental monitoring tasks.

---

## Constants

### `DEFAULT_OUT_DIR_PATH`

- **Type**: `str`
- **Description**: The default path where CSV output files are stored. This path is relative to the module file location.

---

## Functions

### `append_to_csv(data, cols=["latitude", "longitude"], post_fix="", dir_path=None)`

Appends a row of data to a CSV file with a date-based filename.

- **Arguments**:
  - `data (list)`: The list of data values to append.
  - `cols (list, optional)`: Column headers for the CSV file. Default is `["latitude", "longitude"]`.
  - `post_fix (str, optional)`: Optional suffix for the filename. Default is `""`.
  - `dir_path (str, optional)`: Custom directory path for the file. Defaults to `DEFAULT_OUT_DIR_PATH`.

---

### `save(data, post_fix="", dir_path=None)`

Validates and appends a dictionary of data to a CSV file.

- **Arguments**:
  - `data (dict)`: Dictionary of sensor or GPS data.
  - `post_fix (str, optional)`: Suffix for the filename. Default is `""`.
  - `dir_path (str, optional)`: Custom directory path for the file.

---

### `process_gga_and_save_data(surveyor_connection, data_keys=None, post_fix="", delay=1.0, dir_path=None)`

Fetches GPS and sensor data from a surveyor connection and saves it to a CSV file, with a delay between samples to avoid duplication.

- **Arguments**:
  - `surveyor_connection`: Object that provides access to `get_data(keys)` method.
  - `data_keys (list, optional)`: Keys used to extract specific data. Default is `None` (refer to the `surveyor_lib.Surveyor.Surveyor.get_data` func).
  - `post_fix (str, optional)`: Suffix for the filename. Default is `""`.
  - `delay (float, optional)`: Minimum delay between samples. Default is `1.0`.
  - `dir_path (str, optional)`: Directory path to save CSV file.

- **Returns**:
  - `surveyor_data (dict)`: The collected data from the surveyor.

---

### `read_csv_into_tuples(filepath)`

Reads a CSV file and returns its content as a list of `(latitude, longitude)` tuples.

- **Arguments**:
  - `filepath (str)`: Path to the CSV file.

- **Returns**:
  - `list of tuples`: List of `(latitude, longitude)` tuples extracted from the file.

## Messages Utility Module
`surveyor_lib.helpers.surveyor_messages_helper `
## Messages Utility Module
`surveyor_lib.helpers.surveyor_messages_helper`

This module provides utility functions for processing and extracting information from NMEA messages and proprietary surveyor messages.

---

### Functions

#### `are_coordinates_close(coord1, coord2, tolerance_meters=2)`
Checks if two GPS coordinates are within a specified distance tolerance.

- **Arguments**:
    - `coord1 (tuple)`: First set of coordinates `(latitude, longitude)`.
    - `coord2 (tuple)`: Second set of coordinates `(latitude, longitude)`.
    - `tolerance_meters (float, optional)`: Maximum allowed distance in meters. Default is `2`.

- **Returns**:
    - `bool`: `True` if the coordinates are within the tolerance, otherwise `False`.

---

#### `get_message_by_prefix(message, prefix)`
Finds and returns the first message in a multi-line string that starts with a given prefix.

- **Arguments**:
    - `message (str)`: Multi-line string containing NMEA messages.
    - `prefix (str)`: Prefix to search for (e.g., `$GPGGA`).

- **Returns**:
    - `str or None`: The first message matching the prefix, or `None` if not found.

---

#### `get_gga(message)`
Extracts the `$GPGGA` message from a multi-line NMEA message string.

- **Arguments**:
    - `message (str)`: Multi-line string containing NMEA messages.

- **Returns**:
    - `str or None`: The `$GPGGA` message, or `None` if not found.

---

#### `get_attitude_message(message)`
Extracts the `$PSEAA` (attitude) message from a multi-line NMEA message string.

- **Arguments**:
    - `message (str)`: Multi-line string containing NMEA messages.

- **Returns**:
    - `str or None`: The `$PSEAA` message, or `None` if not found.

---

#### `get_command_status_message(message)`
Extracts the `$PSEAD` (command status) message from a multi-line NMEA message string.

- **Arguments**:
    - `message (str)`: Multi-line string containing NMEA messages.

- **Returns**:
    - `str or None`: The `$PSEAD` message, or `None` if not found.

---

#### `get_coordinates(gga_message)`
Parses an NMEA GGA message to extract latitude and longitude coordinates.

- **Arguments**:
    - `gga_message (str)`: The NMEA GGA message string.

- **Returns**:
    - `dict`: A dictionary with `Latitude` and `Longitude` as keys, or an empty dictionary if parsing fails.

---

#### `process_proprietary_message(proprietary_message, value_names, process_fun)`
Processes proprietary NMEA messages and maps their values to a dictionary using custom processing logic.

- **Arguments**:
    - `proprietary_message (str)`: The proprietary message to be parsed.
    - `value_names (list)`: List of value names to map to the message parts.
    - `process_fun (Callable)`: Function to process each message part.

- **Returns**:
    - `dict`: A dictionary mapping value names to processed values.

---

#### `get_attitude(attitude_message)`
Parses an attitude message (`$PSEAA`) and returns a dictionary of attitude-related values (e.g., pitch, roll, heading).

- **Arguments**:
    - `attitude_message (str)`: The `$PSEAA` message string.

- **Returns**:
    - `dict`: A dictionary of attitude-related values.

---

#### `get_command_status(command_message)`
Parses a command status message (`$PSEAD`) and returns a dictionary of control mode and thrust-related values.

- **Arguments**:
    - `command_message (str)`: The `$PSEAD` message string.

- **Returns**:
    - `dict`: A dictionary of command status values.

---

#### `get_date()`
Retrieves the current date and time in a structured dictionary format.

- **Arguments**:
    - None.

- **Returns**:
    - `dict`: A dictionary with `Day` and `Time` as keys.

---

#### `process_surveyor_message(message)`
Processes a multi-line surveyor message and extracts attributes based on line prefixes.

- **Arguments**:
    - `message (str)`: The surveyor message containing multiple lines.

- **Returns**:
    - `dict`: A dictionary of extracted attributes.

## Waypiont Utility Module
`surveyor_lib.helpers.waypoint_helper`

This module provides utilities for working with NMEA (National Marine Electronics Association) messages, including functions for computing checksums, converting coordinates to NMEA format, and generating waypoint missions.

## Functions

### `compute_nmea_checksum(message)`
Compute the checksum for an NMEA message.

- **Arguments**:
    - `message` (str): The NMEA message string.
- **Returns**:
    - `str`: The computed checksum in hexadecimal format.

---

### `convert_lat_to_nmea_degrees_minutes(decimal_degree)`
Convert a decimal degree latitude value to NMEA format (degrees and minutes).

- **Arguments**:
    - `decimal_degree` (float): The decimal degree latitude value.
- **Returns**:
    - `str`: The latitude in NMEA format (degrees and minutes).

---

### `convert_lon_to_nmea_degrees_minutes(decimal_degree)`
Convert a decimal degree longitude value to NMEA format (degrees and minutes).

- **Arguments**:
    - `decimal_degree` (float): The decimal degree longitude value.
- **Returns**:
    - `str`: The longitude in NMEA format (degrees and minutes).

---

### `get_hemisphere_lat(value)`
Get the hemisphere ('N' or 'S') for a given latitude value.

- **Arguments**:
    - `value` (float): The latitude value.
- **Returns**:
    - `str`: The hemisphere ('N' or 'S') for the given latitude value.

---

### `get_hemisphere_lon(value)`
Get the hemisphere ('E' or 'W') for a given longitude value.

- **Arguments**:
    - `value` (float): The longitude value.
- **Returns**:
    - `str`: The hemisphere ('E' or 'W') for the given longitude value.

---

### `create_nmea_message(message, checksum_func=compute_nmea_checksum)`
Create a full NMEA message with checksum.

- **Arguments**:
    - `message` (str): The NMEA message string.
    - `checksum_func` (callable, optional): The function to compute the checksum. Defaults to `compute_nmea_checksum`.
- **Returns**:
    - `str`: The full NMEA message with checksum.

---

### `create_waypoint_message(latitude_minutes, latitude_hemisphere, longitude_minutes, longitude_hemisphere, number)`
Create an NMEA waypoint message.

- **Arguments**:
    - `latitude_minutes` (str): The latitude in degrees and minutes format.
    - `latitude_hemisphere` (str): The latitude hemisphere ('N' or 'S').
    - `longitude_minutes` (str): The longitude in degrees and minutes format.
    - `longitude_hemisphere` (str): The longitude hemisphere ('E' or 'W').
    - `number` (int): The waypoint number.
- **Returns**:
    - `str`: The NMEA waypoint message.

---

### `create_waypoint_messages_df(filename, erp_filename)`
Create a DataFrame with proper waypoint messages to be sent to the surveyor from a CSV file.

- **Arguments**:
    - `filename` (str): The name of the CSV file containing waypoint data.
    - `erp_filename` (str): The name of the CSV file containing emergency recovery point.
- **Returns**:
    - `pandas.DataFrame`: A DataFrame containing NMEA waypoint messages.

---

### `create_waypoint_messages_df_from_list(waypoints, erp)`
Create a DataFrame with waypoint messages from lists of coordinates.

- **Arguments**:
    - `waypoints` (list): A list of tuples with `(latitude, longitude)`.
    - `erp` (tuple): A tuple with `(latitude, longitude)` for the emergency recovery point.
- **Returns**:
    - `pandas.DataFrame`: A pandas DataFrame containing NMEA waypoint messages.

---

### `create_waypoint_mission(df, throttle=20)`
Generate a waypoint mission from a DataFrame.

- **Arguments**:
    - `df` (pandas.DataFrame): The DataFrame containing the waypoint data. It must contain the column `nmea_message` obtained by passing waypoints to `create_waypoint_messages_df` or `create_waypoint_messages_df_from_list`.
    - `throttle` (int, optional): The throttle value for the PSEAR command. Defaults to 20.
- **Returns**:
    - `str`: The waypoint mission string.