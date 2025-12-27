"""Example: Data processing pipeline with multiple dependent modules."""

from agent_compile.core import Module

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
        "Read valid CSV: read_csv('test_data.csv') should return list of dicts with keys matching CSV headers",
        "Missing file: read_csv('nonexistent.csv') should raise FileNotFoundError",
        "Malformed CSV: read_csv('bad.csv') with inconsistent columns should raise ValueError",
        "Empty values: CSV with empty cells should have None for those fields in the output dicts",
    ],
)

# Module 2: Data validator (depends on csv_reader structure)
data_validator = Module(
    name="data_validator",
    purpose="""Validate data records according to schema rules.
    
Takes a list of dictionaries and validation rules dictionary.
Validation rules use Python type objects: {"name": str, "age": int}
Returns tuple of (valid_records, invalid_records).
A record is valid if all required fields exist and match their type constraints.""",
    dependencies=[csv_reader],
    tests=[
        "Valid records: validate([{'name': 'Alice', 'age': 30}], {'name': str, 'age': int}) should return ([{'name': 'Alice', 'age': 30}], [])",
        "Invalid types: validate([{'name': 'Bob', 'age': 'invalid'}], {'name': str, 'age': int}) should put Bob in invalid list",
        "Missing required fields: validate([{'name': None, 'age': 25}], {'name': str, 'age': int}) should put this record in invalid list since name is None",
        "Mixed data: validate with mix of valid/invalid should correctly separate them into two lists",
    ],
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
        "Group and aggregate: aggregate([{'category': 'A', 'value': 10}, {'category': 'A', 'value': 20}, {'category': 'B', 'value': 15}], group_by='category', aggregations={'value': ['sum', 'average']}) should return {'A': {'value_sum': 30, 'value_average': 15.0}, 'B': {'value_sum': 15, 'value_average': 15.0}}",
        "No grouping: aggregate without group_by should aggregate all records together",
        "Multiple aggregations: should support count, sum, average, min, max on numeric fields",
        "Empty data: aggregate([]) should return empty results dict",
    ],
)
