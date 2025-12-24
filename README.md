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
- **tests**: Natural language descriptions of expected behavior

The design is intentionally minimal. The strict ambiguity checker will force you to make the purpose and tests specific enough that compilation is unambiguous.

**Note**: Tests are flexible natural language - not rigid input/output pairs. Describe behavior however makes sense for your module.

### Two-Pass Compilation

1. **Ambiguity Check**: Strictly analyzes the specification for any unclear aspects
2. **Code Generation**: Compiles the spec to executable code (if no ambiguities)

## Usage

### CLI (Recommended)

```bash
python -m src.cli.compile examples/calculator/spec.py --output-dir examples/calculator/compiled_src
```

The CLI will:
- Load all `Module` objects from your spec file
- Check for ambiguities (strict but not pedantic)
- Generate code, tests, and logs in the output directory
- Claude iteratively writes code, runs tests, and fixes failures

Options:
- `--output-dir DIR`: Custom output directory (default: `compiled_src/` next to spec file)
- `--force`: Skip ambiguity checking

## Examples

See `examples/` directory:

- **calculator/** - Simple single-module example (basic arithmetic)
- **data_processor/** - Multi-module pipeline with dependencies (CSV → validation → aggregation)
- **ml_classifier/** - System-level modules (complete ML pipeline, not just functions)

Each example includes:
- `spec.py` - Module specifications
- `README.md` - Example documentation
- `compiled_src/` - Generated code (after compilation)

**Progression**: calculator (single function) → data_processor (function pipeline) → ml_classifier (complete systems)

### Programmatic API

```python
from src.core import Module, LLMCompiler

calculator = Module(
    name="calculator",
    purpose="Performs basic arithmetic operations",
    tests=[
        "Addition: calculate(10, 5, 'add') returns 15",
        "Division by zero raises ZeroDivisionError"
    ]
)

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
