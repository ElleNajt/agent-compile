"""Data Aggregator Module

Aggregate validated data by computing statistics.
"""

from typing import List, Dict, Any, Optional


def aggregate(
    records: List[Dict[str, Any]],
    aggregations: Dict[str, List[str]],
    group_by: Optional[str] = None
) -> Dict[str, Dict[str, Any]]:
    """Aggregate validated data by computing statistics.

    Takes list of valid records and computes aggregations.
    Supports: count, sum, average, min, max for numeric fields.
    Groups by specified categorical field if provided.

    Args:
        records: List of dictionaries to aggregate
        aggregations: Dictionary mapping field names to list of aggregation functions
                     Example: {"value": ["sum", "average"]}
        group_by: Optional field name to group records by

    Returns:
        Dictionary of aggregation results. If group_by is specified, outer keys are
        group values. Inner keys are "{field}_{aggregation}" (e.g., "value_sum").
        If no group_by, returns single dict with key "all".
    """
    # Handle empty records
    if not records:
        return {}

    # Group records
    if group_by is None:
        # All records in one group
        groups = {"all": records}
    else:
        # Group by specified field
        groups = {}
        for record in records:
            group_key = record[group_by]
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(record)

    # Compute aggregations for each group
    results = {}
    for group_key, group_records in groups.items():
        group_results = {}

        for field_name, agg_functions in aggregations.items():
            # Extract numeric values for this field
            values = [record[field_name] for record in group_records]

            for agg_func in agg_functions:
                result_key = f"{field_name}_{agg_func}"

                if agg_func == "count":
                    group_results[result_key] = len(values)
                elif agg_func == "sum":
                    group_results[result_key] = sum(values)
                elif agg_func == "average":
                    group_results[result_key] = sum(values) / len(values)
                elif agg_func == "min":
                    group_results[result_key] = min(values)
                elif agg_func == "max":
                    group_results[result_key] = max(values)

        results[group_key] = group_results

    return results
