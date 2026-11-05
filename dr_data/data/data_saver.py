from pathlib import Path

import pandas as pd

from dr_data import data_folder


class DataSaver:
    @staticmethod
    def save_csv(data: pd.Series,
                 file_name: str,
                 folder_path: Path | None = None,
                 include_index: bool = True):
        """
        Saves a pandas DataFrame to a CSV file on disk.

        :param pd.Series data: The transformed Series to save
        :param str file_name: Name of the file to be saved (without extension)
        :param Path | None folder_path: Path to the file to be saved (without the file name)
        :param bool include_index: Whether to write row names (index) into the CSV
        """

        file_path = DataSaver.make_folder(file_name=file_name,
                                          extension="csv",
                                          folder_path=folder_path)

        # Convert Series to DataFrame and write it to disk
        pd.DataFrame(data).to_csv(path_or_buf=file_path, index=include_index)

    @staticmethod
    def make_folder(file_name: str, extension: str, folder_path: Path | None = None) -> Path:
        """
        Method for creating a folder for the given extension's download destination and for creating a full path

        :param str file_name: Name of the file to be saved (without extension)
        :param str extension: The desired extension of the file e.g.: csv (without dot)
        :param Path folder_path: Path to the output folder (without the file name)

        :return Path file_path: The exact path of the saved file
                that includes the given file name e.g.: data/csv/example.csv
        """

        if folder_path is None:
            folder_path = data_folder / extension
        folder_path.mkdir(parents=True, exist_ok=True)

        new_file_name = file_name + "." + extension
        file_path = folder_path / new_file_name

        return file_path
