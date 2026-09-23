import json
import re

import datetime
import pandas as pd

from src.data.raw.data_preprocessor_raw import DataPreprocessorRaw


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
        self.filled_data = None
        self.file_name = None

    def run(self, file_path: str, t_delta: datetime.timedelta):
        """
        Loads the specified time series, then fills them with the appropriate fill function from DataPreprocessorRaw

        :param str file_path: Path of the time series to be loaded
        :param datetime.timedelta t_delta: Time (in minutes) between data points in the time series (usually 15)
        """

        self.load_file(file_path=file_path)

        if self.d_type == "registered" or self.d_type == "processed":
            func = DataPreprocessorRaw.r_p_fill
        elif self.d_type == "detected":
            func = DataPreprocessorRaw.de_fill
        elif self.d_type == "discharge":
            func = DataPreprocessorRaw.di_fill
        else:
            raise ValueError("Unrecognized d_type")

        func(start_time=self.start_time,
             end_time=self.end_time,
             data=self.raw_data,
             t_delta=t_delta)

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

        # Do unit conversion if do_conversion is True (m -> cm)
        if do_conversion:
            raw['Data'] *= 100

        # Convert the timestamps into pd.TimeStamp type, then set the indexes to them
        raw["UTCTime"] = pd.to_datetime(raw["UTCTime"]).dt.tz_localize(None)
        raw.set_index(keys="UTCTime", inplace=True)

        # Create a complete 15-minute interval timestamp series and reindex
        new_index = pd.date_range(start=raw.index.min(), end=raw.index.max(), freq="15min")
        series = raw["Data"].reindex(new_index)

        return series
