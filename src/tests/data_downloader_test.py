from pathlib import Path
import shutil

import pytest

from src.data_downloader import DataDownloader
from src import data_folder


@pytest.fixture(scope="module")
def download_context():
    """
    Runs the downloader once before tests and returns the downloaded path.
    """

    test_url = "https://drive.google.com/file/d/1KAFC9-N6t0pViqQAmVs5M4AErpQIZdA3/view"
    file_name = "data.zip"

    downloader = DataDownloader(file_url=test_url, file_name=file_name)

    context = {
        "test_url": test_url,  # str: the url of the zip file downloaded
        "file_name": file_name,  # str: name of the zip file downloaded
    }

    yield context

    # Delete the extracted data after all tests run
    if data_folder.exists():
        shutil.rmtree(data_folder)


def test_download_directory_exists(download_context: dict):
    """
    Verify that the base target folder was created.

    :param dict download_context: data related to the download
    """

    assert data_folder.exists(), "The downloaded folder does not exist."
    assert data_folder.is_dir(), "The downloaded path is not a directory."


def test_expected_subdirectories_exist(download_context: dict):
    """
    Verify all top-level extracted folders exist.

    :param dict download_context: data related to the download
    """

    expected_folders = [
        "csv_data",
        "data",
        "discharge",
        "dl",
        "eval_data",
        "reconstructed_data",
    ]

    for folder_name in expected_folders:
        folder_path = data_folder / folder_name
        assert folder_path.exists(), f"Missing subfolder: {folder_name}"
        assert folder_path.is_dir(), f"Expected {folder_name} to be a directory."


def test_specific_files_exist(download_context: dict):
    """
    Verify specific key files exist inside their respective nested directories.

    :param dict download_context: data related to the download
    """

    expected_files = [
        # csv_data structure
        data_folder / "csv_data" / "Szegedhez" / "algyo_vizhozam.csv",
        # data structure
        data_folder / "data" / "tv_210888_2004-01_2010-01.json",
        # reconstructed_data structure
        data_folder / "reconstructed_data" / "Szeged" / "Szeged_dl_teszt.json",
    ]

    for file_path in expected_files:
        assert file_path.exists(), f"Missing file: {file_path.relative_to(data_folder)}"
        assert file_path.is_file(), f"Expected {file_path.name} to be a file."
        assert file_path.stat().st_size > 0, f"File {file_path.name} is empty."


def test_zip_file_deleted(download_context: dict):
    """
    Verify the downloaded zip file was deleted after extraction.

    :param dict download_context: data related to the download
    """

    file_name = download_context["file_name"]

    zip_path = data_folder / file_name

    assert not zip_path.exists(), f"Zip file was not deleted: {zip_path}"
