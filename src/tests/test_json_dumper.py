import json
import pandas as pd
import pytest
from pathlib import Path

from src.data.json_dumper import JsonDumper


@pytest.fixture
def sample_df():
    return pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})


@pytest.fixture
def sample_series():
    return pd.Series([10, 20, 30], name="numbers")


def test_dump_json_dataframe(tmp_path: Path, sample_df: pd.DataFrame):
    """
    Tests whether JsonDumper can dump a pd.DataFrame successfully

    :param Path tmp_path: Path of the output directory
    :param pd.DataFrame sample_df: The dataframe to dump
    """

    file_name = "test_df"

    # Call the method passing the temporary test directory
    JsonDumper.dump_json(sample_df, file_name, file_path=tmp_path)

    expected_file = tmp_path / f"{file_name}.json"

    # Check file existence
    assert expected_file.is_file()

    # Verify content format ("records" orientation)
    with open(expected_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_data = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    assert data == expected_data


def test_dump_json_series(tmp_path: Path, sample_series: pd.Series):
    """
    Tests whether JsonDumper can dump a pd.Series successfully

    :param Path tmp_path: Path of the output directory
    :param pd.DataFrame sample_series: The series to dump
    """

    file_name = "test_series"

    JsonDumper.dump_json(sample_series, file_name, file_path=tmp_path)

    expected_file = tmp_path / f"{file_name}.json"

    assert expected_file.is_file()

    with open(expected_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data == [10, 20, 30]


def test_dump_json_creates_nonexistent_directory(tmp_path: Path, sample_df: pd.DataFrame):
    """
    Tests whether JsonDumper can create a directory that doesn't exist prior to the method call

    :param Path tmp_path: Path of the output directory
    :param pd.DataFrame sample_df: The dataframe to dump
    :return:
    """

    nested_dir = tmp_path / "nested" / "subfolder"
    file_name = "nested_test"

    # Directory should not exist before running
    assert not nested_dir.exists()

    JsonDumper.dump_json(sample_df, file_name, file_path=nested_dir)

    # Directory and file should now exist
    assert nested_dir.exists()
    assert (nested_dir / f"{file_name}.json").is_file()