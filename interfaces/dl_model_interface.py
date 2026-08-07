from dataclasses import dataclass

from src.base_interface import BaseInterface


@dataclass
class DLModelInterface(BaseInterface):
    t_station_r_data: dict
    n_stations_p_data: dict