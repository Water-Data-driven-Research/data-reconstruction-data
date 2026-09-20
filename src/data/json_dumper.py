import pandas as pd
from pathlib import Path


class JsonDumper:
    @staticmethod
    def dump_json(data: pd.DataFrame | pd.Series, file_name: str, file_path: Path = Path.cwd() / "generated"):
        """
        Dumps data into a JSON file at the specified path

        :param pd.DataFrame | pd.Series data: data to be dumped
        :param str file_name: name of the output file
        :param Path file_path: path of the output file
        """

        file_path.mkdir(parents=True, exist_ok=True)
        output_file_path = file_path / (file_name + ".json")

        data.to_json(output_file_path, orient="records")
