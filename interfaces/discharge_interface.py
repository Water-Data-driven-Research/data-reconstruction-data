from dataclasses import dataclass

from src.base_interface import BaseInterface


@dataclass
class DischargeInterface(BaseInterface):
    t_station_p_data: dict
    t_station_null_points: dict
    t_station_river_km: dict
    n_stations_p_data: dict
    n_stations_null_points: dict
    n_stations_river_km: dict
    water_discharge_data: dict
    kh_curve_data: dict