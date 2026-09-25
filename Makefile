.PHONY: install run test lint clean help

help:
	@echo "Available commands:"
	@echo "  install    Install dependencies"
	@echo "  run        Run the application"
	@echo "  test       Run tests"
	@echo "  lint       Run linters (ruff, mypy)"
	@echo "  clean      Clean build artifacts"

install:
	pip install -e .
	pip install pytest ruff mypy

run:
	legal-vacancy-tracker

test:
	pytest

lint:
	ruff check .
	mypy .

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +
