#!/usr/bin/env python3
"""CLI for decompiling code into module specifications."""

import argparse
import sys
from pathlib import Path

from agent_compile.core import ClaudeAgent
from agent_compile.core.decompiler import Decompiler


def decompile_directory(
    code_dir: Path, output_file: Path, claude_command: str = "claude"
):
    """Decompile code directory into spec file."""
    print(f"Decompiling code from {code_dir}...")

    # Create decompiler
    agent = ClaudeAgent(command=claude_command)
    decompiler = Decompiler(agent=agent)

    try:
        # Decompile code to spec (iterates until unambiguous)
        decompiler.decompile(code_dir, output_file)

        print(f"✅ Generated spec file → {output_file}")
        return 0

    except Exception as e:
        print(f"❌ Decompilation failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Decompile existing code into Module specifications"
    )
    parser.add_argument(
        "code_dir",
        type=Path,
        help="Directory containing code to decompile",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output spec file (default: spec.py in code directory)",
    )
    parser.add_argument(
        "--claude-command",
        type=str,
        default="claude",
        help="Command to run Claude (default: 'claude', can use 'claudebox -p' for containerized execution)",
    )

    args = parser.parse_args()

    # Validate code directory
    if not args.code_dir.exists():
        print(f"Error: {args.code_dir} does not exist")
        return 1

    if not args.code_dir.is_dir():
        print(f"Error: {args.code_dir} is not a directory")
        return 1

    # Determine output file
    if args.output:
        output_file = args.output
    else:
        output_file = args.code_dir / "spec.py"

    # Decompile
    return decompile_directory(
        args.code_dir, output_file, claude_command=args.claude_command
    )


if __name__ == "__main__":
    sys.exit(main())
