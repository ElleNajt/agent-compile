# agent-compile

A system for compiling structured prompts into executable code.

## Philosophy

**The problem with "vibe coding"**: When you collaborate with AI agents to generate code, it's easy to produce hundreds of lines quickly. But the *intent* gets lost in implementation details. Someone (including future-you) looking at the code has to reverse-engineer what you were trying to build. Collaboration becomes difficult: reviewing AI-generated code means reading all of it to understand the design decisions.

**The proposed solution**: Treat the intention stored as a specification as the primary artifact, not the code. The spec captures *what* you're building and how the parts fit together. The code is just compiled output that can be regenerated.

You still collaborate with AI to build things, but you collaborate on the *spec*. The ambiguity checker acts as a forcing function—it won't let you proceed until your intent is clear. Once the spec is unambiguous, compilation is deterministic. The spec becomes your communication layer for code review, collaboration, and maintenance.

## Concept

Instead of chatting back-and-forth with an AI agent to generate code directly, you define what you want as a structured specification, and the agent compiles it to working code. You can work with an agent to build the spec. You can also decompile existing projects into specs that you can edit and improve.

For a meta example which also serves as documentation, see [`src/decompiled_spec.py`](src/decompiled_spec.py) which is a spec built by "decompiling" this codebase. 

## Key Components

### Module
A `Module` is a python dataclass that is a minimal high-level specification of what code should do:
- **name**: Identifier for the module
- **purpose**: High-level intent in natural language (be specific!)
- **dependencies**: Other modules this depends on
- **tests**: Natural language descriptions of expected behavior
- **language**: Target language (default: "python", also supports "rust", "javascript", etc.)

The "compilers" ambiguity checker will force you to make the purpose and tests specific enough that compilation is unambiguous.

### Three-Pass Compilation

1. **Ambiguity Check**: Strictly analyzes the specification for any unclear aspects
2. **Dependency Resolution**: Recursively compiles all dependencies first (topological order)
   - Dependencies must compile successfully before dependent modules
   - Each dependency is fully compiled (files written to disk)
3. **Code Generation**: Compiles the spec to executable code (if no ambiguities)
   - Claude receives dependency code in the prompt (to know what's available for import)
   - Generates implementation + pytest tests (writes files directly to disk)
   - Runs tests and iteratively fixes failures until all tests pass
   - Only succeeds if tests pass ✓

## Usage

**Recommended**: Run Claude in a container for isolation and security:

```bash
# Start Claude in container
claudebox

# Inside the container, run agent-compile:
agent-compile spec.py --output-dir compiled_src/
```

This approach provides:
- Isolated environment with credential separation
- Latest version from GitHub (via uvx)
- No nested container complexity

### Compile: Spec → Code

```bash
agent-compile examples/calculator/spec.py --output-dir examples/calculator/compiled_src
```

The CLI will:
- Load all `Module` objects from your spec file
- Check for ambiguities (strict but not pedantic)
- Generate code, tests, and logs in the output directory
- Claude iteratively writes code, runs tests, and fixes failures

Options:
- `--output-dir DIR`: Custom output directory (default: `compiled_src/` next to spec file)
- `--force`: Skip ambiguity checking

### Decompile: Code → Spec

```bash
agent-decompile examples/calculator/compiled_src --output spec.py
```

The decompile CLI will:
- Analyze existing code files in the directory
- Use Claude to infer purpose, behavior, and test cases
- Generate a `spec.py` file with `Module` definitions

Options:
- `--output FILE`: Output spec file (default: `spec.py` in code directory)

**Use case**: Extract specifications from existing codebases to refine or re-compile them

## Using with Claude Code

If you use [Claude Code](https://claude.com/claude-code), you can add agent-compile workflow instructions to your project's `CLAUDE.md` file to teach Claude about the spec-first workflow.

**Quick setup**: Copy or symlink [`CLAUDE_example.md`](CLAUDE_example.md) to your project as `CLAUDE.md`.

The example file covers:
- When to use agent-compile
- Workflow steps (create spec → compile → review → iterate)
- Key principles (never edit compiled code, always work through specs)
- Commands (`agent-compile` and `agent-decompile`)

This teaches Claude to collaborate on specs rather than directly writing implementation code.

## Examples

See [`examples/`](examples/) directory:

- **[calculator/](examples/calculator/)** - Simple single-module example (basic arithmetic)
- **[data_processor/](examples/data_processor/)** - Multi-module pipeline with dependencies (CSV → validation → aggregation)
- **[ml_classifier/](examples/ml_classifier/)** - System-level modules (complete ML pipeline, not just functions)

Each example includes:
- `spec.py` - Module specifications
- `README.md` - Example documentation
- `compiled_src/` - Generated code (after compilation)

**Metaexamples**:
- [`src/decompiled_spec.py`](src/decompiled_spec.py) - Auto-generated by running the decompiler on `src/` - demonstrates the decompiler's output quality

### Workflow

**Forward (Spec → Code):**
1. Write a minimal spec (name + purpose) in a `.py` file
2. Run compiler → identifies ambiguities
3. Work with Claude Code to refine the spec - add tests, clarify purpose
4. Re-run compiler → repeat until no ambiguities
5. Get working, tested code in `compiled_src/`

**Reverse (Code → Spec):**
1. Point decompiler at existing code directory
2. Claude analyzes the code and generates spec
3. Refine the generated spec as needed
4. Re-compile to update implementation

The key insight: You collaborate with Claude Code on the **spec**, then the compiler generates **code** from that spec. The decompiler lets you extract specs from existing code.

## Design Principles

1. **Strict ambiguity checking**: Any aspect that could be interpreted multiple ways is flagged
2. **Fail fast**: Code fails loudly rather than using graceful fallbacks
3. **Composable**: Modules can depend on other modules
4. **Language-agnostic**: Target language is configurable (currently Python)

## Future Work

### Module Freezing 
- Freeze modules at specific git hashes
- A frozen module specifies:
  - Git commit hash when it was finalized
  - Files that implement it
- Compiler behavior:
  - If compilation would modify frozen files → throw error
  - Prevents accidental modification of "done" code
  - Ties frozen state to version control instead of internal checksums

### Deterministic Compilation
- Make compilation deterministic so only specs need to be committed
- Currently compilation can vary between runs, so both spec and code should be committed

### Other Future Features
- Caching: Avoid recompiling unchanged specs (basic cache exists, needs improvement)
- Better multi-language support: Currently Python/Rust/JavaScript templates exist, expand further
