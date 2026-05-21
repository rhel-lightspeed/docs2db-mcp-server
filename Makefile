.PHONY: test test-ci lint format typecheck clean help

test:
	uv run pytest

test-ci:
	uv run pytest -m "not no_ci"

lint:
	uv run ruff check --fix src/ tests/ demos/

format:
	uv run ruff format src/ tests/ demos/

typecheck:
	uv run pyright src/docs2db_mcp/

clean:
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage dist

help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | awk -F: '{print $$1}' | sort
