import socket
import time
from . import helpers as hlp
from . import clients
from geopy.distance import geodesic
import threading
import os
import csv
import json
import numpy as np
import h5py
from datetime import datetime


DEFAULT_CONFIGS = {
            'exo2': {'exo2_server_ip': '192.168.0.68', 'exo2_server_port': 5000},
            'camera': {'camera_server_ip': '192.168.0.20', 'camera_server_port': 5001},
            'lidar': {'lidar_server_ip': '192.168.0.20', 'lidar_server_port': 5002}
        }

class Surveyor:
    def __init__(self, 
             host='192.168.0.50', port=8003,
             sensors_to_use=['exo2', 'camera', 'lidar'], 
             sensors_config={'exo2': {}, 'camera': {}, 'lidar' :{}},
             record = True):
    
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
        
        self._state = {}
        
        # Apply default configurations if not provided
        for sensor in sensors_to_use:
            if sensors_config[sensor]:
                DEFAULT_CONFIGS[sensor].update(sensors_config[sensor])
        
        # Initialize sensors based on sensors_to_use
        if 'exo2' in sensors_to_use:    
            self.exo2 = clients.Exo2Client(DEFAULT_CONFIGS['exo2']['exo2_server_ip'], 
                                        DEFAULT_CONFIGS['exo2']['exo2_server_port'])
        
        if 'camera' in sensors_to_use:     
            self.camera = clients.CameraClient(DEFAULT_CONFIGS['camera']['camera_server_ip'], 
                                            DEFAULT_CONFIGS['camera']['camera_server_port'])
            
        if 'lidar' in sensors_to_use:     
            self.lidar = clients.LidarClient(DEFAULT_CONFIGS['lidar']['lidar_server_ip'], 
                                            DEFAULT_CONFIGS['lidar']['lidar_server_port'])
            
        self._parallel_update = True
        self.record = record


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
            self._receive_and_update_thread = threading.Thread(target=self._receive_and_update_thread)
            self._receive_and_update_thread.daemon = True
            self._receive_and_update_thread.start()
            while not self.get_state():
                time.sleep(0.1)
            if self.record:
                print('Initializing record thread')
                self._recording_thread = threading.Thread(target=self._save_data_continuously)
                self._recording_thread.daemon = True
                self._recording_thread.start()

        except socket.error as e:
            print(f"Error connecting to {self.host}:{self.port} - {e}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close the connection with the remote server.
        """
        self._parallel_update = False
        self._receive_and_update_thread.join()
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

    def _receive_and_update_thread(self):
        while self._parallel_update:
            message = self.receive()
            updated_state = hlp.process_surveyor_message(message)
            self._state.update(updated_state)

    def _save_data_continuously(self):
        # Create the 'records' folder in the current working directory (if it doesn't exist)
        folder_name = "records_" + datetime.now().strftime("%Y%m%d_%H%M%S")

        records_dir = os.path.join(os.getcwd(), folder_name)
        if not os.path.exists(records_dir):
            os.makedirs(records_dir)

        # File paths for saving data inside the 'records' folder
        image_data_path = os.path.join(records_dir, 'image_data.h5')  # Using HDF5 for image data
        state_data_path = os.path.join(records_dir, 'state_data.csv')
        lidar_data_path = os.path.join(records_dir, 'lidar_data.json')

        # Get image shape from a sample image
        shape = self.get_image()[1].shape
        
        # Open or create the HDF5 file for storing images
        with h5py.File(image_data_path, 'a') as f:
            # Create a dataset for images if it doesn't exist
            if 'images' not in f:
                # Create an empty dataset with an initial shape of (0, *shape)
                dataset = f.create_dataset('images', (0, *shape), maxshape=(None, *shape),
                                        dtype=np.uint8, chunks=(1, *shape), compression="gzip", compression_opts=4)
            else:
                dataset = f['images']

            images_received = 0  # Counter to track the number of images

            try:
                while self.record:
                    # Get the current state and data
                    state = self.get_state()
                    lidar_data = None
                    image_data = None

                    if hasattr(self, 'exo2'):
                        exo_data = self.get_exo2_data()
                        state.update(exo_data)

                    if hasattr(self, 'lidar'):
                        distances, angles = self.get_lidar_data()
                        lidar_data = {"distances": distances, "angles": angles}

                    if hasattr(self, 'camera'):
                        ret, image = self.get_image()
                        if ret:
                            image_data = image

                    # Save state data to CSV
                    with open(state_data_path, mode='a', newline='') as csv_file:
                        print('saving', state)
                        fieldnames = list(state.keys())
                        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                        if csv_file.tell() == 0:
                            writer.writeheader()
                        writer.writerow(state)

                    # Save lidar data to JSON
                    if lidar_data:
                        with open(lidar_data_path, mode='a') as json_file:
                            json_file.write(json.dumps(lidar_data) + '\n')

                    # Append image to the HDF5 dataset
                    if image_data is not None:
                        # Resize the dataset to accommodate a new image
                        dataset.resize(dataset.shape[0] + 1, axis=0)  # Increase the size by 1 along the first dimension
                        dataset[-1] = image_data  # Append the new image to the dataset
                        images_received += 1

                        # Manually flush the data to disk after adding an image
                        dataset.flush()

                    time.sleep(1)
            except KeyboardInterrupt:
                print("Process interrupted. Flushing data to disk...")
                dataset.flush()  # Ensure data is saved to disk on exit
            


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

    def get_state(self):
        return self._state

    def get_control_mode(self):
        """
        Get control mode data from the Surveyor connection object.

        Returns:
            Control mode string.
        """
        # control_mode = None
        # while not control_mode:
        #     control_mode = hlp.get_control_mode(self.receive())
        control_mode = self._state.get('Control Mode', 'Unknown')

        return control_mode
    
    def get_gps_coordinates(self):
        """
        Get GPS coordinates from the Surveyor connection object.

        Returns:
            Tuple containing GPS coordinates.
        """
        # coordinates = None
        # gga_message = None
        # while (coordinates == None) or (gga_message == None):
        #     gga_message = hlp.get_gga(self.receive())
        #     coordinates = hlp.get_coordinates(gga_message)

        return (self._state.get('Latitude', 0.0),
                self._state.get('Longitude', 0.0))
    
    # def get_command_status(self):
    #     control_mode = None
    #     control_mode_mesagge = None
    #     while (control_mode == None) or (control_mode_mesagge == None):
    #         control_mode_mesagge = hlp.get_command_status_message(self.receive())
    #         control_mode = hlp.get_command_status(control_mode_mesagge)

    #     return control_mode
    

    # def get_attitude(self):
    #     """
    #     Get Attitude information from the Surveyor connection object.

    #     Returns:
    #         Tuple containing heading.
    #     """
    #     heading = None
    #     attitude_message = None
    #     while (heading == None) or (attitude_message == None):
    #         attitude_message = hlp.get_attitude_message(self.receive())
    #         attitude = hlp.get_attitude(attitude_message)

    #     return attitude
    
    def get_exo2_data(self):
        """
        Retrieve data from the EXO2 sensor.

        Returns:
           list: A list of float values representing the data from the Exo2 sensor.
        """
        return self.exo2.get_exo2_data()
    
    def get_data(self, keys=['state', 'exo2']):
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
            'exo2': self.get_exo2_data, # Dictionary with Exo2 sonde data
            'state': self.get_state,
            'camera': self.get_image,
            'lidar' : self.get_lidar_data
        }
        data_labels = {
            'camera' : ['Image ret', 'Image'],
            'lidar': ['Distances', 'Angles']
        }

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
    
    def get_lidar_data(self):
        """
        Retrieve the lidar measurements.

        Returns:
            tuple: A 360 list containing the lidar measurements 
                and a list with their corresponding angles [0-360] degrees.
        """
        return self.lidar.get_data()

    

