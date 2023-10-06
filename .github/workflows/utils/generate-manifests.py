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
                    print(f"Parsed deploymentTarget '{filename}' successfully.")
            except Exception as e:
                print(f"Error parsing '{filename}': {str(e)}")

    return yaml_data_list

def create_folder(folder_name):
    try:
        # Create the folder
        os.mkdir(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    except FileExistsError:
        print(f"Folder '{folder_name}' already exists.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Check if a directory path argument is provided
    if len(sys.argv) != 4:
        print("Usage: python script.py <deployment_targets_path> <helm_chart_path> <gen_manifests_path>")
        sys.exit(1)

    # Input: Get the directory path from the command-line argument
    deployment_targets_path = sys.argv[1]
    print(f"DeploymentTarget path: '{deployment_targets_path}'")

    # Input: Get the Helm chart path from the command-line argument
    helm_chart_path = sys.argv[2]
    print(f"Helm chart path: '{helm_chart_path}'")

    # Input: Get the generated Helm manifests path from the command-line argument
    gen_manifests_path = sys.argv[3]
    print(f"Generated Helm manifests path: '{gen_manifests_path}'")

    # Create folder for generated helm manifests
    create_folder(gen_manifests_path)

    # Call the function to parse YAML files in the directory
    parsed_yaml_data = parse_yaml_files(deployment_targets_path)

    # You can now work with the parsed YAML data as a list of dictionaries
    for data in parsed_yaml_data:
        print(data)