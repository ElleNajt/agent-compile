# agent-compile

A system for compiling structured prompts into executable code.

## Concept

Instead of chatting back-and-forth with an AI agent, you define what you want as a structured specification (`Module`), and the system compiles it to working code.

## Key Components

### Module
A `Module` is a minimal high-level specification of what code should do:
- **name**: Identifier for the module
- **purpose**: High-level intent in natural language (be specific!)
- **dependencies**: Other modules this depends on
- **tests**: Input/output examples that double as tests

The design is intentionally minimal. The strict ambiguity checker will force you to make the purpose and tests specific enough that compilation is unambiguous.

### Two-Pass Compilation

1. **Ambiguity Check**: Strictly analyzes the specification for any unclear aspects
2. **Code Generation**: Compiles the spec to executable code (if no ambiguities)

## Usage

### CLI (Recommended)

1. Create a spec file (e.g., `my_spec.py`):

```python
from src.core import Module, Example

calculator = Module(
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
            inputs={"a": 10, "b": 5, "operation": "divide"},
            outputs={"result": 2.0},
            description="Division"
        )
    ]
)
```

2. Compile it:

```bash
python -m src.cli.compile my_spec.py
# Compiled code is saved to compiled_src/calculator.py
```

The CLI will:
- Load all `Module` objects from your file
- Check for ambiguities
- Generate code and save to `compiled_src/` (by default)

Options:
- `--output-dir DIR`: Custom output directory
- `--force`: Skip ambiguity checking

### Programmatic API

```python
from src.core import Module, Example, LLMCompiler

calculator = Module(...)
compiler = LLMCompiler()
result = compiler.compile(calculator)

if result.status == "ambiguous":
    for amb in result.ambiguities:
        print(amb)
elif result.status == "compiled":
    print(result.code)
```

### Workflow

1. Start with minimal spec (name + purpose)
2. Run compiler → identifies ambiguities
3. Refine purpose and add tests until unambiguous
4. Get working code in `compiled_src/`

## Design Principles

1. **Strict ambiguity checking**: Any aspect that could be interpreted multiple ways is flagged
2. **Fail fast**: Code fails loudly rather than using graceful fallbacks
3. **Composable**: Modules can depend on other modules
4. **Language-agnostic**: Target language is configurable (currently Python)

## Future Work

### Module Freezing (Optional Feature)
- Freeze modules at specific git hashes
- A frozen module specifies:
  - Git commit hash when it was finalized
  - Files that implement it
- Compiler behavior:
  - If compilation would modify frozen files → throw error
  - Prevents accidental modification of "done" code
  - Ties frozen state to version control instead of internal checksums

### Other Future Features
- Caching: Avoid recompiling unchanged specs
- Testing integration: Auto-generate tests from examples
- Multi-language support: Compile to languages beyond Python
