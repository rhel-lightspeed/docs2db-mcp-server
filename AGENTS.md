# AGENTS.md

Knowledge base for AI agents working on this repository.

## Project Overview

docs2db-mcp-server is an MCP (Model Context Protocol) server that exposes docs2db-api's RAG engine as tools for AI assistants. It provides semantic and hybrid search capabilities for RHEL documentation.

**Stack:** FastMCP → docs2db-api (UniversalRAGEngine) → PostgreSQL/pgvector

**Related repositories:**

- [docs2db](https://github.com/rhel-lightspeed/docs2db) — builds the RAG database that this server queries
- [docs2db-api](https://github.com/rhel-lightspeed/docs2db-api) — RAG query engine this server wraps
- [docs2db-mcp-server](https://github.com/rhel-lightspeed/docs2db-mcp-server) — this repo

**Author:** Ellis Low (elow@redhat.com)
**License:** Apache-2.0
**Python:** >=3.12,<3.14
**Package manager:** uv
**MCP framework:** FastMCP

## Development Environment

```bash
# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run linting/formatting/type checks
uv run pre-commit run --all-files

# CI-safe test run (excludes tests needing external services)
make test-ci

# Run all tests
make test

# Type check
make typecheck

# Run the MCP server locally
export DOCS2DB_MCP_DB_HOST=localhost
export DOCS2DB_MCP_DB_PASSWORD=postgres
uv run python -m docs2db_mcp
```

## Code Architecture

```text
src/docs2db_mcp/
├── __init__.py           # Package metadata
├── __main__.py           # Entry point (python -m docs2db_mcp)
├── config.py             # Pydantic settings (DOCS2DB_MCP_* env vars)
├── engine.py             # Singleton wrapper for UniversalRAGEngine
├── server.py             # FastMCP server instance and @mcp.tool() registrations
└── tools/
    ├── __init__.py
    └── search_documents.py  # MCP tool implementation
```

## Key Patterns and Conventions

- **Logging:** structlog (`structlog.get_logger()`). Do NOT use stdlib `logging`.
- **Log formatting:** Avoid f-strings in structlog calls. Use `%s` style for lazy evaluation.
- **Config/settings:** Pydantic `BaseSettings` with `env_prefix="DOCS2DB_MCP_"`. Environment variables are the ONLY configuration method. No config files.
- **Imports:** Absolute imports only. Example: `from docs2db_mcp.config import CONFIG`
- **FastMCP imports:** `from fastmcp import FastMCP, ToolAnnotations`
- **docs2db-api imports:** `from docs2db_api.rag.engine import UniversalRAGEngine`
- **Singleton engine:** The RAG engine uses a module-level singleton to avoid multiple initializations. See `engine.py`.
- **Async tools:** All MCP tools are `async def`. Use `async def` for all I/O operations.
- **ToolAnnotations:** Set `annotations=ToolAnnotations(readOnlyHint=True)` for read-only tools.
- **Tool returns:** Return dictionaries (JSON-serializable). Include error handling with graceful degradation.
- **Type hints:** Required for all functions and parameters. All modules start with descriptive docstrings.

### Singleton Pattern

```python
# engine.py
_engine: Optional[UniversalRAGEngine] = None

async def get_engine() -> UniversalRAGEngine:
    global _engine
    if _engine is None:
        _engine = UniversalRAGEngine(...)
        await _engine.start()
    return _engine
```

### MCP Tool Registration

```python
from docs2db_mcp.server import mcp

@mcp.tool(
    description="...",
    annotations=ToolAnnotations(readOnlyHint=True)
)
async def my_tool(param: str) -> dict:
    ...
```

### Configuration Singleton

```python
from docs2db_mcp.config import CONFIG

# Use throughout the app
database_url = CONFIG.database_url
```

## Testing

- **Framework:** pytest with pytest-asyncio, pytest-cov, pytest-randomly
- **Style:** Mock-based unit tests (no live PostgreSQL required)
- **Markers:** `no_ci` — tests requiring external services
- **CI test command:** `make test-ci` (runs `pytest -m "not no_ci"`)
- **Coverage:** Configured in `pyproject.toml`

```text
tests/
├── test_config.py          # Configuration tests
├── test_engine.py          # RAG engine tests
└── test_tools.py           # Tool invocation tests
```

```bash
# Run all tests
make test

# Run CI-safe tests only
make test-ci

# Run with coverage
uv run pytest --cov=docs2db_mcp --cov-report=html

# Run specific test
uv run pytest tests/test_tools.py -v
```

## Pre-commit Hooks

These run on every commit and in CI:

- **ruff** — linting with auto-fix
- **ruff-format** — code formatting
- **pyright** — type checking (`src/docs2db_mcp/` only)
- **gitleaks** — secret detection
- **check-toml** — TOML validation
- **end-of-file-fixer** — ensures files end with newline
- **trailing-whitespace** — removes trailing spaces

Run manually: `uv run pre-commit run --all-files`

## Gotchas

- `make test-ci` excludes `no_ci` marked tests
- Do NOT use `uv pip install -e .` — use `uv sync` only
- Type checking uses pyright, NOT mypy: `uv run pyright src/docs2db_mcp/`
- f-strings in structlog calls are discouraged (use `%s` style for lazy evaluation)
- `env_prefix="DOCS2DB_MCP_"` — all config env vars start with this prefix
- FastMCP tools must return JSON-serializable types (prefer `dict`)
- Container build: `podman build -t docs2db-mcp-server .`

## Branch Protection

- **Org-level ruleset:** "Minimum required Branch Protection" (rhel-lightspeed org)
- Requires 1 approving review from code owner (`@rhel-lightspeed/developers`)
- Last pusher cannot approve their own PR
- Cannot be bypassed

## Changelog Policy

Every PR must include an update to `CHANGELOG.md` under the `## [Unreleased]` section.

Follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format:

- **Added** — new features
- **Changed** — changes in existing functionality
- **Deprecated** — soon-to-be removed features
- **Removed** — removed features
- **Fixed** — bug fixes
- **Security** — vulnerability fixes

Keep entries concise (1-2 lines each). Reference issue numbers where applicable.
