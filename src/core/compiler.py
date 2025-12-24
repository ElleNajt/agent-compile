#!/usr/bin/env python3
"""Compiler for module specifications."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from .agent import Agent
from .ambiguity import Ambiguity, AmbiguityChecker
from .claude_agent import ClaudeAgent
from .language_prompts import get_language_instructions
from .module import Module


@dataclass
class CompilationResult:
    """Result of compiling a module."""

    status: Literal["ambiguous", "compiled", "error"]
    ambiguities: list[Ambiguity] = field(default_factory=list)
    code: str | None = None
    metadata: dict = field(default_factory=dict)
    error: str | None = None


class CompilationError(Exception):
    """Raised when compilation fails."""

    pass


class LLMCompiler:
    """
    Compiles module specifications to executable code.

    Uses a two-pass strategy:
    1. Ambiguity checking - identify unclear parts of the spec
    2. Code generation - compile to executable code
    """

    def __init__(self, agent: Agent | None = None, cwd: Path | None = None):
        """
        Initialize the compiler.

        Args:
            agent: Agent to use for LLM queries (default: ClaudeAgent)
            cwd: Working directory for agent (used when compiling)
        """
        self.agent = agent if agent is not None else ClaudeAgent()
        self.cwd = cwd
        self.ambiguity_checker = AmbiguityChecker(agent=self.agent)

    def compile(
        self, module: Module, target_language: str = "python", force: bool = False
    ) -> CompilationResult:
        """
        Compile a module to executable code.

        Args:
            module: The module to compile
            target_language: Target programming language (default: python)
            force: Skip ambiguity checking if True

        Returns:
            CompilationResult with status, code, or ambiguities
        """
        try:
            # Pass 1: Check for ambiguities (unless forced)
            if not force:
                ambiguities = self.ambiguity_checker.check(module)
                if ambiguities:
                    return CompilationResult(
                        status="ambiguous",
                        ambiguities=ambiguities,
                        metadata={"pass": "ambiguity_check"},
                    )

            # Pass 2: Compile dependencies first
            dep_code = {}
            for dep in module.dependencies:
                dep_result = self.compile(
                    dep, target_language=target_language, force=force
                )
                if dep_result.status != "compiled":
                    raise CompilationError(
                        f"Dependency {dep.name} failed to compile: {dep_result.status}"
                    )
                dep_code[dep.name] = dep_result.code

            # Pass 3: Generate code for this module
            code = self._generate_code(module, dep_code, target_language)

            return CompilationResult(
                status="compiled",
                code=code,
                metadata={
                    "pass": "code_generation",
                    "target_language": target_language,
                    "dependencies": list(dep_code.keys()),
                },
            )

        except Exception as e:
            return CompilationResult(
                status="error",
                error=str(e),
                metadata={"exception_type": type(e).__name__},
            )

    def _generate_code(
        self, module: Module, dep_code: dict[str, str], target_language: str
    ) -> str:
        """Generate code for a module."""

        prompt = self._build_code_generation_prompt(module, dep_code, target_language)

        try:
            # Query agent with cwd - Claude will write files directly
            response = self.agent.query(prompt, cwd=self.cwd)

            # Save compilation log (success case)
            self._save_log(module, prompt, response, success=True)

            return response.strip()

        except Exception as e:
            # Save compilation log (failure case)
            self._save_log(module, prompt, str(e), success=False, error=e)
            raise

    def _save_log(
        self,
        module: Module,
        prompt: str,
        response: str,
        success: bool,
        error: Exception = None,
    ):
        """Save compilation log."""
        if not self.cwd:
            return

        log_file = self.cwd / f"COMPILE_{module.name}.log"
        status = "SUCCESS" if success else "FAILED"

        log_content = f"""Compilation Log for {module.name}
{"=" * 60}
Status: {status}

Module Specification:
{"-" * 60}
Name: {module.name}
Purpose: {module.purpose}

Tests: {len(module.tests)} test cases
Dependencies: {[d.name for d in module.dependencies]}

Prompt Sent to Claude:
{"-" * 60}
{prompt}

"""

        if success:
            log_content += f"""Claude's Response:
{"-" * 60}
{response}
"""
        else:
            log_content += f"""Error:
{"-" * 60}
{type(error).__name__}: {str(error)}
"""

        log_content += f"""
{"-" * 60}
End of compilation log
"""

        log_file.write_text(log_content)

    def _build_code_generation_prompt(
        self, module: Module, dep_code: dict[str, str], target_language: str
    ) -> str:
        """Build the prompt for code generation."""

        # Format tests
        tests_str = ""
        if module.tests:
            tests_str = "\n\nTests (your code must pass these):\n"
            for i, test in enumerate(module.tests, 1):
                tests_str += f"\n{i}. {test}"

        # Format dependency code
        deps_str = ""
        if dep_code:
            deps_str = "\n\nDependency Code (available for use):\n"
            for dep_name, code in dep_code.items():
                deps_str += f"\n--- Dependency: {dep_name} ---\n{code}\n"

        # Get language-specific instructions
        language_instructions = get_language_instructions(module.language)

        prompt = f"""You are tasked with implementing a {target_language} module.

Module Specification:
---
Name: {module.name}
Purpose: {module.purpose}{tests_str}{deps_str}
---

Your task:
1. Follow the language-specific instructions below for environment setup and tooling
2. Write the implementation
3. Write tests that verify ALL the test cases above
4. Run the tests iteratively until they all pass
5. FAIL FAST: Let errors surface immediately. Do NOT add try-except blocks or default values unless explicitly specified in the purpose

Work iteratively - write code, run tests, fix failures, repeat until all tests pass.

{language_instructions}
"""

        return prompt
