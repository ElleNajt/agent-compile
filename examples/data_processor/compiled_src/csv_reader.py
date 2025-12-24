"""CSV reader module that reads CSV files and returns data as list of dictionaries."""

import csv
from pathlib import Path
from typing import List, Dict, Any, Optional


def csv_reader(filepath: str) -> List[Dict[str, Any]]:
    """Read CSV file and return data as list of dictionaries.

    Takes a file path and returns parsed CSV data.
    Each row becomes a dictionary with column names as keys.
    Handles missing values by setting them to None.
    Raises FileNotFoundError if file doesn't exist.
    Raises ValueError if CSV is malformed.

    Args:
        filepath: Path to the CSV file to read

    Returns:
        List of dictionaries, where each dictionary represents a row
        with column names as keys

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the CSV is malformed
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    data: List[Dict[str, Any]] = []

    with path.open('r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(f"CSV file is malformed: no headers found in {filepath}")

        for row_num, row in enumerate(reader, start=2):
            processed_row: Dict[str, Any] = {}
            for key, value in row.items():
                if value == '' or value is None:
                    processed_row[key] = None
                else:
                    processed_row[key] = _infer_type(value)
            data.append(processed_row)

    return data


def _infer_type(value: str) -> Any:
    """Infer the type of a string value and convert it."""
    if value == '':
        return None

    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        return value
