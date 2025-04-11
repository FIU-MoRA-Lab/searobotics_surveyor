import argparse
import platform
import re

import serial
from flask import Flask, jsonify, request

app = Flask(__name__)

# Global variables for serial connection
serial_connection = None
COM_PORT = "COM4" if platform.system() == "Windows" else "/dev/ttyUSB1"
BAUD_RATE = 9600
TIMEOUT = 0.1


def initialize_serial():
    """
    Initialize the serial connection with the given parameters.
    """
    global serial_connection
    print("Initializing serial connection...")
    serial_connection = serial.Serial(
        COM_PORT,
        BAUD_RATE,
        timeout=TIMEOUT,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=False,
        rtscts=False,
    )


def send_and_receive_serial_command(command):
    """
    Send a command to the serial port and receive the response.

    Args:
        command (bytes): The command to send.

    Returns:
        bytes: The response from the serial device.
    """
    try:
        serial_connection.write(command)
        data = serial_connection.readline().strip()  # Read the command echo
        if (
            not data
            or data.startswith(b"#")
            or bool(re.search(r"[a-zA-Z]", data.decode("utf-8")))
        ):
            data = serial_connection.readline().strip()  # Read the actual data
        return data
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
        return b"Error in serial communication"


@app.route("/data", methods=["GET", "POST"])
def handle_data():
    """
    Handle GET and POST requests for the /data endpoint.

    - GET: Fetch data from the Exo2 sensor.
    - POST: Send a command to the Exo2 sensor and return the response.

    Returns:
        Response: JSON response containing the data or error message.
    """
    if not serial_connection.is_open:
        initialize_serial()

    if request.method == "GET":
        # Handle GET request to fetch data
        data = send_and_receive_serial_command(b"data\r")
        return jsonify({"data": data.decode("utf-8")})

    elif request.method == "POST":
        # Handle POST request to send a command
        command = request.data + b"\r"
        if command == b"init\r":
            # Special case for the "init" command
            if serial_connection.is_open:
                return jsonify({"message": "Connection Initialized"})
            else:
                return jsonify({"error": "Error opening socket"}), 500
        else:
            # Handle other commands
            data = send_and_receive_serial_command(command)
            return jsonify({"response": data.decode("utf-8")})


@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint to verify the server and serial connection status.

    Returns:
        Response: JSON response indicating the health status.
    """
    return jsonify({"status": "ok", "serial_open": serial_connection.is_open})


def main():
    """
    Main function to start the Flask server.
    """
    try:
        initialize_serial()
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down server.")
        if serial_connection and serial_connection.is_open:
            serial_connection.close()
    except Exception as e:
        print(f"Error: {e}")
        if serial_connection and serial_connection.is_open:
            serial_connection.close()


if __name__ == "__main__":
    # Add arguments
    parser = argparse.ArgumentParser(
        description="Flask-based server for Exo2 serial communication."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port number (default: 5000).",
    )
    parser.add_argument(
        "--com_port",
        type=str,
        default=("COM4" if platform.system() == "Windows" else "/dev/ttyUSB1"),
        help="COM port (default: COM4 for Windows, /dev/ttyUSB1 for Linux).",
    )
    parser.add_argument(
        "--baud_rate",
        type=int,
        default=9600,
        help="Baud rate (default: 9600).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=0.1,
        help="Timeout in seconds (default: 0.1).",
    )

    # Parse the command line arguments
    args = vars(parser.parse_args())

    # Update global variables
    COM_PORT = args["com_port"]
    BAUD_RATE = args["baud_rate"]
    TIMEOUT = args["timeout"]

    # Start the server
    main()
