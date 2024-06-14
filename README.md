# Sea Robotics Surveyor
This repository contains the basic implementation to operate the sea robotics ASV by exposing basic commands and utilities.
Particularly, it is a simplification of [this repo](https://github.com/FIU-MoRA-Lab/searobotics_surveyor_automation). 

# Table of Contents
- [Prerequisites](#Prerequisites)
- [Installation and Set-up](#Installation-and-Set-up)
- [Usage](#usage)
- [Features](#features)

# Prerequisites

To run the code in this repository, you will need the following hardware components:

- Raspberry Pi board (e.g., Raspberry Pi 4)
- YSI Exo2 Multiparameter Sonde
- RS 232 Serial to USB Adapter
- Sea Robotics YSI Sonde Adapter
- Sea Robotics Surveyor Class Unammed Surface Vehicle
- Sea Robotics provided network attached laptop.
- Sea Robotics network box.
- Sea Robotics network antenna

Python pip packages: Coming soon

# Installation and Set-up

1. Clone this repository to your device connected to the Local Area Network e.g. Raspberry Pi, DAC computer.
2. Assign an unused fixed IP Address to your device (if not assigned previously).
3. Connect the Sonde to the Surveyor using the serial to USB adapter and the Sonde adapter.
4. Power on the Surveyor, network box, Antenna, and provided network attached laptop.
5. Using the companion laptop, load the SeaRobotics software and power on the Exo2 Sonde.
6. Using the companion laptop, access the DAC (windows computer with black background) by making a remote connection to the address `192.168.0.68` (it should be preset by default).
7. From the `server_files` folder, copy the file `exo2_server.py` into the DAC desktop and install Python and the necessary packages to run it.
8. Using the companion laptop, access the Raspberry Pi by making a remote connection to the address `192.168.0.20` (the Pi should have this static address set beforehand).
9. From the `server_files` folder, copy either the file `exo2_server.py` into the
10. On the Raspberry Pi, execute the desired Python script.

# Media
- Coming soon

# Usage

- The Raspberry Pi can send commands to the surveyor using NMEA messages via Python scripts.

- The python scripts can send navigatio and data retrieval commands.

- The collected data can be processed and stored locally in a CSV file.

## Related Links
- EXO2 Multiparameter Sonde(https://www.ysi.com/exo2)
- Sea Robotics Surveyor (https://www.searobotics.com/products/autonomous-surface-vehicles/sr-surveyor-class)

