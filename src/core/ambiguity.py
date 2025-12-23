#!/usr/bin/env python3
"""Ambiguity checking for module specifications."""

from dataclasses import dataclass, field
from typing import Literal

from .agent import Agent
from .claude_agent import ClaudeAgent
from .module import Module


@dataclass
class Ambiguity:
    """Represents an ambiguity found in a module specification."""

    module_name: str
    location: str
    issue: str
    severity: Literal["error", "warning"] = "error"
    suggestions: list[str] = field(default_factory=list)

    def __str__(self):
        severity_prefix = "⚠️" if self.severity == "warning" else "❌"
        result = f"{severity_prefix} {self.module_name}.{self.location}: {self.issue}"
        if self.suggestions:
            result += "\n  Suggestions:"
            for suggestion in self.suggestions:
                result += f"\n    - {suggestion}"
        return result


class AmbiguityChecker:
    """Checks module specifications for ambiguities."""

    def __init__(self, agent: Agent | None = None):
        self.agent = agent if agent is not None else ClaudeAgent()

    def check(self, module: Module) -> list[Ambiguity]:
        prompt = self._build_ambiguity_check_prompt(module)
        response = self.agent.query(prompt)
        return self._parse_ambiguities(response, module.name)

    def _build_ambiguity_check_prompt(self, module: Module) -> str:
        tests_str = ""
        if module.tests:
            tests_str = "\n\nTests/Examples:\n"
            for i, test in enumerate(module.tests, 1):
                tests_str += f"\nTest {i}:"
                if test.description:
                    tests_str += f" {test.description}"
                tests_str += f"\n  Inputs: {test.inputs}"
                tests_str += f"\n  Expected Outputs: {test.outputs}"
        else:
            tests_str = "\n\nTests/Examples: (none provided)"

        deps_str = (
            "\n".join(f"  - {dep.name}: {dep.purpose}" for dep in module.dependencies)
            if module.dependencies
            else "  (none)"
        )

        return f"""Ambiguity check on module specification.

Module Specification:
---
Name: {module.name}
Purpose: {module.purpose}

Dependencies:
{deps_str}{tests_str}
---

Check for ambiguities that would make it impossible to implement correctly:

IMPORTANT: Only flag ambiguities that actually matter for correctness:
- Missing critical information (e.g., unclear what algorithm to use, missing edge case handling)
- Tests that contradict the purpose statement
- Genuinely ambiguous behavior (e.g., what should happen when X?)

DO NOT flag:
- Implementation details like function names (infer from module name)
- Minor style choices (case sensitivity, error message wording)
- Things that have obvious reasonable defaults
- Pedantic edge cases not relevant to the core functionality

For each REAL ambiguity:

AMBIGUITY:
Location: <location>
Issue: <description>
Severity: <error|warning>
Suggestions:
- <suggestion>

If NO significant ambiguities: NO_AMBIGUITIES
"""

    def _parse_ambiguities(self, response: str, module_name: str) -> list[Ambiguity]:
        if "NO_AMBIGUITIES" in response:
            return []

        ambiguities = []
        current = {}
        suggestions = []

        for line in response.split("\n"):
            line = line.strip()

            if line.startswith("AMBIGUITY:"):
                if current:
                    current["suggestions"] = suggestions
                    ambiguities.append(Ambiguity(module_name=module_name, **current))
                current = {}
                suggestions = []
            elif line.startswith("Location:"):
                current["location"] = line.split(":", 1)[1].strip()
            elif line.startswith("Issue:"):
                current["issue"] = line.split(":", 1)[1].strip()
            elif line.startswith("Severity:"):
                sev = line.split(":", 1)[1].strip().lower()
                current["severity"] = sev if sev in ["error", "warning"] else "error"
            elif line.startswith("-") and current:
                suggestions.append(line[1:].strip())

        if current:
            current["suggestions"] = suggestions
            ambiguities.append(Ambiguity(module_name=module_name, **current))

        return ambiguities
