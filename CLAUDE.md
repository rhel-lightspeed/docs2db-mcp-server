# docs2db-mcp-server Development Guide

## Project Overview
docs2db-mcp-server is an MCP (Model Context Protocol) server that exposes docs2db-api's RAG engine as tools for AI assistants. It provides semantic and hybrid search capabilities for RHEL documentation.

## Development Environment
- **Python**: >=3.10 (check `pyproject.toml` for supported versions)
- **Package Manager**: **uv** (required - do NOT use pip)
- **Required Commands**:
  - `uv sync` - Install dependencies
  - `uv run <command>` - Run commands in the uv environment
  - `uv add <package>` - Add new dependencies

## Code Architecture & Patterns

### Project Structure
```
src/docs2db_mcp/
├── __init__.py           # Package metadata
├── __main__.py           # Entry point (python -m docs2db_mcp)
├── config.py             # Pydantic settings with env vars
├── engine.py             # Singleton wrapper for UniversalRAGEngine
├── server.py             # FastMCP server instance
└── tools/
    ├── __init__.py
    └── search_documents.py  # MCP tool implementation
```

### Coding Standards

#### Package Manager - uv (REQUIRED)
**ALWAYS use uv, NEVER use pip:**
```bash
# ✅ CORRECT
uv add package-name
uv sync
uv run pytest
uv run python -m docs2db_mcp

# ❌ WRONG - Do not use pip
pip install package-name  # NO!
python -m pytest          # NO! (use uv run)
```

**Why uv?**
- Faster than pip
- Better dependency resolution
- Lock file for reproducibility
- Preferred by project owner

#### Imports & Dependencies
- Use absolute imports: `from docs2db_mcp.config import CONFIG`
- FastMCP imports: `from fastmcp import FastMCP, ToolAnnotations`
- docs2db-api imports: `from docs2db_api.rag.engine import UniversalRAGEngine`
- **ALWAYS** check `pyproject.toml` for existing dependencies before adding new ones
- **ALWAYS** verify current library versions in `pyproject.toml`

#### Module Standards
- All modules start with descriptive docstrings
- Use `logger = logging.getLogger(__name__)` for logging
- Type hints required for all functions and parameters
- Async functions for I/O operations

#### Configuration
- All config via Pydantic `BaseSettings` with `env_prefix="DOCS2DB_MCP_"`
- Environment variables are the ONLY configuration method
- No config files (following OKP pattern)
- Use `Field()` with descriptions and validation

#### Function Standards
- **Documentation**: All functions require docstrings
- **Type Annotations**: Complete type hints for parameters and returns
- **Naming**: snake_case, descriptive names
- **Async**: Use `async def` for I/O operations
- **Error Handling**: Log errors, return structured error responses

#### Tool Implementation
- Use `@mcp.tool()` decorator from FastMCP
- Set `annotations=ToolAnnotations(readOnlyHint=True)` for read-only tools
- Return dictionaries (JSON-serializable)
- Include error handling with graceful degradation
- Log all tool invocations

## Testing Framework

### Test Structure
```
tests/
├── test_config.py          # Configuration tests
├── test_engine.py          # RAG engine tests
└── test_tools.py           # Tool invocation tests
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=docs2db_mcp --cov-report=html

# Run specific test
uv run pytest tests/test_tools.py -v
```

## Development Workflow

### Initial Setup
```bash
# Clone repo (if not already)
cd ~/Documents/Development/docs2db-mcp-server

# Install dependencies with uv
uv sync

# Install in editable mode
uv pip install -e .
```

### Running the Server
```bash
# Set environment variables
export DOCS2DB_MCP_DB_HOST=localhost
export DOCS2DB_MCP_DB_PASSWORD=postgres

# Run the server
uv run python -m docs2db_mcp

# Or with custom config
DOCS2DB_MCP_PORT=8003 uv run python -m docs2db_mcp
```

### Running the Standalone Test
```bash
cd demos/standalone
uv run python test_mcp.py
```

### Building Container
```bash
# Build with podman
podman build -t docs2db-mcp-server .

# Or with docker
docker build -t docs2db-mcp-server .

# Run container
podman run -d \
  -p 8002:8002 \
  -e DOCS2DB_MCP_DB_HOST=postgres \
  -e DOCS2DB_MCP_DB_PASSWORD=postgres \
  docs2db-mcp-server
```

## Quality Assurance

### Linting & Type Checking
```bash
# Run ruff linter
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Type checking with mypy
uv run mypy src/
```

### Code Formatting
```bash
# Format with ruff
uv run ruff format .
```

## Adding New Dependencies

**CRITICAL:** Always use uv to add dependencies:

```bash
# Add production dependency
uv add package-name

# Add development dependency
uv add --dev pytest-something

# Sync after changes
uv sync
```

This updates `pyproject.toml` and `uv.lock` automatically.

## Key Dependencies
**IMPORTANT**: Always check `pyproject.toml` for current versions:
- **fastmcp**: FastMCP framework (>=2.14.4, <3)
- **mcp**: Official MCP SDK (>=1.9.3)
- **docs2db-api**: RAG query engine
- **pydantic**: Data validation
- **pydantic-settings**: Configuration management

## Architecture Patterns

### Singleton Pattern
The RAG engine uses a singleton pattern to avoid multiple initializations:

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
Tools are registered via decorators:

```python
from docs2db_mcp.server import mcp

@mcp.tool(
    description="...",
    annotations=ToolAnnotations(readOnlyHint=True)
)
async def my_tool(param: str) -> dict:
    # Implementation
    pass
```

### Configuration Singleton
Configuration is loaded once globally:

```python
from docs2db_mcp.config import CONFIG

# Use throughout the app
database_url = CONFIG.database_url
```

## Release Process

### Version Bumping
1. Update version in `src/docs2db_mcp/__init__.py`
2. Update version in `pyproject.toml`
3. Add entry to `CHANGELOG.md`
4. Commit: `git commit -m "Bump version to X.Y.Z"`
5. Tag: `git tag vX.Y.Z`

### Building for PyPI
```bash
# Install build tools
uv add --dev build twine

# Build distributions
uv run python -m build

# Check the build
uv run twine check dist/*

# Upload to PyPI
uv run twine upload dist/*
```

## Troubleshooting

### "Command not found: uv"
Install uv:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with brew
brew install uv
```

### "No module named 'docs2db_mcp'"
Install in editable mode:
```bash
uv pip install -e .
```

### "Connection refused to PostgreSQL"
Check database is running:
```bash
psql -h localhost -U postgres -d ragdb -c "SELECT 1"
```

Verify environment variables:
```bash
echo $DOCS2DB_MCP_DB_HOST
echo $DOCS2DB_MCP_DB_DATABASE
```

### "Module 'docs2db_api' not found"
Ensure docs2db-api is installed:
```bash
uv add docs2db-api
uv sync
```

## Contributing

1. Always use `uv` for dependency management
2. Run linters before committing: `uv run ruff check .`
3. Add tests for new functionality
4. Update CHANGELOG.md
5. Follow existing code patterns

## Related Documentation

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://modelcontextprotocol.io/)
- [docs2db-api](https://github.com/rhel-lightspeed/docs2db-api)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
