#!/usr/bin/env python3
"""Core module definition for agent-compile."""

from dataclasses import dataclass, field


@dataclass
class Module:
    """
    A module specification that can be compiled to executable code.

    The design is intentionally minimal - the ambiguity checker will force
    you to make the purpose and tests specific enough that compilation is unambiguous.
    """

    name: str
    purpose: str  # High-level intent in natural language
    dependencies: list["Module"] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)  # Natural language test descriptions

    # Freezing metadata (for future use - see agent-compile-1d6)
    frozen: bool = False
    frozen_code: str | None = None
    frozen_hash: str | None = None

    def __post_init__(self):
        """Validate the module specification."""
        if not self.name:
            raise ValueError("Module must have a name")
        if not self.purpose:
            raise ValueError("Module must have a purpose")
