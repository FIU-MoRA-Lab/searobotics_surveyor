import os
import sys
import pandas as pd


def extract_and_save_coordinates(filepath):
    """
    Extracts the GPS coordinates from the given APM (Ardupilot Mission Planer) mission file and saves it as a CSV.

    Parameters:
    - filepath: str, path to the APM mission file.

    Returns:
    - str, name of the output CSV file.
    """
    # Extract the base filename without extension
    filename = os.path.splitext(os.path.basename(filepath))[0]

    # Construct the output path
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'out'))
    output_filename = os.path.join(output_dir, f"{filename}.csv")

    # Load the APM mission file into a DataFrame
    df = pd.read_csv(filepath, delim_whitespace=True, header=None, skiprows=1)

    # Extract the columns with the GPS coordinates (assuming columns 8 and 9 are lat and lon)
    gps_df = df[[8, 9]]

    gps_df = gps_df[(gps_df[8] != 0.0) & (gps_df[9] != 0.0)]

    # Save the extracted coordinates to the constructed CSV file path
    gps_df.to_csv(output_filename, index=False, header=["Latitude", "Longitude"])

    return output_filename

def main(filepath):
    output_file = extract_and_save_coordinates(filepath)
    print(f"GPS coordinates saved to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <filepath>")
        sys.exit(1)

    main(sys.argv[1])
