#!/usr/bin/env python3
"""Language-specific prompt templates for code generation."""


def get_language_instructions(language: str) -> str:
    """
    Get language-specific instructions for code generation.

    Args:
        language: Target programming language (e.g., "python", "rust", "javascript")

    Returns:
        Language-specific instructions to append to the code generation prompt
    """
    templates = {
        "python": _python_instructions(),
        "rust": _rust_instructions(),
        "javascript": _javascript_instructions(),
    }

    return templates.get(language.lower(), _default_instructions(language))


def _python_instructions() -> str:
    return """
## Python-Specific Instructions

**Environment Setup:**
1. Create an isolated virtual environment using `uv`:
   ```bash
   uv venv .venv
   source .venv/bin/activate  # or `.venv/bin/activate` on Unix
   ```

2. If the module requires external dependencies (numpy, scikit-learn, etc.):
   - Create a `requirements.txt` file listing all dependencies
   - Install them in the venv: `uv pip install -r requirements.txt`

**Code Organization:**
- Write implementation to `{module_name}.py`
- Write pytest tests to `test_{module_name}.py`
- Use type hints for all function signatures
- Follow PEP 8 style guidelines

**Testing:**
- Install pytest in the venv if needed: `uv pip install pytest`
- Run tests: `pytest test_{module_name}.py -v`
- Iterate until all tests pass

**Important:**
- DO NOT install packages globally or outside the venv
- DO NOT vendor (copy) library code into the project
- Use `uv` for all package management (faster than pip)
- The venv is local to this compilation directory
"""


def _rust_instructions() -> str:
    return """
## Rust-Specific Instructions

**Environment Setup:**
1. Create a new Cargo project structure if needed:
   ```bash
   cargo init --lib
   ```

**Code Organization:**
- Write implementation to `src/lib.rs` or `src/{module_name}.rs`
- Write tests in the same file using `#[cfg(test)]` modules
- Use proper error handling with `Result<T, E>`
- Follow Rust naming conventions

**Testing:**
- Run tests: `cargo test`
- Iterate until all tests pass

**Dependencies:**
- Add dependencies to `Cargo.toml` under `[dependencies]`
- Cargo will automatically download and compile them
"""


def _javascript_instructions() -> str:
    return """
## JavaScript-Specific Instructions

**Environment Setup:**
1. Initialize npm project if needed:
   ```bash
   npm init -y
   ```

**Code Organization:**
- Write implementation to `{module_name}.js` (or `.ts` for TypeScript)
- Write Jest tests to `{module_name}.test.js`
- Use ES6+ features (const/let, arrow functions, async/await)

**Testing:**
- Install Jest: `npm install --save-dev jest`
- Add test script to package.json: `"test": "jest"`
- Run tests: `npm test`
- Iterate until all tests pass

**Dependencies:**
- Install via npm: `npm install <package>`
- Dependencies are local to this project (node_modules/)
"""


def _default_instructions(language: str) -> str:
    return f"""
## {language.title()}-Specific Instructions

**Code Organization:**
- Write implementation following {language} conventions
- Write tests using appropriate testing framework
- Iterate until all tests pass

**Dependencies:**
- Use {language}'s standard package manager
- Install dependencies locally to this project
"""
