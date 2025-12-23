#!/usr/bin/env python3
"""CLI for compiling module specifications."""

import argparse
import importlib.util
import sys
from pathlib import Path

from src.core import CompilationResult, LLMCompiler


def load_modules_from_file(filepath: Path) -> list:
    """Load Module objects from a Python file."""
    spec = importlib.util.spec_from_file_location("spec_module", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find all Module instances in the file
    from src.core import Module

    modules = []
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, Module):
            modules.append(obj)

    return modules


def compile_file(filepath: Path, output_dir: Path, force: bool = False):
    """Compile modules from a file."""
    print(f"Loading modules from {filepath}...")

    modules = load_modules_from_file(filepath)

    if not modules:
        print(f"No modules found in {filepath}")
        return 1

    print(f"Found {len(modules)} module(s): {', '.join(m.name for m in modules)}")

    # Create compiler with cwd set to output directory
    compiler = LLMCompiler(cwd=output_dir)

    for module in modules:
        print(f"\nCompiling {module.name}...")
        result = compiler.compile(module, force=force)

        if result.status == "ambiguous":
            print(f"❌ {module.name} has ambiguities:\n")
            for amb in result.ambiguities:
                print(f"  {amb}\n")
            return 1

        elif result.status == "error":
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
    return compile_file(args.file, output_dir, force=args.force)


if __name__ == "__main__":
    sys.exit(main())
