import gc
from pathlib import Path
import zipfile

import gdown


class DataDownloader:
    """
    Class for downloading time series related data
    """
    def __init__(self, file_url: str, file_name: str):
        """
        Downloads the data, unzips it and deletes the original zip file

        :param file_url: The Google Drive url of the file to be downloaded
        :param file_name: The name of the file to be downloaded
        """

        self.data_folder = Path(__file__).resolve().parent / "downloaded"
        self.file_path = self.data_folder / file_name
        self.data_folder.mkdir(parents=True, exist_ok=True)

        self.download(file_url=file_url)

        self.unzip()

    def download(self, file_url: str) -> None:
        """
        Downloads the data from Google Drive
        :param file_url: The Google Drive url of the file to be downloaded
        """

        if not self.file_path.is_file():
            gdown.download(url=file_url,
                           output=str(self.file_path))

    def unzip(self) -> None:
        """
        Unzips the downloaded zip file and deletes the original zip file
        """
        if self.file_path.suffix == ".zip" and self.file_path.is_file():
            with zipfile.ZipFile(self.file_path, "r") as zip_ref:
                zip_ref.extractall(self.data_folder)

            # Force Python to release open file handles left by gdown
            gc.collect()
            try:
                self.file_path.unlink()  # Delete the original zip file
            except PermissionError:
                print(f"Warning: Could not remove {self.file_path} due to locked handle.")