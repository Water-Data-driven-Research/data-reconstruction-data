from dataclasses import dataclass

import pandas as pd

from src.base_interface import BaseInterface


@dataclass
class UnsupervisedEvalInterface(BaseInterface):
    result: pd.DataFrame
    t_station_r_data: dict
    n_stations_p_data: dict