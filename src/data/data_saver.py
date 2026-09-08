from pathlib import Path

import pandas as pd

from src import data_folder


class DataSaver:
    def __init__(self):
        pass

    def save_csv(self, data: pd.DataFrame, file_name: str, include_index: bool = True):
        """Saves a pandas DataFrame to a CSV file on disk.

        :param pd.DataFrame data: The transformed DataFrame to save
        :param str file_name: Destination file name
        :param bool include_index: Whether to write row names (index) into the CSV
        """

        full_path = self.make_folder(file_name=file_name, extension="csv")

        # Convert Series to DataFrame and write it to disk
        pd.DataFrame(data).to_csv(full_path, index=include_index)

    @staticmethod
    def make_folder(file_name: str, extension: str) -> Path:
        """
        Method for creating a folder for the given extension's download destination and for creating a full path

        :param str file_name: Original name of the file (doesn't matter if the extension is included)
        :param str extension: The desired extension of the file e.g.: csv (without dot)

        :return Path full_path: The exact path of the saved file
                that includes the given file name e.g.: data/csv/example.csv
        """

        new_name = file_name.removesuffix(".json") + "." + extension

        dest_path = data_folder / extension
        dest_path.mkdir(parents=True, exist_ok=True)

        full_path = data_folder / extension / new_name

        return full_path
