# 🌊 Sea Robotics Surveyor

This repository provides a simplified implementation to operate the Sea Robotics Surveyor-class Autonomous Surface Vehicle (ASV). It wraps client-server communication for sensors like the YSI Exo2 and LIDAR, and offers utilities for setup and debugging.

This is a lightweight version of the full [FIU MoRA Lab Surveyor Automation Repository](https://github.com/FIU-MoRA-Lab/searobotics_surveyor_automation).

---

## 📚 Table of Contents
- [Prerequisites](#-prerequisites)
- [Repository Structure](#package-contents)
- [Installation and Set-up](#️⚙️-installation-and-set-up)
- [Usage](#usage)
- [Media](#media)
- [Documentation](#📄-package-documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#🤝-contributing)
- [Related Links](#related-links)


## 🔧 Prerequisites

**Hardware Required:**
- Sea Robotics Surveyor-Class ASV
- YSI EXO2 Multiparameter Sonde
- RS-232 to USB Adapter
- Sea Robotics Sonde Adapter & Network Equipment
- Raspberry Pi 4 or DAC (Windows PC)
- Companion laptop connected to the Surveyor network

# Package Contents
## `surveyor_lib/surveyor.py`
Implementation of the main class `Surveyor` managing the boat, allows access to its sensors: IMU, lidar, camera, exo2, as it permits an easy control of the boat. 
## `surveyor_lib/clients`
Each sensor implements a structure server-client to broadcast its data. The clients manage the data as their unique class to be easily accesible by the user and integrate, this classes are used by the boat to retreive sensor data.
## `surveyor_lib/helpers`
Each sensor implements a structure server-client to broadcast its data. The clients manage the data as their unique class to be easily accesible by the user.
## `surveyor_lib/servers` 
As said before each client has a server counterpart in charge of retreiving the information from the sensor and broadcasting it into an ip:port address.
## `debugging`
Files intended to test specific capabilities; they have no use in the library itself. In the future, they will be deprecated.
## `requirements`
.txt files containing the essential Python packages to be installed in order to execute any file contained in the `servers` folder.  

## ⚙️ Installation and Set-up

### 1. Surveyor Setup

1. Clone this repository to the device connected to the Surveyor's LAN (e.g., Raspberry Pi, DAC).
2. Assign a static IP to your device if not done already.
3. Connect the Sonde to the Surveyor using the adapters provided.
4. Power on all hardware: Surveyor, antenna, network box, and laptop.
5. On the laptop, launch the SeaRobotics GUI and power on the Sonde.

---

### 2. DAC Setup

1. Connect via Remote Desktop to `192.168.0.68`.
2. Copy `exo2_server.py` and `requirements_exo2_dac.txt` to the desktop.
3. Install dependencies:
```bash
    pip3 install -r requirements_exo2_dac.txt
```

## 3. Raspberry Pi set-up

### 3.1 Easy set-up

From the `requirements` folder copy the file `setup_pi.py` to the raspberry pi's desktop and execute it by running (if everything is successful you may the Manual set-up section):
```bash
     python3 setup_pi.py
```

### 3.2 Manual set-up
0. Set the Pi with Raspbian OS 64 bits and create a virtual envionment with prefered Python3.11.
1. Make the rasberry Pi to have the static ip address `192.168.0.20` for the ethernet connection.
2. Using the companion laptop, access the Raspberry Pi by making a remote connection to the address `192.168.0.20` (address set beforehand).
3. From the `servers` folder, copy the files `camera_server.py`, `requirements_pi.txt` `lidar_server.py` and `rplidar.cpython-311-arm-linux-gnueabihf.so` (for arm processors) or `rplidar.cpython-311-x86-linux-gnueabihf.so` (for x86 processors) into the Pi.
4. Install Python and the necessary packages. To do so run

```bash
     pip3 install -r requirements_camera.txt
```

# Media
- Coming soon

# Usage
## 🧭 Recommended Project Layout
Clone this repository into a subfolder (e.g., surveyor_library/).

For any application `your_application.py` you want to develop, the following structure is recommended
```
your_project/
├── surveyor_library/
└── your_application.py
```
Where this repo was cloned into the `surveyor_library` folder.
## 🐍 Example Imports

To use the library you can call it in `your_application.py` preamble as
```python
from surveyor_library.surveyor_lib import Surveyor, helpers
```
or
```python
import sys
sys.path.append('./surveyor_library')

from surveyor_lib import Surveyor, helpers
```


## 🛠️ Before Running Your App 
Make sure to start:

1.`exo2_server.py` on the DAC.
2.`camera_server.py` and `lidar_server.py` on the Pi.

# 📄 Package Documentation

For more detailed information, refer to the following linked markdown files:

- [Surveyor Class](surveyor_lib/docs/Surveyor.md)
- [Helpers](surveyor_lib/ddocs/helpers.md)
- [Sensor Clients](surveyor_lib/docs/clients.md)
- [Sensor Servers](surveyor_lib/docs/servers.md)
- [Testing](surveyor_lib/docs/tests.md)

# 🤝 Contributing

We welcome contributions to improve this repository! To ensure consistency and maintain code quality, please follow these guidelines:

1. Before committing your changes, run the following commands to format and lint the code:
     ```bash
     black .
     isort .
     flake8 .
     ```

2. Run the test suite to verify that your changes do not break existing functionality:
     ```bash
     pytest surveyor_lib/tests --verbose
     ```

3. Push your changes with a clear description of the changes and the problem or feature you solved.

Thank you for contributing!

# Troubleshooting
Coming soon. Common issues will be documented here.

# Related Links
- EXO2 Multiparameter Sonde (https://www.ysi.com/exo2)
- Sea Robotics Surveyor (https://www.searobotics.com/products/autonomous-surface-vehicles/sr-surveyor-class)


