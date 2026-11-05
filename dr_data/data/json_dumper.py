from pathlib import Path

import pandas as pd


class JsonDumper:
    @staticmethod
    def dump_json(data: pd.DataFrame | pd.Series, file_name: str, folder_path: Path = Path.cwd() / "generated"):
        """
        Dumps data into a JSON file at the specified path

        :param pd.DataFrame | pd.Series data: Data to be dumped
        :param str file_name: Name of the output file
        :param Path folder_path: Path of the output folder (without the file name)
        """

        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / (file_name + ".json")

        data.to_json(path_or_buf=file_path, orient="records", indent=4)
