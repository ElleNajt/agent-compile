#!/usr/bin/env python3
"""CLI for compiling module specifications."""

import argparse
import importlib.util
import sys
from pathlib import Path

from agent_compile.core import Ambiguity, CompilationResult, LLMCompiler
from agent_compile.core.cache import AmbiguityCache


def load_modules_from_file(filepath: Path) -> list:
    """Load Module objects from a Python file."""
    spec = importlib.util.spec_from_file_location("spec_module", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find all Module instances in the file
    from agent_compile.core import Module

    modules = []
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, Module):
            modules.append(obj)

    return modules


def compile_file(
    filepath: Path,
    output_dir: Path,
    force: bool = False,
    claude_command: str = "claude",
):
    """Compile modules from a file."""
    print(f"Loading modules from {filepath}...")

    modules = load_modules_from_file(filepath)

    if not modules:
        print(f"No modules found in {filepath}")
        return 1

    print(f"Found {len(modules)} module(s): {', '.join(m.name for m in modules)}")

    # Create compiler with cwd set to output directory
    from agent_compile.core import ClaudeAgent

    agent = ClaudeAgent(command=claude_command)
    compiler = LLMCompiler(agent=agent, cwd=output_dir)

    # Phase 1: Check ALL modules for ambiguities first
    if not force:
        print("\nPhase 1: Checking all modules for ambiguities...")
        cache = AmbiguityCache(output_dir)
        all_ambiguities = {}

        for module in modules:
            # Check cache first
            cached = cache.get(module)
            if cached is not None:
                print(f"  Checking {module.name}... (cached)")
                # Reconstruct Ambiguity objects from cached dicts
                if cached:  # If there were ambiguities
                    ambiguities = [Ambiguity(**amb_dict) for amb_dict in cached]
                    all_ambiguities[module.name] = ambiguities
            else:
                print(f"  Checking {module.name}...")
                ambiguities = compiler.ambiguity_checker.check(module)
                # Cache the result
                cache.set(module, ambiguities)
                if ambiguities:
                    all_ambiguities[module.name] = ambiguities

        # If any module has ambiguities, report all and abort
        if all_ambiguities:
            print(f"\n❌ Found ambiguities in {len(all_ambiguities)} module(s):\n")
            for module_name, ambiguities in all_ambiguities.items():
                print(f"Module: {module_name}")
                for amb in ambiguities:
                    print(f"  {amb}\n")
            return 1

        print("✅ All modules passed ambiguity checks\n")

    # Phase 2: Compile all modules (now we know they're all unambiguous)
    print("Phase 2: Compiling modules...")
    for module in modules:
        print(f"\nCompiling {module.name}...")
        # Skip ambiguity check since we already did it
        result = compiler.compile(module, force=True)

        if result.status == "error":
            print(f"❌ {module.name} compilation error: {result.error}")
            return 1

        elif result.status == "compiled":
            # Claude already wrote the files during compilation
            output_file = output_dir / f"{module.name}.py"
            if output_file.exists():
                print(f"✅ {module.name} compiled successfully → {output_file}")
            else:
                print(
                    f"⚠️  {module.name} compilation finished but file not found at {output_file}"
                )

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Compile module specifications to code"
    )
    parser.add_argument(
        "file", type=Path, help="Python file containing Module specifications"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory (default: compiled_src/ in same directory as input file)",
    )
    parser.add_argument("--force", action="store_true", help="Skip ambiguity checking")
    parser.add_argument(
        "--claude-command",
        type=str,
        default="claude",
        help="Command to run Claude (default: 'claude', can use 'claudebox -p' for containerized execution)",
    )

    args = parser.parse_args()

    # Validate input file
    if not args.file.exists():
        print(f"Error: {args.file} does not exist")
        return 1

    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = args.file.parent / "compiled_src"

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Compile
    return compile_file(
        args.file, output_dir, force=args.force, claude_command=args.claude_command
    )


if __name__ == "__main__":
    sys.exit(main())
