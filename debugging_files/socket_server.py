import serial

ser = serial.Serial('/dev/pts/4', 9600, timeout=1)
print("Server is listening on /dev/pts/4")

while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        print(f"Received: {data}")
        ser.write(b"Echo: " + data.encode('utf-8') + b"\n")
        ser.write(b"Second line" + b"\n")

