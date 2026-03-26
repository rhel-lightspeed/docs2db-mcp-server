# docs2db-mcp-server

MCP server for docs2db-api RAG queries. Provides semantic and hybrid search tools for RHEL documentation. Compatible with llama-stack, Goose, Claude Desktop, and other MCP clients.


## Features

- **Hybrid Search**: Combines vector similarity and BM25 keyword search with Reciprocal Rank Fusion
- **Cross-Encoder Reranking**: Improves result quality using ms-marco-MiniLM-L-6-v2
- **MCP Protocol**: Standard Model Context Protocol via FastMCP
- **SSE Transport**: Server-Sent Events for real-time streaming
- **Configurable**: Environment variables for all settings
- **Production Ready**: Containerized, non-root user, health checks

## Installation

### Prerequisites

Install [uv](https://docs.astral.sh/uv/):

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with brew
brew install uv
```

### From PyPI

```bash
uv add docs2db-mcp-server
```

### From Source

```bash
git clone https://github.com/rhel-lightspeed/docs2db-mcp-server.git
cd docs2db-mcp-server
uv sync
uv pip install -e .
```

## Quick Start

### Prerequisites

1. **PostgreSQL with pgvector** containing docs2db RAG database
2. **docs2db** to build the RAG database (see [docs2db](https://github.com/rhel-lightspeed/docs2db))

### Running the Server

```bash
# Start the MCP server (uses localhost defaults)
uv run python -m docs2db_mcp

```

Default configuration connects to `postgresql://postgres:postgres@localhost:5432/ragdb`

Server will start on `http://localhost:8002/sse`

### Using with llama-stack

Add to your `run.yaml`:

```yaml
tool_runtime:
  - provider_id: model-context-protocol
    provider_type: remote::model-context-protocol

registered_resources:
  tool_groups:
    - toolgroup_id: mcp::docs2db-rag
      provider_id: model-context-protocol
      mcp_endpoint:
        uri: http://localhost:8002/sse
```

### Using with Goose

Add to `~/.config/goose/config.yaml`:

```yaml
extensions:
  docs2db-rag:
    enabled: true
    type: stdio
    name: docs2db-rag
    cmd: uv
    args:
    - run
    - python
    - -m
    - docs2db_mcp
    envs:
      DOCS2DB_MCP_TRANSPORT: stdio
```

### Using with Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docs2db-rag": {
      "command": "uv",
      "args": ["run", "python", "-m", "docs2db_mcp"]
    }
  }
}
```

## Configuration

All configuration via environment variables with `DOCS2DB_MCP_` prefix.

**Note**: For stdio transport, `DOCS2DB_LOG_LEVEL` is automatically set to `CRITICAL` to minimize startup logs. Set manually if needed.

### MCP Server Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCS2DB_MCP_TRANSPORT` | `sse` | Transport type (sse/stdio) |
| `DOCS2DB_MCP_HOST` | `0.0.0.0` | Bind address |
| `DOCS2DB_MCP_PORT` | `8002` | Port number |
| `DOCS2DB_MCP_LOG_LEVEL` | `INFO` | Logging level |
| `DOCS2DB_MCP_SHOW_BANNER` | `true` | Show FastMCP banner (auto-suppressed for stdio) |

### Database Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCS2DB_MCP_DB_HOST` | `localhost` | PostgreSQL host |
| `DOCS2DB_MCP_DB_PORT` | `5432` | PostgreSQL port |
| `DOCS2DB_MCP_DB_DATABASE` | `ragdb` | Database name |
| `DOCS2DB_MCP_DB_USER` | `postgres` | Database user |
| `DOCS2DB_MCP_DB_PASSWORD` | `postgres` | Database password |

### RAG Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCS2DB_MCP_RAG_SIMILARITY_THRESHOLD` | `0.7` | Minimum similarity score |
| `DOCS2DB_MCP_RAG_MAX_CHUNKS` | `5` | Maximum chunks to return |
| `DOCS2DB_MCP_RAG_ENABLE_RERANKING` | `true` | Enable cross-encoder reranking |

## Tools

### search_documents

Search RHEL documentation using hybrid search (vector + BM25).

**Parameters:**
- `query` (string, required): Search query
- `max_chunks` (integer, optional): Maximum chunks to return (default: 5)
- `similarity_threshold` (float, optional): Minimum similarity score (default: 0.7)
- `enable_reranking` (boolean, optional): Enable cross-encoder reranking (default: true)

**Returns:**
```json
{
  "chunks": [
    {
      "text": "Chunk content...",
      "contextual_text": "LLM-generated context...",
      "similarity": 0.85,
      "source": "path/to/source/file.html",
      "metadata": {...}
    }
  ],
  "query_used": "original query"
}
```

## Docker/Podman

### Build Image

```bash
podman build -t docs2db-mcp-server .
```

### Run Container

```bash
podman run -d \
  --name docs2db-mcp \
  -p 8002:8002 \
  -e DOCS2DB_MCP_DB_HOST=postgres \
  -e DOCS2DB_MCP_DB_PASSWORD=mysecret \
  docs2db-mcp-server
```

### Docker Compose / Podman Compose

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_PASSWORD: postgres
    volumes:
      - ragdb:/var/lib/postgresql/data
      - ./ragdb_dump.sql:/docker-entrypoint-initdb.d/init.sql

  docs2db-mcp:
    image: docs2db-mcp-server
    ports:
      - "8002:8002"
    environment:
      DOCS2DB_MCP_DB_HOST: postgres
      DOCS2DB_MCP_DB_PASSWORD: postgres
    depends_on:
      - postgres
```

## Development

```bash
# Clone repo
git clone https://github.com/rhel-lightspeed/docs2db-mcp-server.git
cd docs2db-mcp-server

# Install dependencies
uv sync
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run linters
uv run ruff check .
uv run mypy src/
```

## Architecture

```
┌─────────────────────────────────────┐
│ MCP Client                          │
│ (llama-stack, Goose, Claude, etc.)  │
└──────────────┬──────────────────────┘
               │ MCP Protocol (SSE/stdio)
               ↓
┌─────────────────────────────────────┐
│ docs2db-mcp-server                  │
│                                     │
│ FastMCP Server                      │
│   └─ search_documents (tool)        │
│         ↓                           │
│   UniversalRAGEngine                │
│   (from docs2db-api)                │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│ PostgreSQL + pgvector               │
│ (docs2db RAG database)              │
└─────────────────────────────────────┘
```

## Related Projects

- [docs2db](https://github.com/rhel-lightspeed/docs2db) - Build RAG databases from documents
- [docs2db-api](https://github.com/rhel-lightspeed/docs2db-api) - Query API for docs2db databases
- [linux-mcp-server](https://github.com/rhel-lightspeed/linux-mcp-server) - MCP server for Linux diagnostics

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please open an issue or pull request.

## Support

- **Issues**: https://github.com/rhel-lightspeed/docs2db-mcp-server/issues
- **Discussions**: https://github.com/rhel-lightspeed/docs2db-mcp-server/discussions
