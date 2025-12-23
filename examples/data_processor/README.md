# Data Processor Example

Complex multi-module example demonstrating module dependencies.

## Modules

1. **csv_reader**: Reads CSV files and parses to dictionaries
2. **data_validator**: Validates records against schema rules (depends on csv_reader)
3. **data_aggregator**: Computes aggregations on validated data (depends on csv_reader, data_validator)

## Features Demonstrated

- Module dependencies
- Multi-module compilation
- Cross-module data flow
- Dependency ordering

## Run

```bash
python -m src.cli.compile examples/data_processor/spec.py --output-dir examples/data_processor/compiled_src
```

## Output

The compiler will:
1. Compile csv_reader first (no dependencies)
2. Compile data_validator (uses csv_reader types)
3. Compile data_aggregator (uses both previous modules)

Each module gets:
- Implementation file
- Test file
- Compilation log
