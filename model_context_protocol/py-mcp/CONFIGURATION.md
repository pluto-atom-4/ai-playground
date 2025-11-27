# Project Configuration Guide

This document describes the project configuration and development setup.

## Configuration Files

### `pyproject.toml`
The main project configuration file containing:
- **Build system**: setuptools and wheel
- **Project metadata**: name, version, description, Python version requirements
- **Dependencies**: Development dependencies (pytest, ruff, pyright, pre-commit, markdownlint)
- **Tool configurations**:
  - **Ruff**: Python linter and formatter with specific rules
  - **Pyright**: Static type checker for Python
  - **Pytest**: Test framework configuration
  - **Coverage**: Code coverage reporting

### `.pre-commit-config.yaml`
Defines pre-commit hooks that run before each commit:
- **markdownlint**: Validates Markdown files
- **ruff**: Lints and formats Python code
- **pyright**: Performs type checking
- **YAML/JSON/TOML validation**: Ensures configuration file syntax

### `.copilotignore`
GitHub Copilot instructions file containing:
- Shell environment: Use git bash for all commands
- Output directory: `generated/docs-copilot/` for generated documents
- Code style guidelines: Follow pyproject.toml settings
- Tool requirements: Pre-commit hooks, markdownlint, ruff, pyright
- Git bash requirement: All scripts must work with bash.exe

### `.markdownlint.json`
Configuration for Markdown linting with:
- Line length limit: 100 characters
- Consistent list and heading styles
- Prettier-compatible style

### `.editorconfig`
EditorConfig specification for consistent editor settings:
- Charset: UTF-8
- Line endings: LF (Unix-style)
- Indentation: 4 spaces for Python, 2 spaces for JSON/YAML
- Line length: 100 characters for Python files

## Setup Instructions

### Initial Setup

Run the setup script to initialize your development environment:

```bash
bash scripts/setup.sh
```

This script will:
1. Check Python version
2. Create a Python virtual environment
3. Install project dependencies
4. Install pre-commit hooks
5. Create the `generated/docs-copilot` directory

### Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment (Git Bash on Windows)
source .venv/Scripts/activate

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install project and development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Create generated/docs-copilot directory
mkdir -p generated/docs-copilot
```

## Development Workflow

### Running Pre-commit Hooks

Pre-commit hooks run automatically before each commit. To run them manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files
pre-commit run

# Run a specific hook
pre-commit run ruff --all-files
```

### Code Quality

```bash
# Format code with ruff
ruff format src/ tests/

# Lint code with ruff
ruff check --fix src/ tests/

# Type check with pyright
pyright

# Lint Markdown files
markdownlint-cli2 "**/*.md"
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_module.py::test_function
```

## Tool Descriptions

### Ruff
A fast Python linter and formatter written in Rust.
- **Configuration**: `[tool.ruff]` and `[tool.ruff.lint]` in pyproject.toml
- **Selected rules**: E, W, F, I, C, B, UP, ARG, SIM, LOG

### Pyright
Microsoft's static type checker for Python.
- **Configuration**: `[tool.pyright]` in pyproject.toml
- **Mode**: Basic type checking
- **Includes**: src/ directory

### Markdownlint
Markdown linter that ensures consistent Markdown style.
- **Configuration**: `.markdownlint.json`
- **Line length**: 100 characters

### Pre-commit
Framework for managing and maintaining multi-language pre-commit hooks.
- **Configuration**: `.pre-commit-config.yaml`
- **Install hooks**: `pre-commit install`

## GitHub Copilot Integration

The project includes `.copilotignore` instructions for GitHub Copilot:

- **Shell preference**: Git Bash (bash.exe)
- **Generated documents directory**: `generated/docs-copilot/`
- **Code style**: Follows pyproject.toml configuration
- **Tools required**: ruff format, ruff lint, pyright, markdownlint

When using GitHub Copilot for code generation in this project:
1. Copilot will save generated documentation to `generated/docs-copilot/`
2. All scripts should use git bash syntax
3. Generated code follows the ruff and pyright configuration
4. All generated Markdown should comply with markdownlint rules

## Directory Structure

```
py-mcp/
├── .copilotignore                 # GitHub Copilot instructions
├── .editorconfig                  # EditorConfig configuration
├── .markdownlint.json             # Markdownlint configuration
├── .pre-commit-config.yaml        # Pre-commit hooks configuration
├── pyproject.toml                 # Project configuration
├── README.md                      # Project README
├── generated/
│   └── docs-copilot/              # Generated documentation (Copilot)
├── scripts/
│   └── setup.sh                   # Setup script
├── src/                           # Source code
└── tests/                         # Test files
```

## Troubleshooting

### Pre-commit hooks not running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### Virtual environment issues

```bash
# Remove and recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/Scripts/activate
```

### Git Bash not found (Windows)

Install Git for Windows from https://git-scm.com/download/win

## Additional Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pyright Documentation](https://microsoft.github.io/pyright/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/README.md)

