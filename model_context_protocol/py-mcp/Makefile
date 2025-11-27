# Makefile for py-mcp project
# Commands for common development tasks

.PHONY: help setup dev deps lint format check test coverage clean pre-commit docs

help:
	@echo "Available commands:"
	@echo "  make setup          - Initial project setup (virtual environment, dependencies, hooks)"
	@echo "  make dev            - Activate development environment"
	@echo "  make deps           - Install dependencies"
	@echo "  make lint           - Run ruff linter and pyright type checker"
	@echo "  make format         - Format code with ruff"
	@echo "  make check          - Run linter and formatter (with auto-fix)"
	@echo "  make test           - Run tests"
	@echo "  make coverage       - Run tests with coverage report"
	@echo "  make pre-commit     - Run pre-commit hooks on all files"
	@echo "  make clean          - Clean up generated files and caches"
	@echo "  make markdown-lint  - Lint markdown files"

setup:
	@bash scripts/setup.sh

dev:
	@echo "To activate the virtual environment, run:"
	@echo "  source .venv/Scripts/activate  # On Git Bash/Linux/Mac"

deps:
	python -m pip install --upgrade pip setuptools wheel
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/
	pyright

format:
	ruff format src/ tests/
	markdownlint-cli2 "**/*.md"

check: format
	ruff check --fix src/ tests/
	pyright

test:
	pytest

coverage:
	pytest --cov=src --cov-report=html --cov-report=term tests/
	@echo "Coverage report generated in htmlcov/index.html"

pre-commit:
	pre-commit run --all-files

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pyright" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage*" -delete
	@echo "Clean up completed"

markdown-lint:
	markdownlint-cli2 "**/*.md" "#.git"

.DEFAULT_GOAL := help

