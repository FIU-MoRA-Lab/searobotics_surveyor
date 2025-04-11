import socket
import time


def main():
    """
    Main function to send multiple messages over a TCP/IP socket connection.
    """
    HOST = "192.168.0.50"
    PORT = 8001

    # Establishing a TCP socket connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    # List of messages to be sent
    messages = [
        "$PSEAC,L,000,000,000,*14\r\n",
        "$PSEAC,F,005,000,000,*1B\r\n",
        "$PSEAR,0,000,10,0,000*7F\r\n",
        "$OIWPL,2545.4912,N,08022.4373,W,0*7B\r\n",
        "$OIWPL,2545.4912,N,08022.4373,W,1*7A\r\n",
        "$OIWPL,2545.4884,N,08022.4371,W,2*75\r\n",
        "$OIWPL,2545.4942,N,08022.4374,W,3*7A\r\n",
        "$PSEAC,F,000,000,000,*1E\r\n",
    ]

    print("Number of messages to be sent: " + str(len(messages)))

    # Sending each message and waiting for 1 second between each send
    for msg in messages:
        s.send(msg.encode())
        print(msg)
        time.sleep(1)

    print("All messages sent.")

    # Receiving data from the server
    data = s.recv(1024)
    s.close()
    print("Received:", data)


if __name__ == "__main__":
    main()
