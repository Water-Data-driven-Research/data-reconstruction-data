from abc import ABC, abstractmethod
import json
import re

import pandas as pd

from src.data_downloader import DataDownloader


class DataLoaderBase(ABC):
    def __init__(self):
        self.downloader = DataDownloader()

    @abstractmethod
    def load_data(self):
        """
        Abstract method, every class derived from DataDownloader must overwrite this function
        :return None:
        """

        pass

    def load_file(self, file_path: str) -> tuple[pd.Timestamp, pd.Timestamp, str, str, pd.DataFrame]:
        """
        Reads the data file and extracts the necessary information for data loading from the file name
        :param str file_path: Path of the file
        :return tuple[pd.Timestamp, pd.Timestamp, str, str, pd.DataFrame]:
                start_time, end_time, d_nature, d_type, raw JSON data
        """

        with open(file_path, "r") as file:
            f_data = json.load(file)

        # Read the data type, station, start time and end time from the file name
        name_pattern = r"(\S{2})_(\d{6})_(\d{4}-\d{2})_(\d{4}-\d{2})"
        match = re.search(pattern=name_pattern, string=file_path)

        if match:
            start_time = pd.to_datetime(match.group(3))
            end_time = pd.to_datetime(match.group(4))

            return (start_time,
                    end_time,
                    match.group(1)[0],
                    match.group(1)[1],
                    self.transform_json_data(data=f_data[0]["TsItemList"])
                    )

        else:
            raise ValueError("File name does not follow naming format")

    @staticmethod
    def transform_json_data(data: dict, do_multiply: bool = True) -> pd.DataFrame:
        """
        This function corrects the read time series' time zone and unit of measurement

        :param dict data: the data to be transformed
        :param bool do_multiply: True if data should be multiplied by 100 (to become centimeters)
                                 False if data should be multiplied by 1 (to remain in meters)

        :return pd.DataFrame: the transformed data
        """

        ts_list = data
        raw = pd.DataFrame(ts_list)

        raw['Adat'] *= 100 if do_multiply else 1

        raw["UTCTime"] = pd.to_datetime(raw["UTCTime"]).dt.tz_localize(None)
        raw.set_index(keys="UTCTime", inplace=True)

        return raw
