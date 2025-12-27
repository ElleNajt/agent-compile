"""Simple test runner to run csv_reader tests without pytest"""

import tempfile
import os
import sys
from pathlib import Path
from csv_reader import read_csv


def test_read_valid_csv():
    """Test reading a valid CSV file returns list of dicts with correct keys"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        test_file = tmp_path / "test_data.csv"
        test_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,SF\n")

        result = read_csv(str(test_file))

        assert len(result) == 2, f"Expected 2 rows, got {len(result)}"
        assert result[0] == {"name": "Alice", "age": "30", "city": "NYC"}, f"First row mismatch: {result[0]}"
        assert result[1] == {"name": "Bob", "age": "25", "city": "SF"}, f"Second row mismatch: {result[1]}"

        for row in result:
            assert set(row.keys()) == {"name", "age", "city"}, f"Keys mismatch: {set(row.keys())}"

    print("✓ test_read_valid_csv passed")


def test_missing_file():
    """Test that reading a non-existent file raises FileNotFoundError"""
    try:
        read_csv("nonexistent.csv")
        raise AssertionError("Expected FileNotFoundError but no exception was raised")
    except FileNotFoundError as e:
        # Expected - test passes
        assert "File not found" in str(e) or "nonexistent.csv" in str(e)

    print("✓ test_missing_file passed")


def test_malformed_csv_inconsistent_columns():
    """Test that CSV with inconsistent columns raises ValueError"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        test_file = tmp_path / "bad.csv"
        test_file.write_text("col1,col2,col3\nval1,val2,val3\nval4,val5\n")

        try:
            read_csv(str(test_file))
            raise AssertionError("Expected ValueError but no exception was raised")
        except ValueError as e:
            # Expected - test passes
            assert "Inconsistent" in str(e) or "columns" in str(e)

    print("✓ test_malformed_csv_inconsistent_columns passed")


def test_empty_values_converted_to_none():
    """Test that empty CSV cells are converted to None"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        test_file = tmp_path / "empty_values.csv"
        test_file.write_text("name,age,city\nAlice,,NYC\n,25,\nBob,30,SF\n")

        result = read_csv(str(test_file))

        assert len(result) == 3, f"Expected 3 rows, got {len(result)}"
        assert result[0] == {"name": "Alice", "age": None, "city": "NYC"}, f"Row 0 mismatch: {result[0]}"
        assert result[1] == {"name": None, "age": "25", "city": None}, f"Row 1 mismatch: {result[1]}"
        assert result[2] == {"name": "Bob", "age": "30", "city": "SF"}, f"Row 2 mismatch: {result[2]}"

    print("✓ test_empty_values_converted_to_none passed")


def test_empty_file_with_only_headers():
    """Test reading a CSV with only headers returns empty list"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        test_file = tmp_path / "headers_only.csv"
        test_file.write_text("col1,col2,col3\n")

        result = read_csv(str(test_file))

        assert result == [], f"Expected empty list, got {result}"

    print("✓ test_empty_file_with_only_headers passed")


def test_single_column_csv():
    """Test reading a CSV with a single column"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        test_file = tmp_path / "single_column.csv"
        test_file.write_text("name\nAlice\nBob\n")

        result = read_csv(str(test_file))

        assert len(result) == 2, f"Expected 2 rows, got {len(result)}"
        assert result[0] == {"name": "Alice"}, f"Row 0 mismatch: {result[0]}"
        assert result[1] == {"name": "Bob"}, f"Row 1 mismatch: {result[1]}"

    print("✓ test_single_column_csv passed")


def run_all_tests():
    """Run all tests and report results"""
    tests = [
        test_read_valid_csv,
        test_missing_file,
        test_malformed_csv_inconsistent_columns,
        test_empty_values_converted_to_none,
        test_empty_file_with_only_headers,
        test_single_column_csv,
    ]

    failed = 0
    passed = 0

    print("Running tests...\n")

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Test Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
