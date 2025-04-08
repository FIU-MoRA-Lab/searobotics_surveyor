import csv
import os
import time
from datetime import datetime

import pandas as pd
import serial


def main():
    """
    Main function to read data from a serial port, process it, and save it to a CSV file.
    """
    # Serial port configuration
    serial_port = "COM4"
    baudrate = 9600

    # Commands to send to the device
    command1 = b"data\r\n"
    command2 = b"data\r"
    command3 = b"data\n"
    command4 = b"ssn\r"

    # Establishing serial connection
    ser = serial.Serial(
        port=serial_port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=False,  # Disable software flow control
        rtscts=False,  # Disable hardware (RTS/CTS) flow control
        timeout=0.05,  # Read timeout
    )
    print("Serial connection opened")

    # Columns for the CSV file
    columns = [
        "Date",
        "Time",
        "DO (sat)",
        "DO (mg/l)",
        "Temp (C)",
        "Cond (muS/l)",
        "sal (psu)",
        "Pressure (psi a)",
        "Depth (m)",
    ]

    # List to store DataFrame objects
    data_frame_list = []

    # CSV filename with current timestamp
    csv_filename = (
        "exo_data_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
    )

    # Check if the file exists
    file_exists = os.path.isfile(csv_filename)

    try:
        while True:
            ser.write(command4)  # Send command to the device
            row = ser.readline().decode()  # Read the response

            # Create a dictionary from row data and column names
            new_row = {
                column: data
                for data, column in zip(
                    row.strip().split(","),
                    columns,
                )
            }

            # Append the dictionary to the list
            data_frame_list.append(pd.DataFrame([new_row]))

            # Concatenate all DataFrame objects in the list
            combined_data_frame = pd.concat(data_frame_list, ignore_index=True)

            # Write data to CSV file
            with open(csv_filename, "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    combined_data_frame.to_csv(csvfile, index=False)
                    file_exists = True
                else:
                    combined_data_frame.to_csv(
                        csvfile,
                        index=False,
                        header=False,
                    )

            data_frame_list.clear()  # Clear the list for the next iteration

    except KeyboardInterrupt:
        print("Serial connection closed by user")
    finally:
        ser.close()  # Close the serial connection
        print("Serial connection closed")


if __name__ == "__main__":
    main()
