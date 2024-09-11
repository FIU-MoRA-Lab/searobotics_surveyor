import http.server
import socketserver
import sys
import serial

class Exo2Server(http.server.SimpleHTTPRequestHandler):
    com_port = "COM4"  # Default values
    baud_rate = 9600
    port = 5000
    timeout = 0.1
    serial_connection = None

    @classmethod
    def initialize_serial(cls):
        """
        Initialize the serial connection with the given parameters.
        """
        print('Initializing serial connection')
        cls.serial_connection = serial.Serial(
            cls.com_port, cls.baud_rate, timeout=cls.timeout,
            bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE, xonxoff=False, rtscts=False)

    def send_and_receive_serial_command(self, command):
        """
        Send a command to the serial port and receive the response.

        Args:
            command (bytes): The command to send.

        Returns:
            bytes: The response from the serial device.
        """
        try:
            self.serial_connection.write(command)
            self.serial_connection.readline().strip()  # Read the command echo
            data = self.serial_connection.readline().strip()  # Read the actual data
            return data
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
            return b'Error in serial communication'
        
    def handle_command(self, command_received):
        """
        Handles incoming commands.
        
        Args:
            command_received (bytes): The command received from the serial connection.
        
        Returns:
            bytes: Response message based on the command received.
        """
        if command_received == b'init\r':
            # Handles init command (handcrafted command, not exo2 command)
            try:
                if self.serial_connection.is_open:
                    self.serial_connection.close()
                Exo2Server.initialize_serial()
                data = b'Exo2 serial connection initialized'
            except Exception as e:
                # Log the exception if needed: print(f"Exception: {e}")
                data = b'Error opening Exo2 serial socket'
        else:
            # Handles any other command (exo2 commands)
            data = self.send_and_receive_serial_command(command_received)
        
        return data


    def send_response_to_client(self, response_code, data):
        """
        Send a response to the client.

        Args:
            response_code (int): The HTTP response code.
            data (bytes): The data to send in the response body.
        """
        self.send_response(response_code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        """
        Handle GET requests.
        """
        if not self.serial_connection.is_open:
            Exo2Server.initialize_serial()

        if self.path == '/data':
            data = self.send_and_receive_serial_command(b'data\r')
            self.send_response_to_client(200, data)
        else:
            self.send_response_to_client(404, b'Not found')

    def do_POST(self):
        """
        Handle POST requests.
        """
        if not self.serial_connection.is_open:
            Exo2Server.initialize_serial()

        if self.path == '/data':
            content_length = int(self.headers['Content-Length'])
            command_received = self.rfile.read(content_length) + b'\r'
            data = self.handle_command(command_received)
            self.send_response_to_client(200, data)
        else:
            self.send_response_to_client(404, b'Not found')

def main():
    """
    Main function to start the server.
    """
    try:
        Exo2Server.initialize_serial()
        with socketserver.TCPServer(("", Exo2Server.port), Exo2Server) as server:
            print(f"Serving at port {Exo2Server.port}, reading from {Exo2Server.com_port} at {Exo2Server.baud_rate} baud with a timeout of {Exo2Server.timeout} seconds.")
            server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        Exo2Server.serial_connection.close()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        if Exo2Server.serial_connection and Exo2Server.serial_connection.is_open:
            Exo2Server.serial_connection.close()
        sys.exit(1)

if __name__ == "__main__":
    args = {
        'port': 5000,
        'com_port': 'COM4',
        'baud_rate': 9600,
        'timeout': 0.1
    }

    print("Usage: server.py <port> <com_port> <baud_rate> <timeout>\n" \
          f"Default values: {args}")

    if len(sys.argv) > 0:
        args.update(zip(args.keys(), sys.argv[1:]))

    Exo2Server.port = int(args['port'])
    Exo2Server.com_port = args['com_port']
    Exo2Server.baud_rate = int(args['baud_rate'])
    Exo2Server.timeout = float(args['timeout'])

    main()
