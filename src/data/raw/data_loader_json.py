import json
import re

import pandas as pd


class DataLoaderJson:
    """
    Base class for all data loaders
    """

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.d_train_type = None
        self.d_type = None
        self.raw_data = None
        self.file_name = None

    def load_file(self, file_path: str):
        """
        Reads the data file and extracts the necessary information for data loading from the file name which are:
        - start time (pd.Timestamp)
        - end time (pd.Timestamp)
        - time periods (d_train_type): test, train (str)
        - types (d_type): registered, processed, detected (only main stations), discharge (only Makó) (str)
        Saves all this data as class variables alongside the data itself. The data is saved as a pd.Series and some
        transformations are made to it before saving.

        :param str file_path: Path of the file
        """

        with open(file_path, "r") as file:
            f_data = json.load(file)

        # Read the data type, station, start time and end time from the file name
        name_pattern = r"(\S{2})_(\d{6})_(\d{4}-\d{2})_(\d{4}-\d{2})"
        match = re.search(pattern=name_pattern, string=file_path)

        if match:
            self.start_time = pd.to_datetime(match.group(3))
            self.end_time = pd.to_datetime(match.group(4))
            self.d_train_type = match.group(1)[0]
            self.d_type = match.group(1)[1]
            self.raw_data = self.transform_json_data(data=f_data[0]["TsItemList"])
            self.file_name = file_path.split("/")[-1].removesuffix(".json")  # filename without extension
        else:
            raise ValueError("File name does not follow naming format")

    @staticmethod
    def transform_json_data(data: list[dict], do_conversion: bool = True) -> pd.Series:
        """
        This function:
            - renames the "Adat" column to "Data" (translated from Hungarian)
            - corrects the read time series' time zone and unit of measurement
            - converts the read time series from a pd.DataFrame to a pd.Series
              where the ids are the time stamps. There may be missing time samps in the loaded data,
              so this resulting pd.Series will have "holes" in it (rows where there's no value associated to
              the given id), which the DataPreprocessorRaw class will fill.

        :param list[dict] data: the data to be transformed
        :param bool do_conversion: True if data should be multiplied by 100 (to become centimeters)
                                 False if data should be multiplied by 1 (to remain in meters)

        :return pd.Series: The transformed data: The ids are the time samps 15 minutes from each other,
                           the values are the data for the given time stamp, if there is any; else it's empty.
        """

        ts_list = data
        raw = pd.DataFrame(ts_list)

        # Rename key "Adat" to "Data"
        raw.rename(columns={"Adat": "Data"}, inplace=True)

        # Do unit conversion if do_multiply is True (m -> cm)
        if do_conversion:
            raw['Data'] *= 100

        # Convert the timestamps into pd.TimeStamp type, then set the indexes to them
        raw["UTCTime"] = pd.to_datetime(raw["UTCTime"]).dt.tz_localize(None)
        raw.set_index(keys="UTCTime", inplace=True)

        # Create a complete 15-minute interval timestamp series and reindex
        new_index = pd.date_range(start=raw.index.min(), end=raw.index.max(), freq="15min")
        series = raw["Data"].reindex(new_index)

        return series
