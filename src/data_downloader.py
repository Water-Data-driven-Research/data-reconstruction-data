import gc
import zipfile

import gdown

from src import data_folder


class DataDownloader:
    """
    Class for downloading time series related data
    """

    def __init__(self, file_url: str, file_name: str):
        """
        Downloads the data, unzips it and deletes the original zip file

        :param str file_url: The Google Drive url of the file to be downloaded
        :param str file_name: The name of the file to be downloaded
        """

        self.dest_path = data_folder / "json"  # pointing to the folder the zip file will be extracted in

        self.file_path = self.dest_path / file_name  # pointing to the downloaded zip file itself
        self.dest_path.mkdir(parents=True, exist_ok=True)

        self.download(file_url=file_url)

        self.unzip()

    def download(self, file_url: str):
        """
        Downloads the data from Google Drive
        :param str file_url: The Google Drive url of the file to be downloaded
        """

        if not self.file_path.is_file():
            gdown.download(url=file_url,
                           output=str(self.file_path),
                           quiet=False)

    def unzip(self):
        """
        Unzips the downloaded zip file and deletes the original zip file
        """

        if self.file_path.suffix == ".zip" and self.file_path.is_file():
            with zipfile.ZipFile(self.file_path, "r") as zip_ref:
                zip_ref.extractall(self.dest_path)

            # Force Python to release open file handles left by gdown
            gc.collect()
            try:
                self.file_path.unlink()  # Delete the original zip file
            except PermissionError:
                print(f"Warning: Could not remove {self.file_path} due to locked handle.")
