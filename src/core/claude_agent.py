#!/usr/bin/env python3
"""Claude agent implementation using claude CLI subprocess."""

import subprocess
from pathlib import Path

from .agent import Agent


class ClaudeAgent(Agent):
    """Agent implementation using `claude` CLI subprocess."""

    def __init__(self, command: str = "claude"):
        """
        Initialize Claude agent.

        Args:
            command: Command to run (default: "claude")
                    Can be "claudebox" or other containerized commands
        """
        self.command = command

    def query(self, prompt: str, cwd: Path | None = None) -> str:
        """
        Send a prompt to Claude using CLI and get response.

        Claude will execute the task in the specified working directory,
        including writing files, running tests, etc.

        Args:
            prompt: The prompt/task to send
            cwd: Working directory for Claude to execute in

        Returns:
            Claude's final response
        """
        # Run claude/claudebox with the prompt via stdin
        result = subprocess.run(
            [self.command],
            input=prompt,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()
