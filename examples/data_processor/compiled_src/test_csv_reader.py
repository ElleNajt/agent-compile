"""Tests for csv_reader module."""

import pytest
import tempfile
from pathlib import Path
from csv_reader import csv_reader


class TestCSVReader:
    """Test cases for csv_reader function."""

    def test_read_valid_csv(self, tmp_path):
        """Test reading a valid CSV file.

        Test 1: Read valid CSV
        Inputs: {'filepath': 'test_data.csv'}
        Expected Outputs: {'data': [{'name': 'Alice', 'age': 30, 'city': 'NYC'},
                                     {'name': 'Bob', 'age': 25, 'city': 'SF'}]}
        """
        csv_content = """name,age,city
Alice,30,NYC
Bob,25,SF"""

        test_file = tmp_path / "test_data.csv"
        test_file.write_text(csv_content)

        result = csv_reader(str(test_file))

        expected = [
            {'name': 'Alice', 'age': 30, 'city': 'NYC'},
            {'name': 'Bob', 'age': 25, 'city': 'SF'}
        ]

        assert result == expected

    def test_file_not_found(self):
        """Test that FileNotFoundError is raised when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            csv_reader("nonexistent_file.csv")

    def test_missing_values(self, tmp_path):
        """Test handling of missing values (should be set to None)."""
        csv_content = """name,age,city
Alice,30,NYC
Bob,,SF
Charlie,35,"""

        test_file = tmp_path / "test_missing.csv"
        test_file.write_text(csv_content)

        result = csv_reader(str(test_file))

        expected = [
            {'name': 'Alice', 'age': 30, 'city': 'NYC'},
            {'name': 'Bob', 'age': None, 'city': 'SF'},
            {'name': 'Charlie', 'age': 35, 'city': None}
        ]

        assert result == expected

    def test_malformed_csv_no_headers(self, tmp_path):
        """Test that ValueError is raised for malformed CSV (no headers)."""
        csv_content = ""

        test_file = tmp_path / "test_malformed.csv"
        test_file.write_text(csv_content)

        with pytest.raises(ValueError, match="malformed"):
            csv_reader(str(test_file))

    def test_empty_csv_with_headers(self, tmp_path):
        """Test reading CSV with headers but no data rows."""
        csv_content = """name,age,city"""

        test_file = tmp_path / "test_empty.csv"
        test_file.write_text(csv_content)

        result = csv_reader(str(test_file))

        assert result == []
