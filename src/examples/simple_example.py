#!/usr/bin/env python3
"""Simple example demonstrating the agent-compile workflow."""

from src.core.module import Module, Example
from src.core.compiler import LLMCompiler


def main():
    # Define a simple module with ambiguities
    calculator = Module(
        name="calculator",
        purpose="Perform basic arithmetic operations",
        tests=[]
    )
    
    print("=" * 60)
    print("Example 1: Ambiguous specification")
    print("=" * 60)
    print(f"Module: {calculator.name}")
    print(f"Purpose: {calculator.purpose}")
    print(f"Tests: {len(calculator.tests)}")
    
    compiler = LLMCompiler()
    result = compiler.compile(calculator)
    
    if result.status == "ambiguous":
        print("\n❌ Compilation failed due to ambiguities:\n")
        for amb in result.ambiguities:
            print(amb)
            print()
    
    # Now let's fix the ambiguities with a better spec
    print("\n" + "=" * 60)
    print("Example 2: Refined specification")
    print("=" * 60)
    
    calculator_refined = Module(
        name="calculator",
        purpose="""A calculator that performs basic arithmetic operations.
        
Takes two numbers (a, b) and an operation string.
Operations: 'add', 'subtract', 'multiply', 'divide'
Returns the result as a float.
Raises ValueError for invalid operations.
Raises ZeroDivisionError when dividing by zero.""",
        tests=[
            Example(
                inputs={"a": 10, "b": 5, "operation": "add"},
                outputs={"result": 15.0},
                description="Addition"
            ),
            Example(
                inputs={"a": 10, "b": 5, "operation": "subtract"},
                outputs={"result": 5.0},
                description="Subtraction"
            ),
            Example(
                inputs={"a": 10, "b": 5, "operation": "multiply"},
                outputs={"result": 50.0},
                description="Multiplication"
            ),
            Example(
                inputs={"a": 10, "b": 5, "operation": "divide"},
                outputs={"result": 2.0},
                description="Division"
            ),
        ]
    )
    
    print(f"Module: {calculator_refined.name}")
    print(f"Purpose: {calculator_refined.purpose[:50]}...")
    print(f"Tests: {len(calculator_refined.tests)}")
    
    result = compiler.compile(calculator_refined)
    
    if result.status == "compiled":
        print("\n✅ Compilation successful!\n")
        print("Generated code:")
        print("-" * 60)
        print(result.code)
        print("-" * 60)
    
    elif result.status == "ambiguous":
        print("\n❌ Still has ambiguities:\n")
        for amb in result.ambiguities:
            print(amb)
            print()
    
    else:
        print(f"\n❌ Compilation error: {result.error}")


if __name__ == "__main__":
    main()
