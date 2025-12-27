"""Simple test runner for data_aggregator tests"""

import sys
from data_aggregator import aggregate


def test_group_and_aggregate():
    """Test 1: Group and aggregate by category"""
    records = [
        {'category': 'A', 'value': 10},
        {'category': 'A', 'value': 20},
        {'category': 'B', 'value': 15}
    ]
    result = aggregate(
        records,
        group_by='category',
        aggregations={'value': ['sum', 'average']}
    )

    expected = {
        'A': {'value_sum': 30, 'value_average': 15.0},
        'B': {'value_sum': 15, 'value_average': 15.0}
    }
    assert result == expected, f"Expected {expected}, got {result}"

    print("✓ test_group_and_aggregate passed")


def test_no_grouping():
    """Test 2: Aggregate without group_by should aggregate all records together"""
    records = [
        {'value': 10},
        {'value': 20},
        {'value': 30}
    ]
    result = aggregate(
        records,
        aggregations={'value': ['sum', 'average']}
    )

    # Without group_by, all records should be in a single group
    assert len(result) == 1, f"Expected 1 group, got {len(result)}"
    assert 'all' in result, f"Expected 'all' key in result, got {result.keys()}"
    assert result['all']['value_sum'] == 60, f"Expected sum=60, got {result['all']['value_sum']}"
    assert result['all']['value_average'] == 20.0, f"Expected average=20.0, got {result['all']['value_average']}"

    print("✓ test_no_grouping passed")


def test_multiple_aggregations():
    """Test 3: Support count, sum, average, min, max on numeric fields"""
    records = [
        {'score': 10},
        {'score': 20},
        {'score': 15},
        {'score': 25}
    ]
    result = aggregate(
        records,
        aggregations={'score': ['count', 'sum', 'average', 'min', 'max']}
    )

    assert result['all']['score_count'] == 4, f"Expected count=4, got {result['all']['score_count']}"
    assert result['all']['score_sum'] == 70, f"Expected sum=70, got {result['all']['score_sum']}"
    assert result['all']['score_average'] == 17.5, f"Expected average=17.5, got {result['all']['score_average']}"
    assert result['all']['score_min'] == 10, f"Expected min=10, got {result['all']['score_min']}"
    assert result['all']['score_max'] == 25, f"Expected max=25, got {result['all']['score_max']}"

    print("✓ test_multiple_aggregations passed")


def test_empty_data():
    """Test 4: Empty data should return empty results dict"""
    result = aggregate(
        [],
        aggregations={'value': ['sum', 'average']}
    )

    assert result == {}, f"Expected empty dict {{}}, got {result}"

    print("✓ test_empty_data passed")


def test_multiple_fields_aggregation():
    """Test aggregating multiple fields at once"""
    records = [
        {'category': 'X', 'sales': 100, 'quantity': 5},
        {'category': 'X', 'sales': 200, 'quantity': 10},
        {'category': 'Y', 'sales': 150, 'quantity': 7}
    ]
    result = aggregate(
        records,
        group_by='category',
        aggregations={
            'sales': ['sum', 'average'],
            'quantity': ['sum', 'average']
        }
    )

    assert result['X']['sales_sum'] == 300
    assert result['X']['sales_average'] == 150.0
    assert result['X']['quantity_sum'] == 15
    assert result['X']['quantity_average'] == 7.5
    assert result['Y']['sales_sum'] == 150
    assert result['Y']['sales_average'] == 150.0
    assert result['Y']['quantity_sum'] == 7
    assert result['Y']['quantity_average'] == 7.0

    print("✓ test_multiple_fields_aggregation passed")


def test_single_aggregation_function():
    """Test using just one aggregation function"""
    records = [
        {'group': 'A', 'value': 5},
        {'group': 'A', 'value': 10},
        {'group': 'B', 'value': 20}
    ]
    result = aggregate(
        records,
        group_by='group',
        aggregations={'value': ['max']}
    )

    assert result['A']['value_max'] == 10
    assert result['B']['value_max'] == 20

    print("✓ test_single_aggregation_function passed")


def test_float_values():
    """Test aggregating float values"""
    records = [
        {'price': 10.5},
        {'price': 20.7},
        {'price': 15.3}
    ]
    result = aggregate(
        records,
        aggregations={'price': ['sum', 'average', 'min', 'max']}
    )

    # Use approximate comparison for floats
    assert abs(result['all']['price_sum'] - 46.5) < 0.0001
    assert abs(result['all']['price_average'] - 15.5) < 0.0001
    assert abs(result['all']['price_min'] - 10.5) < 0.0001
    assert abs(result['all']['price_max'] - 20.7) < 0.0001

    print("✓ test_float_values passed")


def run_all_tests():
    """Run all tests and report results"""
    tests = [
        test_group_and_aggregate,
        test_no_grouping,
        test_multiple_aggregations,
        test_empty_data,
        test_multiple_fields_aggregation,
        test_single_aggregation_function,
        test_float_values,
    ]

    failed = 0
    passed = 0

    print("Running data_aggregator tests...\n")

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
