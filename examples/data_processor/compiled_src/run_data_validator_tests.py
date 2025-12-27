"""Simple test runner for data_validator tests"""

import sys
from data_validator import validate


def test_valid_records():
    """Test that valid records are correctly identified."""
    records = [{'name': 'Alice', 'age': 30}]
    rules = {'name': str, 'age': int}

    valid, invalid = validate(records, rules)

    assert valid == [{'name': 'Alice', 'age': 30}], f"Expected valid=[{{'name': 'Alice', 'age': 30}}], got {valid}"
    assert invalid == [], f"Expected invalid=[], got {invalid}"

    print("✓ test_valid_records passed")


def test_invalid_types():
    """Test that invalid types are caught."""
    records = [{'name': 'Bob', 'age': 'invalid'}]
    rules = {'name': str, 'age': int}

    valid, invalid = validate(records, rules)

    assert valid == [], f"Expected valid=[], got {valid}"
    assert invalid == [{'name': 'Bob', 'age': 'invalid'}], f"Expected invalid=[{{'name': 'Bob', 'age': 'invalid'}}], got {invalid}"

    print("✓ test_invalid_types passed")


def test_missing_required_fields_none_value():
    """Test that None values in required fields are treated as invalid."""
    records = [{'name': None, 'age': 25}]
    rules = {'name': str, 'age': int}

    valid, invalid = validate(records, rules)

    assert valid == [], f"Expected valid=[], got {valid}"
    assert invalid == [{'name': None, 'age': 25}], f"Expected invalid=[{{'name': None, 'age': 25}}], got {invalid}"

    print("✓ test_missing_required_fields_none_value passed")


def test_missing_required_fields_absent_key():
    """Test that missing field keys are treated as invalid."""
    records = [{'age': 25}]
    rules = {'name': str, 'age': int}

    valid, invalid = validate(records, rules)

    assert valid == [], f"Expected valid=[], got {valid}"
    assert invalid == [{'age': 25}], f"Expected invalid=[{{'age': 25}}], got {invalid}"

    print("✓ test_missing_required_fields_absent_key passed")


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

    assert len(valid) == 3, f"Expected 3 valid records, got {len(valid)}"
    assert len(invalid) == 3, f"Expected 3 invalid records, got {len(invalid)}"
    assert {'name': 'Alice', 'age': 30} in valid
    assert {'name': 'Charlie', 'age': 25} in valid
    assert {'name': 'Dave', 'age': 45} in valid
    assert {'name': 'Bob', 'age': 'invalid'} in invalid
    assert {'name': None, 'age': 35} in invalid
    assert {'age': 40} in invalid

    print("✓ test_mixed_data passed")


def test_empty_records_list():
    """Test that empty records list returns empty valid and invalid lists."""
    records = []
    rules = {'name': str, 'age': int}

    valid, invalid = validate(records, rules)

    assert valid == [], f"Expected valid=[], got {valid}"
    assert invalid == [], f"Expected invalid=[], got {invalid}"

    print("✓ test_empty_records_list passed")


def test_additional_fields_allowed():
    """Test that records with additional fields (beyond rules) are still valid."""
    records = [{'name': 'Alice', 'age': 30, 'city': 'NYC'}]
    rules = {'name': str, 'age': int}

    valid, invalid = validate(records, rules)

    assert valid == [{'name': 'Alice', 'age': 30, 'city': 'NYC'}], f"Expected valid record with extra field, got {valid}"
    assert invalid == [], f"Expected invalid=[], got {invalid}"

    print("✓ test_additional_fields_allowed passed")


def test_multiple_type_constraints():
    """Test validation with various Python types."""
    records = [
        {'name': 'Alice', 'age': 30, 'score': 95.5, 'active': True},  # valid
        {'name': 'Bob', 'age': 25, 'score': 88, 'active': True},      # invalid - score is int not float
        {'name': 'Charlie', 'age': 35, 'score': 92.0, 'active': 1}    # invalid - active is int not bool
    ]
    rules = {'name': str, 'age': int, 'score': float, 'active': bool}

    valid, invalid = validate(records, rules)

    assert len(valid) == 1, f"Expected 1 valid record, got {len(valid)}"
    assert len(invalid) == 2, f"Expected 2 invalid records, got {len(invalid)}"
    assert valid[0]['name'] == 'Alice'

    print("✓ test_multiple_type_constraints passed")


def run_all_tests():
    """Run all tests and report results"""
    tests = [
        test_valid_records,
        test_invalid_types,
        test_missing_required_fields_none_value,
        test_missing_required_fields_absent_key,
        test_mixed_data,
        test_empty_records_list,
        test_additional_fields_allowed,
        test_multiple_type_constraints,
    ]

    failed = 0
    passed = 0

    print("Running data_validator tests...\n")

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*60}")
    print(f"Test Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
