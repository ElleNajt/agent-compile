"""Data Validator Module

Validate data records according to schema rules.
"""

from typing import List, Dict, Any, Tuple, Type


def validate(
    records: List[Dict[str, Any]],
    rules: Dict[str, Type]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Validate data records according to schema rules.

    Args:
        records: List of dictionaries to validate
        rules: Validation rules dictionary mapping field names to Python type objects
               Example: {"name": str, "age": int}

    Returns:
        Tuple of (valid_records, invalid_records)
        A record is valid if all required fields exist and match their type constraints.
    """
    valid_records = []
    invalid_records = []

    for record in records:
        is_valid = True

        # Check all required fields
        for field_name, field_type in rules.items():
            # Field must exist in the record
            if field_name not in record:
                is_valid = False
                break

            # Field value must not be None
            field_value = record[field_name]
            if field_value is None:
                is_valid = False
                break

            # Field value must match the expected type
            if not isinstance(field_value, field_type):
                is_valid = False
                break

        if is_valid:
            valid_records.append(record)
        else:
            invalid_records.append(record)

    return (valid_records, invalid_records)
