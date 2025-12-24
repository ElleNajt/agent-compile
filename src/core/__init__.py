"""Core module definitions and compilation logic."""

from .module import Module, Example
from .ambiguity import Ambiguity, AmbiguityChecker
from .compiler import LLMCompiler, CompilationResult, CompilationError
from .agent import Agent
from .claude_agent import ClaudeAgent

__all__ = [
    'Module',
    'Example',
    'Ambiguity',
    'AmbiguityChecker',
    'LLMCompiler',
    'CompilationResult',
    'CompilationError',
    'Agent',
    'ClaudeAgent'
]

# Cache
from .cache import AmbiguityCache

__all__.extend(['AmbiguityCache'])
