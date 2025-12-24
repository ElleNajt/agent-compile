"""Core module definitions and compilation logic."""

from .agent import Agent
from .ambiguity import Ambiguity, AmbiguityChecker
from .claude_agent import ClaudeAgent
from .compiler import CompilationError, CompilationResult, LLMCompiler
from .module import Module

__all__ = [
    "Module",
    "Ambiguity",
    "AmbiguityChecker",
    "LLMCompiler",
    "CompilationResult",
    "CompilationError",
    "Agent",
    "ClaudeAgent",
]

# Cache
from .cache import AmbiguityCache

__all__.extend(["AmbiguityCache"])
