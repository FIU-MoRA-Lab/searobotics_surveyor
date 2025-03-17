import csv
import datetime
import os
import time
import pandas as pd
from . import config, logger


def append_to_csv(data, cols=["latitude", "longitude"], post_fix=""):
    """
    Append data to a CSV file with a specific date in the filename.

    Args:
        data (list): The list of data to be appended to the CSV file.
        post_fix (str, optional): A string to be appended to the filename. Defaults to an empty string.
        cols (list, optional): A list of column names for the CSV file. Defaults to ["latitude", "longitude"].
    """
    # Get today's date in the "YYYYMMDD" format
    today_date = datetime.date.today().strftime("%Y%m%d")

    # Get the parent's parent directory of the current script
    grandparent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # print(f'saving at {grandparent_dir}')

    # Create the "out" directory if it doesn't exist
    out_dir = os.path.join(grandparent_dir, "out")
    os.makedirs(out_dir, exist_ok=True)

    # Define the CSV file path using today's date
    file_path = os.path.join(out_dir, f"{today_date}{post_fix}.csv")

    # Check if the file already exists, and create it with headers if it doesn't
    if not os.path.isfile(file_path):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(cols)

    # Append the data to the CSV file
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def save(data, post_fix=""):
    """
    Process GPS coordinates and Exo2 sensor data, append them to a CSV file after validation.

    Parameters:
        data: Dictionary containing GPS coordinates and Exo2 sensor data.
        post_fix: (optional) A suffix to append to the CSV file name. Default is "".
    """
    # Initialize lists to store combined data and column names

    # If combined data is not empty, append to CSV
    if data:
        append_to_csv(data.values(), data.keys(), post_fix=post_fix)


def process_gga_and_save_data(surveyor_connection, data_keys=['state', 'exo2'], post_fix="", delay=1.0):
    """
    Retrieve and process GGA and Exo2 data, then append it to a CSV file.

    Args:
        surveyor_connection: The Surveyor connection object providing access to GPS and Exo2 data.
        post_fix: (optional) A suffix to append to the CSV file name. Default is "".

    Returns:
        surveyor_data (dict): Dictionary with the data acquired by the boat (see Surveyor.get_data method)
    """
    surveyor_data = surveyor_connection.get_data(data_keys)

    # Save the data to a CSV file
    if time.time() - process_gga_and_save_data.last_save_time < delay:
        time.sleep(delay - time.time() + process_gga_and_save_data.last_save_time)
    process_gga_and_save_data.last_save_time = time.time()

    save(surveyor_data, post_fix)
    return surveyor_data

process_gga_and_save_data.last_save_time = time.time()

def read_csv_into_tuples(filepath):
    """
    Reads a CSV file into a list of tuples.
    
    Parameters:
        filepath (str): The path to the CSV file.
        
    Returns:
        list of tuples: Each tuple represents a row from the CSV file.
    """
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(filepath)

    try:
        df = df[['Latitude', 'Longitude']]
    except KeyError:
        try:
            df = df[['latitude', 'longitude']]
        except KeyError:
            print('Assuming first column to be Latitude and second to be Longitude')
            df = df.iloc[:, :2]        
    
    # Convert the DataFrame rows into tuples and return as a list
    return [tuple(row) for row in df.values]