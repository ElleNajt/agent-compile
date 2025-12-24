# Machine Learning Classifier Example

This example demonstrates how modules can describe **entire systems**, not just low-level functions.

## Key Difference from Other Examples

**Calculator/Data Processor**: Focus on specific functions with precise inputs/outputs
- "Calculate two numbers with an operation"
- "Read a CSV file and return dictionaries"

**ML Classifier**: Describes complete subsystems with high-level behavior
- "A complete text classification system using TF-IDF and logistic regression"
- "End-to-end ML pipeline that combines preprocessing, training, and evaluation"

## Modules

### 1. `text_classifier`
Complete classification system with training, prediction, and model persistence.
Shows how a module can describe an entire ML system rather than just a single function.

### 2. `text_preprocessor`
Composable text preprocessing pipeline.
Demonstrates system-level behavior (configurable pipeline) rather than function-level.

### 3. `model_evaluator`
Evaluation metrics computation system.
Returns comprehensive metrics dictionary, not just a single number.

### 4. `ml_pipeline`
High-level orchestration that combines all the above.
This is the main entry point - demonstrates how modules compose into complete systems.

## Running

```bash
python -m src.cli.compile examples/ml_classifier/spec.py --output-dir examples/ml_classifier/compiled_src
```

The compiler will generate complete implementations of all four systems, each as a separate Python module.

## Philosophy

Modules don't have to map to individual functions. They can represent:
- Complete subsystems (text_classifier)
- Pipelines (text_preprocessor)
- Utilities with multiple related functions (model_evaluator)
- High-level orchestrators (ml_pipeline)

The tests reflect this - they describe system behavior, not just input/output pairs.
