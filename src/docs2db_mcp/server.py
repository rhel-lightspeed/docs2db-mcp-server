"""FastMCP server instance and initialization."""

import sys

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog

from fastmcp import FastMCP

from docs2db_mcp.config import CONFIG
from docs2db_mcp.engine import health_check
from docs2db_mcp.engine import shutdown_engine


logger = structlog.get_logger(__name__)


@asynccontextmanager
async def engine_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Run startup health check and manage engine lifecycle.

    The server will not accept tool calls until the health check passes.
    If it fails, the server raises and refuses to start.
    """
    await health_check()

    # docs2db-api configures structlog to stdout at import time (triggered
    # by health_check → get_engine).  For non-SSE transports stdout is
    # reserved for MCP protocol messages, so redirect structlog to stderr.
    if CONFIG.transport != "sse":
        import structlog

        structlog.configure(
            logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
            cache_logger_on_first_use=False,
        )

    try:
        yield {}
    finally:
        await shutdown_engine()


mcp = FastMCP(
    "docs2db-rag",
    instructions=(
        "RAG search using docs2db for RHEL documentation. "
        "Use search_documents to find relevant information from "
        "RHEL documentation, knowledge base articles, and guides."
    ),
    lifespan=engine_lifespan,
)

# Import tools to register them with the MCP server
# This must happen after mcp instance is created
from docs2db_mcp.tools import search_documents  # noqa: F401, E402


logger.info("MCP server 'docs2db-rag' initialized")
