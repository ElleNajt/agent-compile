#!/usr/bin/env python3
"""Module specifications for agent-compile system."""

from src.core import Module

# Core abstraction for LLM interaction
agent = Module(
    name="agent",
    purpose="""Abstract interface for LLM agents that can process prompts.

    Defines the contract for any LLM backend - takes a prompt string and optional working directory,
    returns a text response. This abstraction allows swapping different LLM implementations.
    """,
    tests=[
        "Query method accepts a prompt string and returns a response string",
        "Query method accepts an optional cwd Path parameter",
        "Abstract class cannot be instantiated directly",
    ]
)

# Concrete implementation using Claude CLI
claude_agent = Module(
    name="claude_agent",
    purpose="""Concrete Agent implementation that uses the `claude` CLI subprocess.

    Executes prompts by invoking the claude command-line tool. Supports custom commands
    (e.g., 'claudebox -p' for containerized execution). Runs Claude in the specified
    working directory, allowing it to write files and execute tasks directly.
    """,
    dependencies=[agent],
    tests=[
        "Can be initialized with default 'claude' command",
        "Can be initialized with custom command like 'claudebox -p'",
        "Query method runs command via subprocess with prompt as stdin",
        "Query method passes cwd to subprocess if provided",
        "Query method returns stdout from the subprocess",
        "Query method raises exception if subprocess fails (check=True)",
        "Command with arguments (e.g., 'claudebox -p') is parsed correctly using shlex",
    ]
)

# Core data structure representing a compilable module
module = Module(
    name="module",
    purpose="""Data structure representing a module specification that can be compiled to code.

    Contains: name (identifier), purpose (natural language description), dependencies (other Modules),
    and tests (natural language test descriptions). Includes metadata for code freezing.
    Validates that name and purpose are non-empty on initialization.
    """,
    tests=[
        "Module requires non-empty name",
        "Module requires non-empty purpose",
        "Module accepts optional dependencies list (defaults to empty)",
        "Module accepts optional tests list (defaults to empty)",
        "Module has frozen, frozen_code, and frozen_hash fields (default False/None)",
        "Module raises ValueError if name is empty",
        "Module raises ValueError if purpose is empty",
        "Dependencies are stored as list of Module objects",
        "Tests are stored as list of strings",
    ]
)

# Ambiguity detection
ambiguity = Module(
    name="ambiguity",
    purpose="""Represents and checks for ambiguities in module specifications.

    Ambiguity class stores: module_name, location, issue description, severity (error/warning),
    and suggestions. AmbiguityChecker uses an LLM agent to analyze Module specs and identify
    unclear parts that would prevent correct implementation. Returns list of Ambiguity objects.
    """,
    dependencies=[agent, claude_agent, module],
    tests=[
        "Ambiguity has module_name, location, issue, severity, and suggestions fields",
        "Ambiguity severity defaults to 'error'",
        "Ambiguity suggestions defaults to empty list",
        "Ambiguity __str__ includes emoji prefix (⚠️ for warning, ❌ for error)",
        "Ambiguity __str__ formats as '{emoji} {module}.{location}: {issue}'",
        "Ambiguity __str__ includes suggestions if present",
        "AmbiguityChecker can be initialized with custom agent or defaults to ClaudeAgent",
        "AmbiguityChecker.check() takes a Module and returns list of Ambiguity objects",
        "AmbiguityChecker builds prompt with module name, purpose, dependencies, and tests",
        "AmbiguityChecker prompt instructs to only flag critical ambiguities, not style issues",
        "AmbiguityChecker parses 'NO_AMBIGUITIES' response as empty list",
        "AmbiguityChecker parses 'AMBIGUITY:' blocks with Location/Issue/Severity/Suggestions",
        "AmbiguityChecker defaults severity to 'error' if invalid value provided",
        "AmbiguityChecker extracts suggestions from lines starting with '-'",
    ]
)

# Caching layer for ambiguity checks
cache = Module(
    name="cache",
    purpose="""Cache ambiguity check results to avoid redundant LLM queries.

    Stores results in .ambiguity_cache.json keyed by SHA256 hash of module spec.
    Hash includes: name, purpose, dependency names (only), and tests. Supports get/set
    operations with automatic JSON serialization of Ambiguity objects.
    """,
    dependencies=[module],
    tests=[
        "AmbiguityCache initialized with cache directory path",
        "Cache directory is created if it doesn't exist",
        "Cache file is .ambiguity_cache.json in cache directory",
        "Cache is loaded from disk on initialization if file exists",
        "Empty cache is created if file doesn't exist",
        "Module hash is computed from name, purpose, dependency names, and tests only",
        "Module hash uses SHA256 of stable JSON representation (sorted keys)",
        "get() returns None if module not in cache",
        "get() returns list of ambiguities if module in cache",
        "set() serializes Ambiguity objects to dict format before storing",
        "set() saves cache to disk after updating",
        "Cache persists across AmbiguityCache instances",
        "Changing module purpose invalidates cache",
        "Changing module tests invalidates cache",
    ]
)

# Main compilation logic
compiler = Module(
    name="compiler",
    purpose="""Compiles Module specifications to executable code using LLM agent.

    Two-pass process: (1) Ambiguity checking unless forced, (2) Code generation.
    Compiles dependencies recursively first. Instructs Claude to write implementation
    and pytest tests to disk, run tests until they pass. Returns CompilationResult
    with status (ambiguous/compiled/error), code, ambiguities, or error message.
    Saves compilation logs to COMPILE_{module_name}.log in working directory.
    """,
    dependencies=[agent, claude_agent, module, ambiguity],
    tests=[
        "LLMCompiler can be initialized with custom agent or defaults to ClaudeAgent",
        "LLMCompiler accepts optional cwd (working directory) parameter",
        "compile() takes Module, target_language (default 'python'), and force flag",
        "compile() returns CompilationResult with status/code/ambiguities/error/metadata",
        "CompilationResult has status field: 'ambiguous', 'compiled', or 'error'",
        "CompilationResult has optional code, ambiguities, error, and metadata fields",
        "If not forced, compile() runs ambiguity check first",
        "If ambiguities found, returns status='ambiguous' with list of Ambiguity objects",
        "compile() recursively compiles dependencies before main module",
        "If dependency compilation fails, raises CompilationError",
        "Code generation prompt includes module name, purpose, tests, and dependency code",
        "Code generation prompt instructs to write to {module_name}.py",
        "Code generation prompt instructs to write pytest tests to test_{module_name}.py",
        "Code generation prompt instructs to run tests until they pass",
        "Code generation prompt emphasizes FAIL FAST - no try-except unless specified",
        "Successful compilation saves log to COMPILE_{module_name}.log",
        "Failed compilation saves log with error details",
        "Log includes module spec, prompt, and Claude's response or error",
        "Agent.query() is called with cwd so Claude writes files to correct location",
        "Compilation with force=True skips ambiguity checking",
        "CompilationError is raised for dependency failures",
    ]
)

# Decompilation from code to specs
decompiler = Module(
    name="decompiler",
    purpose="""Generates Module specifications from existing code.

    Takes a directory of code files, gathers all .py files (excluding __pycache__ and tests),
    sends them to LLM with prompt to infer Module specs. Returns Python code defining
    Module objects with inferred name, purpose, dependencies, and natural language tests.
    """,
    dependencies=[agent, claude_agent],
    tests=[
        "Decompiler can be initialized with custom agent or defaults to ClaudeAgent",
        "decompile() takes a code directory Path and returns spec code string",
        "decompile() gathers all .py files from directory recursively",
        "decompile() excludes __pycache__ directories",
        "decompile() excludes test files (starting with test_)",
        "decompile() raises ValueError if no code files found",
        "Prompt includes all code files with relative paths and contents",
        "Prompt instructs to generate spec.py with Module definitions",
        "Prompt instructs to infer purpose, dependencies, and tests from code",
        "Prompt emphasizes describing WHAT code does, not HOW",
        "Output format is Python code with 'from src.core import Module' and Module() calls",
    ]
)

# CLI for compilation
compile_cli = Module(
    name="compile_cli",
    purpose="""Command-line interface for compiling Module specifications.

    Loads Module objects from Python file, performs two-phase compilation: (1) check all
    modules for ambiguities (with caching), abort if any found, (2) compile all modules.
    Accepts --output-dir, --force, and --claude-command arguments. Returns exit code 0/1.
    """,
    dependencies=[module, compiler, cache, claude_agent],
    tests=[
        "CLI accepts required 'file' argument (Path to spec file)",
        "CLI accepts optional --output-dir argument",
        "CLI defaults output-dir to 'compiled_src/' in same directory as input file",
        "CLI accepts optional --force flag to skip ambiguity checking",
        "CLI accepts optional --claude-command to specify Claude command",
        "CLI defaults claude-command to 'claude'",
        "CLI validates that input file exists",
        "CLI returns exit code 1 if file doesn't exist",
        "load_modules_from_file() imports Python file and extracts Module instances",
        "compile_file() prints status messages during compilation",
        "Phase 1: Checks all modules for ambiguities before compiling any",
        "Phase 1: Uses AmbiguityCache to avoid redundant checks",
        "Phase 1: Prints 'cached' indicator for cached results",
        "Phase 1: If any ambiguities found, prints all and returns 1",
        "Phase 1: Skipped if --force flag is used",
        "Phase 2: Compiles all modules with force=True (skip redundant ambiguity check)",
        "Phase 2: Claude writes files during compilation to output_dir",
        "CLI verifies output files exist after compilation",
        "CLI returns 0 on success, 1 on failure",
        "CLI creates output directory if it doesn't exist",
    ]
)

# CLI for decompilation
decompile_cli = Module(
    name="decompile_cli",
    purpose="""Command-line interface for decompiling code to Module specifications.

    Takes a code directory, decompiles it to a spec.py file. Accepts --output and
    --claude-command arguments. Validates input directory exists. Returns exit code 0/1.
    """,
    dependencies=[decompiler, claude_agent],
    tests=[
        "CLI accepts required 'code_dir' argument (Path to code directory)",
        "CLI accepts optional --output argument for spec file path",
        "CLI defaults output to 'spec.py' in code directory",
        "CLI accepts optional --claude-command to specify Claude command",
        "CLI defaults claude-command to 'claude'",
        "CLI validates that code_dir exists",
        "CLI returns exit code 1 if code_dir doesn't exist",
        "CLI returns exit code 1 if code_dir is not a directory",
        "decompile_directory() creates Decompiler with specified agent",
        "decompile_directory() calls decompiler.decompile() with code_dir",
        "decompile_directory() writes result to output file",
        "decompile_directory() prints status messages",
        "decompile_directory() returns 0 on success, 1 on failure",
        "CLI catches exceptions and prints error messages",
    ]
)
