.PHONY: help test test-ci lint clean

help:
	@echo "Available targets:"
	@echo "  test    - Run all tests"
	@echo "  test-ci - Run CI tests (excluding no_ci marked tests)"
	@echo "  lint    - Run all pre-commit checks (ruff, pyright, etc.)"
	@echo "  clean   - Remove generated files"

test:
	uv run pytest

test-ci:
	uv run pytest -m "not no_ci"

lint:
	uv run pre-commit run --all-files

clean:
	rm -rf .pytest_cache .ruff_cache htmlcov dist
