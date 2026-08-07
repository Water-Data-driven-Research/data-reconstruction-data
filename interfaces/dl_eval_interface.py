from dataclasses import dataclass

import pandas as pd

from src.base_interface import BaseInterface

@dataclass
class DLEvalInterface(BaseInterface):
    t_station_p_data: dict
    t_station_r_data: dict
    dl_result: pd.DataFrame
