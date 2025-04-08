import time

import serial

ser = serial.Serial("/dev/pts/5", 9600, timeout=1)
print("Client is connected to /dev/pts/5")

time.sleep(0.2)  # Give some time for the server to start

ser.write(b"Hello from client\n")
time.sleep(0.1)
response = ser.readlines()
# response2 = ser.readline().decode('utf-8').strip()
print(f"Response: {response} ")
