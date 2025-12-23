# Agent-Compile: Current State Summary

## What We Built

A system for compiling structured module specifications into executable code using LLM-powered agents.

## Core Concept

Instead of chatting with an AI to write code, you:
1. Write a `Module` spec (name, purpose, tests, dependencies)
2. Run the compiler
3. Get working, tested code

## Architecture

### Module Definition (src/core/module.py)
```python
@dataclass
class Module:
    name: str                      # Module identifier
    purpose: str                   # What it does (natural language)
    dependencies: list[Module]     # Other modules it needs
    tests: list[Example]           # Input/output test cases
```

Intentionally minimal - ambiguity checker forces specificity.

### Two-Pass Compilation

**Pass 1: Ambiguity Check** (src/core/ambiguity.py)
- LLM analyzes spec for unclear/ambiguous parts
- Strict but not pedantic (focuses on correctness, not style)
- Flags missing critical info, contradictions, genuinely ambiguous behavior
- Ignores implementation details like function names, case sensitivity

**Pass 2: Code Generation** (src/core/compiler.py)
- Claude executes full agentic workflow in `compiled_src/`:
  1. Write implementation
  2. Write pytest tests
  3. Run tests
  4. Fix failures
  5. Iterate until all tests pass
- Saves compilation log with all decisions and test results

### Agent Interface (src/core/agent.py)

Abstract interface for LLM interactions:
```python
class Agent(ABC):
    def query(self, prompt: str, cwd: Path | None = None) -> str:
        pass
```

**ClaudeAgent** (src/core/claude_agent.py): Uses `claude` CLI subprocess

### CLI (src/cli/compile.py)

```bash
python -m src.cli.compile examples/calculator/spec.py \
    --output-dir examples/calculator/compiled_src
```

Outputs:
- `{module_name}.py` - Implementation
- `test_{module_name}.py` - Tests
- `COMPILE_{module_name}.log` - Full compilation log (prompt, response, decisions, test results)

## Examples

### 1. Calculator (Simple)
Single module, no dependencies.
- Demonstrates basic usage
- Shows ambiguity checking in action
- Located in `examples/calculator/`

### 2. Data Processor (Complex)
Three-module pipeline with dependencies:
1. **csv_reader** - Parse CSV files
2. **data_validator** - Validate records (depends on csv_reader)
3. **data_aggregator** - Compute statistics (depends on both)

Demonstrates:
- Module dependencies
- Dependency ordering
- Multi-module compilation
- Located in `examples/data_processor/`

## Key Design Decisions

1. **Minimal Module spec** - Only essential fields, let ambiguity checker enforce specificity
2. **Strict but not pedantic** - Flag real ambiguities, not style choices
3. **Fail fast** - Code should crash on errors, no graceful fallbacks unless specified
4. **Full logs** - Complete transparency into compilation process
5. **Agent abstraction** - Easy to swap LLM backends
6. **CLI over library** - Batch compilation workflow

## Current Limitations / Future Work

Tracked in bead issue tracker (`.beads/`):
- **agent-compile-1d6**: Module freezing at git hashes (optional feature)

## Authentication

Uses `claude` CLI which authenticates via:
- `ANTHROPIC_API_KEY` environment variable, OR
- Claude.ai subscription (if logged in)

## File Structure

```
agent-compile/
├── src/
│   ├── core/
│   │   ├── module.py         # Module & Example dataclasses
│   │   ├── agent.py          # Abstract Agent interface
│   │   ├── claude_agent.py   # Claude CLI implementation
│   │   ├── ambiguity.py      # Ambiguity checker
│   │   └── compiler.py       # Two-pass compiler
│   └── cli/
│       └── compile.py        # CLI interface
├── examples/
│   ├── calculator/           # Simple example
│   └── data_processor/       # Complex example
├── README.md                 # User documentation
└── SUMMARY.md               # This file
```

## Commits

1. `2ff00c3` - Initial commit with core functionality
2. `0e37c9d` - Reorganized examples, added complex multi-module example

---

**Status**: Working prototype
**Next Steps**: Test complex example, refine ambiguity checking, add more examples
