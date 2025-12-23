"""Example: Data processing pipeline with multiple dependent modules."""

from src.core import Module, Example

# Module 1: CSV reader
csv_reader = Module(
    name="csv_reader",
    purpose="""Read CSV file and return data as list of dictionaries.
    
Takes a file path and returns parsed CSV data.
Each row becomes a dictionary with column names as keys.
Handles missing values by setting them to None.
Raises FileNotFoundError if file doesn't exist.
Raises ValueError if CSV is malformed.""",
    tests=[
        Example(
            inputs={"filepath": "test_data.csv"},
            outputs={"data": [
                {"name": "Alice", "age": 30, "city": "NYC"},
                {"name": "Bob", "age": 25, "city": "SF"}
            ]},
            description="Read valid CSV"
        )
    ]
)

# Module 2: Data validator (depends on csv_reader structure)
data_validator = Module(
    name="data_validator",
    purpose="""Validate data records according to schema rules.
    
Takes a list of dictionaries and validation rules.
Returns tuple of (valid_records, invalid_records).
Validation rules specify required fields and type constraints.
Example rule: {"name": str, "age": int}""",
    dependencies=[csv_reader],
    tests=[
        Example(
            inputs={
                "data": [
                    {"name": "Alice", "age": 30},
                    {"name": "Bob", "age": "invalid"},
                    {"name": None, "age": 25}
                ],
                "rules": {"name": "str", "age": "int"}
            },
            outputs={
                "valid": [{"name": "Alice", "age": 30}],
                "invalid": [
                    {"name": "Bob", "age": "invalid"},
                    {"name": None, "age": 25}
                ]
            },
            description="Validate mixed data"
        )
    ]
)

# Module 3: Data aggregator (depends on validator)
data_aggregator = Module(
    name="data_aggregator",
    purpose="""Aggregate validated data by computing statistics.
    
Takes list of valid records and computes aggregations.
Supports: count, sum, average, min, max for numeric fields.
Groups by specified categorical field if provided.
Returns dictionary of aggregation results.""",
    dependencies=[csv_reader, data_validator],
    tests=[
        Example(
            inputs={
                "data": [
                    {"category": "A", "value": 10},
                    {"category": "A", "value": 20},
                    {"category": "B", "value": 15}
                ],
                "group_by": "category",
                "aggregations": {"value": ["sum", "average"]}
            },
            outputs={
                "results": {
                    "A": {"value_sum": 30, "value_average": 15.0},
                    "B": {"value_sum": 15, "value_average": 15.0}
                }
            },
            description="Group and aggregate"
        )
    ]
)
