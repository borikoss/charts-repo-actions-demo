#!/usr/bin/env python

import os
import sys
import yaml
import subprocess

def parse_yaml_files_in_directory(directory):

    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    # Initialize an empty list to store the parsed YAML data
    yaml_data_list = []

    for root, _, files in os.walk(directory):
        for file_name in files:

            # Check if the file has a .yaml or .yml extension
            if file_name.endswith(".yaml") or file_name.endswith(".yml"):
                file_path = os.path.join(root, file_name)
                with open(file_path, "r") as yaml_file:

                    # Try to open and parse the YAML file
                    try:
                        yaml_data = yaml.safe_load(yaml_file)
                        yaml_data_list.append(yaml_data)
                        print(f"Parsed deploymentTarget '{file_name}' successfully.")
                        print(yaml_data)
                    except yaml.YAMLError as e:
                        print(f"Error parsing {file_path}: {e}")
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

def run_helm_template_cmd(chart_path, release_name, value_files, output_manifest_file):
    try:
        # Construct the Helm command
        helm_command = [
            "helm",
            "template",
            release_name,
            chart_path
        ]

        # Add each value file using the "--values" flag
        for value_file in value_files:
            helm_command.extend(["--values", value_file])

        # Run the Helm command and send output to the file
        with open(output_manifest_file,'w') as f_obj:
            subprocess.run(helm_command,stdout=f_obj,text=True,check=True)

        print(f"Helm template command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running Helm template command: {e}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def run_command_in_folder(command, working_directory):
    try:
        # Run the command in the specified working directory
        result = subprocess.run(command, shell=True, cwd=working_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Check for errors and print output
        if result.returncode == 0:
            print(f"Command '{command}' executed successfully.")
            print("Output:")
            print(result.stdout)
        else:
            print(f"Error running command '{command}':")
            print("Standard Output:")
            print(result.stdout)
            print("Standard Error:")
            print(result.stderr)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def output_file_content(file_path):
    try:
        with open(file_path, "r") as file:
            file_content = file.read()
            return file_content
    except FileNotFoundError:
        return f"The file '{file_path}' was not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    # Check if a directory path argument is provided
    if len(sys.argv) != 3:
        print("Usage: python script.py <deployment_targets_path> <gen_manifests_path>")
        sys.exit(1)

    # Input: Get the directory path from the command-line argument
    deployment_targets_path = sys.argv[1]
    print(f"DeploymentTarget path: '{deployment_targets_path}'")

    # Input: Get the generated Helm manifests path from the command-line argument
    gen_manifests_path = sys.argv[2]
    print(f"Generated manifests path: '{gen_manifests_path}'")

    # Create base folder for generated helm manifests
    create_folder(gen_manifests_path)

    # Parse YAML files in the directory
    parsed_yaml_data = parse_yaml_files_in_directory(deployment_targets_path)

    sys.exit(0)  # Success


    # Work with the parsed YAML data as a list of dictionaries
    for data in parsed_yaml_data:
        print(f"Parsed YAML data as a list of dictionaries:")
        print(data)

        # construct and create folder for environment
        gen_manifests_env_path = os.path.join(gen_manifests_path, data["environment"])
        create_folder(gen_manifests_env_path)

        # Construct Helm release name
        helm_release_name = data["chartReleaseName"]

        # construct and create folder for chartReleaseName and deploymentTarget
        gen_manifests_deployment_target = os.path.join(gen_manifests_env_path, helm_release_name + "-" + data["deploymentTargetName"])
        create_folder(gen_manifests_deployment_target)

        # construct list of Helm value files
        helm_value_files = data["appValueFiles"] + data["infraValueFiles"]

        # Construct file path for Helm output
        output_manifest_file = os.path.join(gen_manifests_deployment_target, "gen_manifests.yaml")

        # Run Helm template
        run_helm_template_cmd(helm_chart_path, helm_release_name, helm_value_files, output_manifest_file)

        # Run kustomize command in the generated manifests folder
        # command_to_run = "kustomize create --autodetect"
        # run_command_in_folder(command_to_run, gen_manifests_deployment_target)

        # Print generated file content
        content = output_file_content(output_manifest_file)
        if content is not None:
            print(content)
