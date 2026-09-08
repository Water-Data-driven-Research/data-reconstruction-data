import pandas as pd
import datetime


class DataPreprocessorRaw:
    """
    This class fills rows in the loaded time series where there's no data present
    """

    @staticmethod
    def r_p_fill(
            start_time: pd.Timestamp, end_time: pd.Timestamp, data: pd.Series, t_delta: datetime.timedelta
            ) -> pd.Series:
        """
        Fill registered and processed time series
        
        :param pd.Timestamp start_time: Timestamp of the first recorded data
        :param pd.Timestamp end_time: Timestamp of the last recorded data
        :param pd.Series data: The time series to be filled
        :param datetime.timedelta t_delta: The time series' frequency; minutes between data points (usually 15)
        
        :return pd.Series: The filled time series
        """
        
        index = pd.date_range(start=start_time, end=end_time, freq=t_delta)
        dummy_data = pd.DataFrame(index=index)
        dummy_data['Data'] = data
        
        return dummy_data['Data'].interpolate().drop(dummy_data.index[:4]).fillna(0)

    @staticmethod
    def de_fill(
            start_time: pd.Timestamp, end_time: pd.Timestamp, data: pd.Series, t_delta: datetime.timedelta
            ) -> pd.Series:
        """
        Fill detected time series
        
        :param pd.Timestamp start_time: Timestamp of the first recorded data
        :param pd.Timestamp end_time: Timestamp of the last recorded data
        :param pd.Series data: The time series to be filled
        :param datetime.timedelta t_delta: The time series' frequency; minutes between data points (usually 15)
        
        :return pd.Series: The filled time series
        """
        
        index = pd.date_range(start=start_time, end=end_time, freq=datetime.timedelta(minutes=1))
        dummy_data = pd.DataFrame(index=index)
        afternoon_values = data.between_time(start_time='8:10', end_time='3:50').index
        dummy_data['Data'] = data.drop(afternoon_values)
        dummy_data['Data'] = dummy_data['Data'].interpolate(method='polynomial',
                                                            order=3).asfreq(t_delta)
        return dummy_data['Data'][
            dummy_data.index.minute % (t_delta.total_seconds() / 60) == 0]. \
            drop(dummy_data[dummy_data.index.minute % (t_delta.total_seconds() / 60) == 0].index[:4]).fillna(0)

    @staticmethod
    def di_fill(
            start_time: pd.Timestamp, end_time: pd.Timestamp, data: pd.Series, t_delta: datetime.timedelta
            ) -> pd.Series:
        """
        Fill discharge time series
        
        :param pd.Timestamp start_time: Timestamp of the first recorded data
        :param pd.Timestamp end_time: Timestamp of the last recorded data
        :param pd.Series data: The time series to be filled
        :param datetime.timedelta t_delta: The time series' frequency; minutes between data points (usually 15)
        
        :return pd.Series: The filled time series
        """
        
        index = pd.date_range(start=start_time, end=end_time, freq=t_delta)
        dummy_data = pd.DataFrame(index=index)
        dummy_data['Data'] = data / 100
        return dummy_data['Data'].interpolate().drop(dummy_data.index[:4]).fillna(0)
    