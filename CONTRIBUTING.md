# Contributing to docs2db-mcp-server

Thank you for your interest in contributing to docs2db-mcp-server! This guide covers environment setup and development workflow.

## Development Setup

### Prerequisites

- Python 3.12
- [uv](https://github.com/astral-sh/uv) — fast Python package installer and project manager
- A running [docs2db-api](https://github.com/rhel-lightspeed/docs2db-api) instance (for integration testing)

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rhel-lightspeed/docs2db-mcp-server
   cd docs2db-mcp-server
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

## Running the MCP Server

Set the required environment variables then start the server:

```bash
export DOCS2DB_MCP_DB_HOST=localhost
export DOCS2DB_MCP_DB_PASSWORD=postgres

uv run python -m docs2db_mcp
```

All configuration is via `DOCS2DB_MCP_*` environment variables. See `src/docs2db_mcp/config.py` for the full list.

```bash
export DOCS2DB_MCP_PORT=8003 uv run python -m docs2db_mcp
```

## Container Build

```bash
podman build -t docs2db-mcp-server .

podman run -d \
  -p 8002:8002 \
  -e DOCS2DB_MCP_DB_HOST=postgres \
  -e DOCS2DB_MCP_DB_PASSWORD=postgres \
  docs2db-mcp-server
```

Docker works identically (substitute `docker` for `podman`).

## Testing

Tests are mock-based and do not require a live database.

```bash
make test-ci
```

To run specific tests or with coverage:

```bash
uv run pytest tests/test_tools.py -v
uv run pytest --cov=docs2db_mcp --cov-report=html
```

`no_ci` marker: tests decorated with `@pytest.mark.no_ci` require external services and are excluded from `make test-ci`.

## Code Quality

Pre-commit hooks run automatically on every commit. They handle linting, formatting, type checking, and secret detection.

```bash
uv run pre-commit run --all-files
```

Individual tools:

```bash
uv run ruff check src/
uv run ruff format --check src/
uv run pyright src/docs2db_mcp/
```

Makefile shortcuts:

```bash
make lint       # ruff check
make format     # ruff format
make typecheck  # pyright
```

## Continuous Integration

Pull requests are automatically checked by GitHub Actions:

- **Lint**: ruff (linting + formatting) and pyright (type checking)
- **Test**: `make test-ci` (no external services required)

Both checks must pass before merge.

## Making Changes

### Branching

```bash
git checkout -b feature/your-feature-name
```

### Commit Messages

Write clear commit messages using conventional commit style:

```
feat: add keyword search tool

- Implement BM25-based keyword search endpoint
- Add result deduplication across search strategies
```

### Submitting Changes

1. Ensure pre-commit checks pass: `uv run pre-commit run --all-files`
2. Ensure tests pass: `make test-ci`
3. Update `CHANGELOG.md` under `## [Unreleased]`
4. Push your branch and open a pull request

## Project Structure

```
docs2db-mcp-server/
├── src/docs2db_mcp/       # Main package
│   ├── __init__.py
│   ├── __main__.py        # Entry point
│   ├── config.py          # Pydantic settings (DOCS2DB_MCP_*)
│   ├── engine.py          # Singleton RAG engine wrapper
│   ├── server.py          # FastMCP instance
│   └── tools/             # MCP tool implementations
├── tests/                 # Test suite (mock-based)
├── demos/                 # Demo scripts
├── Containerfile          # Container image definition
├── Makefile               # Development tasks
└── pyproject.toml         # Project config and dependencies
```

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 license.
