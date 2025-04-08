import socket
import sys
import time


def send_commands_to_device():
    """
    Sends commands to a device over TCP/IP socket.

    This function connects to a device at a specific IP address and port,
    sends commands to it, and receives data from the device.
    """

    # Device IP address and port
    HOST = "192.168.0.50"
    PORT = 8001

    # Establishing TCP connection
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
    except socket.error as err:
        print(
            "Socket creation failed with error:",
            err,
        )
        sys.exit()

    # Sending commands to the device
    try:
        # Command to turn GPS on
        msg = "$PSEAC,L,0,0,0,GPS_ON*0E\r\n"
        s.send(msg.encode())

        # Delay to allow the device to process the command
        time.sleep(1)

        # Command to turn SONAR on
        msg = "$PSEAC,L,0,0,0,SONAR_ON*0B"
        s.send(msg.encode())

        # Receiving data from the device
        data = s.recv(1024)
        print("Received:", data)

    except socket.error as err:
        print(
            "Socket send/receive failed with error:",
            err,
        )

    finally:
        # Closing the socket connection
        s.close()


if __name__ == "__main__":
    send_commands_to_device()
