from dataclasses import dataclass

from src.base.base_interface import BaseInterface


@dataclass
class SawtoothInterface(BaseInterface):
    n_stations_r_data: dict