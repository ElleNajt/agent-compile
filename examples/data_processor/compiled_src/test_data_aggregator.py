"""Tests for Data Aggregator Module"""

import pytest
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
    assert result == expected


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
    assert len(result) == 1
    assert 'all' in result
    assert result['all']['value_sum'] == 60
    assert result['all']['value_average'] == 20.0


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

    assert result['all']['score_count'] == 4
    assert result['all']['score_sum'] == 70
    assert result['all']['score_average'] == 17.5
    assert result['all']['score_min'] == 10
    assert result['all']['score_max'] == 25


def test_empty_data():
    """Test 4: Empty data should return empty results dict"""
    result = aggregate(
        [],
        aggregations={'value': ['sum', 'average']}
    )

    assert result == {}


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

    assert result['all']['price_sum'] == pytest.approx(46.5)
    assert result['all']['price_average'] == pytest.approx(15.5)
    assert result['all']['price_min'] == pytest.approx(10.5)
    assert result['all']['price_max'] == pytest.approx(20.7)
