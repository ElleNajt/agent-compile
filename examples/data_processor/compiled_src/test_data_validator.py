"""Tests for data_validator module."""

import pytest
from data_validator import validate


def test_valid_records():
    """Test that valid records are correctly identified."""
    records = [{'name': 'Alice', 'age': 30}]
    rules = {'name': str, 'age': int}

    valid, invalid = validate(records, rules)

    assert valid == [{'name': 'Alice', 'age': 30}]
    assert invalid == []


def test_invalid_types():
    """Test that invalid types are caught."""
    records = [{'name': 'Bob', 'age': 'invalid'}]
    rules = {'name': str, 'age': int}

    valid, invalid = validate(records, rules)

    assert valid == []
    assert invalid == [{'name': 'Bob', 'age': 'invalid'}]


def test_missing_required_fields_none_value():
    """Test that None values in required fields are treated as invalid."""
    records = [{'name': None, 'age': 25}]
    rules = {'name': str, 'age': int}

    valid, invalid = validate(records, rules)

    assert valid == []
    assert invalid == [{'name': None, 'age': 25}]


def test_missing_required_fields_absent_key():
    """Test that missing field keys are treated as invalid."""
    records = [{'age': 25}]
    rules = {'name': str, 'age': int}

    valid, invalid = validate(records, rules)

    assert valid == []
    assert invalid == [{'age': 25}]


def test_mixed_data():
    """Test that mixed valid/invalid records are correctly separated."""
    records = [
        {'name': 'Alice', 'age': 30},      # valid
        {'name': 'Bob', 'age': 'invalid'}, # invalid - wrong type
        {'name': 'Charlie', 'age': 25},    # valid
        {'name': None, 'age': 35},         # invalid - None value
        {'age': 40},                        # invalid - missing field
        {'name': 'Dave', 'age': 45}        # valid
    ]
    rules = {'name': str, 'age': int}

    valid, invalid = validate(records, rules)

    assert len(valid) == 3
    assert len(invalid) == 3
    assert {'name': 'Alice', 'age': 30} in valid
    assert {'name': 'Charlie', 'age': 25} in valid
    assert {'name': 'Dave', 'age': 45} in valid
    assert {'name': 'Bob', 'age': 'invalid'} in invalid
    assert {'name': None, 'age': 35} in invalid
    assert {'age': 40} in invalid


def test_empty_records_list():
    """Test that empty records list returns empty valid and invalid lists."""
    records = []
    rules = {'name': str, 'age': int}

    valid, invalid = validate(records, rules)

    assert valid == []
    assert invalid == []


def test_additional_fields_allowed():
    """Test that records with additional fields (beyond rules) are still valid."""
    records = [{'name': 'Alice', 'age': 30, 'city': 'NYC'}]
    rules = {'name': str, 'age': int}

    valid, invalid = validate(records, rules)

    assert valid == [{'name': 'Alice', 'age': 30, 'city': 'NYC'}]
    assert invalid == []


def test_multiple_type_constraints():
    """Test validation with various Python types."""
    records = [
        {'name': 'Alice', 'age': 30, 'score': 95.5, 'active': True},  # valid
        {'name': 'Bob', 'age': 25, 'score': 88, 'active': True},      # invalid - score is int not float
        {'name': 'Charlie', 'age': 35, 'score': 92.0, 'active': 1}    # invalid - active is int not bool
    ]
    rules = {'name': str, 'age': int, 'score': float, 'active': bool}

    valid, invalid = validate(records, rules)

    assert len(valid) == 1
    assert len(invalid) == 2
    assert valid[0]['name'] == 'Alice'
