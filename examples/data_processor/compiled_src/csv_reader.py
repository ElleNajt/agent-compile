"""CSV Reader Module

Read CSV file and return data as list of dictionaries.
Each row becomes a dictionary with column names as keys.
"""

import csv
from typing import List, Dict, Optional


def read_csv(file_path: str) -> List[Dict[str, Optional[str]]]:
    """Read CSV file and return data as list of dictionaries.

    Args:
        file_path: Path to the CSV file to read

    Returns:
        List of dictionaries where each dictionary represents a row,
        with column names as keys. Empty values are set to None.

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the CSV is malformed (inconsistent columns)
    """
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            # Use regular reader to validate column counts
            lines = list(csv.reader(csvfile))

            if len(lines) == 0:
                raise ValueError("CSV file is empty")

            # First line is headers
            headers = lines[0]
            expected_cols = len(headers)

            # Validate all data rows have correct number of columns
            for row_num, row in enumerate(lines[1:], start=2):
                if len(row) != expected_cols:
                    raise ValueError(
                        f"Inconsistent number of columns at row {row_num}: "
                        f"expected {expected_cols}, got {len(row)}"
                    )

            # Now build the result as list of dicts
            result = []
            for row in lines[1:]:
                row_dict = {}
                for i, header in enumerate(headers):
                    value = row[i]
                    row_dict[header] = None if value == '' else value
                result.append(row_dict)

            return result

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
