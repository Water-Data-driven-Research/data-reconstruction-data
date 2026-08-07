from abc import ABC

from src.data_loader import DataLoader


class RuleMLDataLoader(DataLoader, ABC):
    def __init__(self):
        super().__init__()
