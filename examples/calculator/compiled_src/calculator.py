"""A calculator that performs basic arithmetic operations."""


def calculate(a: float, b: float, operation: str) -> dict[str, float]:
    """
    Perform basic arithmetic operations on two numbers.

    Args:
        a: First number
        b: Second number
        operation: Operation to perform ('add', 'subtract', 'multiply', 'divide')

    Returns:
        Dictionary with key 'result' containing the float result

    Raises:
        ValueError: If operation is not valid
        ZeroDivisionError: If dividing by zero
    """
    if operation == 'add':
        result = a + b
    elif operation == 'subtract':
        result = a - b
    elif operation == 'multiply':
        result = a * b
    elif operation == 'divide':
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        result = a / b
    else:
        raise ValueError(f"Invalid operation: {operation}")

    return {'result': float(result)}
