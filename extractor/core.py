from pathlib import Path
from typing import Dict

import pandas as pd
import requests
from rich.progress import track

from extractor.checks import StandardCheck
from extractor.logger import logger
from extractor.render import Requirements

URLBASE = "https://pypi.org/pypi"


def get_raw_data(project: str) -> Dict[str, str]:
    """
    Retrieve raw metadata for a project from a given URL.

    Args:
        project: The name of the project.

    Returns:
        A dictionary containing the raw metadata of the project.
    """
    try:
        r = requests.get(
            f"{URLBASE}/{project}/json", headers={"Accept": "application/json"}
        )
    except Exception as e:
        logger.error(e)
    else:
        return r.json()["info"]


def filter_data(raw_data: Dict[str, str], version: str) -> Dict[str, str]:
    """
    Filter relevant metadata from raw data.

    Args:
        raw_data: The raw metadata of a project.
        version: The version of the project.

    Returns:
        A dictionary containing filtered metadata.
    """
    project_name = raw_data["name"]
    project_url = raw_data["project_url"]
    project_urls = raw_data["project_urls"]
    gh_url_pattern = r"(https:\/\/|http:\/\/)github\.com"
    filtered_data = {
        "name": project_name,
        "version": version or raw_data["version"],
        "license": raw_data["license"],
        "homepage": raw_data["home_page"],
        "release_url": raw_data["release_url"],
    }
    check = StandardCheck()
    logger.info(f"Searching GitHub url for: {project_name}")

    # logger.info(f"Searching GitHub url for: {project_name}")
    if project_url != "" and check.gh_pattern(gh_url_pattern, project_url):
        filtered_data["project_url"] = project_url

    if project_urls:
        logger.debug("Nested metadata found")
        filtered_data["project_url"] = check.additional_urls(
            gh_url_pattern, project_urls
        )
    if project_name == "pandas":
        version = f"v{filtered_data['version']}"
        filtered_data["version"] = version

    filtered_data = check.version(version, gh_url_pattern, raw_data, filtered_data)
    return filtered_data


def extract_data(source_path: Path, format: str) -> None:
    """
    Extract data based on the specified requirements format.

    Args:
        source_path: The path to the requirements file.
        format: The format of the requirements file.

    Returns:
        pd.DataFrame
    """
    logger.info("Starting process")
    logger.debug(f"Retrieving: {source_path}")
    result = Requirements().render(source_path, format)
    pkgs_raw_metadata = []
    for pkg in track(result):
        filtered_data = filter_data(
            get_raw_data(pkg[0]), pkg[1] if len(pkg) > 1 else None
        )
        pkgs_raw_metadata.append(filtered_data)
    return pd.DataFrame(pkgs_raw_metadata)


def save_data(data: pd.DataFrame, output: Path):
    logger.info(f"Storing into: {output}")
    if str(output).endswith(".csv"):
        data.to_csv(output, index=False)
        logger.info("All done! Have a Great day")
    elif str(output).endswith(".xlsx"):
        data.to_excel(output, index=False)
        logger.info("All done! Have a Great day")
    else:
        logger.error("Not supported format.")
