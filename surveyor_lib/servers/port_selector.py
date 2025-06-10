import subprocess

attached_line = "now attached to"


def get_dmesg_ttyusb_lines():
    # Execute the command and capture output
    result = subprocess.run(
    "sudo dmesg | grep ttyUSB", capture_output=True, text=True, check=True, shell=True
    )
    # Filter lines containing 'ttyUSB'
    lines = [line for line in result.stdout.splitlines()]
    # lines = ["[12345.678901] usb 1-1: FTDI USB Serial Device converter now attached to ttyUSB0\n",
    # "[12345.678902] usb 1-2: Prolific USB-to-Serial Comm Port converter now attached to ttyUSB1\n",
    # "[12345.678903] usb 1-3: CP210x USB to UART Bridge Controller converter now attached to ttyUSB2\n"]
    # Return lines from last to first
    return lines[::-1]


def get_serial_port(keyword):
    """
    Get the serial port from dmesg output that contains the specified keyword.

    Args:
        keyword (str): The keyword to search for in the dmesg output.

    Returns:
        str: The serial port if found, otherwise None.
    """
    print(f"Searching for serial port in dmesg output...")
    lines = get_dmesg_ttyusb_lines()
    for line in lines:
        if (keyword in line) and (attached_line in line):
            # Extract the serial port from the line
            parts = line.split()
            for part in parts:
                if part.startswith("ttyUSB"):
                    serial_port = "/dev/" + part
                    print(f"Found serial port: {serial_port}")
                    return serial_port
    print(f"No serial port found with keyword '{keyword}' in dmesg output.")
    return None


if __name__ == "__main__":
    for line in get_dmesg_ttyusb_lines():
        print(line)
    print(
        get_serial_port("cp210x")
    )  # Example usage, searching for FTDI devices
