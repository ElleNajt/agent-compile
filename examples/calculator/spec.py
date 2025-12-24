"""Example module specification for agent-compile."""

from src.core import Module

# Simple calculator module
calculator = Module(
    name="calculator",
    purpose="""A calculator that performs basic arithmetic operations.
    
Takes two numbers (a, b) and an operation string.
Operations: 'add', 'subtract', 'multiply', 'divide'
Returns a dictionary with key 'result' containing the float result.
Raises ValueError for invalid operations.
Raises ZeroDivisionError when dividing by zero.""",
    tests=[
        "Addition: calculate(a=10, b=5, operation='add') should return {'result': 15.0}",
        "Subtraction: calculate(a=10, b=5, operation='subtract') should return {'result': 5.0}",
        "Multiplication: calculate(a=10, b=5, operation='multiply') should return {'result': 50.0}",
        "Division: calculate(a=10, b=5, operation='divide') should return {'result': 2.0}",
        "Invalid operation: calculate(a=10, b=5, operation='invalid') should raise ValueError",
        "Division by zero: calculate(a=10, b=0, operation='divide') should raise ZeroDivisionError",
    ],
)
