import csv
import datetime
import os
import time

import pandas as pd

from .logger import HELPER_LOGGER

DEFAULT_OUT_DIR_PATH = os.path.abspath(
    os.path.join(__file__, "../../../../out/")
)


def append_to_csv(
    data,
    cols=["latitude", "longitude"],
    post_fix="",
    dir_path=None,
):
    """
    Append data to a CSV file with a specific date in the filename.

    Args:
        data (list): The list of data to be appended to the CSV file.
        cols (list, optional): Column names for the CSV file. Defaults to ["latitude", "longitude"].
        post_fix (str, optional): Suffix to be added to the filename. Defaults to "".
        dir_path (str, optional): Directory path where the CSV file will be stored.
            If None, uses the default directory.
    """
    dir_path = dir_path or DEFAULT_OUT_DIR_PATH

    today_date = datetime.date.today().strftime("%Y%m%d")

    HELPER_LOGGER.debug(f"out folder at {dir_path}")
    os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, f"{today_date}{post_fix}.csv")

    # Create file and write header if it doesn't exist
    if not os.path.isfile(file_path):
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(cols)

    # Append the row
    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(data)


def save(data, post_fix="", dir_path=None):
    """
    Process GPS coordinates and Exo2 sensor data, append them to a CSV file after validation.

    Parameters:
        data: Dictionary containing GPS coordinates and Exo2 sensor data.
        post_fix: (optional) A suffix to append to the CSV file name. Default is "".
        dir_path (str, optional): Directory path where the CSV file will be stored. If None, uses the default directory.
    """
    # Initialize lists to store combined data and column names

    # If combined data is not empty, append to CSV
    if data:
        append_to_csv(
            data.values(), data.keys(), post_fix=post_fix, dir_path=dir_path
        )
    else:
        HELPER_LOGGER.error("No values to be appended to the CSV")


def process_gga_and_save_data(
    surveyor_connection,
    data_keys=["state", "exo2"],
    post_fix="",
    delay=1.0,
    dir_path=None,
):
    """
    Retrieve and process GGA and Exo2 data, then append it to a CSV file.

    Args:
        surveyor_connection: The Surveyor connection object providing access to GPS and Exo2 data.
        data_keys (list, optional): List of keys to retrieve specific data from the surveyor connection. Defaults to None.
        post_fix (str, optional): A suffix to append to the CSV file name. Default is "".
        delay (float, optional): Minimum time delay (in seconds) between consecutive saves to prevent duplicate entries. Default is 1.0.
        dir_path (str, optional): Directory path where the CSV file will be stored. If None, uses the default directory.

    Returns:
        surveyor_data (dict): Dictionary with the data acquired by the boat (see Surveyor.get_data method).
    """
    data_keys = (
        [key for key in data_keys if key in ["state", "exo2"]]
        if data_keys is not None
        else ["state", "exo2"]
    )
    if not data_keys:
        raise ValueError("No valid data keys provided.")
    surveyor_data = surveyor_connection.get_data(data_keys)

    # Save the data to a CSV file
    if (
        time.time() - process_gga_and_save_data.last_save_time < delay
    ):  # Apply delay to prevent same location
        time.sleep(
            delay - time.time() + process_gga_and_save_data.last_save_time
        )
    process_gga_and_save_data.last_save_time = time.time()

    save(data=surveyor_data, post_fix=post_fix, dir_path=dir_path)
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
        df = df[["Latitude", "Longitude"]]
    except KeyError:
        try:
            df = df[["latitude", "longitude"]]
        except KeyError:
            HELPER_LOGGER.warning(
                "Assuming first column to be Latitude and second to be Longitude"
            )
            df = df.iloc[:, :2]

    # Convert the DataFrame rows into tuples and return as a list
    return [tuple(row) for row in df.values]
