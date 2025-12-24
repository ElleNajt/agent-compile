#!/usr/bin/env python3
"""Decompiler for generating module specifications from existing code."""

import importlib.util
import sys
from pathlib import Path

from .agent import Agent
from .ambiguity import AmbiguityChecker
from .claude_agent import ClaudeAgent
from .module import Module


class Decompiler:
    """
    Decompiles existing code into Module specifications.

    Takes a directory of code and generates a spec.py file with Module definitions.
    Iteratively refines the spec until it passes ambiguity checking.
    """

    def __init__(self, agent: Agent | None = None):
        """
        Initialize the decompiler.

        Args:
            agent: Agent to use for LLM queries (default: ClaudeAgent)
        """
        self.agent = agent if agent is not None else ClaudeAgent()
        self.ambiguity_checker = AmbiguityChecker(agent=self.agent)

    def decompile(
        self, code_dir: Path, output_file: Path, max_iterations: int = 5
    ) -> str:
        """
        Decompile code directory into Module spec.

        Iteratively generates and refines the spec until it passes ambiguity checking.

        Args:
            code_dir: Directory containing code to decompile
            output_file: Where to write the spec file
            max_iterations: Maximum refinement iterations (default: 5)

        Returns:
            Python code defining Module specifications (unambiguous)
        """
        # Gather all code files
        code_files = self._gather_code_files(code_dir)

        if not code_files:
            raise ValueError(f"No code files found in {code_dir}")

        # Initial decompilation - Claude writes spec file directly
        print(f"  Generating initial spec...", flush=True)
        prompt = self._build_initial_decompile_prompt(code_files, output_file)
        self.agent.query(prompt, cwd=code_dir.parent)
        print(f"  Checking generated spec for ambiguities...", flush=True)

        # Iteratively refine until unambiguous
        for iteration in range(max_iterations):
            # Load modules from generated spec
            modules = self._load_modules_from_spec(output_file)

            if not modules:
                raise ValueError(f"No modules found in generated spec: {output_file}")

            print(f"  Loaded {len(modules)} module(s), checking each...", flush=True)

            # Check each module for ambiguities
            all_ambiguities = {}
            for module in modules:
                ambiguities = self.ambiguity_checker.check(module)
                if ambiguities:
                    all_ambiguities[module.name] = ambiguities

            # If no ambiguities, we're done!
            if not all_ambiguities:
                print(f"  ✅ Spec passes ambiguity checks!", flush=True)
                return output_file.read_text()

            # Refine the spec based on ambiguities
            print(
                f"  Iteration {iteration + 1}: Found ambiguities in {len(all_ambiguities)} module(s), refining...",
                flush=True,
            )
            prompt = self._build_refinement_prompt(
                output_file, all_ambiguities, code_files
            )
            self.agent.query(prompt, cwd=code_dir.parent)

        # After max iterations, return what we have
        print(
            f"  ⚠️  Warning: Spec still has ambiguities after {max_iterations} iterations",
            flush=True,
        )
        return output_file.read_text()

    def _gather_code_files(self, code_dir: Path) -> dict[str, str]:
        """
        Gather all code files from directory.

        Returns:
            Dictionary mapping file paths to file contents
        """
        code_files = {}

        # Support Python for now (can extend to other languages)
        for py_file in code_dir.glob("**/*.py"):
            # Skip __pycache__ and test files for now
            if "__pycache__" in str(py_file) or py_file.name.startswith("test_"):
                continue

            relative_path = py_file.relative_to(code_dir)
            code_files[str(relative_path)] = py_file.read_text()

        return code_files

    def _load_modules_from_spec(self, spec_file: Path) -> list[Module]:
        """Load Module objects from a spec file."""
        spec = importlib.util.spec_from_file_location("decompiled_spec", spec_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules["decompiled_spec"] = module
        spec.loader.exec_module(module)

        # Find all Module instances
        modules = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, Module):
                modules.append(obj)

        return modules

    def _build_initial_decompile_prompt(
        self, code_files: dict[str, str], output_file: Path
    ) -> str:
        """Build prompt for initial decompilation."""
        files_str = ""
        for filepath, content in code_files.items():
            files_str += f"\n--- {filepath} ---\n{content}\n"

        return f"""Analyze the following code and generate a Module specification for it.

Code Files:
{files_str}

Your task:
1. Analyze the code to understand its purpose and behavior
2. Identify the main modules/components (there may be one or multiple)
3. Write a spec.py file to {output_file} with Module definitions

For each Module you should specify:
- name: The module name (infer from code structure)
- purpose: High-level description of what it does (be SPECIFIC - 2-3 sentences minimum)
- dependencies: List of other Modules it depends on (if any)
- tests: Natural language test descriptions (comprehensive, covering all functionality and edge cases)

IMPORTANT - Avoid Ambiguities:
- Purpose must be SPECIFIC enough that implementation is clear
- Include behavioral details, inputs/outputs, error handling
- Tests must cover ALL main functionality and edge cases
- No contradictions between purpose and tests
- Include enough detail that someone could implement correctly from spec alone

Output format (write to {output_file}):
```python
from src.core import Module

# Module definitions here
module_name = Module(
    name="module_name",
    purpose=\"\"\"Detailed description of what this module does.
    
    Include behavioral details, inputs, outputs, error handling, etc.
    Be SPECIFIC.
    \"\"\",
    dependencies=[other_module],  # if any
    tests=[
        "Test description 1 with specific inputs/outputs",
        "Test description 2 covering edge cases",
        ...
    ]
)
```

Focus on WHAT the code does, not HOW it's implemented.
Write the complete spec.py file to {output_file}.
"""

    def _build_refinement_prompt(
        self, spec_file: Path, all_ambiguities: dict, code_files: dict[str, str]
    ) -> str:
        """Build prompt for refining spec based on ambiguities."""
        # Format ambiguities
        ambiguities_str = ""
        for module_name, ambiguities in all_ambiguities.items():
            ambiguities_str += f"\n\nModule: {module_name}\n"
            for amb in ambiguities:
                ambiguities_str += f"  - {amb.location}: {amb.issue}\n"
                if amb.suggestions:
                    for suggestion in amb.suggestions:
                        ambiguities_str += f"    Suggestion: {suggestion}\n"

        current_spec = spec_file.read_text()

        return f"""The generated spec has ambiguities. Please refine it to fix these issues.

Current spec ({spec_file}):
```python
{current_spec}
```

Ambiguities found:
{ambiguities_str}

Your task:
1. Read the current spec and the ambiguities
2. Fix each ambiguity by making the purpose more specific or adding missing tests
3. Rewrite the ENTIRE spec file to {spec_file} with fixes applied

Guidelines:
- Make purposes more specific and detailed
- Add missing test cases
- Resolve contradictions between purpose and tests
- Ensure every module has comprehensive tests

Write the complete, refined spec.py file to {spec_file}.
"""
