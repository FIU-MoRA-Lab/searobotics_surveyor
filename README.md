# Sea Robotics Surveyor
This repository contains the basic implementation to operate the sea robotics ASV by exposing basic commands and utilities.
Particularly, it is a simplification of [this repo](https://github.com/FIU-MoRA-Lab/searobotics_surveyor_automation). 

# Table of Contents
- [Prerequisites](#Prerequisites)
- [Package Contents](#Package-Contents)
- [Installation and Set-up](#Installation-and-Set-up)
- [Usage](#usage)
- [Features](#features)
- [Troubleshooting](#Troubleshooting)
- [Related Links](#Related-Links)

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

# Package Contents
## `clients`
Each sensor implements a structure server-client to broadcast its data. The clients manage the data as their unique class to be easily accesible by the user.
## `debugging_files`
Files intended to test specific capabilities; they have no use in the library itself. In the future, they will be deprecated.
## `servers` 
As said before each client has a server counterpart in charge of retreiving the information from the sensor and broadcasting it into an ip:port address.
## `requirements`
.txt files containing the essential Python packages to be installed in order to execute any file contained in the `servers` folder.  

# Installation and Set-up

1. Clone this repository to your device connected to the Local Area Network e.g. Raspberry Pi, DAC computer.
2. Assign an unused fixed IP Address to your device (if not assigned previously).
3. Connect the Sonde to the Surveyor using the serial to USB adapter and the Sonde adapter.
4. Power on the Surveyor, network box, Antenna, and provided network attached laptop.
5. Using the companion laptop, load the SeaRobotics software and power on the Exo2 Sonde.
6. Using the companion laptop, access the DAC (windows computer with black background) by making a remote connection to the address `192.168.0.68` (it should be preset by default).
7. From the `servers` folder, copy the file `exo2_server.py` and `servers/requirements_exo2_dac.txt` into the DAC desktop and install Python and the necessary packages. To do so run
```bash
    pip3 install -r requirements_exo2_dac.txt
```
8. Using the companion laptop, access the Raspberry Pi by making a remote connection to the address `192.168.0.20` (the Pi should have this static address set beforehand).
9. From the `servers` folder, copy either the file `picamera_server.py` or the file `picamera_server_flask.py` and `servers/requirements_camera.txt` into the Pi and install Python and the necessary packages. To do so run
```bash
    pip3 install -r requirements_camera.txt
```
# Media
- Coming soon

# Usage
- For any application `your_application.py` you want to develop, the following structure is recommended
```
your_project/
├── surveyor_library/
└── your_application.py
```
Where this repo was cloned into the `surveyor_library` folder.

- Before running every application, make sure that `exo2_server.py` and either `picamera_server.py` or `picamera_server_flask.py` are running on their respective devices.

# Troubleshooting
Comming soon

# Related Links
- EXO2 Multiparameter Sonde (https://www.ysi.com/exo2)
- Sea Robotics Surveyor (https://www.searobotics.com/products/autonomous-surface-vehicles/sr-surveyor-class)

