#!/usr/bin/env python3

import os
import subprocess
import urllib.request
import sys
import shutil

# Get the user's home directory
home_dir = os.path.expanduser("~")
current_directory = os.path.dirname(os.path.realpath(__file__))

# Define necessary URLs and paths for the setup
base_git_repo_url = "https://raw.githubusercontent.com/FIU-MoRA-Lab/searobotics_surveyor/refs/heads/main"
reqs_url = f"{base_git_repo_url}/requirements/requirements_pi.txt"  # URL of the reqs.txt file
requirements_filename = reqs_url.split('/')[-1]
virtualenv_path = f"{current_directory}/surveyor_env"  # Path to the virtual environment
bashrc_script = f"{home_dir}/.bashrc"  # The .bashrc file

python_scripts_urls = [
    f"{base_git_repo_url}/servers/camera_server.py",
    f"{base_git_repo_url}/servers/lidar_server.py",
    f"{base_git_repo_url}/servers/exo2_server.py",
]
# Add more script URLs here as needed
python_scripts = [f"{current_directory}/{script.split('/')[-1]}" for script in python_scripts_urls]


# Step 0: Update and upgrade the system
def update_system():
    print("Updating and upgrading the system...")
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(["sudo", "apt-get", "upgrade", "-y"], check=True)
    print("System updated and upgraded.")

# Step 1: Download the requirements file (requirements_pi.txt)
def download_requirements():
    print(f"Downloading {requirements_filename}...")
    urllib.request.urlretrieve(reqs_url, requirements_filename)
    
    
# Step 2: Create a Python 3.11 virtual environment
def create_virtualenv():
    if not os.path.exists(virtualenv_path):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", virtualenv_path, "--system-site-packages"])

# Step 3: Install the dependencies from the requirements file into the virtual environment
def install_requirements():
    print("Installing dependencies from requirements_pi.txt...")
    subprocess.run([f"{virtualenv_path}/bin/pip", "install", "-r", requirements_filename])

# Step 4: Add the virtual environment activation to terminal startup (in .bashrc)
def update_bashrc():
    print("Adding virtual environment activation to terminal startup...")
    with open(bashrc_script, "a") as bashrc:
        bashrc.write(f"\n# Activate virtual environment at terminal startup\n")
        bashrc.write(f"source {virtualenv_path}/bin/activate\n")

# Step 5: Download the Python scripts from the repository
def download_python_scripts():
    print("Downloading Python scripts...")
    for script_url in python_scripts_urls:
        script_name = script_url.split('/')[-1]
        print(f"Downloading {script_name}...")
        urllib.request.urlretrieve(script_url, f"{current_directory}/{script_name}")

# Step 6: Install dependencies (cmake, pybind11)
def install_dependencies():
    try:
        print("Installing cmake via apt-get...")
        subprocess.run(["sudo", "apt-get", "install", "-y", "cmake"], check=True)
        print("Installing pybind11 via apt-get...")
        subprocess.run(["sudo", "apt-get", "install", "-y", "pybind11-dev"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")

# Step 7: Compile the lidar package from source
def compile_lidar_package():
    try:
        print("Trying to compile the lidar package from source...")
        # Clone the repository and recurse submodules
        subprocess.run("git clone --recurse-submodules https://github.com/FIU-MoRA-Lab/rplidar_python.git", shell=True, check=True)

        # Change the directory to rplidar_python
        os.chdir("rplidar_python")

        # Run the 'make' command on the rplidar_sdk directory
        subprocess.run("make -C ./rplidar_sdk", shell=True, check=True)

        # Run cmake to generate build files
        subprocess.run("cmake -S . -B build -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=../", shell=True, check=True)

        # Build the project
        subprocess.run("cmake --build build", shell=True, check=True)

        # Remove the build directory
        subprocess.run("rm -rf build", shell=True, check=True)

        print("Important!!!!!!!!!!!!!!\nCopy the generated .so file from the folder 'rplidar_python' into the desktop.")
    except Exception as e:
        print(f"Error occurred while compiling lidar library: {e}")
        print("Refer to: https://github.com/FIU-MoRA-Lab/rplidar_python")

# Step 8: 
def set_static_ip():
    print("Setting static IP address...")
    with open("/etc/dhcpcd.conf", "a") as dhcpcd:
        dhcpcd.write("interface eth0\n")
        dhcpcd.write("static ip_address=192.168.0.20")



# Main script execution
def main():
    print("Starting setup process...")
    print("Do not install picamera2 using pip3; if so, uninstall it (weird performance issues)")
    
    # Update and upgrade the system
    update_system()

    # Download the requirements file
    download_requirements()
    
    # Create the virtual environment
    create_virtualenv()
    
    # Install the dependencies from requirements.txt
    install_requirements()
    
    # Add virtual environment activation to bashrc
    update_bashrc()
    
    # Download necessary Python scripts
    download_python_scripts()
    
    # Install system dependencies (cmake, pybind11)
    install_dependencies()
    
    # Compile the lidar package
    compile_lidar_package()

    # Set static IP address
    set_static_ip()
    
    print("Setup complete.")
    print("You may delete this file and the folder 'rplidar_python' after moving the .so file.")

# Execute the script
if __name__ == "__main__":
    main()
