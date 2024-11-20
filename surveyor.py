import socket
import time
from . import surveyor_helper as hlp
from . import clients
from geopy.distance import geodesic
from datetime import datetime


class Surveyor:
    def __init__(self, 
             host='192.168.0.50', port=8003,
             sensors_to_use=['exo2', 'camera', 'lidar'], 
             sensors_config={'exo2': {}, 'camera': {}, 'lidar' :{}}):
    
        """
        Initialize the Surveyor object with server connection details and sensor configurations.

        Args:
            host (str, optional): The IP address of the main server to connect to. Defaults to '192.168.0.50'.
            port (int, optional): The port number of the main server. Defaults to 8003.
            sensors_to_use (list of str, optional): List of sensor types to initialize (e.g., 'exo2', 'camera' or 'lidar').
                                                    Defaults to ['exo2', 'camera', 'lidar'].
            sensors_config (dict, optional): A dictionary for configuring each sensor. If a sensor's configuration is empty,
                                            it will be populated with default values. Defaults to 
                                            {'exo2': {}, 'camera': {}, 'lidar' :{}}.

        Sensor Config Defaults:
            - 'exo2': {'exo2_server_ip': '192.168.0.68', 'exo2_server_port': 5000}
            - 'camera': {'camera_server_ip': '192.168.0.20', 'camera_server_port': 5001}
            - 'lidar': {'lidar_server_ip': '192.168.0.20', 'lidar_server_port': 5002}

        Attributes:
            host (str): IP address of the main server.
            port (int): Port number of the main server.
            exo2 (Exo2Client): Client for interacting with the EXO2 sensor (if 'exo2' is in sensors_to_use).
            camera (CameraClient): Client for interacting with the camera sensor (if 'camera' is in sensors_to_use).
            lidar (LidarClient): Client for interacting with the lidar sensor (if 'lidar' is in sensors_to_use).
        """
        self.host = host
        self.port = port
        DEFAULT_CONFIGS = {
            'exo2': {'exo2_server_ip': '192.168.0.68', 'exo2_server_port': 5000},
            'camera': {'camera_server_ip': '192.168.0.20', 'camera_server_port': 5001},
            'lidar': {'lidar_server_ip': '192.168.0.20', 'lidar_server_port': 5002}
        }
        
        # Apply default configurations if not provided
        for sensor in sensors_to_use:
            if not sensors_config[sensor]:
                sensors_config[sensor].update(DEFAULT_CONFIGS[sensor])
        
        # Initialize sensors based on sensors_to_use
        if 'exo2' in sensors_to_use:    
            self.exo2 = clients.Exo2Client(sensors_config['exo2']['exo2_server_ip'], 
                                        sensors_config['exo2']['exo2_server_port'])
        
        if 'camera' in sensors_to_use:     
            self.camera = clients.CameraClient(sensors_config['camera']['camera_server_ip'], 
                                            sensors_config['camera']['camera_server_port'])
            
        if 'lidar' in sensors_to_use:     
            self.lidar = clients.LidarClient(sensors_config['camera']['lidar_server_ip'], 
                                            sensors_config['camera']['lidar_server_port'])
    

    def __enter__(self):
        """
        Establish a connection with the remote server.

        Returns:
            Surveyor: The Surveyor object.

        Raises:
            socket.error: If an error occurs while connecting to the remote server.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.settimeout(5)  # Set a timeout for the connection
            self.socket.connect((self.host, self.port))
            print('Surveyor connected!')
        except socket.error as e:
            print(f"Error connecting to {self.host}:{self.port} - {e}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close the connection with the remote server.
        """
        self.socket.close()

    def send(self, msg):
        """
        Send an NMEA message to the remote server.

        Args:
            msg (str): The NMEA message to be sent.

        Raises:
            socket.error: If an error occurs while sending the message.
        """
        msg = hlp.create_nmea_message(msg)
        try:
            self.socket.send(msg.encode())
            time.sleep(0.005)
        except socket.error as e:
            print(f"Error sending message - {e}")

    def receive(self, bytes=2048):
        """
        Receive data from the remote server.

        Args:
            bytes (int, optional): The maximum number of bytes to receive. Default is 4096.

        Returns:
            str: The received data as a string, or an empty string if no data was received.

        Raises:
            ConnectionError: If the connection is closed by the remote server.
            socket.timeout: If the socket times out while receiving data.
            socket.error: If an error occurs while receiving data.
        """
        try:
            data = self.socket.recv(bytes)
            if not data:
                raise ConnectionError("Connection closed by the server.")
            return data.decode('utf-8')
        except socket.timeout:
            print("Socket timeout.")
            raise
        except socket.error as e:
            print(f"Error receiving data - {e}")
            raise

    def set_standby_mode(self):
        msg = "PSEAC,L,0,0,0,"
        self.send(msg)

    # Thrust and thrust_diff must be an integer between -100 and 100 
    # negative means backwards/counter_clockwise

    def set_thruster_mode(self, thrust, thrust_diff, delay = 0.05): # Delay to ensure that the motors spin?
        msg = f"PSEAC,T,0,{int(thrust)},{int(thrust_diff)},"
        self.send(msg)
        time.sleep(delay)
        
    def set_station_keep_mode(self):
        msg = "PSEAC,R,,,,"
        self.send(msg)

    # degrees has to be an integer between 0 and 360
    def set_heading_mode(self, thrust, degrees):
        msg = f"PSEAC,C,{int(degrees)},{int(thrust)},,"
        self.send(msg)

    def set_waypoint_mode(self):
        msg = "PSEAC,W,0,0,0,"
        self.send(msg)

    def set_erp_mode(self):
        msg = "PSEAC,H,0,0,0,"
        self.send(msg)

    def start_file_download_mode(self, num_lines):
        msg = "PSEAC,F," + str(num_lines) + ",000,000,"
        self.send(msg)
        time.sleep(0.1)

    def end_file_download_mode(self):
        msg = "PSEAC,F,000,000,000"
        self.send(msg)
        time.sleep(0.1)

    def set_control_mode(self, mode, **args):
        """
        Set the control mode for the vehicle.

        Args:
            mode (str): The control mode to set. Possible values are:
                - "Waypoint": Set the waypoint mode with the provided thrust.
                - "Standby": Set the standby mode.
                - "Thruster": Set the thruster mode with the provided thrust and thrust_diff.
                - "Heading": Set the heading mode with the provided thrust and degrees.
                - "Go To ERP": Set the ERP (Emergency Recovery Point) mode.
                - "Station Keep": Set the station keeping mode.
                - "Start File Download": Start the file download mode with the provided num_lines.
                - "End File Download": End the file download mode.
            **args: Additional arguments required for specific modes.
                For "Waypoint" mode: thrust (float)
                For "Thruster" mode: thrust (float), thrust_diff (float), delay (float)
                For "Heading" mode: thrust (float), degrees (float)
                For "Start File Download" mode: num_lines (int)
        """
        match mode:
            case "Waypoint":
                self.set_waypoint_mode(args["thrust"])
            case "Standby":
                self.set_standby_mode()
            case "Thuster":
                self.set_thruster_mode(args["thrust"], args["thrust_diff"], args["delay"])
            case "Heading":
                self.set_heading_mode(args["thrust"], args["degrees"])
            case "Go To ERP":
                self.set_erp_mode()
            case "Station Keep":
                self.set_station_keep_mode()
            case "Start File Download":
                self.start_file_download_mode(args["num_lines"])
            case "End File Download":
                self.end_file_download_mode()
            case _:
                print("Control mode not implemented")


    def send_waypoints(self, waypoints, erp, throttle):
        """
        Send a list of waypoints to the surveyor.

        Args:
            waypoints (list): A list of tuples (latitude, longitude) containing the waypoints.
            erp (list): A list with one tuple (latitude, longitude) for the emergency recovery point.
            throttle (float): The throttle value for the PSEAR command.

        Raises:
            ValueError: If the generated DataFrame from waypoints is empty.
            socket.error: If an error occurs while sending the commands.
        """
        # Create a DataFrame from the list of waypoints and ERP message
        df = hlp.create_waypoint_messages_df_from_list(waypoints, erp)

        if df.empty:
            raise ValueError("DataFrame is empty.")

        # Calculate the total number of lines to send: waypoints + ERP + PSEAR command
        n_lines = len(df) + 1

        # List to store all the commands to be sent
        commands = []

        # Create the PSEAR command with the specified throttle value
        psear_cmd = "PSEAR,0,000,{},0,000".format(throttle)
        psear_cmd_with_checksum = hlp.create_nmea_message(psear_cmd)
        commands.append(psear_cmd_with_checksum)

        # Add OIWPL commands generated from the DataFrame
        oiwpl_cmds = df['nmea_message'].tolist()
        commands.extend(oiwpl_cmds)

        try:
            # Start file download mode with the number of lines to send
            self.start_file_download_mode(n_lines)

            # Send each command to the remote server
            for cmd in commands:
                self.send(cmd)

            # End file download mode
            self.end_file_download_mode()
        except socket.error as e:
            print(f"Error sending waypoints - {e}")
            raise

    def go_to_waypoint(self, waypoint, erp, throttle, tolerance_meters = 2.0):
        """
        Load the next waypoint, send it to the boat and sets the boat to navigate towards it.

        Args:
            waypoint (tuple): The waypoint coordinates to be sent.
            erp (list): A list of ERP coordinates.
            throttle (int): The desired throttle value for the boat.
            tolerance_meters (float): The tolerance distance for the waypoint in meters. If the waypoint is within the margin, it will be loaded only once.
        """
        self.send_waypoints([waypoint], erp, throttle)
        dist = geodesic(waypoint, self.get_gps_coordinates()).meters
        self.set_waypoint_mode()
        while self.get_control_mode() != 'Waypoint' and dist > tolerance_meters:
            dist = geodesic(waypoint, self.get_gps_coordinates()).meters
            self.set_waypoint_mode()

    def get_control_mode(self):
        """
        Get control mode data from the Surveyor connection object.

        Returns:
            Control mode string.
        """
        control_mode = None
        while not control_mode:
            control_mode = hlp.get_control_mode(self.receive())

        return control_mode
    
    def get_gps_coordinates(self):
        """
        Get GPS coordinates from the Surveyor connection object.

        Returns:
            Tuple containing GPS coordinates.
        """
        coordinates = None
        gga_message = None
        while (coordinates == None) or (gga_message == None):
            gga_message = hlp.get_gga(self.receive())
            coordinates = hlp.get_coordinates(gga_message)

        return coordinates
    

    def get_attitude(self):
        """
        Get Attitude information from the Surveyor connection object.

        Returns:
            Tuple containing heading.
        """
        heading = None
        attitude_message = None
        while (heading == None) or (attitude_message == None):
            attitude_message = hlp.get_attitude_message(self.receive())
            heading = hlp.get_heading(attitude_message)

        return heading

    def get_pitch(self):
        """
        Get Pitch information from the Surveyor connection object.

        Returns:
            Tuple containing pitch.
        """
        pitch = None
        attitude_message = None
        while (pitch == None) or (attitude_message == None):
            attitude_message = hlp.get_attitude_message(self.receive())
            pitch = hlp.get_pitch(attitude_message)

        return pitch

    def get_roll(self):
        """
        Get roll information from the Surveyor connection object.

        Returns:
            Tuple containing roll.
        """
        roll = None
        attitude_message = None
        while (roll == None) or (attitude_message == None):
            attitude_message = hlp.get_attitude_message(self.receive())
            roll = hlp.get_roll(attitude_message)

        return roll


    def get_heave(self):
        """
        Get heave information from the Surveyor connection object.

        Returns:
            Tuple containing heave.
        """
        heave = None
        attitude_message = None
        while (heave == None) or (attitude_message == None):
            attitude_message = hlp.get_attitude_message(self.receive())
            heave = hlp.get_heave(attitude_message)

        return heave

    def get_accel_x(self):
        """
        Get accel_x information from the Surveyor connection object.

        Returns:
            Tuple containing accel_x.
        """
        accel_x = None
        attitude_message = None
        while (accel_x == None) or (attitude_message == None):
            attitude_message = hlp.get_attitude_message(self.receive())
            accel_x = hlp.get_accel_x(attitude_message)

        return accel_x

    def get_accel_y(self):
        """
        Get accel_y information from the Surveyor connection object.

        Returns:
            Tuple containing accel_y.
        """
        accel_y = None
        attitude_message = None
        while (accel_y == None) or (attitude_message == None):
            attitude_message = hlp.get_attitude_message(self.receive())
            accel_y = hlp.get_accel_x(attitude_message)

        return accel_y


    def get_accel_z(self):
        """
        Get accel_z information from the Surveyor connection object.

        Returns:
            Tuple containing accel_z.
        """
        accel_z = None
        attitude_message = None
        while (accel_z == None) or (attitude_message == None):
            attitude_message = hlp.get_attitude_message(self.receive())
            accel_z = hlp.get_accel_z(attitude_message)

        return accel_z

    def get_yaw_rate(self):
        """
        Get yaw_rate information from the Surveyor connection object.

        Returns:
            Tuple containing yaw_rate.
        """
        yaw_rate = None
        attitude_message = None
        while (yaw_rate == None) or (attitude_message == None):
            attitude_message = hlp.get_attitude_message(self.receive())
            yaw_rate = hlp.get_yaw_rate(attitude_message)

        return yaw_rate
    
    def get_exo2_data(self):
        """
        Retrieve data from the EXO2 sensor.

        Returns:
           list: A list of float values representing the data from the Exo2 sensor.
        """
        return self.exo2.get_exo2_data()
    
    def get_current_date_and_time(self):
        now = datetime.now()  # Get the current date and time
        date_str = now.strftime("%Y%m%d")  # Format date as YYYY-MM-DD
        time_str = now.strftime("%H%M%S")  # Format time as HH:MM:SS
        return [int(date_str), int(time_str)]
    
    def get_data(self, keys=['coordinates', 'time', 'exo2_data']):
        """
        Retrieve data based on specified keys using corresponding getter functions.

        Args:
            keys (list, optional): A list of keys indicating the types of data to retrieve. Defaults to ['exo2_data', 'time', 'coordinates'].

        Returns:
            dict: A dictionary containing the retrieved data for each specified key.
        """
        # Dictionary mapping keys to corresponding getter functions. 
        # Must return either a list of values or a dictionary paired by name : value.
        # In the case it returns a list, data_labels dict has to be updated with a list of names
        getter_functions = {
            'exo2_data': self.get_exo2_data, # Dictionary with Exo2 sonde data
            'coordinates': self.get_gps_coordinates,# List with ["Latitude", "Longitude"]
            'heading': self.get_attitude, # List with ["Heading (degrees)"]
            'pitch': self.get_pitch, # List with ["Pitch (degrees)"]
            'roll': self.get_roll, # List with ["Roll (degrees)"]
            'heave': self.get_heave, # List with ["Heave"]
            'accel_x': self.get_accel_x, # List with ["Accel_X Forward (G)"]
            'accel_y': self.get_accel_y, # List with ["Accel_Y Starboard (G)"]
            'accel_z': self.get_accel_z, # List with ["Accel_Z Down (G)"]
            'yaw_rate': self.get_yaw_rate, # List with ["Yaw Rate (deg/s)"]
            'control_mode': self.get_control_mode, # List with ["Control mode"]
            'time' : self.get_current_date_and_time # List with ['Local Time (YYMMDD)', 'Local Time (HHMMSS)']
        }
        data_labels = {
            'exo2_data' : ["date", "time", "odo (%sat)", "odo (mg/l)", "temp (c)", "cond (us/cm)", "salinity (ppt)", "pressure (psia)", "depth (m)"],
            'coordinates' : ["Latitude", "Longitude"],
            'heading' : ["Heading (degrees)"],
            'pitch' : ["Pitch (degrees)"],
            'roll' : ["Roll (degrees)"],
            'heave' : ["Heave"],
            'accel_x' : ["Accel_X Forward (G)"],
            'accel_y' : ["Accel_Y Starboard (G)"],
            'accel_z' : ["Accel_Z Down (G)"],
            'yaw_rate' : ["Yaw Rate (deg/s)"],
            'control_mode' : ["Control mode"],
            'time' : ['Local Time (YYMMDD)', 'Local Time (HHMMSS)']}

        # Initialize a list to store retrieved data
        data_dict = {}

        # Iterate over specified keys and retrieve data using corresponding getter functions
        for key in keys:
            data = getter_functions[key]()
            if type(data) == float:
                data = [data]
            if type(data) != dict: 
                data = dict(zip(data_labels[key], data))
            data_dict.update(data)

        return data_dict

    def get_image(self):
        """
        Retrieve an image from the camera.

        Returns:
            tuple: A tuple containing a boolean value indicating whether the frame is read successfully
                   and the frame itself.
        """
        return self.camera.get_image()
    
    def get_lidar_measurements(self):
        """
        Retrieve the lidar measurements.

        Returns:
            list: A 360 list containing the lidar measurements (one per degree) im meters or None if the data was not correclty fetched.
        """
        return self.lidar.get_lidar_measurements()

    

