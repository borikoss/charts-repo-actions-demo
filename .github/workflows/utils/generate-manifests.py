#!/usr/bin/env python

import os
import sys
import yaml

def parse_yaml_files(directory):
    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    # Initialize an empty list to store the parsed YAML data
    yaml_data_list = []

    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        # Check if the file has a .yaml or .yml extension
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            file_path = os.path.join(directory, filename)
            
            # Try to open and parse the YAML file
            try:
                with open(file_path, "r") as yaml_file:
                    yaml_data = yaml.safe_load(yaml_file)
                    yaml_data_list.append(yaml_data)
                    print(f"Parsed '{filename}' successfully.")
            except Exception as e:
                print(f"Error parsing '{filename}': {str(e)}")

    return yaml_data_list

if __name__ == "__main__":
    # Check if a directory path argument is provided
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)

    # Input: Get the directory path from the command-line argument
    directory_path = sys.argv[1]

    # Call the function to parse YAML files in the directory
    parsed_yaml_data = parse_yaml_files(directory_path)

    # You can now work with the parsed YAML data as a list of dictionaries
    for data in parsed_yaml_data:
        print(data)
