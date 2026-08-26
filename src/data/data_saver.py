import os
import pandas as pd


class DataSaver:

    @staticmethod
    def save_csv(df: pd.DataFrame, file_path: str, file_name: str, include_index: bool = True):
        """Saves a pandas DataFrame to a CSV file on disk.

        :param pd.DataFrame df: The transformed DataFrame to save
        :param str file_path: Destination file path
        :param str file_name: Destination file name
        :param bool include_index: Whether to write row names (index) into the CSV
        """

        corrected_file_name = file_name.removesuffix(".json") + ".csv"
        full_path = os.path.join(file_path, corrected_file_name)

        # Ensure directory exists before saving
        os.makedirs(file_path, exist_ok=True)

        # Write DataFrame directly to disk
        df.to_csv(full_path, index=include_index)
