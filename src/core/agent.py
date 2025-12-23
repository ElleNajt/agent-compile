#!/usr/bin/env python3
"""Abstract agent interface for LLM interactions."""

from abc import ABC, abstractmethod
from pathlib import Path


class Agent(ABC):
    """Abstract interface for LLM agents."""

    @abstractmethod
    def query(self, prompt: str, cwd: Path | None = None) -> str:
        """
        Send a prompt to the agent and get a response.

        Args:
            prompt: The prompt to send
            cwd: Working directory for the agent (if relevant)

        Returns:
            The agent's response as a string
        """
        pass
