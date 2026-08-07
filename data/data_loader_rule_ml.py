from abc import ABC

from src.data_loader_base import DataLoaderBase


class DataLoaderRuleML(DataLoaderBase, ABC):
    def __init__(self):
        super().__init__()
