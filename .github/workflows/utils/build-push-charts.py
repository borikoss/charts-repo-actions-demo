#!/usr/bin/env python

import argparse
import os
import subprocess
import yaml


def check_chart_version_exists(
    repo_name, chart_name, chart_version, api_key, artifactory_url
):
    response = subprocess.run(
        [
            "curl",
            "-s",
            "-H",
            f"X-JFrog-Art-Api:{api_key}",
            f"{artifactory_url}/api/helm/{repo_name}/index.yaml",
        ],
        capture_output=True,
    )

    response = response.stdout.decode("utf-8")
    yaml_data = yaml.safe_load(response)

    if 'entries' in yaml_data and chart_name in yaml_data['entries']:
        versions = yaml_data['entries'][chart_name]
        return any(chart_version in version.get('version', '') for version in versions)
    else:
        return False


def update_dependency_helm_chart(chart_path):
    os.chdir(chart_path)
    subprocess.run(
        [
            "helm", 
            "dependency", 
            "update", 
            "--skip-refresh"
        ]
    )


def package_helm_chart(chart_path):
    os.chdir(chart_path)
    subprocess.run(
        [
            "helm", 
            "package", 
            "."
        ]
    )


def push_to_artifactory(
    chart_path, repo_name, chart_name, chart_version, api_key, artifactory_url
):
    chart_file = f"{chart_name}-{chart_version}.tgz"
    subprocess.run(
        [
            "curl",
            "-T",
            chart_file,
            "-H",
            f"X-JFrog-Art-Api:{api_key}",
            f"{artifactory_url}/{repo_name}/{chart_name}/{chart_version}/{chart_file}",
        ]
    )


def extract_chart_details(chart_path):
    chart_file = os.path.join(chart_path, "Chart.yaml")
    with open(chart_file, "r") as stream:
        try:
            chart_data = yaml.safe_load(stream)
            return chart_data["name"], chart_data["version"]
        except yaml.YAMLError as exc:
            print(exc)
            return None, None


def process_charts(chart_folder, repository_name, artifactory_url, api_key, override_charts):
    subfolders = [f.path for f in os.scandir(chart_folder) if f.is_dir()]

    for chart_path in subfolders:
        chart_name, chart_version = extract_chart_details(chart_path)

        print(f"Processing chart path: '{chart_path}'")

        if chart_name and chart_version:
            if not check_chart_version_exists(
                repository_name, chart_name, chart_version, api_key, artifactory_url
            ):
                do_push_to_registry = True
            else:
                if override_charts:
                    do_push_to_registry = True
                    print(f"Overriding chart version {chart_version} for the chart {chart_name} in the repository...")
                else:
                    do_push_to_registry = False
                    print(f"Chart version {chart_version} for the chart {chart_name} already exists in the repository. Skipping...")

            if do_push_to_registry:
                print(f"Updating chart dependencies...")
                update_dependency_helm_chart(chart_path)

                print(f"Building chart...")
                package_helm_chart(chart_path)

                print(f"Pushing chart to registry...")
                push_to_artifactory(
                    chart_path,
                    repository_name,
                    chart_name,
                    chart_version,
                    api_key,
                    artifactory_url,
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process Helm charts and push to Artifactory"
    )
    parser.add_argument(
        "--chart-folder",
        help="Path to the root directory containing Helm charts", required=True,
    )
    parser.add_argument(
        "--repository-name", help="Name of the Artifactory repository", required=True
    )
    parser.add_argument(
        "--artifactory-url", help="URL of the Artifactory instance", required=True
    )
    parser.add_argument(
        "--api-key", help="API key for Artifactory access", required=True
    )
    parser.add_argument(
        "--override-charts", action="store_true", help="Override existing charts in Artifactory"
    )

    args = parser.parse_args()

    chart_folder = args.chart_folder
    repository_name = args.repository_name
    artifactory_url = args.artifactory_url
    api_key = args.api_key
    override_charts = args.override_charts

    process_charts(
        chart_folder, 
        repository_name, 
        artifactory_url, 
        api_key, 
        override_charts
    )
