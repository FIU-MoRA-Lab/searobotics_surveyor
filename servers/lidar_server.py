import numpy as np
import matplotlib.pyplot as plt
from rplidar import LidarWrapper
import time
import threading
import io
from flask import Flask, Response, jsonify
import argparse

# Global variables
LIDAR_MEASUREMENTS = []
FIG = None
SCATTER = None
ANGLES = None
N = None

def initialize_and_start(lidar_port, baudrate, n):
    """
    Initialize the Lidar and start data collection in a separate thread.
    
    Args:
    lidar_port (str): The port for the Lidar device (e.g., '/dev/ttyUSB0').
    baudrate (int): The baud rate for the Lidar communication.
    n (int): The step size for data averaging.
    """
    global FIG, SCATTER, ANGLES, N
    
    # Initialize the Lidar
    lidar = LidarWrapper(lidar_port, baudrate)

    def _data_getter():
        """Thread function to continuously collect Lidar data."""
        global LIDAR_MEASUREMENTS
        while True:
            LIDAR_MEASUREMENTS = lidar.get_scan_data()
            time.sleep(0.05)

    # Start data collection in a separate thread
    get_thread = threading.Thread(target=_data_getter)
    get_thread.daemon = True
    get_thread.start()

    # Setup the plot
    FIG = plt.figure(figsize=(6, 6))
    ax = FIG.add_subplot(111, polar=True)
    SCATTER = ax.scatter([], [], c='b', s=10+n)  # LIDAR trace
    ax.set_ylim(0, 2)  # Adjust max range to your LIDAR's range
    ax.set_theta_offset(np.pi / 2)  # Set 0 degree to the top
    N = n
    ANGLES = np.deg2rad(np.arange(0, 360, N))  # Convert angles to radians

def filter(arr):
    """
    Calculate the median of an array of values, considering only non-zero elements.
    
    Args:
    arr (np.array): The array of distance measurements.
    
    Returns:
    float: The median of the non-zero values, or 0 if all values are zero.
    """
    return np.min(arr) if np.any(arr != 0) else 0

def process_lidar_data(n=1):
    """
    Process Lidar data by applying a median filter over chunks of data.
    
    Args:
    n (int): The number of elements to average over.
    
    Returns:
    np.array: The processed Lidar data.
    """
    if len(LIDAR_MEASUREMENTS) == 0:
        return np.array([])

    # Reshape data into chunks and apply median filtering
    averaged = np.asarray(LIDAR_MEASUREMENTS).reshape(-1, n)
    averaged[averaged == 0.0] = 20.0  # Replace zero values with a maximum placeholder
    return np.apply_along_axis(filter, arr=averaged, axis=1)

app = Flask(__name__)

def generate_mjpeg_stream():
    """
    Generates an MJPEG stream of the Lidar data.
    
    Yields frames in JPEG format for streaming.
    """
    while True:
        # start_time = time.time()
        distances = process_lidar_data(N)  # Process the Lidar data
        # processing_time = time.time() - start_time
        # print(f"Processing time: {processing_time:.4f} seconds")

        # Update the scatter plot with the processed data
        SCATTER.set_offsets(np.c_[ANGLES, distances])
        plt.draw()  # Refresh the plot

        # Save the figure to a buffer
        buf = io.BytesIO()
        FIG.savefig(buf, format='jpeg')
        # save_time = time.time() - processing_time - start_time
        # print(f"Save time: {save_time:.4f} seconds")
        
        buf.seek(0)
        frame = buf.read()

        # Yield the frame as MJPEG data
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """
    Displays a message indicating that the stream is online.
    """
    return 'RPLidar stream online!'

@app.route('/video_feed')
def video_feed():
    """
    Route to stream the MJPEG video feed.
    """
    return Response(generate_mjpeg_stream(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data')
def vector():
    """
    Route to fetch the raw Lidar data as JSON.
    """
    return jsonify(LIDAR_MEASUREMENTS)

def main(host, port, lidar_port, baudrate, n):
    """
    Start the Flask server and initialize Lidar data collection.
    
    Args:
    host (str): The host IP address.
    port (int): The port number for the Flask server.
    lidar_port (str): The port for the Lidar device.
    baudrate (int): The baud rate for the Lidar communication.
    n (int): The step size for data averaging.
    """
    initialize_and_start(lidar_port, baudrate, n)
    app.run(debug=False, port=port, host=host)

if __name__ == '__main__':
    # Argument parsing for configuring the server
    parser = argparse.ArgumentParser(description='Lidar Streaming Server with Flask')
    
    parser.add_argument('--host', type=str, default='172.17.0.1', help='Host IP (default: 172.17.0.1).')
    parser.add_argument('--port', type=int, default=5002, help='Port number (default: 5002).')
    parser.add_argument('--lidar_port', type=str, default='/dev/ttyUSB0', help='Lidar serial port (default: /dev/ttyUSB0).')
    parser.add_argument('--baudrate', type=int, default=1000000, help='Lidar baud rate (default: 1000000).')
    parser.add_argument('--n', type=int, default=1, help='Number of elements to average (default: 1).')
    
    # Parse arguments and start the server
    args = vars(parser.parse_args())
    main(args['host'], args['port'], args['lidar_port'], args['baudrate'], args['n'])
