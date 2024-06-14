# Sea Robotics Surveyor
This repository contains the basic implementation to operate the sea robotics ASV by exposing basic commands and utilities.

## Prerequisites

To run the code in this repository, you will need the following hardware components:

- Raspberry Pi board (e.g., Raspberry Pi 4)
- YSI Exo2 Multiparameter Sonde
- RS 232 Serial to USB Adapter
- Sea Robotics YSI Sonde Adapter
- Sea Robotics Surveryor Class Unammed Surface Vehicle
- Sea Robotics provided network attached laptop.
- Sea Robotics network box.
- Sea Robotics network antenna

Python pip packages: Coming soon

## Getting Started

1. Clone this repository to your Raspberry Pi.
2. Connect the Raspberry Pi to the Surveyor's Local Area Network
3. Assign an unused fixed IP Address to the Raspberry Pi.
4. Connect the Sonde to the Surveyor using the serial to usb adapter and the sonde adapter.
5. Power on the Surveyor, network box, Antenna, and provided network attached laptop.
6. Using the laptop, load the SeaRobotics software and power on the Exo2 Sonde.
7. On the Raspberry Pi, execute the desired python script.

## Media
- Coming soon

## Usage

- The Raspberry Pi can send commands to the surveyor using NMEA messages via Python scripts.

- The python scripts can send navigatio and data retrieval commands.

- The collected data can be processed and stored locally in a CSV file.

## Related Links
- EXO2 Multiparameter Sonde(https://www.ysi.com/exo2)
- Sea Robotics Surveyor (https://www.searobotics.com/products/autonomous-surface-vehicles/sr-surveyor-class)

