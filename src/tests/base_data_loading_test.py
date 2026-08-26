import json
from pathlib import Path
import pandas as pd
import pytest

from src.base.data_loader_base import DataLoaderBase
from src.data.data_saver import DataSaver


class ConcreteDataLoader(DataLoaderBase):
    def load_data(self):
        """
        Concrete implementation of the abstract load_data method for testing
        """

        pass


@pytest.fixture
def sample_json_data():
    """
    Pytest fixture providing mock JSON data matching raw API structure

    :return list[dict]: Mock JSON data containing time series entries
    """

    return [
        {
            "TsItemList": [
                {"UTCTime": "2023-01-01T00:00:00", "Adat": 1.5},
                {"UTCTime": "2023-01-01T01:00:00", "Adat": 2.0},
            ]
        }
    ]


def test_transform_json_data(sample_json_data: list[dict]):
    """
    Tests the transform_json_data function for unit conversion and timezone handling

    :param list[dict] sample_json_data: Pytest fixture containing mock JSON data
    """

    ts_data = sample_json_data[0]["TsItemList"]

    # Test default multiplication (m to cm)
    data_cm = DataLoaderBase.transform_json_data(ts_data, do_multiply=True)
    assert data_cm["Adat"].tolist() == [150.0, 200.0]
    assert isinstance(data_cm.index, pd.DatetimeIndex)

    # Test without multiplication
    data_m = DataLoaderBase.transform_json_data(ts_data, do_multiply=False)
    assert data_m["Adat"].tolist() == [1.5, 2.0]
    assert isinstance(data_cm.index, pd.DatetimeIndex)


def test_load_file_success(tmp_path: Path, sample_json_data: list[dict]):
    """
    Tests successful loading and parsing of a validly named JSON file

    :param Path tmp_path: Pytest temporary directory fixture
    :param list[dict] sample_json_data: Pytest fixture containing mock JSON data
    """

    loader = ConcreteDataLoader()

    file_name = "lb_220029_2020-01_2020-02.json"
    file_path = tmp_path / file_name

    with open(file_path, "w") as f:
        json.dump(sample_json_data, f)

    start_time, end_time, d_nature, d_type, data = loader.load_file(str(file_path))

    assert start_time == pd.to_datetime("2020-01")
    assert end_time == pd.to_datetime("2020-02")
    assert d_nature == "l"
    assert d_type == "b"
    assert len(data) == 2


def test_load_file_invalid_name(tmp_path: Path, sample_json_data: list[dict]):
    """
    Tests that load_file raises a ValueError when given an invalid filename pattern

    :param Path tmp_path: Pytest temporary directory fixture
    :param list[dict] sample_json_data: Pytest fixture containing mock JSON data
    """

    loader = ConcreteDataLoader()
    invalid_path = tmp_path / "invalid_filename.json"

    with open(invalid_path, "w") as f:
        json.dump(sample_json_data, f)

    with pytest.raises(ValueError, match="File name does not follow naming format"):
        loader.load_file(str(invalid_path))


def test_data_saver_save_csv(tmp_path: Path):
    """
    Tests saving a pd.DataFrame to a CSV file on disk using DataSaver

    :param Path tmp_path: Pytest temporary directory fixture
    """

    data = pd.DataFrame({"UTCTime": ["2023-01-01"], "Adat": [150.0]})
    out_dir = tmp_path / "output_dir"
    file_name = "sample_data.json"

    DataSaver.save_csv(data=data, file_path=str(out_dir), file_name=file_name)

    expected_csv_path = out_dir / "sample_data.csv"
    assert expected_csv_path.exists()

    saved_data = pd.read_csv(expected_csv_path)
    assert "Adat" in saved_data.columns
    