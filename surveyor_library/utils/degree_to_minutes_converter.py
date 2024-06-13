import csv
import sys
import os
# This module will be deprecated in the future

def convert_to_degrees_minutes(decimal_degree):
   """
   Convert a decimal degree value to a string in degrees and minutes format.

   Args:
       decimal_degree (float): The decimal degree value to be converted.

   Returns:
       str: The converted value in degrees and minutes format.
   """
   degrees = int(decimal_degree)
   minutes_decimal = (decimal_degree - degrees) * 60
   minutes_formatted = "{:.4f}".format(minutes_decimal)[:-1] + "0"
   return "{}°{}".format(degrees, minutes_formatted)

def main(filename):
   """
   Convert a CSV file containing latitude and longitude values in decimal degrees format
   to a new CSV file with the values in degrees and minutes format.

   Args:
       filename (str): The name of the input CSV file.
   """
   # Read the original CSV
   with open(filename, 'r') as infile:
       reader = csv.reader(infile)
       original_points = list(reader)

   # Skip the header
   original_points = original_points[1:]

   # Convert to desired format
   converted_points = [("Latitude", "Longitude")]
   for point in original_points:
       latitude = convert_to_degrees_minutes(float(point[0]))
       longitude = convert_to_degrees_minutes(float(point[1]))
       converted_points.append((latitude, longitude))

   # Name of the output file
   output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'out'))
#    os.makedirs(output_dir, exist_ok=True)
   output_filename = os.path.join(output_dir, "converted_" + os.path.basename(filename))

   # Write to new CSV
   with open(output_filename, 'w', newline='') as outfile:
       writer = csv.writer(outfile)
       writer.writerows(converted_points)

   print(f"Conversion complete! Data saved in '{output_filename}'.")

if __name__ == "__main__":
   """
   Entry point of the script.
   """
   if len(sys.argv) != 2:
       print("Usage: python degree_to_minutes_converter.py <filename>")
       sys.exit(1)

   main(sys.argv[1])