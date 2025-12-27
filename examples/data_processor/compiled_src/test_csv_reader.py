"""Tests for csv_reader module"""

import pytest
import os
import tempfile
from csv_reader import read_csv


class TestReadCSV:
    """Test cases for read_csv function"""

    def test_read_valid_csv(self, tmp_path):
        """Test reading a valid CSV file returns list of dicts with correct keys"""
        # Create a test CSV file
        test_file = tmp_path / "test_data.csv"
        test_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,SF\n")

        # Read the CSV
        result = read_csv(str(test_file))

        # Verify the result
        assert len(result) == 2
        assert result[0] == {"name": "Alice", "age": "30", "city": "NYC"}
        assert result[1] == {"name": "Bob", "age": "25", "city": "SF"}

        # Verify all rows have the same keys matching headers
        for row in result:
            assert set(row.keys()) == {"name", "age", "city"}

    def test_missing_file(self):
        """Test that reading a non-existent file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            read_csv("nonexistent.csv")

    def test_malformed_csv_inconsistent_columns(self, tmp_path):
        """Test that CSV with inconsistent columns raises ValueError"""
        # Create a malformed CSV with inconsistent columns
        test_file = tmp_path / "bad.csv"
        test_file.write_text("col1,col2,col3\nval1,val2,val3\nval4,val5\n")

        with pytest.raises(ValueError):
            read_csv(str(test_file))

    def test_empty_values_converted_to_none(self, tmp_path):
        """Test that empty CSV cells are converted to None"""
        # Create a CSV with empty values
        test_file = tmp_path / "empty_values.csv"
        test_file.write_text("name,age,city\nAlice,,NYC\n,25,\nBob,30,SF\n")

        result = read_csv(str(test_file))

        assert len(result) == 3
        assert result[0] == {"name": "Alice", "age": None, "city": "NYC"}
        assert result[1] == {"name": None, "age": "25", "city": None}
        assert result[2] == {"name": "Bob", "age": "30", "city": "SF"}

    def test_empty_file_with_only_headers(self, tmp_path):
        """Test reading a CSV with only headers returns empty list"""
        test_file = tmp_path / "headers_only.csv"
        test_file.write_text("col1,col2,col3\n")

        result = read_csv(str(test_file))

        assert result == []

    def test_single_column_csv(self, tmp_path):
        """Test reading a CSV with a single column"""
        test_file = tmp_path / "single_column.csv"
        test_file.write_text("name\nAlice\nBob\n")

        result = read_csv(str(test_file))

        assert len(result) == 2
        assert result[0] == {"name": "Alice"}
        assert result[1] == {"name": "Bob"}

    def test_csv_with_whitespace_values(self, tmp_path):
        """Test that whitespace values are preserved (not converted to None)"""
        test_file = tmp_path / "whitespace.csv"
        test_file.write_text("name,age,city\nAlice,30,  \n  ,25,SF\n")

        result = read_csv(str(test_file))

        # Whitespace should be preserved, empty strings become None
        assert result[0] == {"name": "Alice", "age": "30", "city": "  "}
        assert result[1] == {"name": "  ", "age": "25", "city": "SF"}
