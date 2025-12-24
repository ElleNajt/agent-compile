#!/usr/bin/env python3
"""Decompiler for generating module specifications from existing code."""

from pathlib import Path

from .agent import Agent
from .claude_agent import ClaudeAgent


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

    def decompile(self, code_dir: Path) -> str:
        """
        Decompile code directory into Module spec.

        Args:
            code_dir: Directory containing code to decompile

        Returns:
            Python code defining Module specifications (unambiguous)
        """
        # Gather all code files
        code_files = self._gather_code_files(code_dir)

        if not code_files:
            raise ValueError(f"No code files found in {code_dir}")

        # Build prompt for LLM to analyze code and generate spec
        # The prompt instructs Claude to iteratively check for ambiguities
        prompt = self._build_decompile_prompt(code_files)

        # Get spec from LLM (Claude will iterate internally until unambiguous)
        spec_code = self.agent.query(prompt, cwd=code_dir)

        return spec_code

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

    def _build_decompile_prompt(self, code_files: dict[str, str]) -> str:
        """Build prompt for decompiling code to spec."""

        files_str = ""
        for filepath, content in code_files.items():
            files_str += f"\n--- {filepath} ---\n{content}\n"

        return f"""Analyze the following code and generate a Module specification for it.

Code Files:
{files_str}

Your task:
1. Analyze the code to understand its purpose and behavior
2. Identify the main modules/components (there may be one or multiple)
3. Generate a spec.py file with Module definitions
4. Check the generated spec for ambiguities using the same criteria as the compiler's ambiguity checker
5. Iteratively refine the spec until it would pass ambiguity checking

For each Module you should specify:
- name: The module name (infer from code structure)
- purpose: High-level description of what it does (2-3 sentences, be SPECIFIC)
- dependencies: List of other Modules it depends on (if any)
- tests: Natural language test descriptions (comprehensive, covering functionality and edge cases)

Output format:
```python
from src.core import Module

# Module definitions here
module_name = Module(
    name="module_name",
    purpose=\"\"\"Description of what this module does.
    
    Additional details about behavior, inputs, outputs, etc.
    \"\"\",
    tests=[
        "Test description 1",
        "Test description 2",
        ...
    ]
)
```

IMPORTANT - Avoid Ambiguities:
- Purpose must be SPECIFIC enough that implementation is clear
- Tests must cover all main functionality and edge cases
- If purpose mentions behavior, tests should verify that behavior
- No contradictions between purpose and tests
- Include enough detail that someone could implement correctly from the spec alone

ITERATION INSTRUCTIONS:
1. Generate initial spec
2. Review it for ambiguities (missing details, contradictions, vague descriptions)
3. If ambiguities found, refine and repeat
4. Only output the final unambiguous spec

Focus on WHAT the code does, not HOW it's implemented.

Generate the complete, unambiguous spec.py file:
"""
