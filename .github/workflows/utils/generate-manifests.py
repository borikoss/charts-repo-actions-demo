#!/usr/bin/env python

import os
import sys
import yaml
import subprocess
import shutil

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

def remove_directory_if_exists(directory_path):
    if os.path.exists(directory_path):
        try:
            shutil.rmtree(directory_path)  # Remove the directory
            print(f"Directory incl. content '{directory_path}' removed.")
            return True
        except OSError as e:
            print(f"Error removing directory '{directory_path}': {str(e)}")
            return False
    else:
        print(f"Directory '{directory_path}' does not exist.")
        return True  # The directory doesn't exist, so it's considered "removed"

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
    if len(sys.argv) != 4:
        print("Usage: python script.py <workspace_path> <deployment_targets_path> <gen_manifests_path>")
        sys.exit(1)

    # Input: Get the workspace path from the command-line argument
    workspace_path = sys.argv[1]
    print(f"Workspace path: '{workspace_path}'")

    # Input: Get the directory path from the command-line argument
    deployment_targets_path = sys.argv[2]
    print(f"Deployment targets path: '{deployment_targets_path}'")

    # Input: Get the generated Helm manifests path from the command-line argument
    gen_manifests_path = sys.argv[3]
    print(f"Generated manifests path: '{gen_manifests_path}'")

    # Create base folder for generated helm manifests
    create_folder(gen_manifests_path)

    # Parse YAML files in the directory
    parsed_yaml_data = parse_yaml_files_in_directory(deployment_targets_path)

    # Work with the parsed YAML data as a list of dictionaries
    for data in parsed_yaml_data:

        # Create folder for deployment environment
        gen_manifests_env_path = os.path.join(gen_manifests_path, data["deployment"]["environment"])
        create_folder(gen_manifests_env_path)

        # Collect Helm chart attributed
        helm_release_name = data["chart"]["releaseName"]
        helm_chart_name = data["chart"]["name"]

        # Construct and create manifest path for generated deployment target
        gen_manifests_deployment_target = os.path.join(gen_manifests_env_path, helm_release_name + "-" + data["deployment"]["targetName"])
        create_folder(gen_manifests_deployment_target)

        # Construct file path for Helm output
        output_manifest_file = os.path.join(gen_manifests_deployment_target, "gen_manifests.yaml")

        # Construct list of Helm value files
        helm_value_files = data["deployment"]["valueFiles"]["application"] + data["deployment"]["valueFiles"]["infrastructure"]

        # Process helm chart repository url
        is_helm_chart_local = False
        helm_chart_repository_url = data["chart"]["repository"]
        if helm_chart_repository_url.startswith("file://"):
            is_helm_chart_local = True
            helm_chart_path = os.path.join(workspace_path,helm_chart_repository_url[len("file://"):])

        # Helm chart pull from repo
        if is_helm_chart_local is not True:
            helm_chart_repository_name = data["chart"]["name"] + "-repo"
            helm_chart_version = data["chart"]["version"]
            helm_chart_untardir = os.path.join(workspace_path,"charts_upstream")
            helm_chart_path = os.path.join(helm_chart_untardir,helm_chart_name)

            command = ["helm", "repo", "add", helm_chart_repository_name, helm_chart_repository_url]
            subprocess.run(command,text=True,check=True)

            #remove_directory_if_exists(helm_chart_path)

            command = ["helm", "pull", helm_chart_repository_name + "/" + helm_chart_name]
            command.extend(["--version", helm_chart_version])
            command.extend(["--untar"])
            command.extend(["--untardir", helm_chart_untardir])
            subprocess.run(command,text=True,check=True)

        print(f"Helm chart path: '{helm_chart_path}'")

        # Run Helm template
        run_helm_template_cmd(helm_chart_path, helm_release_name, helm_value_files, output_manifest_file)

        # Print generated file content
        content = output_file_content(output_manifest_file)
        if content is not None:
            print(content)
