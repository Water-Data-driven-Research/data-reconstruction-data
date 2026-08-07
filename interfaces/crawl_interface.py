from dataclasses import dataclass

from src.base_interface import BaseInterface


@dataclass
class CrawlInterface(BaseInterface):
    n_stations_de_data: dict