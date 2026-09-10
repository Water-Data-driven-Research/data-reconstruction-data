import datetime
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.data.raw.data_loader_json import DataLoaderJson
from src.data.raw.data_preprocessor_raw import DataPreprocessorRaw
from src.data.data_saver import DataSaver


@pytest.fixture
def sample_gappy_json() -> list[dict]:
    """
    Pytest fixture providing mock JSON data matching the raw API structure.
    Contains time steps with a 15-minute gap (01:15 is missing) to test gap-filling functionality.

    :return list[dict]: Mock JSON data containing time series entries with missing time stamps.
    """
    return [
        {
            "TsItemList": [
                {"UTCTime": "2023-01-01T00:00:00", "Adat": 1.0},
                {"UTCTime": "2023-01-01T00:15:00", "Adat": 1.2},
                {"UTCTime": "2023-01-01T00:30:00", "Adat": 1.4},
                {"UTCTime": "2023-01-01T00:45:00", "Adat": 1.6},
                {"UTCTime": "2023-01-01T01:00:00", "Adat": 2.0},
                # Gap at 01:15 (missing)
                {"UTCTime": "2023-01-01T01:30:00", "Adat": 4.0},
                {"UTCTime": "2023-01-01T01:45:00", "Adat": 4.5},
            ]
        }
    ]


# ==============================================================================
# DataLoaderJson Tests
# ==============================================================================

def test_transform_json_data_creates_series_with_holes(sample_gappy_json: list[dict]):
    """
    Tests that transform_json_data creates a pd.Series with missing values (NaNs)
    where time stamps are missing in the raw JSON input, and performs unit conversions.

    :param list[dict] sample_gappy_json: Pytest fixture containing gappy mock JSON data.
    """
    ts_data = sample_gappy_json[0]["TsItemList"]

    # Test unit conversion (m to cm) and index reindexing with holes
    series_cm = DataLoaderJson.transform_json_data(data=ts_data, do_conversion=True)

    assert isinstance(series_cm, pd.Series)
    assert len(series_cm) == 8  # 00:00 to 01:45 at 15min intervals
    assert series_cm.loc["2023-01-01 00:00:00"] == 100.0
    assert series_cm.loc["2023-01-01 01:00:00"] == 200.0
    assert pd.isna(series_cm.loc["2023-01-01 01:15:00"])  # Hole verified

    # Test without unit conversion
    series_m = DataLoaderJson.transform_json_data(data=ts_data, do_conversion=False)
    assert series_m.loc["2023-01-01 00:00:00"] == 1.0


def test_load_file_success(tmp_path: Path, sample_gappy_json: list[dict]):
    """
    Tests successful loading and parsing of a validly named JSON file, saving metadata
    and raw data as class attributes.

    :param Path tmp_path: Pytest temporary directory fixture.
    :param list[dict] sample_gappy_json: Pytest fixture containing gappy mock JSON data.
    """
    loader = DataLoaderJson()

    # Pattern: (\S{2})_(\d{6})_(\d{4}-\d{2})_(\d{4}-\d{2})
    file_name = "rp_123456_2023-01_2023-02.json"
    file_path = tmp_path / file_name

    with open(file_path, "w") as f:
        json.dump(sample_gappy_json, f)

    loader.load_file(str(file_path))

    assert loader.start_time == pd.to_datetime("2023-01")
    assert loader.end_time == pd.to_datetime("2023-02")
    assert loader.d_train_type == "r"
    assert loader.d_type == "p"
    assert isinstance(loader.raw_data, pd.Series)


def test_load_file_invalid_name(tmp_path: Path, sample_gappy_json: list[dict]):
    """
    Tests that load_file raises a ValueError when given a file path with an invalid naming pattern.

    :param Path tmp_path: Pytest temporary directory fixture.
    :param list[dict] sample_gappy_json: Pytest fixture containing gappy mock JSON data.
    """
    loader = DataLoaderJson()
    invalid_path = tmp_path / "invalid_filename.json"

    with open(invalid_path, "w") as f:
        json.dump(sample_gappy_json, f)

    with pytest.raises(ValueError, match="File name does not follow naming format"):
        loader.load_file(str(invalid_path))


# ==============================================================================
# DataPreprocessorRaw Tests
# ==============================================================================

def test_preprocessor_r_p_fill_interpolates_holes(sample_gappy_json: list[dict]):
    """
    Tests that r_p_fill takes a pd.Series containing holes (NaNs), interpolates missing values
    across the complete time index, and returns a clean pd.Series with no NaNs.

    :param list[dict] sample_gappy_json: Pytest fixture containing gappy mock JSON data.
    """
    ts_data = sample_gappy_json[0]["TsItemList"]
    raw_series = DataLoaderJson.transform_json_data(data=ts_data, do_conversion=True)

    start_time = raw_series.index.min()
    end_time = raw_series.index.max()
    t_delta = datetime.timedelta(minutes=15)

    filled_series = DataPreprocessorRaw.r_p_fill(start_time, end_time, raw_series, t_delta)

    assert isinstance(filled_series, pd.Series)
    assert not filled_series.isna().any()  # Asserts all holes are filled
    # Linear interpolation between 200.0 (01:00) and 400.0 (01:30) at 01:15 should be 300.0
    assert filled_series.loc["2023-01-01 01:15:00"] == 300.0


def test_preprocessor_di_fill_scales_and_fills(sample_gappy_json: list[dict]):
    """
    Tests discharge filling (di_fill) logic: scales values down by 100, interpolates missing
    holes, and returns a clean pd.Series.

    :param list[dict] sample_gappy_json: Pytest fixture containing gappy mock JSON data.
    """
    ts_data = sample_gappy_json[0]["TsItemList"]
    raw_series = DataLoaderJson.transform_json_data(data=ts_data, do_conversion=True)

    start_time = raw_series.index.min()
    end_time = raw_series.index.max()
    t_delta = datetime.timedelta(minutes=15)

    filled_series = DataPreprocessorRaw.di_fill(start_time, end_time, raw_series, t_delta)

    assert isinstance(filled_series, pd.Series)
    assert not filled_series.isna().any()
    # Interpolated value (300.0) scaled down by 100 should be 3.0
    assert filled_series.loc["2023-01-01 01:15:00"] == 3.0


# ==============================================================================
# DataSaver Tests & Integration Pipeline
# ==============================================================================

def test_data_saver_save_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    Tests saving a pandas Series to disk as a CSV file using DataSaver.

    :param Path tmp_path: Pytest temporary directory fixture.
    :param pytest.MonkeyPatch monkeypatch: Pytest fixture to temporarily override data_folder.
    """
    monkeypatch.setattr("src.data.data_saver.data_folder", tmp_path)

    saver = DataSaver()
    test_series = pd.Series(
        [100.0, 200.0],
        index=pd.date_range("2023-01-01", periods=2, freq="15min"),
        name="Data",
    )

    saver.save_csv(data=test_series, file_name="output_test", include_index=True)

    expected_csv = tmp_path / "csv" / "output_test.csv"
    assert expected_csv.exists()

    saved_data = pd.read_csv(expected_csv)
    assert "Data" in saved_data.columns


def test_full_data_loading_pipeline(tmp_path: Path, sample_gappy_json: list[dict], monkeypatch: pytest.MonkeyPatch):
    """
    Integration test verifying the end-to-end data flow: loading raw JSON data,
    preprocessing and interpolating missing holes, and saving the final result as a CSV file.

    :param Path tmp_path: Pytest temporary directory fixture.
    :param list[dict] sample_gappy_json: Pytest fixture containing gappy mock JSON data.
    :param pytest.MonkeyPatch monkeypatch: Pytest fixture to temporarily override data_folder.
    """
    monkeypatch.setattr("src.data.data_saver.data_folder", tmp_path)

    # 1. Setup raw JSON file
    file_name = "rp_123456_2023-01_2023-02.json"
    file_path = tmp_path / file_name
    with open(file_path, "w") as f:
        json.dump(sample_gappy_json, f)

    # 2. Load
    loader = DataLoaderJson()
    loader.load_file(str(file_path))

    # 3. Preprocess holes
    processed_series = DataPreprocessorRaw.r_p_fill(
        start_time=loader.start_time,
        end_time=loader.end_time,
        data=loader.raw_data,
        t_delta=datetime.timedelta(minutes=15),
    )

    # 4. Save
    saver = DataSaver()
    saver.save_csv(data=processed_series, file_name=file_name.removesuffix(".json"))

    # 5. Assert output CSV state
    expected_path = tmp_path / "csv" / "rp_123456_2023-01_2023-02.csv"
    assert expected_path.exists()

    final_df = pd.read_csv(expected_path)
    assert not final_df.isna().any().any()