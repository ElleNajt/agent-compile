"""Tests for calculator module."""

import pytest
from calculator import calculate


def test_addition():
    """Test addition operation."""
    result = calculate(a=10, b=5, operation='add')
    assert result == {'result': 15.0}


def test_subtraction():
    """Test subtraction operation."""
    result = calculate(a=10, b=5, operation='subtract')
    assert result == {'result': 5.0}


def test_multiplication():
    """Test multiplication operation."""
    result = calculate(a=10, b=5, operation='multiply')
    assert result == {'result': 50.0}


def test_division():
    """Test division operation."""
    result = calculate(a=10, b=5, operation='divide')
    assert result == {'result': 2.0}


def test_invalid_operation():
    """Test that invalid operation raises ValueError."""
    with pytest.raises(ValueError):
        calculate(a=10, b=5, operation='invalid')


def test_division_by_zero():
    """Test that division by zero raises ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError):
        calculate(a=10, b=0, operation='divide')
