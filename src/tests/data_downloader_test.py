import pytest

from pathlib import Path
import shutil

from src.data_downloader import DataDownloader

TEST_URL = "https://drive.google.com/file/d/1KAFC9-N6t0pViqQAmVs5M4AErpQIZdA3/view"
FILE_NAME = "data.zip"


@pytest.fixture(scope="module")
def downloaded_dir():
    """
    Runs the downloader once before tests and returns the downloaded path.
    """

    downloader = DataDownloader(file_url=TEST_URL, file_name=FILE_NAME)
    yield downloader.data_folder

    # Delete the extracted data after all tests run
    if downloader.data_folder.exists():
        shutil.rmtree(downloader.data_folder)


def test_download_directory_exists(downloaded_dir: Path):
    """
    Verify that the base target folder was created.

    :param downloaded_dir: the path of the folder containing the downloaded data
    """

    assert downloaded_dir.exists(), "The downloaded folder does not exist."
    assert downloaded_dir.is_dir(), "The downloaded path is not a directory."


def test_expected_subdirectories_exist(downloaded_dir: Path):
    """
    Verify all top-level extracted folders exist.

    :param downloaded_dir: the path of the folder containing the downloaded data
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
        folder_path = downloaded_dir / folder_name
        assert folder_path.exists(), f"Missing subfolder: {folder_name}"
        assert folder_path.is_dir(), f"Expected {folder_name} to be a directory."


def test_specific_files_exist(downloaded_dir: Path):
    """
    Verify specific key files exist inside their respective nested directories.

    :param downloaded_dir: the path of the folder containing the downloaded data
    """

    expected_files = [
        # csv_data structure
        downloaded_dir / "csv_data" / "Szegedhez" / "algyo_vizhozam.csv",
        # data structure
        downloaded_dir / "data" / "tv_210888_2004-01_2010-01.json",
        # reconstructed_data structure
        downloaded_dir / "reconstructed_data" / "Szeged" / "Szeged_dl_teszt.json",
    ]

    for file_path in expected_files:
        assert file_path.exists(), f"Missing file: {file_path.relative_to(downloaded_dir)}"
        assert file_path.is_file(), f"Expected {file_path.name} to be a file."
        assert file_path.stat().st_size > 0, f"File {file_path.name} is empty."


def test_zip_file_deleted(downloaded_dir: Path):
    """
    Verify the downloaded zip file was deleted after extraction.

    :param downloaded_dir: the path of the folder containing the downloaded data
    """

    zip_path = downloaded_dir / FILE_NAME

    assert not zip_path.exists(), f"Zip file was not deleted: {zip_path}"
