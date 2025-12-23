#!/usr/bin/env python3
"""Claude agent implementation using claude CLI subprocess."""

import subprocess
from pathlib import Path

from .agent import Agent


class ClaudeAgent(Agent):
    """Agent implementation using `claude` CLI subprocess."""

    def query(self, prompt: str, cwd: Path | None = None) -> str:
        """
        Send a prompt to Claude using `claude` CLI and get response.

        Claude will execute the task in the specified working directory,
        including writing files, running tests, etc.

        Args:
            prompt: The prompt/task to send
            cwd: Working directory for Claude to execute in

        Returns:
            Claude's final response
        """
        # Run claude with the prompt via stdin
        result = subprocess.run(
            ["claude"],
            input=prompt,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()
