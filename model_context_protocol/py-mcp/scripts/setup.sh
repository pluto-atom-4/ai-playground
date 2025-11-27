#!/usr/bin/env bash
# Setup script for py-mcp project
# This script initializes the development environment

set -e

echo "🚀 Setting up py-mcp project..."
echo ""

# Check if we're using bash
if [ -z "$BASH_VERSION" ]; then
    echo "⚠️  Please run this script with bash (git bash on Windows)"
    exit 1
fi

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/Scripts/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel
echo "✅ pip upgraded"
echo ""

# Install project dependencies
echo "📚 Installing project dependencies..."
pip install -e ".[dev]"
echo "✅ Project dependencies installed"
echo ""

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install
echo "✅ Pre-commit hooks installed"
echo ""

# Create generated/docs-copilot directory if it doesn't exist
if [ ! -d "generated/docs-copilot" ]; then
    echo "📁 Creating generated/docs-copilot directory..."
    mkdir -p generated/docs-copilot
    touch generated/docs-copilot/.gitkeep
    echo "✅ Directory created"
else
    echo "✅ generated/docs-copilot directory already exists"
fi
echo ""

echo "✨ Setup complete! You're ready to develop."
echo ""
echo "Next steps:"
echo "  - Activate virtual environment: source .venv/Scripts/activate"
echo "  - Run pre-commit: pre-commit run --all-files"
echo "  - Run tests: pytest"
echo "  - Format code: ruff format"
echo "  - Lint code: ruff check --fix"
echo "  - Type check: pyright"

