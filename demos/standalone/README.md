# Standalone Test Demo

Simple test script to verify the docs2db MCP server functionality without requiring llama-stack or other MCP clients.

## Prerequisites

1. PostgreSQL with pgvector running
2. docs2db RAG database loaded (see [docs2db](https://github.com/rhel-lightspeed/docs2db))

## Running the Test

```bash
# Run the test (uses localhost:5432/ragdb defaults)
uv run python test_mcp.py

# Or with custom database
export DOCS2DB_MCP_DB_HOST=myhost
export DOCS2DB_MCP_DB_PASSWORD=mysecret
uv run python test_mcp.py
```

## Expected Output

The script runs 3 test queries and displays:
- Number of results found
- Similarity scores
- Source files
- Text excerpts
- Contextual information (if available)

## Troubleshooting

**Connection refused**:
- Check PostgreSQL is running: `psql -h localhost -U postgres -d ragdb`
- Verify environment variables match your setup

**No results found**:
- Verify database has data: `psql -d ragdb -c "SELECT COUNT(*) FROM chunks;"`
- Check similarity threshold (try lowering to 0.5)

**Module not found**:
- Install package: `uv pip install -e ../..`
- Or add to PYTHONPATH: `export PYTHONPATH=../../src:$PYTHONPATH`
