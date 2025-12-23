# Calculator Example

Simple single-module example demonstrating basic agent-compile usage.

## Module

- **calculator**: Performs basic arithmetic operations (add, subtract, multiply, divide)

## Run

```bash
python -m src.cli.compile examples/calculator/spec.py --output-dir examples/calculator/compiled_src
```

## Output

- `compiled_src/calculator.py` - Implementation
- `compiled_src/test_calculator.py` - Tests  
- `compiled_src/COMPILE_calculator.log` - Compilation log
