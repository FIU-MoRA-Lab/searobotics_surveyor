'''
This module:
    - Handles several tasks associated with the surveyor object, focusing on the manipulation and analysis of geospatial data, 
    particularly GPS coordinates and NMEA messages. 
    - Includes functionalities to create and evaluate coordinates for gradient assessment, generate square areas around specific GPS points,
    checks the proximity of coordinates, and extract specific NMEA messages like GPGGA and PSEAA. 
    - Computes NMEA checksums, converts decimal degrees to NMEA format, and creates waypoint missions from CSV data. 
Also supports saving these missions and related data to CSV files with date-specific filenames, 
thereby facilitating the efficient management of navigation and surveying tasks for the surveyor object.
'''

import csv
import datetime
import math
import os
import time
from geopy.distance import geodesic
import pynmea2
import pandas as pd
from . import logger, config

HELPER_LOGGER = logger.create_logger(name='Helper Logger', log_level=config.LOGGING_LEVEL, log_file='')

def create_grad_eval_coordinates(lat, lon, side_length):
    """
    Create coordinates for gradient evaluation given side distance around a GPS coordinate. (Will be deprecated in the future)

    Parameters:
    lat (float): Latitude of the center point.
    lon (float): Longitude of the center point.
    side_length (float): Length of the side of the square in meters.

    Returns:
    List[tuple]: A list of tuples representing the GPS coordinates of two corners of the square.
    """
    half_diagonal = (side_length / math.sqrt(2)) / 1000  # Convert meters to kilometers

    # Calculate the coordinates of the two corners
    top_left = geodesic(kilometers=half_diagonal).destination((lat, lon), bearing=315)
    top_right = geodesic(kilometers=half_diagonal).destination((lat, lon), bearing=45)
    #bottom_left = geodesic(kilometers=half_diagonal).destination((lat, lon), bearing=225)
    #bottom_right = geodesic(kilometers=half_diagonal).destination((lat, lon), bearing=135)

    return [(top_left.latitude, top_left.longitude),
            (top_right.latitude, top_right.longitude)]


def create_square_coordinates(coordinates, side_length):
    """
    Create a square with a given side length around a GPS coordinate.

    Parameters:
    coordinates (tuple) [float] Latitude and longitude of the center point.
    side_length (float): Length of the side of the square in meters.

    Returns:
    List[tuple]: A list of tuples representing the GPS coordinates of the four corners of the square.
    """
    
    half_diagonal = (side_length / math.sqrt(2)) / 1000  # Convert meters to kilometers

    # Calculate the coordinates of the four corners
    
    bearings = [45 + 90*i for i in range(4)] #bearings = [315, 45, 135, 225]
    coordinates = [(geodesic(kilometers=half_diagonal).destination(coordinates, bearing=bearing).latitude,
                    geodesic(kilometers=half_diagonal).destination(coordinates, bearing=bearing).longitude)
                    for bearing in bearings]
    return coordinates
    # top_left = geodesic(kilometers=half_diagonal).destination((lat, lon), bearing=315)
    # top_right = geodesic(kilometers=half_diagonal).destination((lat, lon), bearing=45)
    # bottom_left = geodesic(kilometers=half_diagonal).destination((lat, lon), bearing=225)
    # bottom_right = geodesic(kilometers=half_diagonal).destination((lat, lon), bearing=135)

    # return [(top_left.latitude, top_left.longitude),
    #         (top_right.latitude, top_right.longitude),
    #         (bottom_right.latitude, bottom_right.longitude),
    #         (bottom_left.latitude, bottom_left.longitude)]


def are_coordinates_close(coord1, coord2, tolerance_meters=2):
    """
    Check if two coordinates are close enough based on a tolerance in meters.

    Parameters:
        coord1: Tuple containing first set of coordinates (latitude, longitude).
        coord2: Tuple containing second set of coordinates (latitude, longitude).
        tolerance_meters: Maximum allowed distance in meters between the two coordinates.

    Returns:
        Boolean indicating if the two coordinates are close enough.
    """
    distance = geodesic(coord1, coord2).meters
    return distance <= tolerance_meters

def get_message_by_prefix(message, prefix):
    """Find the message in the split list that starts with the given prefix."""
    messages = message.split('\r\n')
    for msg in messages:
        if msg.startswith(prefix):
            return msg
    return None

def get_gga(message):
    """Extract the GPGGA message."""
    gga = get_message_by_prefix(message, '$GPGGA')
    if gga:
        return gga
    return None

def get_attitude_message(message):
    """Extract the PSEAA message."""
    attitude = get_message_by_prefix(message, '$PSEAA')
    if attitude:
        return attitude
    return None

def get_command_status_message(message):
    """Extract the PSEAD message."""
    control_mode_message = get_message_by_prefix(message, '$PSEAD')
    if control_mode_message:
        return control_mode_message
    return None

# def get_control_mode(message):
#     """Extract the PSEAD message and determine the control mode."""
#     psead = get_message_by_prefix(message, '$PSEAD')

#     if not psead:
#         return None
    
#     psead = psead.split(',')
#     code = psead[1]
#     return CONTROL_MODE_DICT.get(code, 'Unknown')

def get_coordinates(gga_message):
    global HELPER_LOGGER
    """
    Extract latitude and longitude coordinates from an NMEA GGA message.

    Args:
        gga_message (str): The NMEA GGA message string.

    Returns:
        tuple: A tuple containing the latitude and longitude as floats, or None if the message cannot be parsed.
    """
    if not gga_message:
        HELPER_LOGGER.warning("Received an empty or None GGA message.")
        return None

    HELPER_LOGGER.info("Parsing GGA message: %s", gga_message)

    try:
        # Parse the NMEA GGA message
        gga = pynmea2.parse(gga_message)

        # Extract latitude and longitude if valid
        if gga.latitude != 0.0 and gga.longitude != 0.0:
            HELPER_LOGGER.info("Successfully parsed coordinates: Latitude = %f, Longitude = %f", gga.latitude, gga.longitude)
        else:
            HELPER_LOGGER.warning("Parsed GGA message contains invalid coordinates: Latitude = %f, Longitude = %f", gga.latitude, gga.longitude)
        return {'Latitude' : gga.latitude, 'Longitude' : gga.longitude}

    except pynmea2.ParseError as e:
        HELPER_LOGGER.error("Failed to parse GGA message: %s, Error: %s", gga_message, e)
    except (ValueError, TypeError) as e:
        HELPER_LOGGER.error("Error processing GGA message: %s, Error: %s", gga_message, e)

    # If any exception occurs or the message cannot be parsed, return {}
    HELPER_LOGGER.error("Failed to extract valid coordinates from GGA message.")
    return {}

def process_propietary_message(propietary_message, value_names, process_fun):
    """
    Process the propietary message and convert it into a dictionary with corresponding values.

    Args:
        propietary_message (str): The propietary message to be parsed.
        value_names (list): The list of value names to map to the message parts.

    Returns:
        dict: A dictionary mapping the value names to the corresponding parsed values.
    """
    if not propietary_message:
        HELPER_LOGGER.warning("Received empty or None propietary message.")
        return {}

    HELPER_LOGGER.info("Receiving propietary message: %s", propietary_message)

    # Split the message into parts and remove the first and last item (e.g. '$PESAA' and checksum)
    try:
        message_parts = propietary_message.split(',')[1:]  # Remove the first part ('$PESAA')
        last_element = message_parts.pop(-1).split('*')[0]  # Remove the last part (checksum)
        message_parts.append(last_element)
    except Exception as e:
        HELPER_LOGGER.error("Error processing propietary message: %s", e)
        return {}

    # Convert the message parts to floats, replacing empty values with 0.0
    try:
        message_parts = [process_fun(element) for element in message_parts]
    except ValueError as e:
        HELPER_LOGGER.error("Error converting message parts to floats: %s", e)
        return {}

    # Return the result as a dictionary, mapping names to values
    return {name: value for name, value in zip(value_names, message_parts)}

def get_attitude(attitude_message):
    
    """
    Parses an attitude message string and returns a dictionary of corresponding attitude values.


    Parameters:
        attitude_message (str): A comma-separated string representing attitude data. It may contain
                                 values like pitch, roll, heading, etc. The string should include the
                                 protocol header ('$PESAA') and a checksum (e.g., '*7F') at the end,
                                 which will be discarded.

    Returns:
        dict: A dictionary where the keys are attitude names (e.g., 'Pitch', 'Roll', 'Heading') and
              the values are the corresponding numerical values parsed from the attitude message. If
              the input message is invalid or empty, an empty dictionary is returned.
    
    Example:
        If attitude_message is '$PESAA,12.34,56.78,-90.12,34.56,18.0,0.5,-0.2,0.8,1.5*7F', 
        the function will return:
        {
            'Pitch': 12.34,
            'Roll': 56.78,
            'Heading': -90.12,
            'Heave': 34.56,
            'Temp': 18.0,
            'Acc_x': 0.5,
            'Acc_y': -0.2,
            'Acc_z': 0.8,
            'Yaw_rate': 1.5
        }
    """
    result = process_propietary_message(attitude_message, get_attitude.value_names, get_attitude.process_fun)
    return result

get_attitude.value_names = [
    "Pitch (degrees)",
    "Roll (degrees)",
    "Heading (degrees Magnetic)",
    "Heave",
    "Temperature in electronics box (degrees C)",
    "Acceleration x, forward (G)",
    "Acceleration y, starboard (G)",
    "Acceleration z, down (G)",
    "Yaw rate [degrees/s]"
]
get_attitude.process_fun = lambda x: float(x) if x else 0.0

def get_command_status(command_message):
    """
    Parses a command status message and returns a dictionary of corresponding status values.

    Args:
        command_message (str): A string representing the command status message. It should be a comma-separated
                                message with each part corresponding to a specific value, and may contain a
                                checksum at the end which will be discarded.

    Returns:
        dict: A dictionary where the keys are the command status names (e.g., 'Control Mode', 'Heading') 
              and the values are the corresponding parsed values from the message. If the input message 
              is invalid or empty, an empty dictionary is returned.

    Example:
        If command_message is '$PSEAA,1.5,T,2.5,0.5*7A', the function will return:
        {
            'Control Mode': 1.5,
            'Heading, degrees Magnetic': 'Thruster',
            'Thrust': 2.5,
            'Thrust difference': 0.5
        }

    Notes:
        - The function uses the `process_fun` lambda for processing numeric values and decoding command symbols.
        - The `command_dictionary` is used to map symbols (e.g., 'T', 'C', 'G') to human-readable descriptions.

    """
    result = process_propietary_message(command_message, get_command_status.value_names, get_command_status.process_fun)
    return result

get_command_status.value_names = [
    "Control Mode",
    "Heading (degrees Magnetic)",
    "Thrust (% Thrust)",
    "Thrust difference (% Thrust)"
]
get_command_status.command_dictionary = {
        'L': 'Standby',
        'T': 'Thruster',
        'C': 'Heading',
        'G': 'Speed',
        'R': 'Station Keep',
        'N': 'River Nav',
        'W': 'Waypoint',
        'I': 'Autopilot',
        '3': 'Compass Cal',
        'H': 'Go To ERP',
        'D': 'Depth',
        'S': 'Gravity Vector Direction',
        'F': 'File Download',
        '!': 'Boot Loader'
    }
def _get_command_status_process_fun(x):
    if not x:
        return 0.0
    try:
        return float(x)
    except:
        return get_command_status.command_dictionary.get(x, "Unknown")
    
get_command_status.process_fun = _get_command_status_process_fun


def get_date():
        now = datetime.datetime.now()  # Get the current date and time
        date_str = now.strftime("%Y%m%d")  # Format date as YYYY-MM-DD
        time_str = now.strftime("%H%M%S")  # Format time as HH:MM:SS
        return {'Day': int(date_str), 'Time' : int(time_str)}

def process_surveyor_message(message):
    """
    Processes a surveyor message and extracts attributes based on line prefixes.
    Args:
        message (str): The surveyor message to be parsed, containing multiple lines.

    Returns:
        dict: A dictionary of attributes extracted from the message.

    """
    global HELPER_LOGGER
    messages = message.split('\r\n')
    attribute_dict = get_date()

    for message_line in messages:
        prefix = message_line[:6]
        HELPER_LOGGER.debug(f'Processing message with prefix: {prefix}')
        fun = process_surveyor_message.prefix_map.get(prefix, lambda x: {})
        attribute_dict.update(fun(message_line))
    
    HELPER_LOGGER.debug(f'Attributes updated: {attribute_dict}')
    return attribute_dict

process_surveyor_message.prefix_map = {
    '$GPGGA': get_coordinates,
    '$PSEAA': get_attitude,
    '$PSEAD': get_command_status
}

def compute_nmea_checksum(message):
    """
    Compute the checksum for an NMEA message.

    Args:
        message (str): The NMEA message string.

    Returns:
        str: The computed checksum in hexadecimal format.
    """
    checksum = 0
    for char in message:
        checksum ^= ord(char)
    return '{:02X}'.format(checksum)

def convert_lat_to_nmea_degrees_minutes(decimal_degree):
    """
    Convert a decimal degree latitude value to NMEA format (degrees and minutes).

    Args:
        decimal_degree (float): The decimal degree latitude value.

    Returns:
        str: The latitude in NMEA format (degrees and minutes).
    """
    degrees = int(abs(decimal_degree)) # Degrees
    minutes_decimal = (abs(decimal_degree) - degrees) * 60 # Minutes
    return "{:02d}{:.4f}".format(degrees, minutes_decimal)

def convert_lon_to_nmea_degrees_minutes(decimal_degree):
    """
    Convert a decimal degree longitude value to NMEA format (degrees and minutes).

    Args:
        decimal_degree (float): The decimal degree longitude value.

    Returns:
        str: The longitude in NMEA format (degrees and minutes).
    """
    degrees = int(abs(decimal_degree))
    minutes_decimal = (abs(decimal_degree) - degrees) * 60
    return "{:03d}{:.4f}".format(degrees, minutes_decimal)

def get_hemisphere_lat(value):
    """
    Get the hemisphere ('N' or 'S') for a given latitude value.

    Args:
        value (float): The latitude value.

    Returns:
        str: The hemisphere ('N' or 'S') for the given latitude value.
    """
    return 'N' if value >= 0 else 'S'

def get_hemisphere_lon(value):
    """
    Get the hemisphere ('E' or 'W') for a given longitude value.

    Args:
        value (float): The longitude value.

    Returns:
        str: The hemisphere ('E' or 'W') for the given longitude value.
    """
    return 'E' if value >= 0 else 'W'

def create_nmea_message(message, checksum_func = compute_nmea_checksum):
    """
    Create a full NMEA message with checksum.

    Args:
        message (str): The NMEA message string.
        checksum_func (callable, optional): The function to compute the checksum. Defaults to compute_nmea_checksum.

    Returns:
        str: The full NMEA message with checksum.
    """
    checksum = checksum_func(message)
    return f"${message}*{checksum}\r\n"
    # return "${}\*{}\\r\\n".format(message, checksum) 

def create_waypoint_message(latitude_minutes, latitude_hemisphere, longitude_minutes, longitude_hemisphere, number):
    """
    Create an NMEA waypoint message.

    Args:
        latitude_minutes (str): The latitude in degrees and minutes format.
        latitude_hemisphere (str): The latitude hemisphere ('N' or 'S').
        longitude_minutes (str): The longitude in degrees and minutes format.
        longitude_hemisphere (str): The longitude hemisphere ('E' or 'W').
        number (int): The waypoint number.

    Returns:
        str: The NMEA waypoint message.
    """
    return f"OIWPL,{latitude_minutes},{latitude_hemisphere},{longitude_minutes},{longitude_hemisphere},{number}"
    # return "OIWPL,{},{},".format(latitude_minutes, latitude_hemisphere) + "{},{},".format(longitude_minutes, longitude_hemisphere) + str(number)

def create_waypoint_messages_df(filename, erp_filename):
    """
    Create a DataFrame with proper waypoint messages to be sent to the surveyor from a CSV file.

    Args:
        filename: the name of the CSV file containing waypoint data
        erp_filename: the name of the CSV file containing emergency recovery point
    
    Rreturns: 
        Pandas DataFrame: a DataFrame containing NMEA waypoint messages
    """
    try:
        # Load the CSV into a pandas DataFrame
        df = pd.read_csv(filename)
    except Exception as e:
        print(f"Error loading waypoint CSV file: {e}")
        return pd.DataFrame()

    if df.empty:
        print("The waypoints DataFrame is empty.")
        return df

    try:
        # Load the ERP CSV into a pandas DataFrame
        erp_df = pd.read_csv(erp_filename)
        
        # Only take the first row for the ERP as pandas DataFrame
        erp_df = erp_df.iloc[0:1]

    except Exception as e:
        print(f"Error loading ERP CSV file: {e}")
        return pd.DataFrame()
    
    # Append ERP to the beginning of the DataFrame
    df = pd.concat([erp_df, df], ignore_index=True)

    # Convert latitude and longitude to desired format
    df['latitude_minutes'] = df['latitude'].apply(
        lambda x: convert_lat_to_nmea_degrees_minutes(float(x)))
    df['longitude_minutes'] = df['longitude'].apply(
        lambda x: convert_lon_to_nmea_degrees_minutes(float(x)))

    # Get hemisphere for latitude and longitude
    df['latitude_hemisphere'] = df['latitude'].apply(get_hemisphere_lat)
    df['longitude_hemisphere'] = df['longitude'].apply(get_hemisphere_lon)

    # Adjust the nmea_waypoints column for the emergency recovery point and the sequential waypoints
    df['nmea_waypoints'] = df.apply(lambda row: create_waypoint_message(
        row['latitude_minutes'], row['latitude_hemisphere'], row['longitude_minutes'], row['longitude_hemisphere'],
        row.name), axis=1)

    # Create full NMEA message with checksum
    df['nmea_message'] = df['nmea_waypoints'].apply(
        lambda waypoint: create_nmea_message(waypoint))
    return df

def create_waypoint_messages_df_from_list(waypoints, erp):
    """
    Create a DataFrame with waypoint messages from lists of coordinates.

    Args:
        waypoints: a list of tuples with (latitude, longitude)
        erp: a tuple with (latitude, longitude) for the emergency recovery point
    Returns: 
        Pandas DataFrame: a pandas DataFrame containing NMEA waypoint messages
    """
    # Convert the waypoints list and ERP to pandas DataFrames
    waypoints_df = pd.DataFrame(waypoints, columns=['latitude', 'longitude'])
    erp_df = pd.DataFrame(erp, columns=['latitude', 'longitude'])

    # Validate that the DataFrames are not empty
    if waypoints_df.empty:
        print("The waypoints DataFrame is empty.")
        return pd.DataFrame()
    if erp_df.empty:
        print("The ERP DataFrame is empty.")
        return pd.DataFrame()

    # Append ERP to the beginning of the DataFrame
    df = pd.concat([erp_df, waypoints_df], ignore_index=True)
    
    # Convert latitude and longitude to desired format
    df['latitude_minutes'] = df['latitude'].apply(
        lambda x: convert_lat_to_nmea_degrees_minutes(float(x)))
    df['longitude_minutes'] = df['longitude'].apply(
        lambda x: convert_lon_to_nmea_degrees_minutes(float(x)))

    # Get hemisphere for latitude and longitude
    df['latitude_hemisphere'] = df['latitude'].apply(get_hemisphere_lat)
    df['longitude_hemisphere'] = df['longitude'].apply(get_hemisphere_lon)

    # Adjust the nmea_waypoints column for the emergency recovery point and the sequential waypoints
    df['nmea_waypoints'] = df.apply(lambda row: create_waypoint_message(
        row['latitude_minutes'], row['latitude_hemisphere'], row['longitude_minutes'], row['longitude_hemisphere'],
        row.name), axis=1)

    # Create full NMEA message with checksum
    df['nmea_message'] = df['nmea_waypoints'].apply(
        lambda waypoint: create_nmea_message(waypoint))

    return df


def create_waypoint_mission(df, throttle=20):
    """
    Generate a waypoint mission from a DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the waypoint data. It must contain the column 'nmea_message' 
        obtained by having waypoints in CSV files and passing them to create_waypoint_messages_df function or having a list of coordinates
        and passing them to create_waypoint_messages_df_from_list function.
        throttle (int, optional): The throttle value for the PSEAR command. Defaults to 20.
        pause_time (int, optional): The pause time value for the PSEAR command. Defaults to 0.

    Returns:
        str: The waypoint mission string.
    """
    # Start with the PSEAR command
    psear_cmd = "PSEAR,0,000,{},0,000".format(throttle)
    psear_cmd_with_checksum = "${}\*{}\\r\\n".format(psear_cmd, compute_nmea_checksum(psear_cmd))

    # Generate OIWPL commands from the DataFrame
    oiwpl_cmds = df['nmea_message'].tolist()

    # Concatenate all the commands to form the mission
    mission = psear_cmd_with_checksum + ''.join(oiwpl_cmds)

    return mission

def append_to_csv(data, cols=["latitude", "longitude"], post_fix=""):
    """
    Append data to a CSV file with a specific date in the filename.

    Args:
        data (list): The list of data to be appended to the CSV file.
        post_fix (str, optional): A string to be appended to the filename. Defaults to an empty string.
        cols (list, optional): A list of column names for the CSV file. Defaults to ["latitude", "longitude"].
    """
    # Get today's date in the "YYYYMMDD" format
    today_date = datetime.date.today().strftime("%Y%m%d")

    # Get the parent directory of the current script
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

    # Create the "out" directory if it doesn't exist
    out_dir = os.path.join(parent_dir, "out")
    os.makedirs(out_dir, exist_ok=True)

    # Define the CSV file path using today's date
    file_path = os.path.join(out_dir, f"{today_date}{post_fix}.csv")

    # Check if the file already exists, and create it with headers if it doesn't
    if not os.path.isfile(file_path):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(cols)

    # Append the data to the CSV file
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def save(data, post_fix=""):
    """
    Process GPS coordinates and Exo2 sensor data, append them to a CSV file after validation.

    Parameters:
        data: Dictionary containing GPS coordinates and Exo2 sensor data.
        post_fix: (optional) A suffix to append to the CSV file name. Default is "".
    """
    # Initialize lists to store combined data and column names

    # If combined data is not empty, append to CSV
    if data:
        append_to_csv(data.values(), data.keys(), post_fix=post_fix)


def process_gga_and_save_data(surveyor_connection, data_keys=['state', 'exo2'], post_fix="", delay=1.0):
    """
    Retrieve and process GGA and Exo2 data, then append it to a CSV file.

    Args:
        surveyor_connection: The Surveyor connection object providing access to GPS and Exo2 data.
        post_fix: (optional) A suffix to append to the CSV file name. Default is "".

    Returns:
        surveyor_data (dict): Dictionary with the data acquired by the boat (see Surveyor.get_data method)
    """
    surveyor_data = surveyor_connection.get_data(data_keys)

    # Save the data to a CSV file
    if time.time() - process_gga_and_save_data.last_save_time < delay:
        time.sleep(delay - time.time() + process_gga_and_save_data.last_save_time)
    process_gga_and_save_data.last_save_time = time.time()

    save(surveyor_data, post_fix)
    return surveyor_data

process_gga_and_save_data.last_save_time = time.time()

def read_csv_into_tuples(filepath):
    """
    Reads a CSV file into a list of tuples.
    
    Parameters:
        filepath (str): The path to the CSV file.
        
    Returns:
        list of tuples: Each tuple represents a row from the CSV file.
    """
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(filepath)

    try:
        df = df[['Latitude', 'Longitude']]
    except KeyError:
        try:
            df = df[['latitude', 'longitude']]
        except KeyError:
            print('Assuming first column to be Latitude and second to be Longitude')
            df = df.iloc[:, :2]        
    
    # Convert the DataFrame rows into tuples and return as a list
    return [tuple(row) for row in df.values]


if __name__ == "__main__":
    # Define file names
    filename = "square_mission"
    erp_filename = "erp_FIUMMC_lake"
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    print(parent_dir)
    # Open CSV files and create NMEA messages
    df = create_waypoint_messages_df(parent_dir + "/out/" + filename + ".csv", parent_dir + "/in/" + erp_filename + ".csv")
    mission = create_waypoint_mission(df)

    # Save mission to file
    output_file_path = parent_dir + "/out/" + filename + ".sea"
    with open(output_file_path, 'w') as file:
        file.write(mission)

    # Example usage:
    message = "PSEAA,-2.2,0.7,222.6,,47.8,-0.04,-0.01,-1.00,-0.01*7A\r\n"
    print("checksum", str(compute_nmea_checksum(message)))  # This should print "7D"

    gga_message = "$GPGGA,115739.00,4158.8441367,N,09147.4416929,W,4,13,0.9,255.747,M,-32.00,M,01,0000*6E\r\n"
    coordinates = get_coordinates(gga_message)
    if coordinates:
        latitude, longitude = coordinates
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
    else:
        print("Invalid or incomplete GGA sentence")

    messages = [
        "$GPGGA,,,,,,0,,,,M,,M,,*66\r\n",
        # More messages here...
        "$DEBUG,,,,,,,,,,,,,,,,,*7D\r\n"
    ]
    message = ''.join(messages)
    gga_message = get_gga(message)

    coordinates = get_coordinates(gga_message)
    if coordinates:
        latitude, longitude = coordinates
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
    else:
        print("Invalid or incomplete GGA sentence")

    # Other debug prints and function calls
        

    

