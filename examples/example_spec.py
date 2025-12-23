"""Example module specification for agent-compile."""

from src.core import Example, Module

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
        Example(
            inputs={"a": 10, "b": 5, "operation": "add"},
            outputs={"result": 15.0},
            description="Addition",
        ),
        Example(
            inputs={"a": 10, "b": 5, "operation": "subtract"},
            outputs={"result": 5.0},
            description="Subtraction",
        ),
        Example(
            inputs={"a": 10, "b": 5, "operation": "multiply"},
            outputs={"result": 50.0},
            description="Multiplication",
        ),
        Example(
            inputs={"a": 10, "b": 5, "operation": "divide"},
            outputs={"result": 2.0},
            description="Division",
        ),
    ],
)
