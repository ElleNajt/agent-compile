from agent_compile.core import Module

# Core data structure
module_spec = Module(
    name="module",
    purpose="""Defines the core Module dataclass that represents a compilable specification.

    A Module contains: name (string identifier), purpose (natural language description of intent),
    dependencies (list of other Module objects it requires), and tests (list of natural language
    test descriptions). Also includes frozen/frozen_code/frozen_hash fields for future freezing
    functionality (currently unused).

    Validates on initialization that name and purpose are non-empty. Raises ValueError if validation fails.
    """,
    dependencies=[],
    tests=[
        "Create a Module with name='foo', purpose='test purpose' - should succeed",
        "Create a Module with empty name - should raise ValueError with message 'Module must have a name'",
        "Create a Module with empty purpose - should raise ValueError with message 'Module must have a purpose'",
        "Create a Module with dependencies=[other_module] - should store the dependency",
        "Create a Module with tests=['test 1', 'test 2'] - should store the tests",
        "Create a Module with frozen=True, frozen_code='code', frozen_hash='abc123' - should store frozen metadata",
        "Module should be a dataclass with default empty lists for dependencies and tests",
        "Module frozen field should default to False, frozen_code and frozen_hash to None",
    ]
)

# Agent interface
agent_spec = Module(
    name="agent",
    purpose="""Defines the abstract Agent interface for LLM interactions.

    This is an ABC (Abstract Base Class) with a single abstract method: query(prompt, cwd=None).
    The query method takes a prompt string and optional working directory Path, and returns a
    string response. This interface allows different LLM backends to be plugged in.

    No concrete implementation - just defines the contract that all agent implementations must follow.
    """,
    dependencies=[],
    tests=[
        "Agent should be an ABC (abstract base class)",
        "Agent should have abstract method query(prompt: str, cwd: Path | None = None) -> str",
        "Attempting to instantiate Agent directly should raise TypeError (cannot instantiate abstract class)",
        "A concrete subclass implementing query() should be instantiable",
        "query() method signature should accept prompt as required string and cwd as optional Path",
    ]
)

# Claude CLI agent implementation
claude_agent_spec = Module(
    name="claude_agent",
    purpose="""Implements the Agent interface using the 'claude' CLI tool via subprocess.

    Takes a command string (default: 'claude', but can be 'claudebox -p' or similar) and
    executes prompts by passing them via stdin to the CLI subprocess. The query() method
    runs the command in the specified cwd directory, captures stdout/stderr, and returns
    the stdout output stripped of whitespace.

    Uses shlex.split() to parse the command string into a list (handling arguments).
    Raises subprocess.CalledProcessError if the CLI command fails (check=True).
    """,
    dependencies=[agent_spec],
    tests=[
        "Create ClaudeAgent() with default command - should use 'claude'",
        "Create ClaudeAgent(command='claudebox -p') - should store the command",
        "ClaudeAgent should be a subclass of Agent",
        "query('test prompt') should run 'claude' with prompt via stdin and return stdout stripped",
        "query('prompt', cwd=Path('/tmp')) should run command with cwd=/tmp",
        "query() with multi-argument command like 'claudebox -p' should correctly parse using shlex.split()",
        "query() should capture_output=True, text=True, and check=True for subprocess.run()",
        "query() should raise subprocess.CalledProcessError if CLI command fails",
        "query() should return only stdout (not stderr) stripped of whitespace",
    ]
)

# Ambiguity detection
ambiguity_spec = Module(
    name="ambiguity",
    purpose="""Defines Ambiguity dataclass and AmbiguityChecker for validating module specifications.

    Ambiguity dataclass represents a found issue with fields: module_name, location, issue,
    severity ('error' or 'warning', default 'error'), and suggestions (list of strings).
    Has a __str__ method that formats as "⚠️/❌ module.location: issue" with suggestions listed.

    AmbiguityChecker takes an Agent and checks Module specs for ambiguities that would prevent
    correct implementation. Builds a prompt asking the agent to identify critical missing information,
    contradictions, or unclear behavior (NOT minor style issues). Parses response for AMBIGUITY blocks
    or NO_AMBIGUITIES marker. Returns list of Ambiguity objects.
    """,
    dependencies=[agent_spec, claude_agent_spec, module_spec],
    tests=[
        "Create Ambiguity with module_name='foo', location='tests', issue='unclear', severity='error' - should store all fields",
        "Ambiguity severity should default to 'error' if not specified",
        "Ambiguity suggestions should default to empty list",
        "Ambiguity.__str__() with severity='error' should start with '❌'",
        "Ambiguity.__str__() with severity='warning' should start with '⚠️'",
        "Ambiguity.__str__() should format as 'emoji module.location: issue'",
        "Ambiguity.__str__() with suggestions should include '  Suggestions:' section with each suggestion indented",
        "AmbiguityChecker() with no agent should use ClaudeAgent() by default",
        "AmbiguityChecker(agent=custom_agent) should use the provided agent",
        "AmbiguityChecker.check(module) should build prompt with module name, purpose, dependencies, and tests",
        "AmbiguityChecker prompt should ask agent to identify critical ambiguities only (not style issues)",
        "AmbiguityChecker prompt should list dependencies with 'name: purpose' format",
        "AmbiguityChecker prompt should handle modules with no tests (show 'Tests: (none provided)')",
        "AmbiguityChecker should parse 'NO_AMBIGUITIES' response as empty list",
        "AmbiguityChecker should parse 'AMBIGUITY:' blocks with Location/Issue/Severity/Suggestions",
        "AmbiguityChecker should handle multiple AMBIGUITY blocks in response",
        "AmbiguityChecker should default severity to 'error' if parsing fails or value is invalid",
        "AmbiguityChecker should collect suggestions (lines starting with '-') for each ambiguity",
        "AmbiguityChecker.check() should return list of Ambiguity objects with correct module_name",
    ]
)

# Caching layer
cache_spec = Module(
    name="cache",
    purpose="""Implements AmbiguityCache for caching ambiguity check results to avoid redundant LLM calls.

    Takes a cache_dir Path and stores results in .ambiguity_cache.json. Computes SHA256 hash
    of module specs (name, purpose, dependency names, tests) to detect changes. Provides get(module)
    to retrieve cached results (returns None if not cached) and set(module, ambiguities) to store.

    Serializes Ambiguity objects to dicts with all fields. Loads/saves cache from disk automatically.
    Creates cache_dir if it doesn't exist. Cache is a dict mapping hash -> list of ambiguity dicts
    (or empty list if no ambiguities).
    """,
    dependencies=[module_spec],
    tests=[
        "Create AmbiguityCache(cache_dir=Path('/tmp/cache')) - should create directory if it doesn't exist",
        "AmbiguityCache should load existing .ambiguity_cache.json if present",
        "AmbiguityCache with no existing cache file should start with empty cache dict",
        "AmbiguityCache._hash_module() should compute SHA256 of JSON with name, purpose, dependency names, tests",
        "AmbiguityCache._hash_module() should produce same hash for same module spec",
        "AmbiguityCache._hash_module() should produce different hash if purpose changes",
        "AmbiguityCache._hash_module() should produce different hash if tests change",
        "AmbiguityCache._hash_module() should use dependency names only (not full objects) for hashing",
        "AmbiguityCache.get(module) with no cached result should return None",
        "AmbiguityCache.get(module) with cached empty list should return empty list",
        "AmbiguityCache.get(module) with cached ambiguities should return list of dicts",
        "AmbiguityCache.set(module, []) should cache empty list and save to disk",
        "AmbiguityCache.set(module, [ambiguity_obj]) should serialize Ambiguity to dict and save",
        "AmbiguityCache serialized dicts should include module_name, location, issue, severity, suggestions",
        "AmbiguityCache._save_cache() should write JSON with indent=2 to .ambiguity_cache.json",
        "AmbiguityCache should persist across instances (write with one instance, read with another)",
    ]
)

# Compiler
compiler_spec = Module(
    name="compiler",
    purpose="""Implements LLMCompiler for compiling Module specifications to executable code.

    Takes an Agent and optional cwd Path. Compilation is a multi-pass process:
    1. Ambiguity checking (unless force=True) - abort if any ambiguities found
    2. Compile dependencies recursively (fail if any dependency fails)
    3. Generate code using agent with detailed prompt including purpose, tests, and dependency code

    Returns CompilationResult with status ('ambiguous', 'compiled', 'error'), ambiguities list,
    code string, metadata dict, and error string. Saves compilation logs to COMPILE_{module.name}.log
    in cwd. Generates code by sending prompt to agent which writes files directly.
    """,
    dependencies=[agent_spec, claude_agent_spec, module_spec, ambiguity_spec],
    tests=[
        "LLMCompiler() with no agent should use ClaudeAgent() by default",
        "LLMCompiler(agent=custom_agent, cwd=Path('/tmp')) should use provided agent and cwd",
        "CompilationResult dataclass should have status, ambiguities, code, metadata, error fields",
        "CompilationResult.ambiguities should default to empty list",
        "CompilationResult.metadata should default to empty dict",
        "compile(module) without force should check for ambiguities first",
        "compile(module) with ambiguities should return CompilationResult(status='ambiguous', ambiguities=[...])",
        "compile(module, force=True) should skip ambiguity checking",
        "compile(module) should compile dependencies recursively before compiling module",
        "compile(module) with failing dependency should return CompilationResult(status='error', error='Dependency X failed...')",
        "compile(module) should pass dependency code to _generate_code() as dict",
        "compile(module) on success should return CompilationResult(status='compiled', code='...')",
        "_generate_code() should build prompt with module name, purpose, tests, and dependency code",
        "_generate_code() should instruct agent to write code to {module.name}.py and tests to test_{module.name}.py",
        "_generate_code() should instruct agent to run pytest until all tests pass",
        "_generate_code() should call agent.query(prompt, cwd=cwd)",
        "_generate_code() should save log to {cwd}/COMPILE_{module.name}.log on success",
        "_generate_code() should save log with error on failure",
        "_save_log() should write module name, purpose, tests, dependencies, prompt, and response to log file",
        "_save_log() with error should include exception type and message",
        "compile() should catch exceptions and return CompilationResult(status='error', error=str(e), metadata={'exception_type': ...})",
        "CompilationResult metadata should include 'pass' (ambiguity_check or code_generation), 'target_language', 'dependencies'",
    ]
)

# Decompiler
decompiler_spec = Module(
    name="decompiler",
    purpose="""Implements Decompiler for reverse-engineering code into Module specifications.

    Takes an Agent and generates spec.py files from existing code directories. Process:
    1. Gather all .py files (skip __pycache__ and test_ files)
    2. Generate initial spec by sending code to agent with instructions to write Module definitions
    3. Load modules from generated spec using importlib
    4. Check each module for ambiguities
    5. If ambiguities found, refine spec iteratively (up to max_iterations, default 5)
    6. Return final spec code (warns if still ambiguous after max iterations)

    Agent writes spec.py directly. Uses AmbiguityChecker for validation loop.
    """,
    dependencies=[agent_spec, claude_agent_spec, module_spec, ambiguity_spec],
    tests=[
        "Decompiler() with no agent should use ClaudeAgent() by default",
        "Decompiler(agent=custom_agent) should use provided agent",
        "decompile(code_dir, output_file) should gather all .py files from code_dir recursively",
        "_gather_code_files() should skip __pycache__ directories",
        "_gather_code_files() should skip files starting with 'test_'",
        "_gather_code_files() should return dict mapping relative paths to file contents",
        "decompile() with empty code_dir should raise ValueError('No code files found...')",
        "decompile() should send initial prompt to agent with all code files",
        "_build_initial_decompile_prompt() should include code for each file with '--- filepath ---' markers",
        "_build_initial_decompile_prompt() should instruct agent to write spec.py to output_file",
        "_build_initial_decompile_prompt() should specify Module format with name, purpose, dependencies, tests",
        "_build_initial_decompile_prompt() should emphasize avoiding ambiguities",
        "decompile() should load modules from generated spec using _load_modules_from_spec()",
        "_load_modules_from_spec() should use importlib to load the spec file",
        "_load_modules_from_spec() should find all Module instances in the loaded module",
        "_load_modules_from_spec() should return list of Module objects",
        "decompile() with no modules in generated spec should raise ValueError('No modules found...')",
        "decompile() should check each module for ambiguities using AmbiguityChecker",
        "decompile() with no ambiguities should return immediately with spec code",
        "decompile() with ambiguities should refine spec using _build_refinement_prompt()",
        "_build_refinement_prompt() should include current spec, all ambiguities with locations and suggestions",
        "_build_refinement_prompt() should instruct agent to rewrite entire spec file with fixes",
        "decompile() should iterate up to max_iterations times refining spec",
        "decompile() after max_iterations with ambiguities should print warning and return spec",
        "decompile() should print progress messages for each iteration",
        "decompile() on success should print '✅ Spec passes ambiguity checks'",
        "decompile() should return final spec.py file contents as string",
    ]
)

# Compile CLI
compile_cli_spec = Module(
    name="compile_cli",
    purpose="""Implements CLI tool for compiling Module specifications to executable code.

    Takes a Python file containing Module definitions, loads all Module objects using importlib,
    and compiles them using LLMCompiler. Has two phases:
    1. Check ALL modules for ambiguities first (with caching) - abort if any have issues
    2. Compile all modules to code (writes to output_dir, default: compiled_src/)

    Supports --force to skip ambiguity checks, --output-dir to specify output location,
    and --claude-command to use alternative agent commands (e.g., 'claudebox -p').
    Uses AmbiguityCache to avoid redundant checks. Returns 0 on success, 1 on failure.
    """,
    dependencies=[module_spec, compiler_spec, cache_spec, claude_agent_spec],
    tests=[
        "load_modules_from_file(filepath) should use importlib to load the file",
        "load_modules_from_file() should find all Module instances in loaded file",
        "load_modules_from_file() should return list of Module objects",
        "compile_file() should load modules from filepath",
        "compile_file() with no modules should print error and return 1",
        "compile_file() should print count of found modules",
        "compile_file() without --force should do Phase 1: check all modules for ambiguities",
        "compile_file() should use AmbiguityCache with output_dir",
        "compile_file() should check cache.get(module) before running checker",
        "compile_file() should print '(cached)' for cached ambiguity results",
        "compile_file() should cache ambiguity results with cache.set(module, ambiguities)",
        "compile_file() with ambiguities should print all ambiguities and return 1",
        "compile_file() should abort before compilation if any module has ambiguities",
        "compile_file() should print '✅ All modules passed ambiguity checks' if all clear",
        "compile_file() should do Phase 2: compile all modules with force=True",
        "compile_file() should create LLMCompiler with ClaudeAgent(command=claude_command) and cwd=output_dir",
        "compile_file() should compile each module and report success/failure",
        "compile_file() should return 1 if any compilation returns status='error'",
        "compile_file() should print success message with output file path for each compiled module",
        "compile_file() should return 0 on full success",
        "main() should parse --force, --output-dir, --claude-command arguments",
        "main() should default output_dir to input_file.parent / 'compiled_src'",
        "main() should default claude_command to 'claude'",
        "main() should validate input file exists and return 1 if not",
        "main() should create output_dir with mkdir(exist_ok=True)",
        "main() should call compile_file() and return its result",
    ]
)

# Decompile CLI
decompile_cli_spec = Module(
    name="decompile_cli",
    purpose="""Implements CLI tool for decompiling existing code into Module specifications.

    Takes a code directory path and generates a spec.py file using Decompiler. Default output
    is spec.py in the code directory, but --output/-o can specify a different location.
    Supports --claude-command for alternative agent commands.

    Validates that code_dir exists and is a directory before proceeding. Creates Decompiler
    with ClaudeAgent, runs decompile(), prints success/error messages, and returns 0 on
    success or 1 on failure.
    """,
    dependencies=[decompiler_spec, claude_agent_spec],
    tests=[
        "decompile_directory(code_dir, output_file) should create Decompiler with ClaudeAgent(command=claude_command)",
        "decompile_directory() should call decompiler.decompile(code_dir, output_file)",
        "decompile_directory() on success should print '✅ Generated spec file → {output_file}' and return 0",
        "decompile_directory() on exception should print error with traceback and return 1",
        "main() should parse code_dir positional argument as Path",
        "main() should parse --output/-o optional argument as Path",
        "main() should parse --claude-command with default 'claude'",
        "main() should default output to code_dir / 'spec.py' if --output not provided",
        "main() should validate code_dir exists and return 1 if not",
        "main() should validate code_dir is a directory and return 1 if not",
        "main() should call decompile_directory() and return its result",
        "CLI should support 'claudebox -p' for containerized execution via --claude-command",
    ]
)
